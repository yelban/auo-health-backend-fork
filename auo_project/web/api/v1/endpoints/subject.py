from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote
from uuid import UUID
from zipfile import ZIP_DEFLATED, ZipFile

import pandas as pd
import pydash as py_
from fastapi import APIRouter, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import and_
from sqlalchemy.orm import selectinload
from sqlmodel import String, cast, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud, models, schemas
from auo_project.core.constants import (
    HAND_TYPE_LABEL,
    MAX_DEPTH_RATIO,
    MEASURE_TIMES,
    POSITION_TYPE_LABEL,
    RANGE_TYPE_LABEL,
    SEX_TYPE_LABEL,
    LikeItemType,
    ReportType,
    SexType,
)
from auo_project.core.dateutils import DateUtils
from auo_project.core.file import get_max_amp_depth_of_range
from auo_project.core.pagination import Pagination
from auo_project.core.utils import (
    get_filters,
    get_hr_type,
    get_pct_cmp_base,
    get_pct_cmp_overall_and_standard,
    get_subject_schema,
    safe_divide,
)
from auo_project.models import MeasureInfo, Org
from auo_project.web.api import deps

router = APIRouter()


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
    items: List[Union[schemas.SubjectRead, schemas.SubjectSecretRead]]


class SubjectListResponse(BaseModel):
    subject: SubjectPage
    measure_times: List[Dict[str, Any]]
    proj_nums: List[Dict[str, Any]] = Field(default=[], title="計畫編號")
    sids: List[Dict[str, Any]] = Field(default=[], title="身分證字號")
    numbers: List[Dict[str, Any]] = Field(default=[], title="受測者編號")
    names: List[Dict[str, Any]] = Field(default=[], title="姓名")
    tags: List[Dict[str, Any]] = Field(default=[], title="受測者標籤")
    measure_operators: List[Dict[str, Any]] = Field(default=[], title="檢測人員")
    irregular_hrs: List[Dict[str, Any]] = Field(default=[], title="節律標記")
    sexes: List[Dict[str, Any]] = Field(default=[], title="生理性別")


class MultiMeasuresBody(BaseModel):
    org_id: UUID = None
    measure_ids: List[UUID] = []
    survey_names: List[str] = []


class ExportReportInputPayload(BaseModel):
    org_id: UUID
    subject_ids: List[UUID]
    report_types: List[ReportType]


