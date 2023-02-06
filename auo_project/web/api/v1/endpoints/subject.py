from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from fastapi.param_functions import Depends
from pydantic import BaseModel
from sqlalchemy.orm import lazyload, selectinload
from sqlmodel import extract, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud, models, schemas
from auo_project.core.constants import MEASURE_TIMES
from auo_project.core.dateutils import DateUtils
from auo_project.core.pagination import Pagination
from auo_project.core.utils import get_filters
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
    items: List[schemas.SubjectSecretRead]


class SubjectListResponse(BaseModel):
    subject: SubjectPage
    measure_times: List[Dict[str, Any]]


@router.get("/", response_model=SubjectListResponse)
async def get_subject(
    name: Optional[str] = Query(None, regex="contains__", title="姓名"),
    sid: Optional[str] = Query(None, regex="contains__", title="ID"),
    birth_date: Optional[List[str]] = Query(None, regex="(ge|le)__", title="出生年月日"),
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
    pagniation: Pagination = Depends(),
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    start_date, end_date = dateutils.get_dates()

    filters = {
        "name__contains": name,
        "sid__contains": sid,
        "birth_date__ge": birth_date[0] if birth_date else None,
        "birth_date__le": birth_date[1] if birth_date else None,
    }
    filters = dict([(k, v) for k, v in filters.items() if v])
    sort_expr = sort_expr.split(",") if sort_expr else ["-updated_at"]
    sort_expr = [e.replace("+", "") for e in sort_expr]
    order_expr = models.Subject.order_expr(*sort_expr)

    time_filters = get_filters(
        {
            "measure_time__ge": start_date,
            "measure_time__le": end_date,
        },
    )
    time_expressions = models.MeasureInfo.filter_expr(**time_filters)
    if specific_months:
        time_expressions.append(
            extract("month", models.MeasureInfo.measure_time).in_(specific_months),
        )
    subquery = (
        select(models.Subject)
        .join(MeasureInfo)
        .where(*time_expressions)
        .distinct()
        .subquery()
    )

    query = (
        select(models.Subject)
        .join(subquery, models.Subject.id == subquery.c.id)
        .where(*models.Subject.filter_expr(**filters))
        .options(
            lazyload(models.Subject.measure_infos),
            selectinload(models.Subject.standard_measure_info),
        )
    )

    items = await crud.subject.get_multi(
        db_session=db_session,
        query=query,
        order_expr=order_expr,
        skip=(pagniation.page - 1) * pagniation.per_page,
        limit=pagniation.per_page,
    )
    resp = await db_session.execute(select(func.count()).select_from(query.subquery()))
    total_count = resp.scalar_one()

    return SubjectListResponse(
        subject=await pagniation.paginate2(total_count, items),
        measure_times=MEASURE_TIMES,
    )


@router.get("/{subject_id}/measures", response_model=schemas.SubjectReadWithMeasures)
async def get_subject_measures(
    subject_id: UUID,
    specific_months: Optional[List[int]] = Query(
        [],
        alias="specific_months[]",
        title="指定月份",
    ),
    org_name: Optional[List[str]] = Query(
        [],
        title="檢測單位",
    ),
    measure_operator: Optional[List[str]] = Query([], title="檢測人員"),
    irregular_hr: Optional[List[bool]] = Query(
        None,
        title="節律標記",
        alias="irregular_hr[]",
    ),
    proj_num: Optional[str] = Query(None, title="計畫編號"),
    has_memos: Optional[str] = Query(None, title="檢測標記"),
    not_include_low_pass_rates: Optional[List[bool]] = Query(None, title="排除通過率低項目"),
    sort_expr: Optional[str] = Query(
        "-measure_time",
        title="measure_time 代表由小到大排。-measure_time 代表由大到小排。",
    ),
    dateutils: DateUtils = Depends(),
    pagniation: Pagination = Depends(),
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

    # TODO: make frontend remove +
    sort_expr = sort_expr.split(",") if sort_expr else ["-updated_at"]
    order_expr = models.MeasureInfo.order_expr(*[e.replace("+", "") for e in sort_expr])
    # TODO: implement
    # TODO: add division constraint
    has_memos = (
        [True if e == "true" else False for e in has_memos.split(",")]
        if has_memos
        else []
    )
    start_date, end_date = dateutils.get_dates()

    # TODO: check
    irregular_hr = (
        [1 if e == False else 0 for e in irregular_hr] if irregular_hr else []
    )
    # TODO: check not_include_low_pass_rates
    expressions = []
    filters = get_filters(
        {
            "subject_id": subject_id,
            "org_id": current_user.org_id,
            "measure_time__ge": start_date,
            "measure_time__le": end_date,
            # "org___name__in": org_name, # TODO: KeyError: 'Expression `org___name__in` has incorrect attribute `org___name`'
            "measure_operator__in": measure_operator,
            "irregular_hr__in": irregular_hr,
            "proj_num": proj_num,
            "has_memos__in": has_memos,
            "not_include_low_pass_rates__not_in": not_include_low_pass_rates,
        },
    )
    # print("filters", filters)
    # filters = dict([(k, v) for k, v in filters.items() if v is not None and v != []])
    # print("filters", filters)
    expressions = models.MeasureInfo.filter_expr(**filters)
    if specific_months:
        expressions.append(
            extract("month", models.MeasureInfo.measure_time).in_(specific_months),
        )
    query = select(MeasureInfo).join(Org).where(*expressions).distinct()
    measures = await crud.measure_info.get_multi(
        db_session=db_session,
        query=query,
        order_expr=order_expr,
        relations=["org"],
        unique=False,
        skip=(pagniation.page - 1) * pagniation.per_page,
        limit=pagniation.per_page,
    )

    measures = [
        schemas.MeasureInfoReadByList(
            **measure.dict(),
            org_name=measure.org.name,
            is_standard_measure=(subject.standard_measure_id == measure.id),
        )
        for measure in measures
    ]

    resp = await db_session.execute(select(func.count()).select_from(query.subquery()))
    total_count = resp.scalar_one()
    page_result = await pagniation.paginate2(total_count, measures)

    # TODO: user, division mapping
    org_names = [
        {"value": "center1", "key": "某某醫學中心"},
        {"value": "center2", "key": "某Ｂ醫學中心"},
    ]
    org_names = [{"value": current_user.org.id, "key": current_user.org.name}]
    # print("org", current_user.org)

    measure_operators = [
        {"value": "operator_id_1", "key": "某某Ａ"},
        {"value": "operator_id_2", "key": "某某B"},
    ]
    measure_operators_query = select(
        func.distinct(MeasureInfo.measure_operator),
    ).select_from(query.subquery())
    measure_operators_result = await db_session.execute(measure_operators_query)
    measure_operators = [
        {"value": operator[0], "key": operator[0]}
        for operator in measure_operators_result.fetchall()
        if operator[0]
    ]

    proj_nums = [
        {"value": "0000000001", "key": "0000000001"},
        {"value": "0000000002", "key": "0000000002"},
        {"value": "0000000003", "key": "0000000003"},
    ]
    proj_nums_query = select(func.distinct(MeasureInfo.proj_num)).select_from(
        query.subquery(),
    )
    proj_nums_result = await db_session.execute(proj_nums_query)
    proj_nums = [
        {"value": proj_num[0], "key": proj_num[0]}
        for proj_num in proj_nums_result.fetchall()
        if proj_num[0]
    ]

    return schemas.SubjectReadWithMeasures(
        subject=subject,
        measure=page_result,
        measure_times=MEASURE_TIMES,
        org_names=org_names,
        measure_operators=measure_operators,
        irregular_hrs=[{"value": True, "key": "規律"}, {"value": False, "key": "不規律"}],
        proj_nums=proj_nums,
        has_memos=[{"value": True, "key": "有"}, {"value": False, "key": "無"}],
        not_include_low_pass_rates=[
            {"value": True, "key": "是"},
            {"value": False, "key": "否"},
        ],
    )


@router.patch("/{subject_id}/memo", response_model=schemas.SubjectRead)
async def update_subject_memo(
    subject_id: UUID,
    memo: str,
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
    if len(memo) > 1024:
        raise HTTPException(status_code=422, detail=f"memo max length is 1024")
    subject.memo = memo
    db_session.add(subject)
    await db_session.commit()
    await db_session.refresh(subject)
    return subject


@router.patch(
    "/{subject_id}/measure/{measure_id}/standard_value",
    response_model=schemas.SubjectRead,
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
