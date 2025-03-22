from datetime import datetime, timedelta
from io import StringIO
from math import ceil
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

import pydash as py_
from azure.storage.blob import BlobSasPermissions, generate_blob_sas
from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Depends
from pydantic import BaseModel
from sqlalchemy import and_
from sqlmodel import String, cast, extract, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud, models, schemas
from auo_project.core.azure import internet_blob_service, upload_blob_file
from auo_project.core.config import settings
from auo_project.core.constants import MEASURE_TIMES, SexType
from auo_project.core.dateutils import DateUtils
from auo_project.core.pagination import Pagination
from auo_project.core.tongue import get_tongue_summary
from auo_project.core.utils import get_age, get_filters, get_subject_schema, safe_int
from auo_project.web.api import deps

surface_disease_content = """
tongue_tip	tongue_color	tongue_shap	tongue_status1	tongue_status2	tongue_coating_color	tongue_coating_status	surface_disease
紅	淡紅	正常	正常	榮舌	白	薄	心火上炎
	青	老	正常	榮舌	白	薄	肝膽兩經邪氣盛
	青	瘦薄	正常	榮舌	白	滑、光剝	傷寒直中肝腎陰證
	青、紫	正常	正常	榮舌	灰黑	滑	痰飲內停或寒濕內阻
	青、紫	正常	正常	榮舌	白	厚、膩、滑	停飲
	青、紫	正常	正常	榮舌	白	薄	寒邪直中
	紅	正常	正常	榮舌	黃	薄	實熱
	紅	正常	正常	榮舌	白	燥	胃津已傷
	紅	正常	萎軟	榮舌	白	燥	熱灼陰傷
	紅	正常	強硬	榮舌	白	薄	熱入心包
	紅	正常	正常	榮舌	白	薄	熱證
	紅	正常	正常	榮舌	黃	腐、膩	脾胃濕熱壅滯
	紅	正常	正常	榮舌	灰黑	燥	熱熾傷津或陰虛火旺
	紅	正常	正常	榮舌	白	厚、膩、燥	濕邪困遏，陽氣不伸
	紅	正常	正常	榮舌	白	光剝、燥	胃陰虛
	紅	芒刺	正常	榮舌	白	薄	營分有熱
	紅	芒刺	正常	榮舌	黃	燥	氣分熱盛
	紅	芒刺	正常	榮舌	黃	薄	胃腸熱盛
	紅	裂紋	正常	榮舌	白	燥	熱盛傷津
	紅	裂紋	正常	榮舌	白	少	氣陰兩虛
	紅	裂紋	正常	榮舌	白	光剝	氣陰兩虛
	紅	嫩	正常	榮舌	白	光剝	陰虛火旺
	紅	瘦薄	正常	枯舌	白	光剝、燥	腎陰欲竭
	紅、絳	正常	短縮	榮舌	灰黑	燥	熱病傷津
	紅、絳	正常	短縮	榮舌	白	光剝、燥	熱病傷津
	紅、絳	瘦薄	正常	榮舌	白	燥	陰虛火旺
	淡白	正常	正常	榮舌	白	滑	大腸陽氣虛
	淡白	正常	正常	榮舌	白	燥	肺臟火旺
	淡白	正常	萎軟	榮舌	白	薄	氣血俱虛
	淡白	正常	吐弄	榮舌	白	薄	虛象
	淡白	正常	短縮	榮舌	白	滑	寒凝經脈
	淡白	正常	正常	榮舌	白	薄	寒證
	淡白	正常	正常	榮舌	灰黑	滑	痰飲內停或寒濕內阻
	淡白	正常	正常	榮舌	白	厚	痰熱
	淡白	正常	正常	榮舌	白	花剝、滑	脾胃陽氣不足
	淡白	正常	正常	榮舌	白	光剝	氣血兩虛
	淡白	胖大、嫩	正常	榮舌	白	薄	肺與大腸精氣虛
	淡白	胖大、嫩	正常	榮舌	黃	滑	陽虛水濕不化
	淡白	胖大、嫩、齒痕	正常	榮舌	白	薄	脾氣虛
	淡白	裂紋	正常	榮舌	白	薄	氣血兩虛
	淡白	裂紋、胖大	正常	榮舌	白	膩	脾虛濕浸
	淡白	瘦薄	正常	榮舌	白	薄	氣血兩虛
	淡紅	正常	顫動	榮舌	白	薄	血虛生風
	淡紅	正常	顫動	榮舌	白	厚	酒精中毒
	淡紅	正常	正常	榮舌	白	厚、膩	里寒兼濕
	淡紅	正常	正常	榮舌	白	滑	寒濕襲表
	淡紅	正常	正常	榮舌	白	光剝	脾陽虛衰
	淡紅	正常	正常	榮舌	黃	滑	濕熱
	淡紅	正常	正常	榮舌	灰黑	滑	痰飲寒濕
	淡紅	正常	正常	榮舌	灰黑	燥	陰虛火旺
	淡紅	正常	正常	榮舌	灰黑	膩	濕熱
	淡紅	正常	正常	榮舌	灰黑	少	陰虛
	淡紅	正常	正常	榮舌	灰黑	花剝	陰虛
	淡紅	正常	正常	榮舌	白	滑、膩	寒濕束表
	淡紅	正常	正常	榮舌	白	花剝、燥	氣陰兩傷
	淡紅	正常	正常	榮舌	白	光剝、燥	氣陰兩虛
	淡紅	胖大	短縮	榮舌	白	膩	痰濕阻閉
	淡紅	裂紋	正常	榮舌	白	少	氣陰兩虛
	淡紅	裂紋	正常	榮舌	白	光剝	氣陰兩虛
	紫	正常	正常	榮舌	灰黑	薄	瘀血
	紫	正常	顫動	榮舌	白	薄	熱極生風
	紫	芒刺	正常	榮舌	白	薄	血分熱毒盛
	紫、紅	正常	正常	榮舌	白	燥	瘀熱
	紫、紅	正常	吐弄	榮舌	白	薄	熱毒攻心
	紫、淡白	正常	正常	榮舌	白	薄	寒凝血瘀 / 陽陽虛生寒
	紫、絳	正常	正常	榮舌	白	滑	熱傳營血
	紫、絳	正常	正常	榮舌	白	薄	血分熱毒
	紫、絳	正常	顫動	榮舌	灰黑	薄	肝風內動
	絳	正常	正常	榮舌	白	燥	邪入營血
	絳	正常	正常	榮舌	白	光剝	胃陰大傷
	絳	正常	正常	枯舌	白	薄	胃陰已涸
	絳	正常	正常	榮舌	白	薄	飲食中風寒 / 熱積涼飲
	絳	正常	正常	榮舌	白	厚	內夾宿食，中風寒
	絳	正常	正常	榮舌	白	厚、膩、燥	表里合邪
	絳	正常	正常	榮舌	黃	厚、膩、燥	邪熱內結
	絳	正常	萎軟	榮舌	白	薄	陰虧已極
	絳	正常	強硬	榮舌	白	薄	熱入心包
	絳	正常	正常	榮舌	灰黑	燥	熱熾傷津或陰虛火旺
	絳	正常	正常	榮舌	白	光剝、燥	胃陰虛
	絳	朱點	正常	榮舌	白	薄	熱毒乘心
	絳	裂紋	正常	榮舌	白	薄	胃火傷津
	絳	裂紋	正常	榮舌	白	燥	熱盛傷津
	絳	瘦薄	正常	枯舌	白	光剝、燥	腎陰欲竭
"""
import pandas as pd