# 下拉選單：計畫編號、受測者編號、身分證字號、姓名、受測者標籤、檢測人員
@router.get("/", response_model=SubjectListResponse)
async def get_subject(
    proj_num: Optional[List[str]] = Query([], title="計畫編號", alias="proj_num[]"),
    number: Optional[List[str]] = Query([], title="受測者編號", alias="number[]"),
    sid: Optional[List[str]] = Query([], title="身分證字號 ID", alias="sid[]"),
    name: Optional[List[str]] = Query([], title="姓名", alias="name[]"),
    birth_date: Optional[str] = Query(
        None,
        regex="^(YYYY|[0-9]{4})-(MM|[0-9]{2})-(DD|[0-9]{2})$",
        title="出生年月日",
    ),
    sex: Optional[List[SexType]] = Query(
        [],
        title="生理性別：男=0, 女=1）",
        alias="sex[]",
    ),
    tag: Optional[List[UUID]] = Query([], title="受測者標籤", alias="tag[]"),
    measure_operator: Optional[List[str]] = Query(
        [],
        title="檢測人員",
        alias="measure_operator[]",
    ),
    irregular_hr: Optional[List[bool]] = Query(
        [],
        title="節律標記",
        alias="irregular_hr[]",
    ),
    bmi: Optional[List[str]] = Query(
        [],
        regex="(ge|le)__",
        title="BMI",
        alias="bmi[]",
    ),  # measure bmi
    memo: Optional[str] = Query(None, regex="contains__", title="檢測標記"),
    liked: Optional[bool] = Query(
        None,
        title="是否篩選已加星號項目",
    ),
    sort_expr: Optional[str] = Query(
        None,
        title="updated_at 代表由小到大排。-updated_at 代表由大到小排。",
    ),
    dateutils: DateUtils = Depends(),
    pagination: Pagination = Depends(),
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    start_date, end_date = dateutils.get_dates()
    birth_date_like = (
        birth_date.replace("YYYY", "%").replace("MM", "%").replace("DD", "%")
        if birth_date
        else None
    )

    bmi_start = py_.head(list(filter(lambda x: x.startswith("ge"), bmi)))
    bmi_end = py_.head(list(filter(lambda x: x.startswith("le"), bmi)))
    irregular_hr = (
        [0 if e == False else 1 for e in irregular_hr] if irregular_hr else []
    )

    subject_base_filters = {
        "is_active": True,
        "org_id": None if current_user.is_superuser else current_user.org_id,
    }

    subject_filters = {
        **subject_base_filters,
        "proj_num__in": proj_num,
        "number__in": number,
        "sid__in": sid,
        "name__in": name,
        "sex__in": sex,
    }
    subject_base_filters = get_filters(subject_base_filters)
    subject_filters = get_filters(subject_filters)
    filter_expr = models.Subject.filter_expr(**subject_filters)
    if birth_date_like:
        filter_expr += [cast(models.Subject.birth_date, String).like(birth_date_like)]
    if tag:
        filter_expr += [models.Subject.tag_ids.overlap(tag)]

    sort_expr = sort_expr.split(",") if sort_expr else ["-last_measure_time"]
    sort_expr = [e.replace("+", "") for e in sort_expr]
    order_expr = models.Subject.order_expr(*sort_expr)

    measure_base_filters = {
        "is_active": True,
        "org_id": None if current_user.is_superuser else current_user.org_id,
    }
    measure_filters = get_filters(
        {
            **measure_base_filters,
            "measure_operator__in": measure_operator,
            "bmi__ge": bmi_start and int(bmi_start.replace("ge__", "")),
            "bmi__le": bmi_end and int(bmi_end.replace("le__", "")),
            "irregular_hr__in": irregular_hr,
            "memo__contains": (memo.replace("contains__", "") if memo else None),
            "measure_time__ge": start_date,
            "measure_time__le": end_date,
        },
    )

    measure_expressions = models.MeasureInfo.filter_expr(**measure_filters)

    if crud.user.has_requires(user=current_user, groups=["user", "subject"]) and (
        crud.user.has_requires(
            user=current_user,
            groups=["admin", "manager"],
        )
        is False
    ):
        file_filters = get_filters(
            {
                "owner_id": current_user.id,
            },
        )
        file_expressions = models.File.filter_expr(**file_filters)
        subquery = (
            select(models.Subject)
            .join(MeasureInfo)
            .join(models.File)
            .where(*measure_expressions, *file_expressions)
            .distinct()
            .subquery()
        )
    else:
        subquery = (
            select(models.Subject)
            .join(MeasureInfo)
            .where(*measure_expressions)
            .distinct()
            .subquery()
        )

    query = select(models.Subject).join(subquery, models.Subject.id == subquery.c.id)
    if liked:
        query = query.join(
            models.UserLikedItem,
            and_(
                models.UserLikedItem.item_id == models.Subject.id,
                models.UserLikedItem.item_type == LikeItemType.subjects,
                models.UserLikedItem.user_id == current_user.id,
            ),
        )
    query = query.where(*filter_expr).options(
        selectinload(models.Subject.standard_measure_info),
    )

    subject_tags = await crud.subject_tag.get_all(db_session=db_session)
    subject_tag_options = crud.subject_tag.format_options(options=subject_tags)
    subject_tag_dict = {
        tag.id: {
            "value": tag.id,
            "key": tag.name,
            "type": tag.tag_type,
        }
        for tag in subject_tags
    }

    items = await crud.subject.get_multi(
        db_session=db_session,
        query=query,
        order_expr=order_expr,
        skip=(pagination.page - 1) * pagination.per_page,
        limit=pagination.per_page,
    )

    if liked:
        liked_items_ids_set = set([item.id for item in items])
    else:
        liked_items = await crud.user_liked_item.get_by_item_type_and_ids(
            db_session=db_session,
            user_id=current_user.id,
            item_type=LikeItemType.subjects,
            item_ids=[item.id for item in items],
            is_active=True,
        )
        liked_items_ids_set = set([item.item_id for item in liked_items])

    # enrich subject tags and liked
    item_dicts = [
        {
            **jsonable_encoder(item),
            "tags": list(
                filter(
                    lambda x: x is not None,
                    [subject_tag_dict.get(tag_id) for tag_id in item.tag_ids],
                ),
            ),
            "liked": item.id in liked_items_ids_set,
        }
        for item in items
    ]
    subject_schema = get_subject_schema(org_name=current_user.org.name)
    items = [subject_schema(**item_dict) for item_dict in item_dicts]
    resp = await db_session.execute(select(func.count()).select_from(query.subquery()))
    total_count = resp.scalar_one()

    # 下拉選單：計畫編號、受測者編號、身分證字號、姓名、受測者標籤、檢測人員
    def format_option_key_value(query_result):
        return sorted(
            [
                {"value": result[0], "key": result[0]}
                for result in query_result.fetchall()
                if result[0]
            ],
            key=lambda x: x["key"],
        )

    async def get_option_list(db_session):
        dropdown_filters1 = MeasureInfo.filter_expr(**measure_base_filters)
        dropdown_filters2 = models.Subject.filter_expr(**subject_base_filters)
        measure_dropdown_query = (
            select(MeasureInfo)
            .join(models.Subject)
            .where(*dropdown_filters1, *dropdown_filters2)
        )

        measure_operators_query = select(
            func.distinct(measure_dropdown_query.c.measure_operator),
        ).select_from(measure_dropdown_query.subquery())
        measure_operators_result = await db_session.execute(measure_operators_query)
        measure_operators = format_option_key_value(measure_operators_result)

        subject_dropdown_query = (
            select(models.Subject)
            .join(MeasureInfo)
            .where(*dropdown_filters1, *dropdown_filters2)
        )
        proj_nums_query = select(
            func.distinct(subject_dropdown_query.c.proj_num),
        ).select_from(
            subject_dropdown_query.subquery(),
        )
        proj_nums_result = await db_session.execute(proj_nums_query)
        proj_nums = format_option_key_value(proj_nums_result)

        sids_query = select(func.distinct(subject_dropdown_query.c.sid)).select_from(
            subject_dropdown_query.subquery(),
        )
        sids_result = await db_session.execute(sids_query)
        sids = format_option_key_value(sids_result)

        names_query = select(func.distinct(subject_dropdown_query.c.name)).select_from(
            subject_dropdown_query.subquery(),
        )
        names_result = await db_session.execute(names_query)
        names = format_option_key_value(names_result)

        numbers_query = select(
            func.distinct(subject_dropdown_query.c.number),
        ).select_from(subject_dropdown_query.subquery())
        numbers_result = await db_session.execute(numbers_query)
        numbers = format_option_key_value(numbers_result)

        return {
            "proj_nums": proj_nums,
            "measure_operators": measure_operators,
            "sids": sids,
            "names": names,
            "numbers": numbers,
            "tags": subject_tag_options,
        }

    dropdown_options = await get_option_list(db_session=db_session)
    return SubjectListResponse(
        subject=await pagination.paginate2(total_count, items),
        measure_times=MEASURE_TIMES,
        proj_nums=dropdown_options["proj_nums"],
        sids=dropdown_options["sids"],
        names=dropdown_options["names"],
        numbers=dropdown_options["numbers"],
        tags=dropdown_options["tags"],
        measure_operators=dropdown_options["measure_operators"],
        irregular_hrs=[
            {"value": False, "key": "規律"},
            {"value": True, "key": "不規律"},
        ],
        pass_rates=[{"value": pct, "key": f"{pct}%"} for pct in range(10, 110, 10)],
        sexes=[{"value": 0, "key": "男"}, {"value": 1, "key": "女"}],
    )


@router.get("/{subject_id}/measures", response_model=schemas.SubjectReadWithMeasures)
async def get_subject_measures(
    subject_id: UUID,
    measure_operator: Optional[List[str]] = Query(
        [],
        title="檢測人員",
        alias="measure_operator[]",
    ),
    measure_memo: Optional[str] = Query(None, regex="contains__", title="檢測標記"),
    irregular_hr: Optional[List[bool]] = Query(
        [],
        title="節律標記",
        alias="irregular_hr[]",
    ),
    has_bcq: Optional[List[bool]] = Query(
        [],
        title="BCQ 檢測/體質量表",
        alias="has_bcq[]",
    ),
    # TODO: implement filter by pass rate
    pass_rate: Optional[List[int]] = Query(
        [],
        title="脈波通過率",
        alias="pass_rate[]",
    ),
    sort_expr: Optional[str] = Query(
        "-measure_time",
        title="measure_time 代表由小到大排。-measure_time 代表由大到小排。",
    ),
    dateutils: DateUtils = Depends(),
    pagination: Pagination = Depends(),
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    subject = await crud.subject.get(
        db_session=db_session,
        id=subject_id,
        relations=[models.Subject.standard_measure_info],
    )
    if not subject:
        raise HTTPException(
            status_code=400,
            detail=f"Not found subject id: {subject_id}",
        )
    if subject.is_active is False:
        raise HTTPException(
            status_code=400,
            detail=f"Subject is not active.",
        )

    # TODO: make frontend remove +
    sort_expr = sort_expr.split(",") if sort_expr else ["-updated_at"]
    order_expr = models.MeasureInfo.order_expr(
        *[e.replace("+", "") for e in sort_expr if "org_name" not in e]
    )
    org_order_expr = []
    org_sort_expr = [e.replace("org_id", "name") for e in sort_expr if "org_id" in e]
    if org_sort_expr:
        org_order_expr = models.Org.order_expr(*org_sort_expr)
    order_expr += org_order_expr
    # TODO: implement
    # TODO: add division constraint
    start_date, end_date = dateutils.get_dates()
    irregular_hr = (
        [0 if e == False else 1 for e in irregular_hr] if irregular_hr else []
    )
    expressions = []
    filters = get_filters(
        {
            "is_active": True,
            "subject_id": subject_id,
            "measure_time__ge": start_date,
            "measure_time__le": end_date,
            "measure_operator__in": measure_operator,
            "irregular_hr__in": irregular_hr,
            "has_bcq__in": has_bcq,
            "memo__contains": (
                measure_memo.replace("contains__", "") if measure_memo else None
            ),
            "org_id": None if current_user.is_superuser else current_user.org_id,
        },
    )
    print("filters", filters)
    expressions = models.MeasureInfo.filter_expr(**filters)
    org_expressions = []
    print("expressions", expressions)
    base_query = select(MeasureInfo).where(MeasureInfo.subject_id == subject_id)
    query = (
        select(MeasureInfo).join(Org).where(*expressions, *org_expressions).distinct()
    )
    measures = await crud.measure_info.get_multi(
        db_session=db_session,
        query=query,
        order_expr=order_expr,
        relations=["org"],
        unique=False,
        skip=(pagination.page - 1) * pagination.per_page,
        limit=pagination.per_page,
    )
    tongue_measures = await crud.measure_advanced_tongue2.get_by_owner_id(
        db_session=db_session,
        owner_id=current_user.id,
    )
    tongue_measure_ids = {tongue_measure.info_id for tongue_measure in tongue_measures}
    measures = [
        schemas.MeasureInfoReadByList(
            id=measure.id,
            org_name=measure.org.name,
            irregular_hr=measure.irregular_hr,
            measure_time=measure.measure_time,
            measure_operator=measure.measure_operator,
            proj_num=measure.proj_num,
            memo=measure.memo,
            has_memo=measure.has_memo,
            age=measure.age,
            bmi=measure.bmi,
            sbp=measure.sbp,
            dbp=measure.dbp,
            bcq=measure.has_bcq,
            has_tongue_measure=measure.id in tongue_measure_ids,
            is_standard_measure=(subject.standard_measure_id == measure.id),
        )
        for measure in measures
    ]

    resp = await db_session.execute(select(func.count()).select_from(query.subquery()))
    total_count = resp.scalar_one()
    page_result = await pagination.paginate2(total_count, measures)

    # # TODO: user, division mapping
    # org_names = [{"value": current_user.org.id, "key": current_user.org.name}]

    measure_operators_query = select(
        func.distinct(base_query.c.measure_operator),
    ).select_from(base_query.subquery())
    measure_operators_result = await db_session.execute(measure_operators_query)
    measure_operators = [
        {"value": operator[0], "key": operator[0]}
        for operator in measure_operators_result.fetchall()
        if operator[0]
    ]

    all_subject_tags = await crud.subject_tag.get_all(db_session=db_session)
    subject_tags = [
        subject_tag
        for subject_tag in all_subject_tags
        if subject_tag.id in subject.tag_ids
    ]
    liked_items = await crud.user_liked_item.get_by_item_type_and_ids(
        db_session=db_session,
        user_id=current_user.id,
        item_type=LikeItemType.subjects,
        item_ids=[subject_id],
        is_active=True,
    )
    liked_items_ids_set = set([item.item_id for item in liked_items])

    subject_tag_options = crud.subject_tag.format_options(options=subject_tags)
    subject_dict = {
        **jsonable_encoder(subject),
        "liked": subject_id in liked_items_ids_set,
        "tags": subject_tag_options,
    }
    return schemas.SubjectReadWithMeasures(
        subject=get_subject_schema(org_name=current_user.org.name)(**subject_dict),
        measure=page_result,
        measure_times=MEASURE_TIMES,
        measure_operators=measure_operators,
        irregular_hrs=[
            {"value": False, "key": "規律"},
            {"value": True, "key": "不規律"},
        ],
        has_bcqs=[{"value": True, "key": "有"}, {"value": False, "key": "無"}],
        pass_rates=[{"value": pct, "key": f"{pct}% 以上"} for pct in range(10, 110, 10)],
        subject_tags=crud.subject_tag.format_options(options=all_subject_tags),
        normal_spec=[
            {"column": "irregular_hrs", "range": [0, 1]},
            {"column": "bmi", "range": [18.5, 24]},
            {"column": "sbp", "range": [90, 130]},
            {"column": "dbp", "range": [60, 80]},
        ],
    )


@router.patch("/{subject_id}")
async def update_subject(
    subject_id: UUID,
    subject_in: schemas.SubjectUpdateInput,
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    subject = await crud.subject.get(db_session=db_session, id=subject_id)
    if not subject:
        raise HTTPException(
            status_code=400,
            detail=f"Not found subject id: {subject_id}",
        )

    if current_user.org_id != subject.org_id:
        raise HTTPException(
            status_code=400,
            detail="Permission Error",
        )

    # if number already exists, raise error
    same_number_subject = await crud.subject.get_by_number_and_org_id(
        db_session=db_session,
        org_id=current_user.org_id,
        number=subject_in.number,
    )
    # TODO: check whether need merge different subjects to the one
    if same_number_subject and same_number_subject.id != subject_id:
        raise HTTPException(
            status_code=400,
            detail=f"Number already exists: {subject_in.number}",
        )

    subject = await crud.subject.update(
        db_session=db_session,
        obj_current=subject,
        obj_new=subject_in.dict(exclude_none=True),
    )
    return subject


@router.patch("/{subject_id}/tags", response_model=schemas.SubjectRead)
async def update_subject_tags(
    subject_id: UUID,
    tag_input: schemas.SubjectTagUpdateInput,
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    subject = await crud.subject.get(
        db_session=db_session,
        id=subject_id,
        relations=[models.Subject.standard_measure_info],
    )
    if not subject:
        raise HTTPException(
            status_code=400,
            detail=f"Not found subject id: {subject_id}",
        )

    if (current_user.org_id != subject.org_id) and current_user.is_superuser is False:
        raise HTTPException(
            status_code=400,
            detail="Permission Error",
        )

    all_subject_tags = await crud.subject_tag.get_all(db_session=db_session)
    all_subject_tag_ids = [tag.id for tag in all_subject_tags]
    extra_ids = set(tag_input.tag_ids) - set(all_subject_tag_ids)
    if len(extra_ids) > 0:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid tag ids: {extra_ids}",
        )
    subject.tag_ids = tag_input.tag_ids
    db_session.add(subject)
    await db_session.commit()
    await db_session.refresh(subject)

    subject_tags = [
        subject_tag
        for subject_tag in all_subject_tags
        if subject_tag.id in subject.tag_ids
    ]
    subject_tag_options = crud.subject_tag.format_options(options=subject_tags)
    return {**jsonable_encoder(subject), "tags": subject_tag_options}


# @depreciated: use subject tags instead
@router.patch("/{subject_id}/memo", response_model=schemas.SubjectRead)
async def update_subject_memo(
    subject_id: UUID,
    memo: str,
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    subject = await crud.subject.get(
        db_session=db_session,
        id=subject_id,
        relations=[models.Subject.standard_measure_info],
    )
    if not subject:
        raise HTTPException(
            status_code=400,
            detail=f"Not found subject id: {subject_id}",
        )
    if len(memo) > 1024:
        raise HTTPException(status_code=422, detail=f"memo max length is 1024")
    subject.memo = memo
    db_session.add(subject)
    await db_session.commit()
    await db_session.refresh(subject)
    return subject


@router.patch(
    "/{subject_id}/measure/{measure_id}/standard_value",
    # response_model=schemas.SubjectRead, # TODO: fixme
)
async def set_standard_value(
    subject_id: UUID,
    measure_id: UUID,
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    subject = await crud.subject.get(db_session=db_session, id=subject_id)
    if not subject:
        raise HTTPException(
            status_code=400,
            detail=f"Not found subject id: {subject_id}",
        )

    measure = await crud.measure_info.get(db_session=db_session, id=measure_id)
    if not measure:
        raise HTTPException(
            status_code=400,
            detail=f"Not found measure id: {measure_id}",
        )
    if subject.id != measure.subject_id:
        raise HTTPException(
            status_code=400,
            detail=f"subject id and measure id are not aligned",
        )

    subject.standard_measure_id = measure_id
    db_session.add(subject)
    await db_session.commit()
    await db_session.refresh(subject)
    return subject


@router.post(
    "/{subject_id}/reset_standard_value",
    response_model=schemas.SubjectRead,
)
async def reset_standard_value(
    subject_id: UUID,
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    subject = await crud.subject.get(db_session=db_session, id=subject_id)
    if not subject:
        raise HTTPException(
            status_code=400,
            detail=f"Not found subject id: {subject_id}",
        )

    subject.standard_measure_id = None
    db_session.add(subject)
    await db_session.commit()
    await db_session.refresh(subject)
    return subject


@router.get(
    "/{subject_id}/multi_measures",
    response_model=schemas.MultiMeasureDetailResponse,
)
async def get_multi_measure_summary(
    subject_id: UUID,
    measure_ids: List[UUID] = Query([], alias="measure_ids[]", title="受測編號清單"),
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    if len(measure_ids) > 20:
        raise HTTPException(
            status_code=400,
            detail=f"The number of ids cannot be more than 20.",
        )
    # TODO: add current_user permission filter
    subject = await crud.subject.get(db_session=db_session, id=subject_id)
    standard_measure_info = None
    standard_cn_dict = {}
    if subject.standard_measure_id:
        standard_measure_info = await crud.measure_info.get(
            db_session=db_session,
            id=subject.standard_measure_id,
        )
        standard_cn_dict = await crud.measure_statistic.get_means_dict(
            db_session=db_session,
            measure_id=subject.standard_measure_id,
        )
    measures_infos = await crud.measure_info.get_by_ids(
        db_session=db_session,
        list_ids=measure_ids,
        relations=["bcq"],
    )
    # check all measure ids are valid: owned by the subject
    for measure in measures_infos:
        if measure.subject_id != subject_id:
            raise HTTPException(
                status_code=400,
                detail=f"The subject id and subject id of the measure is not the same.",
            )

    measures_infos = py_.sort(
        measures_infos,
        key=lambda item: item.measure_time,
        reverse=False,
    )

    mean_statistic_dict = (
        await crud.measure_statistic.get_flat_dict_by_ids_and_statistics(
            db_session=db_session,
            measure_ids=measure_ids,
            statistic_name="MEAN",
        )
    )
    # TODO: optimize because only used by pw, CNCV
    cv_statistic_dict = (
        await crud.measure_statistic.get_flat_dict_by_ids_and_statistics(
            db_session=db_session,
            measure_ids=measure_ids,
            statistic_name="CV",
        )
    )
    # TODO: optimize because only used by PNSD
    std_statistic_dict = (
        await crud.measure_statistic.get_flat_dict_by_ids_and_statistics(
            db_session=db_session,
            measure_ids=measure_ids,
            statistic_name="STD",
        )
    )

    mean_statistic_model_dict = {}
    for key, val in mean_statistic_dict.items():
        mean_statistic_model_dict[
            key
        ] = crud.measure_statistic.get_flat_statistic_model2(val)

    cv_statistic_model_dict = {}
    for key, val in cv_statistic_dict.items():
        cv_statistic_model_dict[key] = crud.measure_statistic.get_flat_statistic_model2(
            val,
        )

    std_statistic_model_dict = {}
    for key, val in std_statistic_dict.items():
        std_statistic_model_dict[
            key
        ] = crud.measure_statistic.get_flat_statistic_model2(val)

    # TODO: add CV and STD
    means_dict = await crud.measure_cn_mean.get_dict_by_sex(
        db_session=db_session,
        sex=subject.sex,
    )

    measures = [
        schemas.MultiMeasureDetailRead(
            id=measure.id,
            tn=f"T{idx+1}",
            measure_time=measure.measure_time,
            hr_l=measure.hr_l,
            hr_l_type=get_hr_type(measure.hr_l, measure.hr_r),
            hr_r=measure.hr_r,
            hr_r_type=get_hr_type(measure.hr_r, measure.hr_l),
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
            xingcheng_l_cu=safe_divide(measure.xingcheng_l_cu, 0.2),
            xingcheng_l_qu=safe_divide(measure.xingcheng_l_qu, 0.2),
            xingcheng_l_ch=safe_divide(measure.xingcheng_l_ch, 0.2),
            xingcheng_r_cu=safe_divide(measure.xingcheng_r_cu, 0.2),
            xingcheng_r_qu=safe_divide(measure.xingcheng_r_qu, 0.2),
            xingcheng_r_ch=safe_divide(measure.xingcheng_r_ch, 0.2),
            # TODO: add these extra cols to measure.infos
            h1_l_cu=mean_statistic_model_dict.get(measure.id).h1_l_cu,
            h1_l_qu=mean_statistic_model_dict.get(measure.id).h1_l_qu,
            h1_l_ch=mean_statistic_model_dict.get(measure.id).h1_l_ch,
            h1_r_cu=mean_statistic_model_dict.get(measure.id).h1_r_cu,
            h1_r_qu=mean_statistic_model_dict.get(measure.id).h1_r_qu,
            h1_r_ch=mean_statistic_model_dict.get(measure.id).h1_r_ch,
            h1_div_t1_l_cu=safe_divide(
                mean_statistic_model_dict.get(measure.id).h1_div_t1_l_cu,
                1000,
            ),
            h1_div_t1_l_qu=safe_divide(
                mean_statistic_model_dict.get(measure.id).h1_div_t1_l_qu,
                1000,
            ),
            h1_div_t1_l_ch=safe_divide(
                mean_statistic_model_dict.get(measure.id).h1_div_t1_l_ch,
                1000,
            ),
            h1_div_t1_r_cu=safe_divide(
                mean_statistic_model_dict.get(measure.id).h1_div_t1_r_cu,
                1000,
            ),
            h1_div_t1_r_qu=safe_divide(
                mean_statistic_model_dict.get(measure.id).h1_div_t1_r_qu,
                1000,
            ),
            h1_div_t1_r_ch=safe_divide(
                mean_statistic_model_dict.get(measure.id).h1_div_t1_r_ch,
                1000,
            ),
            pr_l_cu=mean_statistic_model_dict.get(measure.id).pr_l_cu,
            pr_l_qu=mean_statistic_model_dict.get(measure.id).pr_l_qu,
            pr_l_ch=mean_statistic_model_dict.get(measure.id).pr_l_ch,
            pr_r_cu=mean_statistic_model_dict.get(measure.id).pr_r_cu,
            pr_r_qu=mean_statistic_model_dict.get(measure.id).pr_r_qu,
            pr_r_ch=mean_statistic_model_dict.get(measure.id).pr_r_ch,
            w1_l_cu=mean_statistic_model_dict.get(measure.id).w1_l_cu,
            w1_l_qu=mean_statistic_model_dict.get(measure.id).w1_l_qu,
            w1_l_ch=mean_statistic_model_dict.get(measure.id).w1_l_ch,
            w1_r_cu=mean_statistic_model_dict.get(measure.id).w1_r_cu,
            w1_r_qu=mean_statistic_model_dict.get(measure.id).w1_r_qu,
            w1_r_ch=mean_statistic_model_dict.get(measure.id).w1_r_ch,
            w1_div_t_l_cu=mean_statistic_model_dict.get(measure.id).w1_div_t_l_cu,
            w1_div_t_l_qu=mean_statistic_model_dict.get(measure.id).w1_div_t_l_qu,
            w1_div_t_l_ch=mean_statistic_model_dict.get(measure.id).w1_div_t_l_ch,
            w1_div_t_r_cu=mean_statistic_model_dict.get(measure.id).w1_div_t_r_cu,
            w1_div_t_r_qu=mean_statistic_model_dict.get(measure.id).w1_div_t_r_qu,
            w1_div_t_r_ch=mean_statistic_model_dict.get(measure.id).w1_div_t_r_ch,
            t1_div_t_l_cu=mean_statistic_model_dict.get(measure.id).t1_div_t_l_cu,
            t1_div_t_l_qu=mean_statistic_model_dict.get(measure.id).t1_div_t_l_qu,
            t1_div_t_l_ch=mean_statistic_model_dict.get(measure.id).t1_div_t_l_ch,
            t1_div_t_r_cu=mean_statistic_model_dict.get(measure.id).t1_div_t_r_cu,
            t1_div_t_r_qu=mean_statistic_model_dict.get(measure.id).t1_div_t_r_qu,
            t1_div_t_r_ch=mean_statistic_model_dict.get(measure.id).t1_div_t_r_ch,
            pw_l_cu=mean_statistic_model_dict.get(measure.id).pw_l_cu,
            pw_l_qu=mean_statistic_model_dict.get(measure.id).pw_l_qu,
            pw_l_ch=mean_statistic_model_dict.get(measure.id).pw_l_ch,
            pw_r_cu=mean_statistic_model_dict.get(measure.id).pw_r_cu,
            pw_r_qu=mean_statistic_model_dict.get(measure.id).pw_r_qu,
            pw_r_ch=mean_statistic_model_dict.get(measure.id).pw_r_ch,
            pwcv_l_cu=cv_statistic_model_dict.get(measure.id).pw_l_cu,
            pwcv_l_qu=cv_statistic_model_dict.get(measure.id).pw_l_qu,
            pwcv_l_ch=cv_statistic_model_dict.get(measure.id).pw_l_ch,
            pwcv_r_cu=cv_statistic_model_dict.get(measure.id).pw_r_cu,
            pwcv_r_qu=cv_statistic_model_dict.get(measure.id).pw_r_qu,
            pwcv_r_ch=cv_statistic_model_dict.get(measure.id).pw_r_ch,
            a0_l_cu=mean_statistic_model_dict.get(measure.id).a0_l_cu,
            a0_l_qu=mean_statistic_model_dict.get(measure.id).a0_l_qu,
            a0_l_ch=mean_statistic_model_dict.get(measure.id).a0_l_ch,
            a0_r_cu=mean_statistic_model_dict.get(measure.id).a0_r_cu,
            a0_r_qu=mean_statistic_model_dict.get(measure.id).a0_r_qu,
            a0_r_ch=mean_statistic_model_dict.get(measure.id).a0_r_ch,
            cn=get_pct_cmp_overall_and_standard(
                mean_statistic_dict.get(measure.id),
                means_dict,
                standard_cn_dict,
                "c",
            ),
            # TODO: changeme
            cncv=get_pct_cmp_base(
                cv_statistic_dict.get(measure.id),
                "c",
            ),
            # TODO: changeme
            pn=get_pct_cmp_overall_and_standard(
                mean_statistic_dict.get(measure.id),
                means_dict,
                standard_cn_dict,
                "p",
            ),
            # TODO: changeme
            pnsd=get_pct_cmp_base(
                std_statistic_dict.get(measure.id),
                "p",
            ),
            # TODO: remove me
            bcq=schemas.BCQ(
                exist=measure.has_bcq,
                score_yang=measure.bcq.percentage_yang if measure.bcq else None,
                score_yin=measure.bcq.percentage_yin if measure.bcq else None,
                score_phlegm=measure.bcq.percentage_phlegm if measure.bcq else None,
                score_yang_head=(
                    measure.bcq.percentage_yang_head if measure.bcq else None
                ),
                score_yang_chest=(
                    measure.bcq.percentage_yang_chest if measure.bcq else None
                ),
                score_yang_limbs=(
                    measure.bcq.percentage_yang_limbs if measure.bcq else None
                ),
                score_yang_abdomen=(
                    measure.bcq.percentage_yang_abdomen if measure.bcq else None
                ),
                score_yang_surface=(
                    measure.bcq.percentage_yang_surface if measure.bcq else None
                ),
                score_yin_head=measure.bcq.percentage_yin_head if measure.bcq else None,
                score_yin_limbs=(
                    measure.bcq.percentage_yin_limbs if measure.bcq else None
                ),
                score_yin_gt=measure.bcq.percentage_yin_gt if measure.bcq else None,
                score_yin_surface=(
                    measure.bcq.percentage_yin_surface if measure.bcq else None
                ),
                score_yin_abdomen=(
                    measure.bcq.percentage_yin_abdomen if measure.bcq else None
                ),
                score_phlegm_trunk=(
                    measure.bcq.percentage_phlegm_trunk if measure.bcq else None
                ),
                score_phlegm_surface=(
                    measure.bcq.percentage_phlegm_surface if measure.bcq else None
                ),
                score_phlegm_head=(
                    measure.bcq.percentage_phlegm_head if measure.bcq else None
                ),
                score_phlegm_gt=(
                    measure.bcq.percentage_phlegm_gt if measure.bcq else None
                ),
                percentage_yang=measure.bcq.percentage_yang if measure.bcq else None,
                percentage_yin=measure.bcq.percentage_yin if measure.bcq else None,
                percentage_phlegm=(
                    measure.bcq.percentage_phlegm if measure.bcq else None
                ),
                percentage_yang_head=(
                    measure.bcq.percentage_yang_head if measure.bcq else None
                ),
                percentage_yang_chest=(
                    measure.bcq.percentage_yang_chest if measure.bcq else None
                ),
                percentage_yang_limbs=(
                    measure.bcq.percentage_yang_limbs if measure.bcq else None
                ),
                percentage_yang_abdomen=(
                    measure.bcq.percentage_yang_abdomen if measure.bcq else None
                ),
                percentage_yang_surface=(
                    measure.bcq.percentage_yang_surface if measure.bcq else None
                ),
                percentage_yin_head=(
                    measure.bcq.percentage_yin_head if measure.bcq else None
                ),
                percentage_yin_limbs=(
                    measure.bcq.percentage_yin_limbs if measure.bcq else None
                ),
                percentage_yin_gt=(
                    measure.bcq.percentage_yin_gt if measure.bcq else None
                ),
                percentage_yin_surface=(
                    measure.bcq.percentage_yin_surface if measure.bcq else None
                ),
                percentage_yin_abdomen=(
                    measure.bcq.percentage_yin_abdomen if measure.bcq else None
                ),
                percentage_phlegm_trunk=(
                    measure.bcq.percentage_phlegm_trunk if measure.bcq else None
                ),
                percentage_phlegm_surface=(
                    measure.bcq.percentage_phlegm_surface if measure.bcq else None
                ),
                percentage_phlegm_head=(
                    measure.bcq.percentage_phlegm_head if measure.bcq else None
                ),
                percentage_phlegm_gt=(
                    measure.bcq.percentage_phlegm_gt if measure.bcq else None
                ),
            ),
            # bcq=measure.bcq or {},
        )
        for idx, measure in enumerate(measures_infos)
    ]

    normal_spec = schemas.MeasureNormalRange(
        hr=schemas.NormalRange(lower=50, upper=90),
        mean_prop_range_max=schemas.NormalRange(lower=1, upper=2),
        max_amp_depth_of_range=schemas.NormalRange(lower=1, upper=2),
        max_empt_value=schemas.NormalRange(lower=10, upper=35),
        max_slope_value=schemas.NormalRange(lower=100, upper=200),
        xingcheng=schemas.NormalRange(lower=10, upper=40),  # TODO: check / 0.2 or not
        h1=schemas.NormalRange(lower=10, upper=35),
        h1_div_t1=schemas.NormalRange(lower=1, upper=2),
        pr=schemas.NormalRange(lower=30, upper=150),
        w1=schemas.NormalRange(lower=0.3, upper=0.6),
        w1_div_t=schemas.NormalRange(lower=0.4, upper=0.8),
        t1_div_t=schemas.NormalRange(lower=0.1, upper=0.3),
        pw=schemas.NormalRange(lower=0.1, upper=0.2),
        pwcv=schemas.NormalRange(lower=None, upper=None),
        a0=schemas.NormalRange(lower=None, upper=None),
        cn=schemas.NormalRange(lower=None, upper=None),
        cncv=schemas.NormalRange(lower=None, upper=None),
        pn=schemas.NormalRange(lower=None, upper=None),
        pnsd=schemas.NormalRange(lower=None, upper=None),
    )

    return schemas.MultiMeasureDetailResponse(
        subject=get_subject_schema(org_name=current_user.org.name)(
            **jsonable_encoder(subject),
            standard_measure_info=standard_measure_info,
        ),
        measures=measures,
        normal_spec=normal_spec,
    )


@router.get(
    "/{subject_id}/multi_measures/export",
    response_model=schemas.MultiMeasureDetailResponse,
)
async def get_multi_measure_summary_data(
    subject_id: UUID,
    measure_ids: List[UUID] = Query([], alias="measure_ids[]", title="受測編號清單"),
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    if len(measure_ids) > 20:
        raise HTTPException(
            status_code=400,
            detail=f"The number of ids cannot be more than 20.",
        )
    # TODO: add current_user permission filter
    subject = await crud.subject.get(db_session=db_session, id=subject_id)

    measures_infos = await crud.measure_info.get_by_ids(
        db_session=db_session,
        list_ids=measure_ids,
        relations=["bcq"],
    )

    # check all measure ids are valid: owned by the subject
    for measure in measures_infos:
        if measure.subject_id != subject_id:
            raise HTTPException(
                status_code=400,
                detail=f"The subject id and subject id of the measure is not the same.",
            )

    measures_infos = py_.sort(
        measures_infos,
        key=lambda item: item.measure_time,
        reverse=False,
    )

    mean_statistic_dict = (
        await crud.measure_statistic.get_flat_dict_by_ids_and_statistics(
            db_session=db_session,
            measure_ids=measure_ids,
            statistic_name="MEAN",
        )
    )
    # TODO: optimize because only used by pw, CNCV
    cv_statistic_dict = (
        await crud.measure_statistic.get_flat_dict_by_ids_and_statistics(
            db_session=db_session,
            measure_ids=measure_ids,
            statistic_name="CV",
        )
    )
    # TODO: optimize because only used by PNSD
    std_statistic_dict = (
        await crud.measure_statistic.get_flat_dict_by_ids_and_statistics(
            db_session=db_session,
            measure_ids=measure_ids,
            statistic_name="STD",
        )
    )

    mean_statistic_model_dict = {}
    for key, val in mean_statistic_dict.items():
        mean_statistic_model_dict[
            key
        ] = crud.measure_statistic.get_flat_statistic_model2(val)

    cv_statistic_model_dict = {}
    for key, val in cv_statistic_dict.items():
        cv_statistic_model_dict[key] = crud.measure_statistic.get_flat_statistic_model2(
            val,
        )

    std_statistic_model_dict = {}
    for key, val in std_statistic_dict.items():
        std_statistic_model_dict[
            key
        ] = crud.measure_statistic.get_flat_statistic_model2(val)

    hands = ["r", "l"]
    positions = ["cu", "qu", "ch"]

    file1_records = [
        schemas.DF1Schema(
            measure_time=measure.measure_time.strftime("%Y/%m/%d %H:%M:%S"),
            number=subject.number,
            birth_date=(
                subject.birth_date.strftime("%Y-%m-%d") if subject.birth_date else None
            ),
            sex_label=SEX_TYPE_LABEL.get(subject.sex),
            bmi=measure.bmi,
            hand=HAND_TYPE_LABEL.get(hand),
            position=POSITION_TYPE_LABEL.get(position),
            pass_rate=py_.get(measure, f"pass_rate_{hand}_{position}"),
            hr=py_.get(measure, f"hr_{hand}"),
            range=RANGE_TYPE_LABEL.get(
                get_max_amp_depth_of_range(
                    py_.get(measure, f"static_range_start_{hand}_{position}"),
                    py_.get(measure, f"static_range_end_{hand}_{position}"),
                    py_.get(measure, f"static_max_amp_{hand}_{position}"),
                    ratio=MAX_DEPTH_RATIO,
                ),
            ),
            static_max_amp=py_.get(measure, f"max_amp_value_{hand}_{position}"),
            max_slope_value=py_.get(measure, f"max_slope_value_{hand}_{position}"),
            width=safe_divide(py_.get(measure, f"xingcheng_{hand}_{position}"), 0.2),
            h1=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"h1_{hand}_{position}",
            ),
            h1_div_t1=safe_divide(
                py_.get(
                    mean_statistic_model_dict.get(measure.id),
                    f"h1_div_t1_{hand}_{position}",
                ),
                1000,
            ),
            w1=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"w1_{hand}_{position}",
            ),
            w1_div_t=safe_divide(
                py_.get(
                    mean_statistic_model_dict.get(measure.id),
                    f"w1_div_t_{hand}_{position}",
                ),
                1000,
            ),
            t1_div_t=safe_divide(
                py_.get(
                    mean_statistic_model_dict.get(measure.id),
                    f"t1_div_t_{hand}_{position}",
                ),
                1000,
            ),
            pw=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"pw_{hand}_{position}",
            ),
            pwcv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"pw_{hand}_{position}",
            ),
            a0=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"a0_{hand}_{position}",
            ),
            c1_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c1_{hand}_{position}",
            ),
            c2_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c2_{hand}_{position}",
            ),
            c3_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c3_{hand}_{position}",
            ),
            c4_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c4_{hand}_{position}",
            ),
            c5_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c5_{hand}_{position}",
            ),
            c6_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c6_{hand}_{position}",
            ),
            c7_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c7_{hand}_{position}",
            ),
            c8_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c8_{hand}_{position}",
            ),
            c9_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c9_{hand}_{position}",
            ),
            c10_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c10_{hand}_{position}",
            ),
            c11_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c11_{hand}_{position}",
            ),
            c12_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c12_{hand}_{position}",
            ),
            c1_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c1_{hand}_{position}",
            ),
            c2_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c2_{hand}_{position}",
            ),
            c3_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c3_{hand}_{position}",
            ),
            c4_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c4_{hand}_{position}",
            ),
            c5_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c5_{hand}_{position}",
            ),
            c6_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c6_{hand}_{position}",
            ),
            c7_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c7_{hand}_{position}",
            ),
            c8_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c8_{hand}_{position}",
            ),
            c9_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c9_{hand}_{position}",
            ),
            c10_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c10_{hand}_{position}",
            ),
            c11_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c11_{hand}_{position}",
            ),
            c12_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c12_{hand}_{position}",
            ),
            p1_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p1_{hand}_{position}",
            ),
            p2_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p2_{hand}_{position}",
            ),
            p3_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p3_{hand}_{position}",
            ),
            p4_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p4_{hand}_{position}",
            ),
            p5_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p5_{hand}_{position}",
            ),
            p6_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p6_{hand}_{position}",
            ),
            p7_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p7_{hand}_{position}",
            ),
            p8_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p8_{hand}_{position}",
            ),
            p9_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p9_{hand}_{position}",
            ),
            p10_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p10_{hand}_{position}",
            ),
            p11_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p11_{hand}_{position}",
            ),
            p12_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p12_{hand}_{position}",
            ),
            p1_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p1_{hand}_{position}",
            ),
            p2_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p2_{hand}_{position}",
            ),
            p3_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p3_{hand}_{position}",
            ),
            p4_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p4_{hand}_{position}",
            ),
            p5_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p5_{hand}_{position}",
            ),
            p6_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p6_{hand}_{position}",
            ),
            p7_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p7_{hand}_{position}",
            ),
            p8_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p8_{hand}_{position}",
            ),
            p9_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p9_{hand}_{position}",
            ),
            p10_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p10_{hand}_{position}",
            ),
            p11_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p11_{hand}_{position}",
            ),
            p12_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p12_{hand}_{position}",
            ),
        )
        for measure in measures_infos
        for position in positions
        for hand in hands
    ]

    df2_columns = [
        ("yang", "陰虛", ""),
        ("yin", "陽虛", ""),
        ("phlegm", "痰瘀", ""),
        ("yin_head", "陰虛次因子", "頭部"),
        ("yin_limbs", "陰虛次因子", "四肢"),
        ("yin_gt", "陰虛次因子", "腸胃道"),
        ("yin_surface", "陰虛次因子", "體表"),
        ("yin_abdomen", "陰虛次因子", "腹腔"),
        ("yang_head", "陽虛次因子", "頭部"),
        ("yang_chest", "陽虛次因子", "胸部"),
        ("yang_limbs", "陽虛次因子", "四肢"),
        ("yang_abdomen", "陽虛次因子", "腹腔"),
        ("yang_surface", "陽虛次因子", "體表"),
        ("phlegm_trunk", "痰瘀次因子", "軀幹"),
        ("phlegm_surface", "痰瘀次因子", "體表"),
        ("phlegm_head", "痰瘀次因子", "頭部"),
        ("phlegm_gt", "痰瘀次因子", "腸胃道"),
    ]

    file2_records = py_.flatten(
        [
            [
                schemas.DF2Schema(
                    measure_time=measure.measure_time.strftime("%Y/%m/%d %H:%M:%S"),
                    number=subject.number.upper(),
                    item_type=column_pair[1],
                    position=column_pair[2],
                    score=py_.get(measure.bcq, f"score_{column_pair[0]}"),
                    percentage=py_.get(measure.bcq, f"percentage_{column_pair[0]}"),
                )
                for column_pair in df2_columns
            ]
            for measure in measures_infos
            if measure.bcq
        ],
    )

    file1_content = BytesIO()
    file2_content = BytesIO()

    df1 = pd.DataFrame.from_records(jsonable_encoder(file1_records))
    df1.to_csv(file1_content, index=False, encoding="big5")
    file1_content.seek(0)

    df2 = pd.DataFrame.from_records(jsonable_encoder(file2_records))
    df2.to_csv(file2_content, index=False, encoding="big5")
    file2_content.seek(0)

    output_zip = BytesIO()
    with ZipFile(output_zip, "a", ZIP_DEFLATED, compresslevel=9) as output_zip_obj:
        output_zip_obj.writestr(f"量測資料.csv", file1_content.getvalue())
    with ZipFile(output_zip, "a", ZIP_DEFLATED, compresslevel=9) as output_zip_obj:
        output_zip_obj.writestr(f"BCQ.csv", file2_content.getvalue())
    output_zip.seek(0)

    today_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"單人多次下載檔案_{today_str}.zip"

    return StreamingResponse(
        output_zip,
        media_type="application/x-zip-compressed",
        headers={
            "Access-Control-Expose-Headers": "Content-Disposition",
            "Content-Disposition": "inline; filename*=utf-8''{}".format(
                quote(filename),
            ),
            "Content-Type": "application/octet-stream",
        },
    )


