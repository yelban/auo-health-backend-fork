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


# @router.get("/data/sample", response_model=AdvancedTongueOutput)
# async def get_sample_data(
#     db_session: AsyncSession = Depends(deps.get_db),
#     # current_user: models.User = Depends(deps.get_current_active_user),
# ):
#     if settings.ENVIRONMENT == "dev":
#         measure = await crud.measure_info.get(
#             db_session=db_session,
#             id="46dc24fe-2ae6-40df-bf2e-7733b7f8dc88",
#             relations=["subject", "tongue"],
#         )
#     else:
#         measure = await crud.measure_info.get(
#             db_session=db_session,
#             id="edf0680d-c4f1-457b-9ff4-ce885d5b9659",
#             relations=["subject", "tongue"],
#         )
#     tongue = measure.tongue
#     if tongue:
#         if tongue.up_img_uri:
#             container_name = settings.AZURE_STORAGE_CONTAINER_INTERNET_IMAGE
#             file_path = "tongue/tongue_example/T_up.jpg"
#             expiry = datetime.utcnow() + timedelta(minutes=15)
#             sas_token = generate_blob_sas(
#                 account_name=settings.AZURE_STORAGE_ACCOUNT_INTERNET,
#                 container_name=container_name,
#                 blob_name=file_path,
#                 account_key=settings.AZURE_STORAGE_KEY_INTERNET,
#                 permission=BlobSasPermissions(read=True),
#                 expiry=expiry,
#                 # TODO: add ip
#             )
#             front_tongue_image_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_INTERNET}.blob.core.windows.net/{container_name}/{file_path}?{sas_token}"

#         if tongue.down_img_uri:
#             container_name = settings.AZURE_STORAGE_CONTAINER_INTERNET_IMAGE
#             file_path = "tongue/tongue_example/T_down.jpg"
#             expiry = datetime.utcnow() + timedelta(minutes=15)
#             sas_token = generate_blob_sas(
#                 account_name=settings.AZURE_STORAGE_ACCOUNT_INTERNET,
#                 container_name=container_name,
#                 blob_name=file_path,
#                 account_key=settings.AZURE_STORAGE_KEY_INTERNET,
#                 permission=BlobSasPermissions(read=True),
#                 expiry=expiry,
#                 # TODO: add ip
#             )
#             back_tongue_image_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_INTERNET}.blob.core.windows.net/{container_name}/{file_path}?{sas_token}"

#     tongue_symptoms = await crud.measure_tongue_symptom.get_all(db_session=db_session)
#     tongue_symptoms = py_.order_by(tongue_symptoms, ["order"])
#     tongue_symptom_diseases = await crud.measure_tongue_symptom_disease.get_all(
#         db_session=db_session,
#     )
#     tongue_symptom_diseases_dict = {}
#     tongue_groups = await crud.measure_tongue_group_symptom.get_all(
#         db_session=db_session,
#     )
#     tongue_groups = sorted(tongue_groups, key=lambda x: (x.item_id, x.group_id))
#     tongue_group_dict = dict(
#         [
#             (f"{item.item_id}:{item.group_id}", item.component_type)
#             for item in tongue_groups
#         ],
#     )

#     for item in tongue_symptom_diseases:
#         tongue_symptom_diseases_dict[item.item_id] = tongue_symptom_diseases_dict.get(
#             item.item_id,
#             {},
#         )
#         disease_item = Disease(
#             value=item.disease_id,
#             label=item.disease_id,  # TODO; item.disease.disease_name
#             selected=False,
#         )

#         if item.symptom_id in tongue_symptom_diseases_dict[item.item_id]:
#             tongue_symptom_diseases_dict[item.item_id][item.symptom_id].append(
#                 disease_item,
#             )
#         else:
#             tongue_symptom_diseases_dict[item.item_id][item.symptom_id] = [disease_item]

#     level_map = {
#         1: "輕",
#         2: "中",
#         3: "重",
#     }
#     result = {}
#     result2 = []

#     for item in tongue_symptoms:
#         append_item = {
#             "id": item.id,
#             "item_id": item.item_id,
#             "item_name": item.item_name,
#             "group_id": item.group_id or "0",
#             "symptom_id": item.symptom_id,
#             "symptom_name": item.symptom_name,
#             "symptom_description": item.symptom_description,
#             "level_options": (
#                 [
#                     LevelOption(
#                         label=level_map.get(int(level)),
#                         value=int(level),
#                         selected=False,
#                     )
#                     for level in item.symptom_levels
#                 ]
#                 if item.symptom_levels
#                 else []
#             ),
#             "is_default": item.is_default or False,
#             "is_normal": item.is_normal or False,
#             "diseases": tongue_symptom_diseases_dict.get(item.item_id, {}).get(
#                 item.symptom_id,
#                 [],
#             ),
#             "selected": item.is_default or False,
#         }
#         if item.item_id in result:
#             result[item.item_id].append(append_item)
#         else:
#             result[item.item_id] = [append_item]

#         for key, value in result.items():
#             result2.append(
#                 {
#                     "item_id": key,
#                     "item_name": value[0]["item_name"],
#                     "symptoms": py_.chain(value)
#                     .group_by("group_id")
#                     .map_(
#                         lambda objs, group_id: {
#                             "item_id": key,
#                             "component_id": f"{key}:{group_id}",
#                             "component_type": tongue_group_dict.get(
#                                 f"{key}:{group_id}",
#                                 "radio",
#                             ),
#                             "children": py_.map_(
#                                 objs,
#                                 lambda x: py_.pick_by(
#                                     x,
#                                     [
#                                         "id",
#                                         "symptom_id",
#                                         "symptom_name",
#                                         "symptom_description",
#                                         "level_options",
#                                         "is_default",
#                                         "is_normal",
#                                         "selected",
#                                         "diseases",
#                                     ],
#                                 ),
#                             ),
#                         },
#                     )
#                     .value(),
#                 },
#             )

#     return AdvancedTongueOutput(
#         subject=measure.subject,
#         measure_tongue=TongueSampleMeasure(
#             image=TongueSampleImage(
#                 front=front_tongue_image_url or "",
#                 back=back_tongue_image_url or "",
#             ),
#             measure_time=measure.measure_time.strftime("%Y-%m-%d %H:%M"),
#             symptom=result2,
#             summary="內容內容內容內容內容內容內容內容內容內容",
#             memo="檢測標記",
#         ),
#     )


# @router.post("/upload/config_zip", response_model=TongueConfigUploadResponse)
# async def upload_config_zip(
#     upload_file: UploadFile = File(description="校色 ZIP 檔"),
#     db_session: AsyncSession = Depends(deps.get_db),
#     current_user: models.User = Depends(deps.get_current_active_user),
# ):

#     pickle_sha256_hex = None
#     color_ini_content = None

#     with ZipFile(upload_file.file._file, mode="r") as config_zip:
#         infolist = config_zip.infolist()
#         print(infolist)

