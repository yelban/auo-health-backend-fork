from datetime import datetime, timedelta
from io import StringIO
from typing import Any, Dict, List
from uuid import UUID

import pandas as pd
from azure.storage.blob import BlobSasPermissions, generate_blob_sas
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Depends
from numpy.polynomial.polynomial import Polynomial
from pydantic import BaseModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud, models, schemas
from auo_project.core.config import settings
from auo_project.core.constants import MAX_DEPTH_RATIO
from auo_project.core.file import get_max_amp_depth_of_range
from auo_project.core.utils import (
    compare_cn_diff,
    get_hr_type,
    get_measure_strength,
    get_measure_width,
    get_subject_schema,
    safe_divide,
)
from auo_project.web.api import deps

router = APIRouter()


class Memo(BaseModel):
    content: str = Field(None, title="內容")


class Link(BaseModel):
    self: str
    next: str = None
    prev: str = None


class SubjectPage(BaseModel):
    page: int
    per_page: int
    page_count: int
    total_count: int
    link: Link
    items: List["SubjectReadWithMeasures"]


class BaseChart(BaseModel):
    chart_type: str = Field(title="圖表類型")
    data: List[Dict[str, Any]] = Field(title="對應 data")
    x_field: str = Field(title="對應 xField")
    y_field: str = Field(title="對應 yField")


class ScatterChart(BaseChart):
    chart_type: str = Field("scatter", title="圖表類型")
    regression_type: str = Field(
        None,
        title="linear, exp, loess, log, poly, pow, quad",
    )
    regression_points: List[List[float]] = Field([], title="regressionLine.algorithm")


class LineChart(BaseChart):
    chart_type: str = Field("line", title="圖表類型")


class MeasureSixSecPWResponse(BaseModel):
    l_cu: LineChart = Field(title="左寸")
    l_qu: LineChart = Field(title="左關")
    l_ch: LineChart = Field(title="左尺")
    r_cu: LineChart = Field(title="右寸")
    r_qu: LineChart = Field(title="右關")
    r_ch: LineChart = Field(title="右尺")


class ColumnChart(BaseChart):
    chart_type: str = Field("column", title="圖表類型")


class CNChart(BaseModel):
    l_cu: ColumnChart = Field(title="左寸")
    l_qu: ColumnChart = Field(title="左關")
    l_ch: ColumnChart = Field(title="左尺")
    r_cu: ColumnChart = Field(title="右寸")
    r_qu: ColumnChart = Field(title="右關")
    r_ch: ColumnChart = Field(title="右尺")


def get_poly_points(x, y, degree, step):
    if x.shape[0] == 0 or y.shape[0] == 0:
        return []
    p = Polynomial.fit(x, y, deg=degree)
    points = [
        [round(i, 1), round(p(i), 1)]
        for i in range(int(x[0]), int(x[-1]) + 1, step)
        if round(i, 1) >= 0
    ]
    return points