surface_disease_records = pd.read_csv(
    StringIO(surface_disease_content),
    sep="\t",
).to_dict("records")


from auo_project.schemas.measure_tongue_schema import TongueListOutput

router = APIRouter()


@router.get("/", response_model=TongueListOutput)
async def get_tongue_list(
    number: Optional[str] = Query(None, regex="contains__", title="受測者編號"),
    sid: Optional[str] = Query(None, regex="contains__", title="ID"),
    name: Optional[str] = Query(None, regex="contains__", title="姓名"),
    tongue_memo: Optional[str] = Query(None, regex="contains__", title="受測者標記"),
    sort_expr: Optional[str] = Query(
        None,
        title="updated_at 代表由小到大排。-updated_at 代表由大到小排。",
    ),
    specific_months: Optional[List[int]] = Query(
        [],
        alias="specific_months[]",
        title="指定月份",
    ),
    dateutils: DateUtils = Depends(),
    pagination: Pagination = Depends(),
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> TongueListOutput:
    org = await crud.org.get_by_name(db_session=db_session, name="tongue_label")
    if current_user.org_id != org.id:
        raise HTTPException(
            status_code=400,
            detail=f"Permission Error",
        )

    start_date, end_date = dateutils.get_dates()
    measure_filters = get_filters(
        {
            "measure_time__ge": start_date,
            "measure_time__le": end_date,
            "has_tongue": True,
        },
    )
    measure_expr = models.MeasureInfo.filter_expr(**measure_filters)
    if specific_months:
        measure_expr.append(
            extract("month", models.MeasureInfo.measure_time).in_(specific_months),
        )
    subject_filters = get_filters(
        {
            "name__contains": name.replace("contains__", "") if name else None,
            "sid__contains": sid.replace("contains__", "") if sid else None,
        },
    )

    subject_expr = models.Subject.filter_expr(**subject_filters)
    if number:
        subject_expr.append(
            cast(models.Subject.number, String).ilike(
                f'%{number.replace("contains__", "")}%',
            ),
        )
    advanced_tongue_filters = get_filters(
        {
            "tongue_memo__contains": (
                tongue_memo.replace("contains__", "") if tongue_memo else None
            ),
        },
    )
    advacned_tongue_expr = models.MeasureAdvancedTongue.filter_expr(
        **advanced_tongue_filters
    )

    sort_expr = (
        [e.replace("+", "") for e in sort_expr.split(",")]
        if sort_expr
        else ["-measure_time"]
    )
    order_expr = []
    if "measure_time" in sort_expr or "-measure_time" in sort_expr:
        order_expr += models.MeasureInfo.order_expr(*sort_expr)
    if (
        "name" in sort_expr
        or "-name" in sort_expr
        or "sid" in sort_expr
        or "-sid" in sort_expr
    ):
        order_expr += models.Subject.order_expr(*sort_expr)
    if "has_tongue_label" in sort_expr or "-has_tongue_label" in sort_expr:
        order_expr += models.MeasureAdvancedTongue.order_expr(*sort_expr)

    org = await crud.org.get_by_name(db_session=db_session, name="tongue_label")
    query = (
        select(models.MeasureInfo)
        .join(models.Subject)
        .join(
            models.MeasureAdvancedTongue,
            and_(
                models.MeasureAdvancedTongue.measure_id == models.MeasureInfo.id,
                models.MeasureAdvancedTongue.owner_id == current_user.id,
            ),
            isouter=True,
        )
        .where(
            *measure_expr,
            *subject_expr,
            *advacned_tongue_expr,
        )
    )
    items = await crud.measure_info.get_multi(
        db_session=db_session,
        query=query,
        order_expr=order_expr,
        relations=["subject"],
        skip=(pagination.page - 1) * pagination.per_page,
        limit=pagination.per_page,
    )
    advanced_tongue_query = select(models.MeasureAdvancedTongue).where(
        models.MeasureAdvancedTongue.measure_id.in_(
            [item.id for item in items if item],
        ),
        models.MeasureAdvancedTongue.owner_id == current_user.id,
    )
    response = await db_session.execute(advanced_tongue_query)
    advanced_tongues = response.scalars().all()
    advanced_tongues_dict = {str(t.measure_id): t for t in advanced_tongues}

    resp = await db_session.execute(select(func.count()).select_from(query.subquery()))
    total_count = resp.scalar_one()
    items = [
        {
            "subject": item.subject,
            "measure": {
                "id": item.id,
                "measure_time": item.measure_time.strftime("%Y-%m-%d %H:%M"),
                "tongue": {
                    "info": {
                        "has_tongue_label": py_.get(
                            advanced_tongues_dict,
                            f"{item.id}.has_tongue_label",
                        ),
                        "tongue_memo": py_.get(
                            advanced_tongues_dict,
                            f"{item.id}.tongue_memo",
                        ),
                    },
                },
            },
        }
        for item in items
    ]

    return {
        "measure_times": MEASURE_TIMES,
        "tongue": schemas.TongueListPage(
            page=pagination.page,
            per_page=pagination.per_page,
            page_count=ceil(total_count / pagination.per_page),
            total_count=total_count,
            link=schemas.Link(
                self=pagination.get_self_url(),
                next=pagination.get_next_url(),
                prev=pagination.get_previous_url(),
            ),
            items=items,
        ),
    }


@router.get("/{measure_id}")
async def get_tongue(
    measure_id: UUID,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    org = await crud.org.get_by_name(db_session=db_session, name="tongue_label")
    if current_user.org_id != org.id:
        raise HTTPException(
            status_code=400,
            detail=f"Permission Error",
        )

    measure = await crud.measure_info.get(
        db_session=db_session,
        id=measure_id,
        relations=["subject", "tongue"],
    )
    if measure is None:
        raise HTTPException(
            status_code=400,
            detail=f"Not found measure id: {measure_id}",
        )

    if measure.tongue is None:
        raise HTTPException(status_code=404, detail="Tongue not found")

    tongue = measure.tongue
    if tongue:
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

    advanced_tongue = await crud.measure_advanced_tongue.get_by_measure_id(
        db_session=db_session,
        measure_id=measure_id,
        owner_id=current_user.id,
    )
    toungue_info = (
        advanced_tongue
        if advanced_tongue
        else schemas.MeasureAdvancedTongueRead(
            measure_id=measure_id,
            owner_id=current_user.id,
            id=measure_id,
            tongue_color=0,
            tongue_status2=0,
            tongue_coating_status=[0],
        )
    )
    subject_schema = get_subject_schema(org_name=current_user.org.name)
    return {
        "subject": subject_schema.from_orm(measure.subject),
        "measure": {
            "tongue": {
                "exist": True if advanced_tongue else False,
                "info": jsonable_encoder(toungue_info),
                "image": schemas.TongueImage(
                    front=front_tongue_image_url or "",
                    back=back_tongue_image_url or "",
                ),
            },
        },
    }


@router.patch("/{measure_id}/tongue_info")
async def update_measure_tongue_info(
    measure_id: UUID,
    tongue_info: schemas.MeasureAdvancedTongueUpdate,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    org = await crud.org.get_by_name(db_session=db_session, name="tongue_label")
    if current_user.org_id != org.id:
        raise HTTPException(
            status_code=400,
            detail=f"Permission Error",
        )
    measure = await crud.measure_info.get(
        db_session=db_session,
        id=measure_id,
    )
    if measure is None:
        raise HTTPException(
            status_code=400,
            detail=f"Not found measure id: {measure_id}",
        )

    advanced_tongue = await crud.measure_advanced_tongue.get_by_measure_id(
        db_session=db_session,
        measure_id=measure_id,
        owner_id=current_user.id,
    )

    def clean_level_map(
        number_list: List[int],
        level_map: Dict[str, int],
    ) -> Dict[str, Any]:
        return {
            key: value
            for key, value in level_map.items()
            if safe_int(key) in number_list and value is not None
        }

    # TODO: validate
    if advanced_tongue:
        tongue_in = schemas.MeasureAdvancedTongueUpdate(
            tongue_tip=tongue_info.tongue_tip,
            tongue_color=tongue_info.tongue_color,
            tongue_shap=tongue_info.tongue_shap,
            tongue_shap_level_map=clean_level_map(
                tongue_info.tongue_shap,
                tongue_info.tongue_shap_level_map,
            ),
            tongue_status1=tongue_info.tongue_status1,
            tongue_status2=tongue_info.tongue_status2,
            tongue_status2_level_map=clean_level_map(
                [tongue_info.tongue_status2],
                tongue_info.tongue_status2_level_map,
            ),
            tongue_coating_color=tongue_info.tongue_coating_color,
            tongue_coating_color_level_map=clean_level_map(
                tongue_info.tongue_coating_color,
                tongue_info.tongue_coating_color_level_map,
            ),
            tongue_coating_status=tongue_info.tongue_coating_status,
            tongue_coating_status_level_map=clean_level_map(
                tongue_info.tongue_coating_status,
                tongue_info.tongue_coating_status_level_map,
            ),
            tongue_coating_bottom=tongue_info.tongue_coating_bottom,
            tongue_coating_bottom_level_map=clean_level_map(
                tongue_info.tongue_coating_bottom,
                tongue_info.tongue_coating_bottom_level_map,
            ),
            has_tongue_label=True,
        )

        tongue_info = await crud.measure_advanced_tongue.update(
            db_session=db_session,
            obj_current=advanced_tongue,
            obj_new=tongue_in.dict(exclude_unset=True),
        )
    else:
        tongue_in = schemas.MeasureAdvancedTongueCreate(
            measure_id=measure_id,
            owner_id=current_user.id,
            tongue_tip=tongue_info.tongue_tip,
            tongue_color=tongue_info.tongue_color,
            tongue_shap=tongue_info.tongue_shap,
            tongue_shap_level_map=clean_level_map(
                tongue_info.tongue_shap,
                tongue_info.tongue_shap_level_map,
            ),
            tongue_status1=tongue_info.tongue_status1,
            tongue_status2=tongue_info.tongue_status2,
            tongue_status2_level_map=clean_level_map(
                [tongue_info.tongue_status2],
                tongue_info.tongue_status2_level_map,
            ),
            tongue_coating_color=tongue_info.tongue_coating_color,
            tongue_coating_color_level_map=clean_level_map(
                tongue_info.tongue_coating_color,
                tongue_info.tongue_coating_color_level_map,
            ),
            tongue_coating_status=tongue_info.tongue_coating_status,
            tongue_coating_status_level_map=clean_level_map(
                tongue_info.tongue_coating_status,
                tongue_info.tongue_coating_status_level_map,
            ),
            tongue_coating_bottom=tongue_info.tongue_coating_bottom,
            tongue_coating_bottom_level_map=clean_level_map(
                tongue_info.tongue_coating_bottom,
                tongue_info.tongue_coating_bottom_level_map,
            ),
            has_tongue_label=True,
        )
        tongue_info = await crud.measure_advanced_tongue.create(
            db_session=db_session,
            obj_in=tongue_in,
        )
    return {
        **jsonable_encoder(tongue_info),
        "tongue_status2_level": tongue_info.tongue_status2_level_map.get(
            tongue_info.tongue_status2,
        ),
    }


@router.patch("/{measure_id}/memo")
async def update_tongue_memo(
    measure_id: UUID,
    memo: schemas.Memo,
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    org = await crud.org.get_by_name(db_session=db_session, name="tongue_label")
    if current_user.org_id != org.id:
        raise HTTPException(
            status_code=400,
            detail=f"Permission Error",
        )
    measure = await crud.measure_info.get(
        db_session=db_session,
        id=measure_id,
    )
    if not measure:
        raise HTTPException(
            status_code=400,
            detail=f"Not found measure id: {measure_id}",
        )

    advanced_tongue = await crud.measure_advanced_tongue.get_by_measure_id(
        db_session=db_session,
        measure_id=measure_id,
        owner_id=current_user.id,
    )
    if advanced_tongue:
        tongue_in = schemas.MeasureAdvancedTongueUpdate(
            tongue_memo=memo.content,
        )
        await crud.measure_advanced_tongue.update(
            db_session=db_session,
            obj_current=measure.advanced_tongue,
            obj_new=tongue_in,
        )
    else:
        tongue_in = schemas.MeasureAdvancedTongueCreate(
            measure_id=measure_id,
            owner_id=current_user.id,
            tongue_memo=memo.content,
        )
        await crud.measure_advanced_tongue.create(
            db_session=db_session,
            obj_in=tongue_in,
        )
    return {"tongue_memo": memo.content}


@router.post("/upload/measure", response_model=schemas.MeasureTongueUploadRead)
async def upload_measure(
    id: Optional[str] = Form(
        None,
        max_length=128,
        description="身分證字號/護照/居留證號 varchar(128)",
    ),
    name: Optional[str] = Form(
        None,
        max_length=128,
        description="受測者姓名 varchar(128)",
    ),
    birthday: Optional[str] = Form(
        None,
        min_length=10,
        max_length=10,
        regex="^[0-9]{4}/[0-9]{2}/[0-9]{2}$",
        description="生日，格式為 YYYY/MM/DD",
    ),
    sex: Optional[SexType] = Form(SexType.unkwown, description="性別。0: 男, 1: 女, -1: 未知。"),
    number: str = Form(
        ...,
        max_length=128,
        description="受測者編號或病歷編號 varchar(128)",
    ),
    proj_num: Optional[str] = Form(
        None, max_length=128, description="計畫編號 varchar(128)",
    ),
    consult_dr_id: Optional[UUID] = Form(None, description="判讀醫師 ID varchar(128)"),
    tongue_front_file: UploadFile = File(description="舌象正面圖片"),
    tongue_back_file: UploadFile = File(description="舌象背面圖片"),
    device_id: Optional[str] = Form(
        None,
        max_length=128,
        description="舌診擷取設備編號 varchar(128)",
    ),
    pad_id: Optional[str] = Form(
        None,
        max_length=128,
        description="平板 ID varchar(128)",
    ),
    celery_app=Depends(deps.get_celery_app),
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    try:
        birth_date = datetime.strptime(birthday, "%Y/%m/%d") if birthday else None
    except:
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": ["birthday"],
                    "msg": f"date value is invalid: {birthday}",
                    "type": "value_error",
                },
            ],
        )
    if birth_date is None:
        birth_date = datetime(1900, 1, 1)

    # 未來不需要 device_id, pad_id 因為不用根據場域校色

    org_id = current_user.org_id

    doctor = None
    doctor_id = None
    if consult_dr_id:
        doctor = await crud.doctor.get(db_session=db_session, id=consult_dr_id)
        doctor_id = doctor.id if doctor else None

    age = get_age(
        measure_time=datetime.utcnow() + timedelta(hours=8),
        birth_date=birth_date,
    )

    # create subject if not exists
    subject = await crud.subject.get_by_number_and_org_id(
        db_session=db_session,
        number=number,
        org_id=org_id,
    )
    if not subject:
        subject_in = schemas.SubjectCreate(
            org_id=org_id,
            number=number,
            name=name or number,
            sid=id or number,
            birth_date=birth_date,
            age=age,
            sex=sex,
            deleted_mark=False,
        )
        subject = await crud.subject.create(db_session=db_session, obj_in=subject_in)

    # TODO: don't hard code timezone
    measure_time = datetime.utcnow() + timedelta(hours=8)
    measure_info_in = schemas.MeasureInfoCreate(
        subject_id=subject.id,
        branch_id=current_user.branch_id,
        file_id=None,
        org_id=org_id,
        number=number,
        name=name,
        sid=id,
        birth_date=birth_date,
        has_measure=False,
        has_bcq=False,
        has_tongue=True,
        has_memo=False,
        measure_time=measure_time,
        measure_operator=current_user.username,
        sex=sex,
        age=age,
        judge_time=measure_time,
        judge_dr=doctor.name if doctor else "",
        proj_num=proj_num,
        is_active=False,
    )
    measure_info = await crud.measure_info.create(
        db_session=db_session,
        obj_in=measure_info_in,
    )

    # 是否需要紀錄 branch id? 以現階段來說不用
    tongue_upload_in = schemas.MeasureTongueUploadCreate(
        measure_id=measure_info.id,
        org_id=current_user.org_id,
        branch_id=None,
        field_id=None,
        owner_id=current_user.id,
        subject_id=subject.id,
        name=name,
        sid=id,
        birth_date=birth_date,
        age=age,
        sex=sex,
        number=number,
        measure_operator="",  # TODO: depreciated
        color_hash="",  # TODO: depreciated
        tongue_front_original_loc="",
        tongue_back_original_loc="",
        device_id=device_id,
        pad_id=pad_id,
        proj_num=proj_num,
        doctor_id=doctor_id,
        created_at=measure_time,
    )

    tongue_upload = await crud.measure_tongue_upload.create(
        db_session=db_session,
        obj_in=tongue_upload_in,
    )

    # TODO: update other subject info?
    subject_in = schemas.SubjectUpdate(
        last_measure_time=measure_time,
    )
    await crud.subject.update(
        db_session=db_session,
        obj_current=subject,
        obj_new=subject_in,
    )

    # upload to azure blob
    blob_prefix = crud.measure_tongue_upload.get_blob_prefix()
    blob_container = crud.measure_tongue_upload.get_container_name()
    tongue_front_original_loc = (
        f"{blob_prefix}/{org_id}/{current_user.id}/{tongue_upload.id}/T_up.jpg"
    )
    tongue_back_original_loc = (
        f"{blob_prefix}/{org_id}/{current_user.id}/{tongue_upload.id}/T_down.jpg"
    )
    upload_blob_file(
        blob_service_client=internet_blob_service,
        category=blob_container,
        file_path=tongue_front_original_loc,
        object=tongue_front_file.file,
        overwrite=True,
    )
    upload_blob_file(
        blob_service_client=internet_blob_service,
        category=blob_container,
        file_path=tongue_back_original_loc,
        object=tongue_back_file.file,
        overwrite=True,
    )

    tongue_upload_in = schemas.MeasureTongueUploadUpdate(
        tongue_front_original_loc=tongue_front_original_loc,
        tongue_back_original_loc=tongue_back_original_loc,
    )
    await crud.measure_tongue_upload.update(
        db_session=db_session,
        obj_current=tongue_upload,
        obj_new=tongue_upload_in,
    )
    measure_info_in = schemas.MeasureInfoUpdate(
        is_active=True,
    )
    await crud.measure_info.update(
        db_session=db_session,
        obj_current=measure_info,
        obj_new=measure_info_in,
    )

    # send task to worker
    celery_app.send_task(
        "auo_project.services.celery.tasks.task_process_tongue_image",
        kwargs={"tongue_upload_id": tongue_upload.id},
    )

    return tongue_upload


@router.post("/summary")
async def create_measure_tongue_summary(
    tongue_info: schemas.MeasureAdvancedTongue2UpdateInput,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    tongue_sympotms = await crud.measure_tongue_symptom.get_all(db_session=db_session)
    tongue_summary = get_tongue_summary(
        tongue_info=tongue_info,
        tongue_sympotms=tongue_sympotms,
    )

    return {"tongue_summary": tongue_summary}


class SubjectPage(BaseModel):
    page: int
    per_page: int
    page_count: int
    total_count: int
    link: schemas.Link
    items: List[Union[schemas.SubjectRead, schemas.SubjectSecretRead]]


class SubjectListResponse(BaseModel):
    subject: SubjectPage
    measure_times: List[Dict[str, Any]]