@router.post(
    "/multi_measures/export_by_conditions",
    response_model=schemas.MultiMeasureDetailResponse,
)
async def get_multi_measure_by_conditions(
    body: MultiMeasuresBody,
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    if body.measure_ids != [] and body.survey_names != []:
        raise HTTPException(
            status_code=422,
            detail="Cannot provide measure_ids and survey_names together",
        )
    if body.measure_ids:
        measure_ids = body.measure_ids
    elif body.survey_names:
        measure_ids = []
        survey_ids = []
        for survey_name in body.survey_names:
            survey = await crud.measure_survey.get_by_name(
                db_session=db_session,
                name=survey_name,
            )
            if survey is not None:
                survey_ids.append(survey.id)
        survey_results = await crud.measure_survey_result.get_by_survey_ids(
            db_session=db_session,
            survey_ids=survey_ids,
        )
        measure_ids.extend(
            [
                survey_result.measure_id
                for survey_result in survey_results
                if survey_result.measure_id
            ],
        )
    elif body.org_id:
        result = await db_session.execute(
            select(models.MeasureInfo.id).where(
                models.MeasureInfo.org_id == body.org_id,
            ),
        )
        measure_ids = result.scalars().all()
    else:
        raise HTTPException(
            status_code=422,
            detail="Please provide measure_ids or survey_names",
        )
    measures_infos = await crud.measure_info.get_by_ids(
        db_session=db_session,
        list_ids=measure_ids,
        relations=["bcq"],
    )
    subject_list = [
        await crud.subject.get(db_session=db_session, id=measure.subject_id)
        for measure in measures_infos
    ]
    subject_dict = {subject.id: subject for subject in subject_list}

    measures_infos = py_.sort(
        measures_infos,
        key=lambda item: item.measure_time,
        reverse=False,
    )

    mean_statistic_dict = (
        await crud.measure_statistic.get_flat_dict_by_ids_and_statistics(
            db_session=db_session,
            measure_ids=measure_ids,
            statistic_name="MEAN",
        )
    )
    # TODO: optimize because only used by pw, CNCV
    cv_statistic_dict = (
        await crud.measure_statistic.get_flat_dict_by_ids_and_statistics(
            db_session=db_session,
            measure_ids=measure_ids,
            statistic_name="CV",
        )
    )
    # TODO: optimize because only used by PNSD
    std_statistic_dict = (
        await crud.measure_statistic.get_flat_dict_by_ids_and_statistics(
            db_session=db_session,
            measure_ids=measure_ids,
            statistic_name="STD",
        )
    )

    mean_statistic_model_dict = {}
    for key, val in mean_statistic_dict.items():
        mean_statistic_model_dict[
            key
        ] = crud.measure_statistic.get_flat_statistic_model2(val)

    cv_statistic_model_dict = {}
    for key, val in cv_statistic_dict.items():
        cv_statistic_model_dict[key] = crud.measure_statistic.get_flat_statistic_model2(
            val,
        )

    std_statistic_model_dict = {}
    for key, val in std_statistic_dict.items():
        std_statistic_model_dict[
            key
        ] = crud.measure_statistic.get_flat_statistic_model2(val)

    hands = ["r", "l"]
    positions = ["cu", "qu", "ch"]

    file1_records = [
        schemas.DF1Schema(
            measure_time=measure.measure_time.strftime("%Y/%m/%d %H:%M:%S"),
            number=subject_dict[measure.subject_id].number.upper(),
            birth_date=(
                subject_dict[measure.subject_id].birth_date.strftime("%Y-%m-%d")
                if subject_dict[measure.subject_id].birth_date
                else None
            ),
            sex_label=SEX_TYPE_LABEL.get(subject_dict[measure.subject_id].sex),
            bmi=measure.bmi,
            hand=HAND_TYPE_LABEL.get(hand),
            position=POSITION_TYPE_LABEL.get(position),
            pass_rate=py_.get(measure, f"pass_rate_{hand}_{position}"),
            hr=py_.get(measure, f"hr_{hand}"),
            range=RANGE_TYPE_LABEL.get(
                get_max_amp_depth_of_range(
                    py_.get(measure, f"static_range_start_{hand}_{position}"),
                    py_.get(measure, f"static_range_end_{hand}_{position}"),
                    py_.get(measure, f"static_max_amp_{hand}_{position}"),
                    ratio=MAX_DEPTH_RATIO,
                ),
            ),
            static_max_amp=py_.get(measure, f"max_amp_value_{hand}_{position}"),
            max_slope_value=py_.get(measure, f"max_slope_value_{hand}_{position}"),
            width=safe_divide(py_.get(measure, f"xingcheng_{hand}_{position}"), 0.2),
            h1=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"h1_{hand}_{position}",
            ),
            h1_div_t1=safe_divide(
                py_.get(
                    mean_statistic_model_dict.get(measure.id),
                    f"h1_div_t1_{hand}_{position}",
                ),
                1000,
            ),
            w1=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"w1_{hand}_{position}",
            ),
            w1_div_t=safe_divide(
                py_.get(
                    mean_statistic_model_dict.get(measure.id),
                    f"w1_div_t_{hand}_{position}",
                ),
                1000,
            ),
            t1_div_t=safe_divide(
                py_.get(
                    mean_statistic_model_dict.get(measure.id),
                    f"t1_div_t_{hand}_{position}",
                ),
                1000,
            ),
            pw=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"pw_{hand}_{position}",
            ),
            pwcv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"pw_{hand}_{position}",
            ),
            a0=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"a0_{hand}_{position}",
            ),
            c1_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c1_{hand}_{position}",
            ),
            c2_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c2_{hand}_{position}",
            ),
            c3_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c3_{hand}_{position}",
            ),
            c4_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c4_{hand}_{position}",
            ),
            c5_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c5_{hand}_{position}",
            ),
            c6_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c6_{hand}_{position}",
            ),
            c7_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c7_{hand}_{position}",
            ),
            c8_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c8_{hand}_{position}",
            ),
            c9_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c9_{hand}_{position}",
            ),
            c10_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c10_{hand}_{position}",
            ),
            c11_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c11_{hand}_{position}",
            ),
            c12_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"c12_{hand}_{position}",
            ),
            c1_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c1_{hand}_{position}",
            ),
            c2_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c2_{hand}_{position}",
            ),
            c3_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c3_{hand}_{position}",
            ),
            c4_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c4_{hand}_{position}",
            ),
            c5_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c5_{hand}_{position}",
            ),
            c6_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c6_{hand}_{position}",
            ),
            c7_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c7_{hand}_{position}",
            ),
            c8_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c8_{hand}_{position}",
            ),
            c9_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c9_{hand}_{position}",
            ),
            c10_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c10_{hand}_{position}",
            ),
            c11_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c11_{hand}_{position}",
            ),
            c12_cv=py_.get(
                cv_statistic_model_dict.get(measure.id),
                f"c12_{hand}_{position}",
            ),
            p1_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p1_{hand}_{position}",
            ),
            p2_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p2_{hand}_{position}",
            ),
            p3_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p3_{hand}_{position}",
            ),
            p4_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p4_{hand}_{position}",
            ),
            p5_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p5_{hand}_{position}",
            ),
            p6_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p6_{hand}_{position}",
            ),
            p7_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p7_{hand}_{position}",
            ),
            p8_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p8_{hand}_{position}",
            ),
            p9_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p9_{hand}_{position}",
            ),
            p10_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p10_{hand}_{position}",
            ),
            p11_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p11_{hand}_{position}",
            ),
            p12_mean=py_.get(
                mean_statistic_model_dict.get(measure.id),
                f"p12_{hand}_{position}",
            ),
            p1_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p1_{hand}_{position}",
            ),
            p2_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p2_{hand}_{position}",
            ),
            p3_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p3_{hand}_{position}",
            ),
            p4_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p4_{hand}_{position}",
            ),
            p5_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p5_{hand}_{position}",
            ),
            p6_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p6_{hand}_{position}",
            ),
            p7_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p7_{hand}_{position}",
            ),
            p8_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p8_{hand}_{position}",
            ),
            p9_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p9_{hand}_{position}",
            ),
            p10_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p10_{hand}_{position}",
            ),
            p11_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p11_{hand}_{position}",
            ),
            p12_std=py_.get(
                std_statistic_model_dict.get(measure.id),
                f"p12_{hand}_{position}",
            ),
        )
        for idx, measure in enumerate(measures_infos)
        for position in positions
        for hand in hands
    ]

    df2_columns = [
        ("yang", "陰虛", ""),
        ("yin", "陽虛", ""),
        ("phlegm", "痰瘀", ""),
        ("yin_head", "陰虛次因子", "頭部"),
        ("yin_limbs", "陰虛次因子", "四肢"),
        ("yin_gt", "陰虛次因子", "腸胃道"),
        ("yin_surface", "陰虛次因子", "體表"),
        ("yin_abdomen", "陰虛次因子", "腹腔"),
        ("yang_head", "陽虛次因子", "頭部"),
        ("yang_chest", "陽虛次因子", "胸部"),
        ("yang_limbs", "陽虛次因子", "四肢"),
        ("yang_abdomen", "陽虛次因子", "腹腔"),
        ("yang_surface", "陽虛次因子", "體表"),
        ("phlegm_trunk", "痰瘀次因子", "軀幹"),
        ("phlegm_surface", "痰瘀次因子", "體表"),
        ("phlegm_head", "痰瘀次因子", "頭部"),
        ("phlegm_gt", "痰瘀次因子", "腸胃道"),
    ]

    file2_records = py_.flatten(
        [
            [
                schemas.DF2Schema(
                    measure_time=measure.measure_time.strftime("%Y/%m/%d %H:%M:%S"),
                    number=subject_dict[measure.subject_id].number.upper(),
                    item_type=column_pair[1],
                    position=column_pair[2],
                    score=py_.get(measure.bcq, f"score_{column_pair[0]}"),
                    percentage=py_.get(measure.bcq, f"percentage_{column_pair[0]}"),
                )
                for column_pair in df2_columns
            ]
            for idx, measure in enumerate(measures_infos)
            if measure.bcq
        ],
    )

    file1_content = BytesIO()
    file1_utf8_content = BytesIO()
    file2_content = BytesIO()

    df1 = pd.DataFrame.from_records(jsonable_encoder(file1_records))
    df1.to_csv(file1_content, index=False, encoding="big5")
    file1_content.seek(0)

    df1.to_csv(file1_utf8_content, index=False, encoding="utf8")
    file1_utf8_content.seek(0)

    df2 = pd.DataFrame.from_records(jsonable_encoder(file2_records))
    df2.to_csv(file2_content, index=False, encoding="big5")
    file2_content.seek(0)

    now_ts = datetime.utcnow()
    today_str = now_ts.strftime("%Y%m%d_%H%M%S")

    output_zip = BytesIO()
    with ZipFile(output_zip, "a", ZIP_DEFLATED, compresslevel=9) as output_zip_obj:
        output_zip_obj.writestr(f"量測資料_{today_str}.csv", file1_content.getvalue())
    with ZipFile(output_zip, "a", ZIP_DEFLATED, compresslevel=9) as output_zip_obj:
        output_zip_obj.writestr(
            f"量測資料_utf8_{today_str}.csv",
            file1_utf8_content.getvalue(),
        )
    with ZipFile(output_zip, "a", ZIP_DEFLATED, compresslevel=9) as output_zip_obj:
        output_zip_obj.writestr(f"BCQ_{today_str}.csv", file2_content.getvalue())
    output_zip.seek(0)

    filename = f"量測資料_{today_str}.zip"

    return StreamingResponse(
        output_zip,
        media_type="application/x-zip-compressed",
        headers={
            "Access-Control-Expose-Headers": "Content-Disposition",
            "Content-Disposition": "inline; filename*=utf-8''{}".format(
                quote(filename),
            ),
            "Content-Type": "application/octet-stream",
        },
    )