#         for file in infolist:
#             filepath = Path(file.filename)
#             filename = filepath.name
#             if filename == "color_correction.pkl":
#                 with config_zip.open(str(filepath), mode="r") as f:
#                     pickle_content = f.read()
#                     pickle_sha256 = hashlib.sha256()
#                     pickle_sha256.update(pickle_content)
#                     pickle_sha256_hex = pickle_sha256.hexdigest()
#             elif filename == "color.ini":
#                 with config_zip.open(str(filepath), mode="r") as f:
#                     color_ini_content = f.read()

#     if pickle_sha256_hex and color_ini_content:
#         # upload to azure blob

#         file_loc = f"{current_user.org_id}/{pickle_sha256_hex}.zip"
#         upload_file.file._file.seek(0)
#         upload_blob_file(
#             blob_service_client=private_blob_service,
#             category=settings.AZURE_STORAGE_CONTAINER_TONGUE_CONFIG,
#             file_path=file_loc,
#             object=upload_file.file._file,
#             overwrite=True,
#         )

#         # save to db

#         # pickle_content_base64_zlib = base64.b64encode(
#         #     zlib.compress(pickle_content, level=9)
#         # ).decode("utf-8")
#         measure_tongue_config_upload_in = schemas.MeasureTongueConfigUploadCreate(
#             org_id=current_user.org_id,
#             user_id=current_user.id,
#             color_correction_pkl="",
#             color_ini=color_ini_content,
#             file_loc=file_loc,
#             color_hash=pickle_sha256_hex,
#         )
#         measure_tongue_config_upload = await crud.measure_tongue_config_upload.create(
#             db_session=db_session,
#             obj_in=measure_tongue_config_upload_in,
#         )

#         measure_tongue_config = await crud.measure_tongue_config.get_by_org_id(
#             db_session=db_session,
#             org_id=current_user.org_id,
#         )
#         if measure_tongue_config:
#             await crud.measure_tongue_config.update(
#                 db_session=db_session,
#                 obj_current=measure_tongue_config,
#                 obj_new=schemas.MeasureTongueConfigUpdate(
#                     upload_id=measure_tongue_config_upload.id,
#                 ),
#             )
#         else:
#             await crud.measure_tongue_config.create(
#                 db_session=db_session,
#                 obj_in=schemas.MeasureTongueConfigCreate(
#                     org_id=current_user.org_id,
#                     upload_id=measure_tongue_config_upload.id,
#                 ),
#             )

#         return {
#             "msg": "File uploaded",
#             "upload_id": measure_tongue_config_upload.id,
#             "color_hash": pickle_sha256_hex,
#         }

#     else:
#         raise HTTPException(
#             status_code=422,
#             detail=[
#                 {
#                     "loc": ["color_correction.pkl"],
#                     "msg": "the file does not exist in the zip file",
#                     "type": "value_error",
#                 },
#             ],
#         )


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
        ...,
        min_length=10,
        max_length=10,
        regex="^[0-9]{4}/[0-9]{2}/[0-9]{2}$",
        description="生日，格式為 YYYY/MM/DD",
    ),
    # TODO: depreciated
    # age: Optional[int] = Form(..., ge=0, description="年齡。需大於 0。"),
    sex: Optional[SexType] = Form(..., description="性別。0: 男, 1: 女"),
    number: str = Form(
        ...,
        max_length=128,
        description="受測者編號或病歷編號 varchar(128)",
    ),
    proj_num: str = Form(None, max_length=128, description="計畫編號 varchar(128)"),
    # consult_dr_name: str = Form(None, max_length=128, description="判讀醫師姓名 varchar(128)"),
    consult_dr_id: UUID = Form(None, description="判讀醫師 ID varchar(128)"),
    # TODO: depreciated
    # measure_operator: str = Form(
    #     None,
    #     max_length=128,
    #     description="檢測人員 email varchar(128)",
    # ),
    # TODO: depreciated
    # color_hash: str = Form(
    #     None,
    #     min_length=64,
    #     max_length=64,
    #     description="校正檔 SHA256 varchar(64)",
    # ),
    tongue_front_file: UploadFile = File(description="舌象正面圖片"),
    tongue_back_file: UploadFile = File(description="舌象背面圖片"),
    # field_id: UUID = Form(
    #     ...,
    #     description="場域 ID UUID",
    # ),
    device_id: str = Form(
        ...,
        max_length=128,
        description="舌診擷取設備編號 varchar(128)",
    ),
    pad_id: str = Form(
        ...,
        max_length=128,
        description="平板 ID varchar(128)",
    ),
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
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": ["birthday"],
                    "msg": "date value is invalid",
                    "type": "value_error",
                },
            ],
        )

    cc_config = await crud.tongue_cc_config.get_by_device_id(
        db_session=db_session,
        device_id=device_id,
    )
    if cc_config is None:
        raise HTTPException(
            status_code=404,
            detail=f"Not found tongue_cc_config by device_id: {device_id}",
        )
    field = await crud.branch_field.get(
        db_session=db_session,
        id=cc_config.field_id,
        relations=["branch"],
    )
    if field is None:
        raise HTTPException(
            status_code=404,
            detail=f"Not found field by device_id: {device_id}",
        )
    if field.branch.org_id != current_user.org_id:
        raise HTTPException(
            status_code=400,
            detail=f"Permission Error",
        )

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
        org_id=current_user.org_id,
    )
    if not subject:
        subject_in = schemas.SubjectCreate(
            org_id=current_user.org_id,
            number=number,
            name=name or number,
            sid=id or number,
            birth_date=birth_date,
            age=age,
            sex=sex,
            deleted_mark=False,
        )
        subject = await crud.subject.create(db_session=db_session, obj_in=subject_in)

    tongue_upload_in = schemas.MeasureTongueUploadCreate(
        org_id=field.branch.org_id,
        branch_id=field.branch_id,
        field_id=field.id,
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
    )

    tongue_upload = await crud.measure_tongue_upload.create(
        db_session=db_session,
        obj_in=tongue_upload_in,
    )

    # TODO: update other subject info?
    subject_in = schemas.SubjectUpdate(
        last_measure_time=tongue_upload.created_at,
    )
    await crud.subject.update(
        db_session=db_session,
        obj_current=subject,
        obj_new=subject_in,
    )

    # upload to azure blob
    blob_prefix = crud.measure_tongue_upload.get_blob_prefix()
    blob_container = crud.measure_tongue_upload.get_container_name()
    tongue_front_original_loc = f"{blob_prefix}/{current_user.org_id}/{current_user.id}/{tongue_upload.id}/T_up.jpg"
    tongue_back_original_loc = f"{blob_prefix}/{current_user.org_id}/{current_user.id}/{tongue_upload.id}/T_down.jpg"
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

    # send task to worker
    # celery_app.send_task(
    #     "auo_project.services.celery.tasks.task_process_tongue_image_by_id",
    #     kwargs={"upload_id": tongue_upload.id},
    # )

    return tongue_upload