def get_scatter_chart(data):
    if not data:
        return {
            "static_amp": ScatterChart(
                data=[],
                x_field="static",
                y_field="amp",
            ),
            "depth_amp": ScatterChart(
                data=[],
                x_field="depth",
                y_field="amp",
            ),
        }

    if not isinstance(data, str):
        raise Exception("file type not valid")
    file = StringIO(data)
    names = ("amp", "depth", "slope", "static")
    df = pd.read_csv(file, names=names, sep="\t")
    for c in names:
        df.loc[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna()
    df = df.assign(depth=df.depth / 0.2)

    return {
        "static_amp": ScatterChart(
            data=df[["static", "amp"]].to_dict("records"),
            x_field="static",
            y_field="amp",
            regression_points=get_poly_points(
                x=df.static.values,
                y=df.amp.values,
                degree=7,
                step=2,
            ),
        ),
        "depth_amp": ScatterChart(
            data=df[["depth", "amp"]].to_dict("records"),
            x_field="depth",
            y_field="amp",
            regression_points=get_poly_points(
                x=df.depth.values,
                y=df.amp.values,
                degree=7,
                step=1,
            ),
        ),
    }


@router.get("/{measure_id}", response_model=schemas.MeasureDetailResponse)
async def get_measure_summary(
    measure_id: UUID,
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    measure = await crud.measure_info.get(
        db_session=db_session,
        id=measure_id,
        relations=[
            "bcq",
            "statistics",
            "tongue",
            "raw",
            "subject",
            "measure_survey_result",
        ],
    )
    if not measure:
        raise HTTPException(
            status_code=400,
            detail=f"Not found measure id: {measure_id}",
        )
    if measure.org_id != current_user.org_id:
        raise HTTPException(
            status_code=400,
            detail=f"Measure id: {measure_id} not belong to org id: {current_user.org_id}",
        )

    subject = measure.subject
    standard_measure_info = None
    if subject.standard_measure_id:
        standard_measure_info = await crud.measure_info.get(
            db_session=db_session,
            id=subject.standard_measure_id,
        )

    front_tongue_image_url = None
    back_tongue_image_url = None
    tongue = measure.tongue
    tongue_info = {}
    if tongue:
        tongue_info = schemas.TongueInfo(
            tongue_color=tongue.tongue_color,
            tongue_shap=tongue.tongue_shap,
            tongue_status1=tongue.tongue_status1,
            tongue_status2=tongue.tongue_status2,
            tongue_coating_color=tongue.tongue_coating_color,
            tongue_coating_status=tongue.tongue_coating_status,
            tongue_coating_bottom=tongue.tongue_coating_bottom,
        )
        if tongue.up_img_uri:
            container_name = settings.AZURE_STORAGE_CONTAINER_INTERNET_IMAGE
            file_path = tongue.up_img_uri
            expiry = datetime.utcnow() + timedelta(minutes=15)
            sas_token = generate_blob_sas(
                account_name=settings.AZURE_STORAGE_ACCOUNT_INTERNET,
                container_name=container_name,
                blob_name=file_path,
                account_key=settings.AZURE_STORAGE_KEY_INTERNET,
                permission=BlobSasPermissions(read=True),
                expiry=expiry,
                # TODO: add ip
            )
            front_tongue_image_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_INTERNET}.blob.core.windows.net/{container_name}/{file_path}?{sas_token}"

        if tongue.down_img_uri:
            container_name = settings.AZURE_STORAGE_CONTAINER_INTERNET_IMAGE
            file_path = tongue.down_img_uri
            expiry = datetime.utcnow() + timedelta(minutes=15)
            sas_token = generate_blob_sas(
                account_name=settings.AZURE_STORAGE_ACCOUNT_INTERNET,
                container_name=container_name,
                blob_name=file_path,
                account_key=settings.AZURE_STORAGE_KEY_INTERNET,
                permission=BlobSasPermissions(read=True),
                expiry=expiry,
                # TODO: add ip
            )
            back_tongue_image_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_INTERNET}.blob.core.windows.net/{container_name}/{file_path}?{sas_token}"

    raw_data = measure.raw

    all_chart = {
        "l_cu": get_scatter_chart(raw_data.all_sec_analyze_raw_l_cu),
        "l_qu": get_scatter_chart(raw_data.all_sec_analyze_raw_l_qu),
        "l_ch": get_scatter_chart(raw_data.all_sec_analyze_raw_l_ch),
        "r_cu": get_scatter_chart(raw_data.all_sec_analyze_raw_r_cu),
        "r_qu": get_scatter_chart(raw_data.all_sec_analyze_raw_r_qu),
        "r_ch": get_scatter_chart(raw_data.all_sec_analyze_raw_r_ch),
    }

    all_sec = {
        # 振幅與靜態壓
        "static_amp": {
            "l_cu": all_chart["l_cu"]["static_amp"],
            "l_qu": all_chart["l_qu"]["static_amp"],
            "l_ch": all_chart["l_ch"]["static_amp"],
            "r_cu": all_chart["r_cu"]["static_amp"],
            "r_qu": all_chart["r_qu"]["static_amp"],
            "r_ch": all_chart["r_ch"]["static_amp"],
        },
        # 振幅與時間
        "depth_amp": {
            "l_cu": all_chart["l_cu"]["depth_amp"],
            "l_qu": all_chart["l_qu"]["depth_amp"],
            "l_ch": all_chart["l_ch"]["depth_amp"],
            "r_cu": all_chart["r_cu"]["depth_amp"],
            "r_qu": all_chart["r_qu"]["depth_amp"],
            "r_ch": all_chart["r_ch"]["depth_amp"],
        },
    }

    cn_dict = await crud.measure_statistic.get_means_dict(
        db_session=db_session,
        measure_id=measure_id,
    )
    cn_means_dict = await crud.measure_cn_mean.get_dict_by_sex(
        db_session=db_session,
        sex=subject.sex,
    )
    standard_cn_dict = {}
    if subject.standard_measure_id:
        standard_cn_dict = await crud.measure_statistic.get_means_dict(
            db_session=db_session,
            measure_id=subject.standard_measure_id,
        )

    cn = {
        "overall": {
            "l_cu": compare_cn_diff(cn_dict["l_cu"], cn_means_dict["l_cu"]),
            "l_qu": compare_cn_diff(cn_dict["l_qu"], cn_means_dict["l_qu"]),
            "l_ch": compare_cn_diff(cn_dict["l_ch"], cn_means_dict["l_ch"]),
            "r_cu": compare_cn_diff(cn_dict["r_cu"], cn_means_dict["r_cu"]),
            "r_qu": compare_cn_diff(cn_dict["r_qu"], cn_means_dict["r_qu"]),
            "r_ch": compare_cn_diff(cn_dict["r_ch"], cn_means_dict["r_ch"]),
        },
        "standard_value": {
            "l_cu": compare_cn_diff(cn_dict["l_cu"], standard_cn_dict.get("l_cu", {})),
            "l_qu": compare_cn_diff(cn_dict["l_qu"], standard_cn_dict.get("l_qu", {})),
            "l_ch": compare_cn_diff(cn_dict["l_ch"], standard_cn_dict.get("l_ch", {})),
            "r_cu": compare_cn_diff(cn_dict["r_cu"], standard_cn_dict.get("r_cu", {})),
            "r_qu": compare_cn_diff(cn_dict["r_qu"], standard_cn_dict.get("r_qu", {})),
            "r_ch": compare_cn_diff(cn_dict["r_ch"], standard_cn_dict.get("r_ch", {})),
        },
    }

    width_value_l_cu = safe_divide(measure.range_length_l_cu, 0.2)
    width_value_l_qu = safe_divide(measure.range_length_l_qu, 0.2)
    width_value_l_ch = safe_divide(measure.range_length_l_ch, 0.2)
    width_value_r_cu = safe_divide(measure.range_length_r_cu, 0.2)
    width_value_r_qu = safe_divide(measure.range_length_r_qu, 0.2)
    width_value_r_ch = safe_divide(measure.range_length_r_ch, 0.2)

    # TODO: remove me
    sbp = measure.sbp
    dbp = measure.dbp
    if (sbp is None or dbp is None) and measure.measure_survey_result is not None:
        survey_result_value = measure.measure_survey_result.value
        if sbp is None:
            sbp = survey_result_value.get("sbp", None)
        if dbp is None:
            dbp = survey_result_value.get("dbp", None)

    return schemas.MeasureDetailResponse(
        subject=get_subject_schema(org_name=current_user.org.name)(
            **jsonable_encoder(subject),
            standard_measure_info=standard_measure_info,
        ),
        measure=schemas.MeasureDetailRead(
            measure_time=measure.measure_time,
            measure_operator=measure.measure_operator,
            proj_num=measure.proj_num,
            sbp=sbp,
            dbp=dbp,
            memo=measure.memo,
            age=measure.age,
            height=measure.height,
            weight=measure.weight,
            bmi=measure.bmi,
            irregular_hr_l=measure.irregular_hr_l,
            irregular_hr_type_l=measure.irregular_hr_type_l,
            irregular_hr_r=measure.irregular_hr_r,
            irregular_hr_type_r=measure.irregular_hr_type_r,
            hr_l=measure.hr_l,
            hr_l_type=get_hr_type(measure.hr_l, measure.hr_r),
            hr_r=measure.hr_r,
            hr_r_type=get_hr_type(measure.hr_r, measure.hr_l),
            mean_prop_range_1_l_cu=measure.mean_prop_range_1_l_cu,
            mean_prop_range_2_l_cu=measure.mean_prop_range_2_l_cu,
            mean_prop_range_3_l_cu=measure.mean_prop_range_3_l_cu,
            mean_prop_range_1_l_qu=measure.mean_prop_range_1_l_qu,
            mean_prop_range_2_l_qu=measure.mean_prop_range_2_l_qu,
            mean_prop_range_3_l_qu=measure.mean_prop_range_3_l_qu,
            mean_prop_range_1_l_ch=measure.mean_prop_range_1_l_ch,
            mean_prop_range_2_l_ch=measure.mean_prop_range_2_l_ch,
            mean_prop_range_3_l_ch=measure.mean_prop_range_3_l_ch,
            mean_prop_range_1_r_cu=measure.mean_prop_range_1_r_cu,
            mean_prop_range_2_r_cu=measure.mean_prop_range_2_r_cu,
            mean_prop_range_3_r_cu=measure.mean_prop_range_3_r_cu,
            mean_prop_range_1_r_qu=measure.mean_prop_range_1_r_qu,
            mean_prop_range_2_r_qu=measure.mean_prop_range_2_r_qu,
            mean_prop_range_3_r_qu=measure.mean_prop_range_3_r_qu,
            mean_prop_range_1_r_ch=measure.mean_prop_range_1_r_ch,
            mean_prop_range_2_r_ch=measure.mean_prop_range_2_r_ch,
            mean_prop_range_3_r_ch=measure.mean_prop_range_3_r_ch,
            mean_prop_range_max_l_cu=get_max_amp_depth_of_range(
                static_range_start_hand_position=measure.static_range_start_l_cu,
                static_range_end_hand_position=measure.static_range_end_l_cu,
                static_max_amp_hand_position=measure.static_max_amp_l_cu,
                ratio=MAX_DEPTH_RATIO,
            ),
            mean_prop_range_max_l_qu=get_max_amp_depth_of_range(
                static_range_start_hand_position=measure.static_range_start_l_qu,
                static_range_end_hand_position=measure.static_range_end_l_qu,
                static_max_amp_hand_position=measure.static_max_amp_l_qu,
                ratio=MAX_DEPTH_RATIO,
            ),
            mean_prop_range_max_l_ch=get_max_amp_depth_of_range(
                static_range_start_hand_position=measure.static_range_start_l_ch,
                static_range_end_hand_position=measure.static_range_end_l_ch,
                static_max_amp_hand_position=measure.static_max_amp_l_ch,
                ratio=MAX_DEPTH_RATIO,
            ),
            mean_prop_range_max_r_cu=get_max_amp_depth_of_range(
                static_range_start_hand_position=measure.static_range_start_r_cu,
                static_range_end_hand_position=measure.static_range_end_r_cu,
                static_max_amp_hand_position=measure.static_max_amp_r_cu,
                ratio=MAX_DEPTH_RATIO,
            ),
            mean_prop_range_max_r_qu=get_max_amp_depth_of_range(
                static_range_start_hand_position=measure.static_range_start_r_qu,
                static_range_end_hand_position=measure.static_range_end_r_qu,
                static_max_amp_hand_position=measure.static_max_amp_r_qu,
                ratio=MAX_DEPTH_RATIO,
            ),
            mean_prop_range_max_r_ch=get_max_amp_depth_of_range(
                static_range_start_hand_position=measure.static_range_start_r_ch,
                static_range_end_hand_position=measure.static_range_end_r_ch,
                static_max_amp_hand_position=measure.static_max_amp_r_ch,
                ratio=MAX_DEPTH_RATIO,
            ),
            max_amp_depth_of_range_l_cu=get_max_amp_depth_of_range(
                static_range_start_hand_position=measure.static_range_start_l_cu,
                static_range_end_hand_position=measure.static_range_end_l_cu,
                static_max_amp_hand_position=measure.static_max_amp_l_cu,
                ratio=MAX_DEPTH_RATIO,
            ),
            max_amp_depth_of_range_l_qu=get_max_amp_depth_of_range(
                static_range_start_hand_position=measure.static_range_start_l_qu,
                static_range_end_hand_position=measure.static_range_end_l_qu,
                static_max_amp_hand_position=measure.static_max_amp_l_qu,
                ratio=MAX_DEPTH_RATIO,
            ),
            max_amp_depth_of_range_l_ch=get_max_amp_depth_of_range(
                static_range_start_hand_position=measure.static_range_start_l_ch,
                static_range_end_hand_position=measure.static_range_end_l_ch,
                static_max_amp_hand_position=measure.static_max_amp_l_ch,
                ratio=MAX_DEPTH_RATIO,
            ),
            max_amp_depth_of_range_r_cu=get_max_amp_depth_of_range(
                static_range_start_hand_position=measure.static_range_start_r_cu,
                static_range_end_hand_position=measure.static_range_end_r_cu,
                static_max_amp_hand_position=measure.static_max_amp_r_cu,
                ratio=MAX_DEPTH_RATIO,
            ),
            max_amp_depth_of_range_r_qu=get_max_amp_depth_of_range(
                static_range_start_hand_position=measure.static_range_start_r_qu,
                static_range_end_hand_position=measure.static_range_end_r_qu,
                static_max_amp_hand_position=measure.static_max_amp_r_qu,
                ratio=MAX_DEPTH_RATIO,
            ),
            max_amp_depth_of_range_r_ch=get_max_amp_depth_of_range(
                static_range_start_hand_position=measure.static_range_start_r_ch,
                static_range_end_hand_position=measure.static_range_end_r_ch,
                static_max_amp_hand_position=measure.static_max_amp_r_ch,
                ratio=MAX_DEPTH_RATIO,
            ),
            max_amp_value_l_cu=measure.max_amp_value_l_cu,
            max_amp_value_l_qu=measure.max_amp_value_l_qu,
            max_amp_value_l_ch=measure.max_amp_value_l_ch,
            max_amp_value_r_cu=measure.max_amp_value_r_cu,
            max_amp_value_r_qu=measure.max_amp_value_r_qu,
            max_amp_value_r_ch=measure.max_amp_value_r_ch,
            max_slope_value_l_cu=measure.max_slope_value_l_cu,
            max_slope_value_l_qu=measure.max_slope_value_l_qu,
            max_slope_value_l_ch=measure.max_slope_value_l_ch,
            max_slope_value_r_cu=measure.max_slope_value_r_cu,
            max_slope_value_r_qu=measure.max_slope_value_r_qu,
            max_slope_value_r_ch=measure.max_slope_value_r_ch,
            strength_l_cu=get_measure_strength(
                measure.max_slope_value_l_cu,
                measure.max_amp_value_l_cu,
            ),
            strength_l_qu=get_measure_strength(
                measure.max_slope_value_l_qu,
                measure.max_amp_value_l_qu,
            ),
            strength_l_ch=get_measure_strength(
                measure.max_slope_value_l_ch,
                measure.max_amp_value_l_ch,
            ),
            strength_r_cu=get_measure_strength(
                measure.max_slope_value_r_cu,
                measure.max_amp_value_r_cu,
            ),
            strength_r_qu=get_measure_strength(
                measure.max_slope_value_r_qu,
                measure.max_amp_value_r_qu,
            ),
            strength_r_ch=get_measure_strength(
                measure.max_slope_value_r_ch,
                measure.max_amp_value_r_ch,
            ),
            width_l_cu=get_measure_width(
                measure.range_length_l_cu,
                measure.max_amp_value_l_cu,
                measure.max_slope_value_l_cu,
            ),
            width_l_qu=get_measure_width(
                measure.range_length_l_qu,
                measure.max_amp_value_l_qu,
                measure.max_slope_value_l_qu,
            ),
            width_l_ch=get_measure_width(
                measure.range_length_l_ch,
                measure.max_amp_value_l_ch,
                measure.max_slope_value_l_ch,
            ),
            width_r_cu=get_measure_width(
                measure.range_length_r_cu,
                measure.max_amp_value_r_cu,
                measure.max_slope_value_r_cu,
            ),
            width_r_qu=get_measure_width(
                measure.range_length_r_qu,
                measure.max_amp_value_r_qu,
                measure.max_slope_value_r_qu,
            ),
            width_r_ch=get_measure_width(
                measure.range_length_r_ch,
                measure.max_amp_value_r_ch,
                measure.max_slope_value_r_ch,
            ),
            width_value_l_cu=round(width_value_l_cu, 1) if width_value_l_cu else None,
            width_value_l_qu=round(width_value_l_qu, 1) if width_value_l_qu else None,
            width_value_l_ch=round(width_value_l_ch, 1) if width_value_l_ch else None,
            width_value_r_cu=round(width_value_r_cu, 1) if width_value_r_cu else None,
            width_value_r_qu=round(width_value_r_qu, 1) if width_value_r_qu else None,
            width_value_r_ch=round(width_value_r_ch, 1) if width_value_r_ch else None,
            comment=measure.comment,
            # TODO: changme
            bcq=schemas.BCQ(
                exist=measure.has_bcq,
                score_yang=measure.bcq.percentage_yang,
                score_yin=measure.bcq.percentage_yin,
                score_phlegm=measure.bcq.percentage_phlegm,
                score_yang_head=measure.bcq.percentage_yang_head,
                score_yang_chest=measure.bcq.percentage_yang_chest,
                score_yang_limbs=measure.bcq.percentage_yang_limbs,
                score_yang_abdomen=measure.bcq.percentage_yang_abdomen,
                score_yang_surface=measure.bcq.percentage_yang_surface,
                score_yin_head=measure.bcq.percentage_yin_head,
                score_yin_limbs=measure.bcq.percentage_yin_limbs,
                score_yin_gt=measure.bcq.percentage_yin_gt,
                score_yin_surface=measure.bcq.percentage_yin_surface,
                score_yin_abdomen=measure.bcq.percentage_yin_abdomen,
                score_phlegm_trunk=measure.bcq.percentage_phlegm_trunk,
                score_phlegm_surface=measure.bcq.percentage_phlegm_surface,
                score_phlegm_head=measure.bcq.percentage_phlegm_head,
                score_phlegm_gt=measure.bcq.percentage_phlegm_gt,
                percentage_yang=measure.bcq.percentage_yang,
                percentage_yin=measure.bcq.percentage_yin,
                percentage_phlegm=measure.bcq.percentage_phlegm,
                percentage_yang_head=0,
                percentage_yang_chest=0,
                percentage_yang_limbs=0,
                percentage_yang_abdomen=0,
                percentage_yang_surface=0,
                percentage_yin_head=0,
                percentage_yin_limbs=0,
                percentage_yin_gt=0,
                percentage_yin_surface=0,
                percentage_yin_abdomen=0,
                percentage_phlegm_trunk=0,
                percentage_phlegm_surface=0,
                percentage_phlegm_head=0,
                percentage_phlegm_gt=0,
            )
            if measure.has_bcq
            else {},
            all_sec=all_sec,
            cn=cn,
            tongue=schemas.Tongue(
                exist=True if tongue else False,
                info=tongue_info,
                image=schemas.TongueImage(
                    front=front_tongue_image_url or "",
                    back=back_tongue_image_url or "",
                ),
            ),
        ),
    )