@router.post("/export_report")
async def export_report(
    input_payload: ExportReportInputPayload,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    if input_payload.org_id != current_user.org_id:
        raise HTTPException(
            status_code=400,
            detail="The user doesn't have enough privileges",
        )

    for subject_id in input_payload.subject_ids:
        if not await crud.subject.get(db_session=db_session, id=subject_id):
            raise HTTPException(
                status_code=400,
                detail="The subject with this id does not exist in the system",
            )

    filename = "sample.pdf"
    headers = {
        "Content-Disposition": "inline; filename*=utf-8" '{}"'.format(quote(filename)),
        "Content-Type": "application/octet-stream",
        "X-Suggested-Filename": filename,
    }
    from io import BytesIO

    with open(filename, "rb") as file:
        data = BytesIO(file.read())
    data.seek(0)
    return StreamingResponse(data, media_type="application/pdf", headers=headers)


@router.put("/{subject_id}/activate")
async def activate_subject(
    subject_id: UUID,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    subject = await crud.subject.get(db_session=db_session, id=subject_id)
    if subject is None:
        raise HTTPException(
            status_code=400,
            detail="The subject with this id does not exist in the system",
        )
    await crud.subject.update(
        db_session=db_session,
        obj_current=subject,
        obj_new=schemas.SubjectUpdate(is_active=True),
    )

    return {"subject_id": subject_id}


@router.put("/{subject_id}/deactivate")
async def deactivate_subject(
    subject_id: UUID,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    subject = await crud.subject.get(db_session=db_session, id=subject_id)
    if subject is None:
        raise HTTPException(
            status_code=400,
            detail="The subject with this id does not exist in the system",
        )
    await crud.subject.update(
        db_session=db_session,
        obj_current=subject,
        obj_new=schemas.SubjectUpdate(is_active=False),
    )

    return {"subject_id": subject_id}


@router.delete(
    "/{subject_id}",
)
async def delete_subject(
    subject_id: UUID,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    if current_user.is_superuser is False:
        raise HTTPException(
            status_code=400,
            detail="The user doesn't have enough privileges",
        )
    subject = await crud.subject.get(db_session=db_session, id=subject_id)
    if subject is None:
        raise HTTPException(
            status_code=400,
            detail="The subject with this id does not exist in the system",
        )
    measures = await crud.measure_info.get_by_subject_id(
        db_session=db_session,
        subject_id=subject_id,
    )
    for measure in measures:
        # bcq = measure.bcq
        await crud.measure_info.remove(db_session=db_session, id=measure.id)

    await crud.subject.remove(db_session=db_session, id=subject_id)

    return {"subject_id": subject_id, "subject": subject, "measures": measures}


@router.post("/batch/activate", response_model=schemas.BatchResponse)
async def batch_activate_subjects(
    body: schemas.BatchRequestBody,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    result = {"success": [], "failure": []}
    for obj_id in body.ids:
        subject = await crud.subject.get(db_session=db_session, id=obj_id)
        if subject is None:
            result["failure"].append({"id": obj_id, "reason": "not found"})
        else:
            subject = await crud.subject.update(
                db_session=db_session,
                obj_current=subject,
                obj_new=schemas.SubjectUpdate(is_active=True),
            )
            result["success"].append({"id": obj_id})

    return result


@router.post("/batch/deactivate", response_model=schemas.BatchResponse)
async def batch_deactivate_subjects(
    body: schemas.BatchRequestBody,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    result = {"success": [], "failure": []}
    for obj_id in body.ids:
        subject = await crud.subject.get(db_session=db_session, id=obj_id)
        if subject is None:
            result["failure"].append({"id": obj_id, "reason": "not found"})
        else:
            subject = await crud.subject.update(
                db_session=db_session,
                obj_current=subject,
                obj_new=schemas.SubjectUpdate(is_active=False),
            )
            result["success"].append({"id": obj_id})

    return result