# @router.get("/demo/{measure_id}", response_model=AdvancedTongueOutput)
# async def get_tongue(
#     measure_id: UUID,
#     db_session: AsyncSession = Depends(deps.get_db),
#     current_user: models.User = Depends(deps.get_current_active_user),
# ):
#     tongue_upload = await crud.measure_tongue_upload.get(
#         db_session=db_session,
#         id=measure_id,
#         relations=["subject", "advanced_tongue2"],
#     )
#     if tongue_upload is None:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Not found measure id: {measure_id}",
#         )

#     front_loc = (
#         tongue_upload.tongue_front_corrected_loc
#         or tongue_upload.tongue_front_original_loc
#     )
#     back_loc = (
#         tongue_upload.tongue_back_corrected_loc
#         or tongue_upload.tongue_back_original_loc
#     )
#     if front_loc:
#         container_name = settings.AZURE_STORAGE_CONTAINER_INTERNET_IMAGE
#         file_path = front_loc
#         expiry = datetime.utcnow() + timedelta(minutes=15)
#         sas_token = generate_blob_sas(
#             account_name=settings.AZURE_STORAGE_ACCOUNT_INTERNET,
#             container_name=container_name,
#             blob_name=file_path,
#             account_key=settings.AZURE_STORAGE_KEY_INTERNET,
#             permission=BlobSasPermissions(read=True),
#             expiry=expiry,
#             # TODO: add ip
#         )
#         front_tongue_image_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_INTERNET}.blob.core.windows.net/{container_name}/{file_path}?{sas_token}"

#     if back_loc:
#         container_name = settings.AZURE_STORAGE_CONTAINER_INTERNET_IMAGE
#         file_path = back_loc
#         expiry = datetime.utcnow() + timedelta(minutes=15)
#         sas_token = generate_blob_sas(
#             account_name=settings.AZURE_STORAGE_ACCOUNT_INTERNET,
#             container_name=container_name,
#             blob_name=file_path,
#             account_key=settings.AZURE_STORAGE_KEY_INTERNET,
#             permission=BlobSasPermissions(read=True),
#             expiry=expiry,
#             # TODO: add ip
#         )
#         back_tongue_image_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_INTERNET}.blob.core.windows.net/{container_name}/{file_path}?{sas_token}"

#     advanced_tongue = (
#         tongue_upload.advanced_tongue2
#         or schemas.MeasureAdvancedTongue2Read(
#             id=measure_id,
#             measure_id=measure_id,
#             owner_id=current_user.id,
#         )
#     )

#     # TODO: merge to func
#     labled_symptom_map = {}
#     labeled_symptom_level_map = {}
#     labeled_symptom_disease_map = {}
#     if tongue_upload.advanced_tongue2:
#         for column in advanced_tongue.columns:
#             if "tongue" in column and "level" not in column and "disease" not in column:
#                 values = getattr(advanced_tongue, column, [])
#                 if isinstance(values, list) is False:
#                     values = [] if values is None else [values]
#                 labled_symptom_map[column] = set(values)

#         for column in advanced_tongue.columns:
#             if "_level_map" in column:
#                 item_id = column.replace("_level_map", "")
#                 obj = getattr(advanced_tongue, column)
#                 labeled_symptom_level_map[item_id] = {
#                     str(key): val for key, val in obj.items()
#                 }

#         for column in advanced_tongue.columns:
#             if "_disease_map" in column:
#                 item_id = column.replace("_disease_map", "")
#                 labeled_symptom_disease_map[item_id] = getattr(advanced_tongue, column)

#     # prepare component
#     tongue_symptoms = await crud.measure_tongue_symptom.get_all(db_session=db_session)
#     tongue_symptoms = py_.order_by(tongue_symptoms, ["order"])
#     tongue_symptom_diseases = await crud.measure_tongue_symptom_disease.get_all(
#         db_session=db_session,
#     )
#     tongue_symptom_diseases_dict = {}
#     tongue_groups = await crud.measure_tongue_group_symptom.get_all(
#         db_session=db_session,
#     )
#     tongue_groups = sorted(tongue_groups, key=lambda x: f"{x.item_id}:{x.group_id}")
#     tongue_group_dict = dict(
#         [
#             (f"{item.item_id}_{item.group_id}", item.component_type)
#             for item in tongue_groups
#         ],
#     )
#     for item in tongue_symptom_diseases:
#         tongue_symptom_diseases_dict[item.item_id] = tongue_symptom_diseases_dict.get(
#             item.item_id,
#             {},
#         )

#         disease_item = Disease(
#             value=item.disease_id,
#             # label=item.tongue_disease.disease_name,  # TODO: item.disease.disease_name
#             label=item.disease_id,  # TODO: item.disease.disease_name
#             selected=item.disease_id
#             in py_.get(
#                 labeled_symptom_disease_map,
#                 f"{item.item_id}.{item.symptom_id}",
#                 [],
#             ),
#         )

#         if item.symptom_id in tongue_symptom_diseases_dict[item.item_id]:
#             tongue_symptom_diseases_dict[item.item_id][item.symptom_id].append(
#                 disease_item,
#             )
#         else:
#             tongue_symptom_diseases_dict[item.item_id][item.symptom_id] = [disease_item]

#     level_map = {
#         1: "輕",
#         2: "中",
#         3: "重",
#     }
#     result = {}
#     result2 = []
#     for item in tongue_symptoms:
#         labeled_symptom_set = py_.get(labled_symptom_map, item.item_id, set())

#         append_item = {
#             "id": item.id,
#             "item_id": item.item_id,
#             "item_name": item.item_name,
#             "group_id": item.group_id or "0",
#             "symptom_id": item.symptom_id,
#             "symptom_name": item.symptom_name,
#             "symptom_description": item.symptom_description,
#             "level_options": (
#                 [
#                     LevelOption(
#                         label=level_map.get(int(level)),
#                         value=int(level),
#                         selected=int(level)
#                         == py_.get(
#                             labeled_symptom_level_map,
#                             f"{item.item_id}.{item.symptom_id}",
#                         ),
#                     )
#                     for level in item.symptom_levels
#                 ]
#                 if item.symptom_levels
#                 else []
#             ),
#             "is_default": item.is_default or False,
#             "is_normal": item.is_normal or False,
#             "diseases": tongue_symptom_diseases_dict.get(item.item_id, {}).get(
#                 item.symptom_id,
#                 [],
#             ),
#             "selected": (
#                 True
#                 if item.symptom_id in labeled_symptom_set
#                 else (
#                     (True if item.is_default else False)
#                     if len(labeled_symptom_set) == 0
#                     else False
#                 )
#             ),
#         }
#         if item.item_id in result:
#             result[item.item_id].append(append_item)
#         else:
#             result[item.item_id] = [append_item]

#         result2 = []
#         for key, value in result.items():
#             result2.append(
#                 {
#                     "item_id": key,
#                     "item_name": value[0]["item_name"],
#                     "symptoms": py_.chain(value)
#                     .group_by("group_id")
#                     .map_(
#                         lambda objs, group_id: {
#                             "item_id": key,
#                             "component_id": f"{key}_{group_id}",
#                             "component_type": tongue_group_dict.get(
#                                 f"{key}_{group_id}",
#                                 "radio",
#                             ),
#                             "children": py_.map_(
#                                 objs,
#                                 lambda x: py_.pick_by(
#                                     x,
#                                     [
#                                         "id",
#                                         "symptom_id",
#                                         "symptom_name",
#                                         "symptom_description",
#                                         "level_options",
#                                         "is_default",
#                                         "is_normal",
#                                         "selected",
#                                         "diseases",
#                                     ],
#                                 ),
#                             ),
#                         },
#                     )
#                     .value(),
#                 },
#             )