@router.get("/mock/{measure_id}", response_model=schemas.MeasureDetailResponse)
async def get_mock_measure_summary(
    measure_id: UUID,
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    from datetime import date, datetime
    from random import choice, randrange

    from azure.storage.blob import BlobSasPermissions, generate_blob_sas

    container_name = "image"
    file_path = "tongue-front-sample.png"
    expiry = datetime.utcnow() + timedelta(minutes=15)
    sas_token = generate_blob_sas(
        account_name=settings.AZURE_STORAGE_ACCOUNT,
        container_name=container_name,
        blob_name="tongue-front-sample.png",
        account_key=settings.AZURE_STORAGE_KEY,
        permission=BlobSasPermissions(read=True),
        expiry=expiry,
        # ip
    )
    front_tongue_image_url = f"https://auotest.blob.core.windows.net/image/tongue-front-sample.png?{sas_token}"
    sas_token = generate_blob_sas(
        account_name=settings.AZURE_STORAGE_ACCOUNT,
        container_name=container_name,
        blob_name="tongue-back-sample.png",
        account_key=settings.AZURE_STORAGE_KEY,
        permission=BlobSasPermissions(read=True),
        expiry=expiry,
        # ip
    )
    back_tongue_image_url = f"https://auotest.blob.core.windows.net/image/tongue-back-sample.png?{sas_token}"

    static_amp_scatter_chart = ScatterChart(
        data=[
            {"static": 18.982, "amp": 2.876},
            {"static": 24.197, "amp": 0.555},
            {"static": 25.088, "amp": 1.234},
            {"static": 25.334, "amp": 0.83},
            {"static": 25.241, "amp": 0.565},
            {"static": 25.698, "amp": 0.437},
            {"static": 26.719, "amp": 0.657},
            {"static": 27.752, "amp": 0.951},
            {"static": 28.707, "amp": 0.647},
            {"static": 31.447, "amp": 1.398},
            {"static": 34.066, "amp": 1.03},
            {"static": 35.704, "amp": 0.444},
            {"static": 36.37, "amp": 1.479},
            {"static": 37.82, "amp": 1.176},
            {"static": 40.24, "amp": 1.995},
            {"static": 43.087, "amp": 2.091},
            {"static": 46.295, "amp": 2.803},
            {"static": 48.408, "amp": 2.898},
            {"static": 50.864, "amp": 2.618},
            {"static": 55.212, "amp": 3.979},
            {"static": 59.008, "amp": 4.637},
            {"static": 61.813, "amp": 4.729},
            {"static": 65.359, "amp": 5.112},
            {"static": 69.818, "amp": 5.825},
            {"static": 74.31, "amp": 7.001},
            {"static": 77.898, "amp": 7.739},
            {"static": 80.133, "amp": 7.774},
            {"static": 84.732, "amp": 9.513},
            {"static": 89.671, "amp": 11.523},
            {"static": 94.369, "amp": 12.707},
            {"static": 97.579, "amp": 12.707},
            {"static": 99.932, "amp": 12.517},
            {"static": 104.983, "amp": 16.042},
            {"static": 110.479, "amp": 17.102},
            {"static": 114.834, "amp": 18.422},
            {"static": 116.636, "amp": 17.284},
            {"static": 119.033, "amp": 18.705},
            {"static": 123.57, "amp": 22.006},
            {"static": 128.643, "amp": 23.629},
            {"static": 133.088, "amp": 25.912},
            {"static": 134.244, "amp": 25.576},
            {"static": 137.371, "amp": 26.918},
            {"static": 143.566, "amp": 33.138},
            {"static": 149.274, "amp": 34.125},
            {"static": 152.15, "amp": 35.898},
            {"static": 153.077, "amp": 36.264},
            {"static": 158.524, "amp": 39.836},
            {"static": 164.246, "amp": 42.631},
            {"static": 169.301, "amp": 43.374},
            {"static": 171.919, "amp": 40.435},
            {"static": 175.242, "amp": 40.106},
            {"static": 183.436, "amp": 40.743},
            {"static": 193.247, "amp": 40.435},
            {"static": 200.385, "amp": 37.944},
            {"static": 204.196, "amp": 31.488},
            {"static": 206.712, "amp": 25.432},
            {"static": 213.845, "amp": 19.557},
            {"static": 222.348, "amp": 14.771},
            {"static": 231.453, "amp": 10.8},
            {"static": 241.219, "amp": 7.658},
            {"static": 249.477, "amp": 2.788},
            {"static": 253.891, "amp": 0.783},
            {"static": 267.327, "amp": 2.142},
            {"static": 278.277, "amp": 1.356},
            {"static": 292.52, "amp": 1.854},
            {"static": 300.154, "amp": 1.892},
            {"static": 308.297, "amp": 1.235},
            {"static": 315.285, "amp": 4.892},
            {"static": 325.732, "amp": 0.588},
            {"static": 329.157, "amp": 2.268},
            {"static": 337.499, "amp": 1.5},
            {"static": 346.402, "amp": 1.12},
            {"static": 353.634, "amp": 3.686},
            {"static": 353.56, "amp": 2.862},
            {"static": 354.507, "amp": 1.164},
            {"static": 354.761, "amp": 0.0},
            {"static": 354.761, "amp": 0.0},
            {"static": 354.761, "amp": 0.0},
            {"static": 354.761, "amp": 0.0},
            {"static": 354.761, "amp": 0.0},
            {"static": 354.761, "amp": 0.0},
            {"static": 354.761, "amp": 0.0},
            {"static": 354.761, "amp": 0.0},
            {"static": 354.761, "amp": 0.0},
            {"static": 350.115, "amp": 9.935},
            {"static": 353.597, "amp": 12.244},
        ],
        x_field="static",
        y_field="amp",
    )

    depth_amp_scatter_chart = ScatterChart(
        data=[
            {"depth": 0.142, "amp": 2.876},
            {"depth": 0.396, "amp": 0.555},
            {"depth": 0.516, "amp": 1.234},
            {"depth": 0.684, "amp": 0.83},
            {"depth": 0.848, "amp": 0.565},
            {"depth": 1.004, "amp": 0.437},
            {"depth": 1.136, "amp": 0.657},
            {"depth": 1.29, "amp": 0.951},
            {"depth": 1.46, "amp": 0.647},
            {"depth": 1.606, "amp": 1.398},
            {"depth": 1.78, "amp": 1.03},
            {"depth": 1.9, "amp": 0.444},
            {"depth": 1.952, "amp": 1.479},
            {"depth": 2.12, "amp": 1.176},
            {"depth": 2.238, "amp": 1.995},
            {"depth": 2.402, "amp": 2.091},
            {"depth": 2.562, "amp": 2.803},
            {"depth": 2.72, "amp": 2.898},
            {"depth": 2.872, "amp": 2.618},
            {"depth": 3.022, "amp": 3.979},
            {"depth": 3.168, "amp": 4.637},
            {"depth": 3.32, "amp": 4.729},
            {"depth": 3.468, "amp": 5.112},
            {"depth": 3.618, "amp": 5.825},
            {"depth": 3.77, "amp": 7.001},
            {"depth": 3.922, "amp": 7.739},
            {"depth": 4.076, "amp": 7.774},
            {"depth": 4.23, "amp": 9.513},
            {"depth": 4.38, "amp": 11.523},
            {"depth": 4.53, "amp": 12.707},
            {"depth": 4.684, "amp": 12.707},
            {"depth": 4.838, "amp": 12.517},
            {"depth": 4.986, "amp": 16.042},
            {"depth": 5.14, "amp": 17.102},
            {"depth": 5.294, "amp": 18.422},
            {"depth": 5.448, "amp": 17.284},
            {"depth": 5.598, "amp": 18.705},
            {"depth": 5.744, "amp": 22.006},
            {"depth": 5.892, "amp": 23.629},
            {"depth": 6.04, "amp": 25.912},
            {"depth": 6.192, "amp": 25.576},
            {"depth": 6.34, "amp": 26.918},
            {"depth": 6.488, "amp": 33.138},
            {"depth": 6.638, "amp": 34.125},
            {"depth": 6.792, "amp": 35.898},
            {"depth": 6.944, "amp": 36.264},
            {"depth": 7.096, "amp": 39.836},
            {"depth": 7.246, "amp": 42.631},
            {"depth": 7.396, "amp": 43.374},
            {"depth": 7.546, "amp": 40.435},
            {"depth": 7.696, "amp": 40.106},
            {"depth": 7.84, "amp": 40.743},
            {"depth": 7.986, "amp": 40.435},
            {"depth": 8.13, "amp": 37.944},
            {"depth": 8.282, "amp": 31.488},
            {"depth": 8.428, "amp": 25.432},
            {"depth": 8.574, "amp": 19.557},
            {"depth": 8.718, "amp": 14.771},
            {"depth": 8.864, "amp": 10.8},
            {"depth": 9.02, "amp": 7.658},
            {"depth": 9.178, "amp": 2.788},
            {"depth": 9.238, "amp": 0.783},
            {"depth": 9.392, "amp": 2.142},
            {"depth": 9.55, "amp": 1.356},
            {"depth": 9.742, "amp": 1.854},
            {"depth": 9.874, "amp": 1.892},
            {"depth": 10.088, "amp": 1.235},
            {"depth": 10.2, "amp": 4.892},
            {"depth": 10.524, "amp": 0.588},
            {"depth": 10.58, "amp": 2.268},
            {"depth": 10.752, "amp": 1.5},
            {"depth": 10.9, "amp": 1.12},
            {"depth": 10.998, "amp": 3.686},
            {"depth": 11.252, "amp": 2.862},
            {"depth": 11.36, "amp": 1.164},
            {"depth": 11.66, "amp": 0.0},
            {"depth": 11.664, "amp": 0.0},
            {"depth": 11.666, "amp": 0.0},
            {"depth": 11.67, "amp": 0.0},
            {"depth": 11.672, "amp": 0.0},
            {"depth": 11.676, "amp": 0.0},
            {"depth": 11.678, "amp": 0.0},
            {"depth": 11.682, "amp": 0.0},
            {"depth": 11.684, "amp": 0.0},
            {"depth": 11.774, "amp": 9.935},
            {"depth": 11.962, "amp": 12.244},
        ],
        x_field="depth",
        y_field="amp",
    )

    all_sec = {
        "static_amp": {
            "l_cu": static_amp_scatter_chart,
            "l_qu": static_amp_scatter_chart,
            "l_ch": static_amp_scatter_chart,
            "r_cu": static_amp_scatter_chart,
            "r_qu": static_amp_scatter_chart,
            "r_ch": static_amp_scatter_chart,
        },
        "depth_amp": {
            "l_cu": depth_amp_scatter_chart,
            "l_qu": depth_amp_scatter_chart,
            "l_ch": depth_amp_scatter_chart,
            "r_cu": depth_amp_scatter_chart,
            "r_qu": depth_amp_scatter_chart,
            "r_ch": depth_amp_scatter_chart,
        },
    }

    def get_cn_chart():
        return {
            "data": [
                {"x": f"C{i}", "pct": randrange(0, 100), "type": choice(["pos", "neg"])}
                for i in range(1, 12)
            ],
            "x_field": "x",
            "y_field": "pct",
        }

    cn = {
        "overall": {
            "l_cu": get_cn_chart(),
            "l_qu": get_cn_chart(),
            "l_ch": get_cn_chart(),
            "r_cu": get_cn_chart(),
            "r_qu": get_cn_chart(),
            "r_ch": get_cn_chart(),
        },
        "standard_value": {
            "l_cu": get_cn_chart(),
            "l_qu": get_cn_chart(),
            "l_ch": get_cn_chart(),
            "r_cu": get_cn_chart(),
            "r_qu": get_cn_chart(),
            "r_ch": get_cn_chart(),
        },
    }

    return schemas.MeasureDetailResponse(
        subject=schemas.SubjectRead(
            sid="M123456789",
            name="陳小虎",
            birth_date=date.today(),
            sex=0,
            sex_label="男",
            memo="高山茶",
            id="45d7b6b4-8611-4f95-9263-dbdcb9b7b4e3",
        ),
        measure=schemas.MeasureDetailRead(
            measure_time=datetime.now(),
            measure_operator="DadaHu",
            proj_num="0000000001",
            sbp=180,
            dbp=180,
            memo="字數最多顯示九十個字字數最多顯示九十個字字數最多顯示九十個字字數最多顯示九十個字字數最多顯示九十個字字數最多顯示九十個字字數最多顯示九十個字字數最多顯示九十個字字數最多超過就點點",
            age=50,
            height=168,
            weight=58,
            bmi=20.5,
            irregular_hr_l=randrange(0, 2),
            irregular_hr_l_type=randrange(0, 2),
            irregular_hr_r=randrange(0, 2),
            irregular_hr_r_type=randrange(0, 2),
            hr_l=randrange(0, 100),
            hr_l_type=randrange(0, 3),
            hr_r=randrange(0, 100),
            hr_r_type=randrange(0, 3),
            # infos_analyze
            mean_prop_range_1_l_cu=20,
            mean_prop_range_2_l_cu=60,
            mean_prop_range_3_l_cu=20,
            mean_prop_range_1_l_qu=20,
            mean_prop_range_2_l_qu=60,
            mean_prop_range_3_l_qu=20,
            mean_prop_range_1_l_ch=20,
            mean_prop_range_2_l_ch=60,
            mean_prop_range_3_l_ch=20,
            mean_prop_range_1_r_cu=20,
            mean_prop_range_2_r_cu=20,
            mean_prop_range_3_r_cu=60,
            mean_prop_range_1_r_qu=60,
            mean_prop_range_2_r_qu=20,
            mean_prop_range_3_r_qu=20,
            mean_prop_range_1_r_ch=20,
            mean_prop_range_2_r_ch=60,
            mean_prop_range_3_r_ch=20,
            mean_prop_range_max_l_cu=randrange(0, 3),
            mean_prop_range_max_l_qu=randrange(0, 3),
            mean_prop_range_max_l_ch=randrange(0, 3),
            mean_prop_range_max_r_cu=randrange(0, 3),
            mean_prop_range_max_r_qu=randrange(0, 3),
            mean_prop_range_max_r_ch=randrange(0, 3),
            max_amp_depth_of_range_l_cu=randrange(0, 3),
            max_amp_depth_of_range_l_qu=randrange(0, 3),
            max_amp_depth_of_range_l_ch=randrange(0, 3),
            max_amp_depth_of_range_r_cu=randrange(0, 3),
            max_amp_depth_of_range_r_qu=randrange(0, 3),
            max_amp_depth_of_range_r_ch=randrange(0, 3),
            # infos_analyze
            max_amp_value_l_cu=randrange(0, 60),
            max_amp_value_l_qu=randrange(0, 60),
            max_amp_value_l_ch=randrange(0, 60),
            max_amp_value_r_cu=randrange(0, 60),
            max_amp_value_r_qu=randrange(0, 60),
            max_amp_value_r_ch=randrange(0, 60),
            # analyze_raw
            max_slope_value_l_cu=randrange(0, 200),
            max_slope_value_l_qu=randrange(0, 200),
            max_slope_value_l_ch=randrange(0, 200),
            max_slope_value_r_cu=randrange(0, 200),
            max_slope_value_r_qu=randrange(0, 200),
            max_slope_value_r_ch=randrange(0, 200),
            # report / info
            strength_l_cu=randrange(0, 3),
            strength_l_qu=randrange(0, 3),
            strength_l_ch=randrange(0, 3),
            strength_r_cu=randrange(0, 3),
            strength_r_qu=randrange(0, 3),
            strength_r_ch=randrange(0, 3),
            # report / info
            width_l_cu=randrange(0, 3),
            width_l_qu=randrange(0, 3),
            width_l_ch=randrange(0, 3),
            width_r_cu=randrange(0, 3),
            width_r_qu=randrange(0, 3),
            width_r_ch=randrange(0, 3),
            ### bcq.txt
            bcq=schemas.BCQ(
                exist=randrange(0, 1),
                score_yang=randrange(0, 100),
                score_yin=randrange(0, 100),
                score_phlegm=randrange(0, 100),
                score_yang_head=randrange(0, 100),
                score_yang_chest=randrange(0, 100),
                score_yang_limbs=randrange(0, 100),
                score_yang_abdomen=randrange(0, 100),
                score_yang_surface=randrange(0, 100),
                score_yin_head=randrange(0, 100),
                score_yin_limbs=randrange(0, 100),
                score_yin_gt=randrange(0, 100),
                score_yin_surface=randrange(0, 100),
                score_yin_abdomen=randrange(0, 100),
                score_phlegm_trunk=randrange(0, 100),
                score_phlegm_surface=randrange(0, 100),
                score_phlegm_head=randrange(0, 100),
                score_phlegm_gt=randrange(0, 100),
                percentage_yang=randrange(0, 100),
                percentage_yin=randrange(0, 100),
                percentage_phlegm=randrange(0, 100),
                percentage_yang_head=randrange(0, 100),
                percentage_yang_chest=randrange(0, 100),
                percentage_yang_limbs=randrange(0, 100),
                percentage_yang_abdomen=randrange(0, 100),
                percentage_yang_surface=randrange(0, 100),
                percentage_yin_head=randrange(0, 100),
                percentage_yin_limbs=randrange(0, 100),
                percentage_yin_gt=randrange(0, 100),
                percentage_yin_surface=randrange(0, 100),
                percentage_yin_abdomen=randrange(0, 100),
                percentage_phlegm_trunk=randrange(0, 100),
                percentage_phlegm_surface=randrange(0, 100),
                percentage_phlegm_head=randrange(0, 100),
                percentage_phlegm_gt=randrange(0, 100),
            ),
            comment="帶入單機版文字描述，此次結果診斷的紀錄為，整體評論甚是好",
            all_sec=all_sec,
            cn=cn,
            tongue=schemas.Tongue(
                exist=choice([True, False]),
                info=schemas.TongueInfo(
                    tongue_color=randrange(0, 5),
                    tongue_shap=[randrange(0, 8)],
                    tongue_status1=[randrange(0, 8)],
                    tongue_status2=randrange(0, 2),
                    tongue_coating_color=randrange(0, 4),
                    tongue_coating_status=[randrange(0, 12)],
                    tongue_coating_bottom=randrange(0, 2),
                ),
                image=schemas.TongueImage(
                    front=front_tongue_image_url,
                    back=back_tongue_image_url,
                ),
            ),
        ),
    )


@router.get("/{measure_id}/six_sec_pw", response_model=MeasureSixSecPWResponse)
async def get_measure_six_sec_pw(
    measure_id: UUID,
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    measure = await crud.measure_info.get(
        db_session=db_session,
        id=measure_id,
        relations=["raw"],
    )
    if not measure:
        raise HTTPException(
            status_code=400,
            detail=f"Not found measure id: {measure_id}",
        )

    if measure.org_id != current_user.org_id:
        raise HTTPException(
            status_code=400,
            detail=f"Measure id: {measure_id} not belong to org id: {current_user.org_id}",
        )

    def gen_data(content):
        if not content:
            return LineChart(data=[], x_field="x", y_field="y")
        y = content.split("\n")
        x = [i * 1.0 / len(y) * 6 for i in range(len(y))]
        data = [
            {"x": x[i], "y": float(y[i]) if y[i] else 0}
            for i in range(len(y))
            if i % 10 == 0
        ]
        return LineChart(data=data, x_field="x", y_field="y")

    raw_data = measure.raw
    return {
        "l_cu": gen_data(raw_data.six_sec_l_cu),
        "l_qu": gen_data(raw_data.six_sec_l_qu),
        "l_ch": gen_data(raw_data.six_sec_l_ch),
        "r_cu": gen_data(raw_data.six_sec_r_cu),
        "r_qu": gen_data(raw_data.six_sec_r_qu),
        "r_ch": gen_data(raw_data.six_sec_r_ch),
    }


@router.patch("/{measure_id}/memo")
async def update_measure_memo(
    measure_id: UUID,
    memo: Memo,
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    measure = await crud.measure_info.get(
        db_session=db_session,
        id=measure_id,
    )
    if not measure:
        raise HTTPException(
            status_code=400,
            detail=f"Not found measure id: {measure_id}",
        )

    if measure.org_id != current_user.org_id:
        raise HTTPException(
            status_code=400,
            detail=f"Measure id: {measure_id} not belong to org id: {current_user.org_id}",
        )

    measure_in = schemas.MeasureInfoUpdate(
        memo=memo.content,
        has_memo=isinstance(memo.content, str) and len(memo.content) > 0,
    )
    await crud.measure_info.update(
        db_session=db_session,
        obj_current=measure,
        obj_new=measure_in,
    )
    return memo.content


@router.patch("/{measure_id}/comment")
async def update_measure_comment(
    measure_id: UUID,
    comment: Memo,
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    measure = await crud.measure_info.get(
        db_session=db_session,
        id=measure_id,
    )
    if not measure:
        raise HTTPException(
            status_code=400,
            detail=f"Not found measure id: {measure_id}",
        )

    if measure.org_id != current_user.org_id:
        raise HTTPException(
            status_code=400,
            detail=f"Measure id: {measure_id} not belong to org id: {current_user.org_id}",
        )

    measure_in = schemas.MeasureInfoUpdate(
        comment=comment.content,
    )
    await crud.measure_info.update(
        db_session=db_session,
        obj_current=measure,
        obj_new=measure_in,
    )
    return comment.content


@router.patch("/{measure_id}/tongue_info")
async def update_measure_tongue_info(
    measure_id: UUID,
    tongue_info: schemas.TongueInfo,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    measure = await crud.measure_info.get(
        db_session=db_session,
        id=measure_id,
        relations=["tongue"],
    )
    if not measure:
        raise HTTPException(
            status_code=400,
            detail=f"Not found measure id: {measure_id}",
        )
    if not measure.tongue:
        raise HTTPException(
            status_code=400,
            detail=f"Not found tongue of measure id: {measure_id}",
        )

    if measure.org_id != current_user.org_id:
        raise HTTPException(
            status_code=400,
            detail=f"Measure id: {measure_id} not belong to org id: {current_user.org_id}",
        )

    tongue_in = schemas.MeasureTongueUpdate(
        tongue_color=tongue_info.tongue_color,
        tongue_shap=tongue_info.tongue_shap if tongue_info.tongue_shap else None,
        tongue_status1=tongue_info.tongue_status1
        if tongue_info.tongue_status1
        else None,
        tongue_status2=tongue_info.tongue_status2,
        tongue_coating_color=tongue_info.tongue_coating_color,
        tongue_coating_status=tongue_info.tongue_coating_status
        if tongue_info.tongue_coating_status
        else None,
        tongue_coating_bottom=tongue_info.tongue_coating_bottom,
    )
    await crud.measure_tongue.update(
        db_session=db_session,
        obj_current=measure.tongue,
        obj_new=tongue_in,
    )
    return tongue_info


@router.patch("/{measure_id}/irregular_hr")
async def update_measure_irregular_hr(
    measure_id: UUID,
    irregular_hr: schemas.IrregularHR,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    measure = await crud.measure_info.get(
        db_session=db_session,
        id=measure_id,
    )
    if not measure:
        raise HTTPException(
            status_code=400,
            detail=f"Not found measure id: {measure_id}",
        )

    if measure.org_id != current_user.org_id:
        raise HTTPException(
            status_code=400,
            detail=f"Measure id: {measure_id} not belong to org id: {current_user.org_id}",
        )

    irregular_hr_type_l = None
    irregular_hr_type_r = None
    if measure.irregular_hr_l == 1 and irregular_hr.side == 0:
        if not irregular_hr.type in (0, 1):
            raise HTTPException(
                status_code=400,
                detail=f"irregular_hr type allowd: 0, 1",
            )
        irregular_hr_type_l = irregular_hr.type

    elif measure.irregular_hr_r == 1 and irregular_hr.side == 1:
        if not irregular_hr.type in (0, 1):
            raise HTTPException(
                status_code=400,
                detail=f"irregular_hr type allowd: 0, 1",
            )
        irregular_hr_type_r = irregular_hr.type

    else:
        raise Exception(
            "irregular_hr_type could be only updated when irregular_hr is true",
        )

    measure_in = schemas.MeasureInfoUpdate(
        irregular_hr_type_l=irregular_hr_type_l,
        irregular_hr_type_r=irregular_hr_type_r,
    )
    await crud.measure_info.update(
        db_session=db_session,
        obj_current=measure,
        obj_new=measure_in,
    )
    return irregular_hr
