from datetime import datetime, timedelta
from math import ceil
from typing import Any, Dict, List, Optional
from uuid import UUID

import pydash as py_
from azure.storage.blob import BlobSasPermissions, generate_blob_sas
from fastapi import APIRouter, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Depends
from pydantic import BaseModel, Field
from sqlalchemy import and_
from sqlmodel import String, cast, extract, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud, models, schemas
from auo_project.core.config import settings
from auo_project.core.constants import MEASURE_TIMES
from auo_project.core.dateutils import DateUtils
from auo_project.core.pagination import Pagination
from auo_project.core.utils import get_filters, safe_int
from auo_project.web.api import deps


class Memo(BaseModel):
    content: str = Field(None, title="內容")


class Link(BaseModel):
    self: str
    next: str = None
    prev: str = None


class TongueMeasure(BaseModel):
    id: UUID
    measure_time: str
    tongue: Dict[str, Any]


class TongueItem(BaseModel):
    subject: schemas.SubjectSecretRead
    measure: TongueMeasure


class TongueListPage(BaseModel):
    page: int
    per_page: int
    page_count: int
    total_count: int
    link: Link
    items: List[TongueItem] = Field(
        default=[],
        title="舌象紀錄",
    )


class TongueListOutput(BaseModel):
    measure_times: List[dict]
    tongue: TongueListPage


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
            "tongue_memo__contains": tongue_memo.replace("contains__", "")
            if tongue_memo
            else None,
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
        "tongue": TongueListPage(
            page=pagination.page,
            per_page=pagination.per_page,
            page_count=ceil(total_count / pagination.per_page),
            total_count=total_count,
            link=Link(
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
    return {
        "subject": schemas.SubjectSecretRead(
            **jsonable_encoder(measure.subject),
        ),
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
    memo: Memo,
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