#     return AdvancedTongueOutput(
#         subject=tongue_upload.subject,
#         measure_tongue=TongueSampleMeasure(
#             image=schemas.TongueImage(
#                 front=front_tongue_image_url or "",
#                 back=back_tongue_image_url or "",
#             ),
#             measure_time=(tongue_upload.created_at + timedelta(hours=8)).strftime(
#                 "%Y-%m-%d %H:%M:%S",
#             ),
#             symptom=result2,
#             summary=advanced_tongue.tongue_summary,
#             memo=advanced_tongue.tongue_memo,
#             age=tongue_upload.age,
#             measure_operator=tongue_upload.measure_operator,
#         ),
#     )


# @router.patch("/demo/{measure_id}/tongue_info")
# async def update_measure_tongue_info(
#     measure_id: UUID,
#     tongue_info: schemas.MeasureAdvancedTongue2UpdateInput,
#     db_session: AsyncSession = Depends(deps.get_db),
#     current_user: models.User = Depends(deps.get_current_active_user),
#     ip_allowed: bool = Depends(deps.get_ip_allowed),
# ):
#     measure = await crud.measure_tongue_upload.get(
#         db_session=db_session,
#         id=measure_id,
#         relations=["owner", "subject", "advanced_tongue2"],
#     )
#     if measure is None:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Not found measure id: {measure_id}",
#         )
#     if (
#         current_user.org_id != measure.owner.org_id
#         and current_user.org.name != "tongue_label"
#     ):
#         raise HTTPException(
#             status_code=400,
#             detail=f"Permission Error",
#         )

#     advanced_tongue = await crud.measure_advanced_tongue2.get_by_measure_id(
#         db_session=db_session,
#         measure_id=measure_id,
#         owner_id=current_user.id,
#     )

#     def clean_level_map(
#         synptom_id_list: List[str],
#         level_map: Dict[str, int],
#     ) -> Dict[str, int]:
#         return {
#             key: value
#             for key, value in level_map.items()
#             if key in synptom_id_list and key is not None
#         }

#     def clean_disease_map(disease_map: Dict[str, str]) -> Dict[str, str]:
#         return disease_map

#     # TODO: validate
#     if advanced_tongue:
#         tongue_in = schemas.MeasureAdvancedTongue2Update(
#             tongue_tip=tongue_info.tongue_tip,
#             tongue_tip_disease_map=clean_disease_map(
#                 tongue_info.tongue_tip_disease_map,
#             ),
#             tongue_color=tongue_info.tongue_color,
#             tongue_color_disease_map=clean_disease_map(
#                 tongue_info.tongue_color_disease_map,
#             ),
#             tongue_shap=tongue_info.tongue_shap,
#             tongue_shap_level_map=clean_level_map(
#                 tongue_info.tongue_shap,
#                 tongue_info.tongue_shap_level_map,
#             ),
#             tongue_shap_disease_map=clean_disease_map(
#                 tongue_info.tongue_shap_disease_map,
#             ),
#             tongue_status1=tongue_info.tongue_status1,
#             tongue_status1_disease_map=clean_disease_map(
#                 tongue_info.tongue_status1_disease_map,
#             ),
#             tongue_status2=tongue_info.tongue_status2,
#             tongue_status2_level_map=clean_level_map(
#                 tongue_info.tongue_status2,
#                 tongue_info.tongue_status2_level_map,
#             ),
#             tongue_status2_disease_map=clean_disease_map(
#                 tongue_info.tongue_status2_disease_map,
#             ),
#             tongue_coating_color=tongue_info.tongue_coating_color,
#             tongue_coating_color_level_map=clean_level_map(
#                 tongue_info.tongue_coating_color,
#                 tongue_info.tongue_coating_color_level_map,
#             ),
#             tongue_coating_color_disease_map=clean_disease_map(
#                 tongue_info.tongue_coating_color_disease_map,
#             ),
#             tongue_coating_status=tongue_info.tongue_coating_status,
#             tongue_coating_status_level_map=clean_level_map(
#                 tongue_info.tongue_coating_status,
#                 tongue_info.tongue_coating_status_level_map,
#             ),
#             tongue_coating_status_disease_map=clean_disease_map(
#                 tongue_info.tongue_coating_status_disease_map,
#             ),
#             tongue_coating_bottom=tongue_info.tongue_coating_bottom,
#             tongue_coating_bottom_level_map=clean_level_map(
#                 tongue_info.tongue_coating_bottom,
#                 tongue_info.tongue_coating_bottom_level_map,
#             ),
#             tongue_coating_bottom_disease_map=clean_disease_map(
#                 tongue_info.tongue_coating_bottom_disease_map,
#             ),
#             tongue_summary=tongue_info.tongue_summary,
#             has_tongue_label=True,
#         )

#         tongue_info = await crud.measure_advanced_tongue2.update(
#             db_session=db_session,
#             obj_current=advanced_tongue,
#             obj_new=tongue_in.dict(exclude_unset=True),
#         )
#     else:
#         tongue_in = schemas.MeasureAdvancedTongue2Create(
#             measure_id=measure_id,
#             owner_id=current_user.id,
#             tongue_tip=tongue_info.tongue_tip,
#             tongue_tip_disease_map=clean_disease_map(
#                 tongue_info.tongue_tip_disease_map,
#             ),
#             tongue_color=tongue_info.tongue_color,
#             tongue_color_disease_map=clean_disease_map(
#                 tongue_info.tongue_color_disease_map,
#             ),
#             tongue_shap=tongue_info.tongue_shap,
#             tongue_shap_level_map=clean_level_map(
#                 tongue_info.tongue_shap,
#                 tongue_info.tongue_shap_level_map,
#             ),
#             tongue_shap_disease_map=clean_disease_map(
#                 tongue_info.tongue_shap_disease_map,
#             ),
#             tongue_status1=tongue_info.tongue_status1,
#             tongue_status1_disease_map=clean_disease_map(
#                 tongue_info.tongue_status1_disease_map,
#             ),
#             tongue_status2=tongue_info.tongue_status2,
#             tongue_status2_level_map=clean_level_map(
#                 tongue_info.tongue_status2,
#                 tongue_info.tongue_status2_level_map,
#             ),
#             tongue_status2_disease_map=clean_disease_map(
#                 tongue_info.tongue_status2_disease_map,
#             ),
#             tongue_coating_color=tongue_info.tongue_coating_color,
#             tongue_coating_color_level_map=clean_level_map(
#                 tongue_info.tongue_coating_color,
#                 tongue_info.tongue_coating_color_level_map,
#             ),
#             tongue_coating_color_disease_map=clean_disease_map(
#                 tongue_info.tongue_coating_color_disease_map,
#             ),
#             tongue_coating_status=tongue_info.tongue_coating_status,
#             tongue_coating_status_level_map=clean_level_map(
#                 tongue_info.tongue_coating_status,
#                 tongue_info.tongue_coating_status_level_map,
#             ),
#             tongue_coating_status_disease_map=clean_disease_map(
#                 tongue_info.tongue_coating_status_disease_map,
#             ),
#             tongue_coating_bottom=tongue_info.tongue_coating_bottom,
#             tongue_coating_bottom_level_map=clean_level_map(
#                 tongue_info.tongue_coating_bottom,
#                 tongue_info.tongue_coating_bottom_level_map,
#             ),
#             tongue_coating_bottom_disease_map=clean_disease_map(
#                 tongue_info.tongue_coating_bottom_disease_map,
#             ),
#             tongue_summary=tongue_info.tongue_summary,
#             tongue_memo="",
#             has_tongue_label=True,
#         )
#         tongue_info = await crud.measure_advanced_tongue2.create(
#             db_session=db_session,
#             obj_in=tongue_in,
#         )
#     return tongue_info


# @router.patch("/demo/{measure_id}/memo")
# async def update_tongue_memo(
#     measure_id: UUID,
#     memo: schemas.Memo,
#     *,
#     db_session: AsyncSession = Depends(deps.get_db),
#     current_user: models.User = Depends(deps.get_current_active_user),
#     ip_allowed: bool = Depends(deps.get_ip_allowed),
# ):
#     measure = await crud.measure_tongue_upload.get(
#         db_session=db_session,
#         id=measure_id,
#         relations=["owner", "subject", "advanced_tongue2"],
#     )
#     if measure is None:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Not found measure id: {measure_id}",
#         )
#     if (
#         current_user.org_id != measure.owner.org_id
#         and current_user.org.name != "tongue_label"
#     ):
#         raise HTTPException(
#             status_code=400,
#             detail=f"Permission Error",
#         )

#     advanced_tongue = await crud.measure_advanced_tongue2.get_by_measure_id(
#         db_session=db_session,
#         measure_id=measure_id,
#         owner_id=current_user.id,
#     )
#     if advanced_tongue:
#         tongue_in = schemas.MeasureAdvancedTongue2Update(
#             tongue_memo=memo.content,
#         )
#         tongue_info = await crud.measure_advanced_tongue2.update(
#             db_session=db_session,
#             obj_current=advanced_tongue,
#             obj_new=tongue_in,
#         )
#     else:
#         tongue_in = schemas.MeasureAdvancedTongue2Create(
#             measure_id=measure_id,
#             owner_id=current_user.id,
#             tongue_memo=memo.content,
#         )
#         tongue_info = await crud.measure_advanced_tongue2.create(
#             db_session=db_session,
#             obj_in=tongue_in,
#         )

#     return tongue_info


@router.post("/summary")
async def create_measure_tongue_summary(
    tongue_info: schemas.MeasureAdvancedTongue2UpdateInput,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    summary_components = [
        ("舌尖", ["tongue_tip"], ""),
        ("舌", ["tongue_color", "tongue_shap"], ""),
        ("苔", ["tongue_coating_color", "tongue_coating_status"], ""),
        ("舌態", ["tongue_status1"], ""),
        ("舌神", ["tongue_status2"], ""),
        ("舌下脈絡", ["tongue_coating_bottom"], ""),
    ]
    tongue_sympotms = await crud.measure_tongue_symptom.get_all(db_session=db_session)
    normal_symptoms = py_.filter_(tongue_sympotms, lambda x: x.is_normal)
    normal_symptom_dict = (
        py_.chain(normal_symptoms)
        .group_by("item_id")
        .map_values(lambda values: [e.symptom_id for e in values])
        .value()
    )

    # tongue_info ={"tongue_status1": ["白"], "tongue_status2": ["少"]}
    # tongue_info = {"tongue_status1": ["白"], "tongue_status2": ["薄"]}
    # show the symptom of the summary
    special_rules = {
        "tongue_coating_color": {
            "tongue_coating_color": ["白"],
            "tongue_coating_status": [
                "少",
                "厚",
                "腐",
                "膩",
                "潤",
                "燥",
                "花剝",
                "光剝",
            ],
        },
    }
    special_rules_match = py_.map_values(
        special_rules,
        lambda rule: py_.chain(rule)
        .map_values(
            lambda value, key: len(py_.intersection(py_.get(tongue_info, key), value))
            > 0,
        )
        .values()
        .every()
        .value(),
    )

    tongue_summary_list = []
    for prefix, items, suffix in summary_components:
        abnormal_symptoms_list = []
        for item in items:
            symptoms = getattr(tongue_info, item, [])

            if special_rules_match.get(item) is True:
                sub_abnormal_symptoms = symptoms
            else:
                sub_abnormal_symptoms = py_.difference(
                    symptoms,
                    normal_symptom_dict.get(item, []),
                )
            abnormal_symptoms_list.extend(sub_abnormal_symptoms)
        if abnormal_symptoms_list:
            tongue_summary_list.append(
                f"{prefix}{'、'.join(abnormal_symptoms_list)}{suffix}",
            )

    # 證型 disease
    disease_list = []
    for key in tongue_info.__fields__.keys():
        if key.endswith("_disease_map"):
            disease_map = getattr(tongue_info, key, {})
            disease_list.extend(py_.flatten(disease_map.values()))
    uniq_disease_list = list(set(disease_list))
    if uniq_disease_list:
        tongue_summary_list.append(f"一般會有{'、'.join(uniq_disease_list)}的傾向")

    def process_symptom_id_list(content: str):
        if isinstance(content, str):
            return content.split("、")
        return []

    records = surface_disease_records
    records = [
        {
            "tongue_tip": process_symptom_id_list(record["tongue_tip"]),
            "tongue_color": process_symptom_id_list(record["tongue_color"]),
            "tongue_shap": process_symptom_id_list(record["tongue_shap"]),
            "tongue_coating_color": process_symptom_id_list(
                record["tongue_coating_color"],
            ),
            "tongue_coating_status": process_symptom_id_list(
                record["tongue_coating_status"],
            ),
            "tongue_status1": process_symptom_id_list(record["tongue_status1"]),
            "tongue_status2": process_symptom_id_list(record["tongue_status2"]),
            # "tongue_coating_bottom": process_symptom_id_list(
            #     record["tongue_coating_bottom"]
            # ),
            "surface_disease": record["surface_disease"],
        }
        for record in records
    ]

    surface_summary_list = []
    for record in records:
        condition_match = []
        for item_id, symptom_id_list in record.items():
            if item_id == "surface_disease":
                continue

            selected_symptoms = getattr(tongue_info, item_id, [])
            match = sorted(selected_symptoms) == sorted(symptom_id_list)
            condition_match.append(match)

        if all(condition_match):
            surface_summary_list.append(record["surface_disease"])
            break
    if surface_summary_list:
        tongue_summary_list.append(f"可能有{'、'.join(surface_summary_list)}的情況")

    tongue_summary = "，".join(tongue_summary_list)
    tongue_summary = tongue_summary and tongue_summary + "。"

    return {"tongue_summary": tongue_summary}


@router.post("/summary")
async def create_measure_tongue_summary(
    tongue_info: schemas.MeasureAdvancedTongue2UpdateInput,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    summary_components = [
        ("舌尖", ["tongue_tip"], ""),
        ("舌", ["tongue_color", "tongue_shap"], ""),
        ("苔", ["tongue_coating_color", "tongue_coating_status"], ""),
        ("舌態", ["tongue_status1"], ""),
        ("舌神", ["tongue_status2"], ""),
        ("舌下脈絡", ["tongue_coating_bottom"], ""),
    ]
    tongue_sympotms = await crud.measure_tongue_symptom.get_all(db_session=db_session)
    normal_symptoms = py_.filter_(tongue_sympotms, lambda x: x.is_normal)
    normal_symptom_dict = (
        py_.chain(normal_symptoms)
        .group_by("item_id")
        .map_values(lambda values: [e.symptom_id for e in values])
        .value()
    )

    # tongue_info ={"tongue_status1": ["白"], "tongue_status2": ["少"]}
    # tongue_info = {"tongue_status1": ["白"], "tongue_status2": ["薄"]}
    # show the symptom of the summary
    special_rules = {
        "tongue_coating_color": {
            "tongue_coating_color": ["白"],
            "tongue_coating_status": [
                "少",
                "厚",
                "腐",
                "膩",
                "潤",
                "燥",
                "花剝",
                "光剝",
            ],
        },
    }
    special_rules_match = py_.map_values(
        special_rules,
        lambda rule: py_.chain(rule)
        .map_values(
            lambda value, key: len(py_.intersection(py_.get(tongue_info, key), value))
            > 0,
        )
        .values()
        .every()
        .value(),
    )

    tongue_summary_list = []
    for prefix, items, suffix in summary_components:
        abnormal_symptoms_list = []
        for item in items:
            symptoms = getattr(tongue_info, item, [])

            if special_rules_match.get(item) is True:
                sub_abnormal_symptoms = symptoms
            else:
                sub_abnormal_symptoms = py_.difference(
                    symptoms,
                    normal_symptom_dict.get(item, []),
                )
            abnormal_symptoms_list.extend(sub_abnormal_symptoms)
        if abnormal_symptoms_list:
            tongue_summary_list.append(
                f"{prefix}{'、'.join(abnormal_symptoms_list)}{suffix}",
            )

    # 證型 disease
    disease_list = []
    for key in tongue_info.__fields__.keys():
        if key.endswith("_disease_map"):
            disease_map = getattr(tongue_info, key, {})
            disease_list.extend(py_.flatten(disease_map.values()))
    uniq_disease_list = list(set(disease_list))
    if uniq_disease_list:
        tongue_summary_list.append(f"一般會有{'、'.join(uniq_disease_list)}的傾向")

    def process_symptom_id_list(content: str):
        if isinstance(content, str):
            return content.split("、")
        return []

    records = surface_disease_records
    records = [
        {
            "tongue_tip": process_symptom_id_list(record["tongue_tip"]),
            "tongue_color": process_symptom_id_list(record["tongue_color"]),
            "tongue_shap": process_symptom_id_list(record["tongue_shap"]),
            "tongue_coating_color": process_symptom_id_list(
                record["tongue_coating_color"],
            ),
            "tongue_coating_status": process_symptom_id_list(
                record["tongue_coating_status"],
            ),
            "tongue_status1": process_symptom_id_list(record["tongue_status1"]),
            "tongue_status2": process_symptom_id_list(record["tongue_status2"]),
            # "tongue_coating_bottom": process_symptom_id_list(
            #     record["tongue_coating_bottom"]
            # ),
            "surface_disease": record["surface_disease"],
        }
        for record in records
    ]

    surface_summary_list = []
    for record in records:
        condition_match = []
        for item_id, symptom_id_list in record.items():
            if item_id == "surface_disease":
                continue

            selected_symptoms = getattr(tongue_info, item_id, [])
            match = sorted(selected_symptoms) == sorted(symptom_id_list)
            condition_match.append(match)

        if all(condition_match):
            surface_summary_list.append(record["surface_disease"])
            break
    if surface_summary_list:
        tongue_summary_list.append(f"可能有{'、'.join(surface_summary_list)}的情況")

    tongue_summary = "，".join(tongue_summary_list)
    tongue_summary = tongue_summary and tongue_summary + "。"

    return {"tongue_summary": tongue_summary}


# @router.post("/demo/tongue_summary")
# async def create_measure_tongue_summary(
#     tongue_info: schemas.MeasureAdvancedTongue2UpdateInput,
#     db_session: AsyncSession = Depends(deps.get_db),
#     current_user: models.User = Depends(deps.get_current_active_user),
#     ip_allowed: bool = Depends(deps.get_ip_allowed),
# ):
#     summary_components = [
#         ("舌尖", ["tongue_tip"], ""),
#         ("舌", ["tongue_color", "tongue_shap"], ""),
#         ("苔", ["tongue_coating_color", "tongue_coating_status"], ""),
#         ("舌態", ["tongue_status1"], ""),
#         ("舌神", ["tongue_status2"], ""),
#         ("舌下脈絡", ["tongue_coating_bottom"], ""),
#     ]
#     tongue_sympotms = await crud.measure_tongue_symptom.get_all(db_session=db_session)
#     normal_symptoms = py_.filter_(tongue_sympotms, lambda x: x.is_normal)
#     normal_symptom_dict = (
#         py_.chain(normal_symptoms)
#         .group_by("item_id")
#         .map_values(lambda values: [e.symptom_id for e in values])
#         .value()
#     )

#     # tongue_info ={"tongue_status1": ["白"], "tongue_status2": ["少"]}
#     # tongue_info = {"tongue_status1": ["白"], "tongue_status2": ["薄"]}
#     # show the symptom of the summary
#     special_rules = {
#         "tongue_coating_color": {
#             "tongue_coating_color": ["白"],
#             "tongue_coating_status": [
#                 "少",
#                 "厚",
#                 "腐",
#                 "膩",
#                 "潤",
#                 "燥",
#                 "花剝",
#                 "光剝",
#             ],
#         },
#     }
#     special_rules_match = py_.map_values(
#         special_rules,
#         lambda rule: py_.chain(rule)
#         .map_values(
#             lambda value, key: len(py_.intersection(py_.get(tongue_info, key), value))
#             > 0,
#         )
#         .values()
#         .every()
#         .value(),
#     )

#     tongue_summary_list = []
#     for prefix, items, suffix in summary_components:
#         abnormal_symptoms_list = []
#         for item in items:
#             symptoms = getattr(tongue_info, item, [])

#             if special_rules_match.get(item) is True:
#                 sub_abnormal_symptoms = symptoms
#             else:
#                 sub_abnormal_symptoms = py_.difference(
#                     symptoms,
#                     normal_symptom_dict.get(item, []),
#                 )
#             abnormal_symptoms_list.extend(sub_abnormal_symptoms)
#         if abnormal_symptoms_list:
#             tongue_summary_list.append(
#                 f"{prefix}{'、'.join(abnormal_symptoms_list)}{suffix}",
#             )

#     # 證型 disease
#     disease_list = []
#     for key in tongue_info.__fields__.keys():
#         if key.endswith("_disease_map"):
#             disease_map = getattr(tongue_info, key, {})
#             disease_list.extend(py_.flatten(disease_map.values()))
#     uniq_disease_list = list(set(disease_list))
#     if uniq_disease_list:
#         tongue_summary_list.append(f"一般會有{'、'.join(uniq_disease_list)}的傾向")

#     def process_symptom_id_list(content: str):
#         if isinstance(content, str):
#             return content.split("、")
#         return []

#     records = surface_disease_records
#     records = [
#         {
#             "tongue_tip": process_symptom_id_list(record["tongue_tip"]),
#             "tongue_color": process_symptom_id_list(record["tongue_color"]),
#             "tongue_shap": process_symptom_id_list(record["tongue_shap"]),
#             "tongue_coating_color": process_symptom_id_list(
#                 record["tongue_coating_color"],
#             ),
#             "tongue_coating_status": process_symptom_id_list(
#                 record["tongue_coating_status"],
#             ),
#             "tongue_status1": process_symptom_id_list(record["tongue_status1"]),
#             "tongue_status2": process_symptom_id_list(record["tongue_status2"]),
#             # "tongue_coating_bottom": process_symptom_id_list(
#             #     record["tongue_coating_bottom"]
#             # ),
#             "surface_disease": record["surface_disease"],
#         }
#         for record in records
#     ]

#     surface_summary_list = []
#     for record in records:
#         condition_match = []
#         for item_id, symptom_id_list in record.items():
#             if item_id == "surface_disease":
#                 continue

#             selected_symptoms = getattr(tongue_info, item_id, [])
#             match = sorted(selected_symptoms) == sorted(symptom_id_list)
#             condition_match.append(match)

#         if all(condition_match):
#             surface_summary_list.append(record["surface_disease"])
#             break
#     if surface_summary_list:
#         tongue_summary_list.append(f"可能有{'、'.join(surface_summary_list)}的情況")

#     tongue_summary = "，".join(tongue_summary_list)
#     tongue_summary = tongue_summary and tongue_summary + "。"

#     return {"tongue_summary": tongue_summary}


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


# @router.get("/demo/subject/list", response_model=SubjectListResponse)
# async def get_subject(
#     number: Optional[str] = Query(None, regex="contains__", title="受測者編號"),
#     sid: Optional[str] = Query(None, regex="contains__", title="ID"),
#     name: Optional[str] = Query(None, regex="contains__", title="姓名"),
#     sex: Optional[SexType] = Query(None, title="性別：男=0, 女=1）"),
#     memo: Optional[str] = Query(None, regex="contains__", title="受測者標記"),
#     age: Optional[List[str]] = Query(
#         [],
#         regex="(ge|le)__",
#         title="年齡",
#         alias="age[]",
#     ),
#     sort_expr: Optional[str] = Query(
#         None,
#         title="updated_at 代表由小到大排。-updated_at 代表由大到小排。",
#     ),
#     specific_months: Optional[List[int]] = Query(
#         [],
#         alias="specific_months[]",
#         title="指定月份",
#     ),
#     dateutils: DateUtils = Depends(),
#     pagination: Pagination = Depends(),
#     *,
#     db_session: AsyncSession = Depends(deps.get_db),
#     current_user: models.User = Depends(deps.get_current_active_user),
#     ip_allowed: bool = Depends(deps.get_ip_allowed),
# ):
#     start_date, end_date = dateutils.get_dates()

#     utc8_now = datetime.utcnow() + timedelta(hours=8)
#     from dateutil.relativedelta import relativedelta

#     age_start = py_.head(list(filter(lambda x: x.startswith("ge__"), age)))
#     age_end = py_.head(list(filter(lambda x: x.startswith("le__"), age)))
#     birth_date_start = (
#         datetime(year=utc8_now.year, month=1, day=1)
#         - relativedelta(years=int(age_end.replace("le__", "")))
#         if age_end
#         else None
#     )
#     birth_date_end = (
#         datetime(year=utc8_now.year, month=12, day=31)
#         - relativedelta(years=int(age_start.replace("ge__", "")))
#         if age_start
#         else None
#     )
#     print("birth_date_start", birth_date_start, "birth_date_end", birth_date_end)
#     filters = {
#         "is_active": True,
#         "name__contains": name.replace("contains__", "") if name else None,
#         "sid__contains": sid.replace("contains__", "") if sid else None,
#         "birth_date__ge": func.date(birth_date_start) if birth_date_start else None,
#         "birth_date__le": func.date(birth_date_end) if birth_date_end else None,
#         "sex": sex,
#         "memo__contains": memo.replace("contains__", "") if memo else None,
#     }
#     filters = dict([(k, v) for k, v in filters.items() if v is not None and v != []])
#     filter_expr = models.Subject.filter_expr(**filters)
#     if number:
#         filter_expr.append(
#             cast(models.Subject.number, String).ilike(
#                 f'%{number.replace("contains__", "")}%',
#             ),
#         )
#     sort_expr = sort_expr.split(",") if sort_expr else ["-last_measure_time"]
#     sort_expr = [e.replace("+", "") for e in sort_expr]
#     order_expr = models.Subject.order_expr(*sort_expr)

#     start_date_utc0 = start_date - timedelta(hours=8) if start_date else None
#     end_date_utc0 = end_date - timedelta(hours=8) if end_date else None
#     time_filters = get_filters(
#         {
#             "created_at__ge": start_date_utc0,
#             "created_at__le": end_date_utc0,
#         },
#     )
#     org_filters = get_filters(
#         {
#             "org_id": (
#                 None
#                 if (
#                     current_user.is_superuser or current_user.org.name == "tongue_label"
#                 )
#                 else current_user.org_id
#             ),
#         },
#     )

#     org_expressions = models.MeasureTongueUpload.filter_expr(**org_filters)
#     time_expressions = models.MeasureTongueUpload.filter_expr(**time_filters)
#     if specific_months:
#         # TOOD: add 8 hours or add column created_at_utc8
#         time_expressions.append(
#             extract("month", models.MeasureTongueUpload.created_at).in_(
#                 specific_months,
#             ),
#         )

#     if crud.user.has_requires(user=current_user, groups=["user", "subject"]) and (
#         crud.user.has_requires(
#             user=current_user,
#             groups=["admin", "manager"],
#         )
#         is False
#     ):
#         measure_filters = get_filters(
#             {
#                 "owner_id": current_user.id,
#             },
#         )
#         subquery = (
#             select(models.Subject)
#             .join(models.MeasureTongueUpload)
#             .where(*time_expressions, *org_expressions, **measure_filters)
#             .distinct()
#             .subquery()
#         )
#     else:
#         subquery = (
#             select(models.Subject)
#             .join(models.MeasureTongueUpload)
#             .where(*time_expressions, *org_expressions)
#             .distinct()
#             .subquery()
#         )

#     query = (
#         select(models.Subject)
#         .join(subquery, models.Subject.id == subquery.c.id)
#         .where(*filter_expr)
#         # .options(
#         #     selectinload(models.Subject.standard_measure_info),
#         # )
#     )

#     items = await crud.subject.get_multi(
#         db_session=db_session,
#         query=query,
#         order_expr=order_expr,
#         skip=(pagination.page - 1) * pagination.per_page,
#         limit=pagination.per_page,
#     )
#     # subject_schema = get_subject_schema(org_name=current_user.org.name)
#     subject_schema = schemas.SubjectRead
#     items = [subject_schema.from_orm(item) for item in items]
#     resp = await db_session.execute(select(func.count()).select_from(query.subquery()))
#     total_count = resp.scalar_one()

#     return SubjectListResponse(
#         subject=await pagination.paginate2(total_count, items),
#         measure_times=MEASURE_TIMES,
#     )


# @router.get(
#     "/demo/subject/{subject_id}/measures",
#     response_model=schemas.SubjectReadWithMeasures,
# )
# async def get_subject_measures(
#     subject_id: UUID,
#     specific_months: Optional[List[int]] = Query(
#         [],
#         alias="specific_months[]",
#         title="指定月份",
#     ),
#     org_id: Optional[List[str]] = Query(
#         [],
#         title="檢測單位",
#     ),
#     measure_operator: Optional[List[str]] = Query(
#         [],
#         title="檢測人員",
#         alias="measure_operator[]",
#     ),
#     age: Optional[List[str]] = Query(
#         [],
#         regex="(ge|le)__",
#         title="年齡",
#         alias="age[]",
#     ),
#     sort_expr: Optional[str] = Query(
#         "-created_at",
#         title="created_at 代表由小到大排。-created_at 代表由大到小排。",
#     ),
#     dateutils: DateUtils = Depends(),
#     pagination: Pagination = Depends(),
#     *,
#     db_session: AsyncSession = Depends(deps.get_db),
#     current_user: models.User = Depends(deps.get_current_active_user),
#     ip_allowed: bool = Depends(deps.get_ip_allowed),
# ):
#     subject = await crud.subject.get(
#         db_session=db_session,
#         id=subject_id,
#     )
#     if not subject:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Not found subject id: {subject_id}",
#         )

#     # TODO: make frontend remove +
#     sort_expr = sort_expr.split(",") if sort_expr else ["-updated_at"]
#     order_expr = models.MeasureTongueUpload.order_expr(
#         *[e.replace("+", "") for e in sort_expr if "org_name" not in e]
#     )
#     org_order_expr = []
#     org_sort_expr = [e.replace("org_id", "name") for e in sort_expr if "org_id" in e]
#     if org_sort_expr:
#         org_order_expr = models.Org.order_expr(*org_sort_expr)
#     order_expr += org_order_expr

#     start_date, end_date = dateutils.get_dates()
#     age_start = py_.head(list(filter(lambda x: x.startswith("ge"), age)))
#     age_end = py_.head(list(filter(lambda x: x.startswith("le"), age)))

#     expressions = []

#     filters = get_filters(
#         {
#             "subject_id": subject_id,
#             "created_at__ge": start_date - timedelta(hours=8) if start_date else None,
#             "created_at__le": end_date - timedelta(hours=8) if end_date else None,
#             "age__ge": age_start and int(age_start.replace("ge__", "")),
#             "age__le": age_end and int(age_end.replace("le__", "")),
#             # TODO: filter org_id by user permission
#             "org_id__in": org_id,
#             "measure_operator__in": measure_operator,
#             # "has_memo__in": has_memos, # TODO
#             "org_id": (
#                 None
#                 if (
#                     current_user.is_superuser or current_user.org.name == "tongue_label"
#                 )
#                 else current_user.org_id
#             ),
#         },
#     )
#     print("filters", filters)
#     expressions = models.MeasureTongueUpload.filter_expr(**filters)
#     org_expressions = []
#     print("expressions", expressions)
#     if specific_months:
#         # TODO: fixme
#         expressions.append(
#             extract("month", models.MeasureTongueUpload.created_at).in_(
#                 specific_months,
#             ),
#         )
#     base_query = select(models.MeasureTongueUpload).where(
#         models.MeasureTongueUpload.subject_id == subject_id,
#     )
#     query = (
#         select(models.MeasureTongueUpload)
#         .join(models.Org)
#         .where(*expressions, *org_expressions)
#         .distinct()
#     )
#     measures = await crud.measure_tongue_upload.get_multi(
#         db_session=db_session,
#         query=query,
#         order_expr=order_expr,
#         relations=["org", "advanced_tongue2"],
#         unique=False,
#         skip=(pagination.page - 1) * pagination.per_page,
#         limit=pagination.per_page,
#     )

#     measures = [
#         schemas.MeasureInfoReadByList(
#             id=measure.id,
#             org_name=measure.org.name,
#             irregular_hr=None,
#             measure_time=(
#                 measure.created_at + timedelta(hours=8) if measure.created_at else None
#             ),
#             measure_operator=measure.measure_operator,
#             proj_num=None,
#             memo=(
#                 measure.advanced_tongue2.tongue_memo or ""
#                 if measure.advanced_tongue2
#                 else ""
#             ),
#             has_memo=(
#                 True
#                 if measure.advanced_tongue2 and measure.advanced_tongue2.tongue_memo
#                 else True
#             ),
#             age=measure.age,
#             bmi=None,
#             bcq=False,
#             is_standard_measure=False,
#         )
#         for measure in measures
#     ]

#     resp = await db_session.execute(select(func.count()).select_from(query.subquery()))
#     total_count = resp.scalar_one()
#     page_result = await pagination.paginate2(total_count, measures)

#     # TODO: user, division mapping
#     org_names = [{"value": current_user.org.id, "key": current_user.org.name}]

#     measure_operators_query = select(
#         func.distinct(base_query.c.measure_operator),
#     ).select_from(base_query.subquery())
#     measure_operators_result = await db_session.execute(measure_operators_query)
#     measure_operators = [
#         {"value": operator[0], "key": operator[0]}
#         for operator in measure_operators_result.fetchall()
#         if operator[0]
#     ]

#     subject_schema = schemas.SubjectRead
#     return schemas.SubjectReadWithMeasures(
#         subject=subject_schema(**subject.dict()),
#         measure=page_result,
#         measure_times=MEASURE_TIMES,
#         org_names=org_names,
#         measure_operators=measure_operators,
#         consult_drs=[],
#         irregular_hrs=[
#             {"value": False, "key": "規律"},
#             {"value": True, "key": "不規律"},
#         ],
#         proj_nums=[],
#         has_memos=[{"value": True, "key": "有"}, {"value": False, "key": "無"}],
#         not_include_low_pass_rates=[
#             {"value": True, "key": "是"},
#             {"value": False, "key": "否"},
#         ],
#     )
