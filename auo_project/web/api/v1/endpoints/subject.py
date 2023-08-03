from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

import pydash as py_
from fastapi import APIRouter, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Depends
from pydantic import BaseModel
from sqlalchemy.orm import selectinload
from sqlmodel import String, cast, extract, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud, models, schemas
from auo_project.core.constants import MEASURE_TIMES, SexType
from auo_project.core.dateutils import DateUtils
from auo_project.core.pagination import Pagination
from auo_project.core.utils import (
    get_filters,
    get_hr_type,
    get_pct_cmp_base,
    get_pct_cmp_overall_and_standard,
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
    items: List[schemas.SubjectSecretRead]


class SubjectListResponse(BaseModel):
    subject: SubjectPage
    measure_times: List[Dict[str, Any]]


class MultiMeasuresBody(BaseModel):
    measure_ids: List[UUID]


@router.get("/", response_model=SubjectListResponse)
async def get_subject(
    number: Optional[str] = Query(None, regex="contains__", title="受測者編號"),
    sid: Optional[str] = Query(None, regex="contains__", title="ID"),
    name: Optional[str] = Query(None, regex="contains__", title="姓名"),
    sex: Optional[SexType] = Query(None, title="性別：男=0, 女=1）"),
    memo: Optional[str] = Query(None, regex="contains__", title="受測者標記"),
    birth_date: Optional[str] = Query(None, regex="[0-9\-]+", title="出生年月日"),
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
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    start_date, end_date = dateutils.get_dates()
    if birth_date:
        try:
            birth_date = datetime.strptime(birth_date.replace("-", ""), "%Y%m%d")
        except Exception:
            raise HTTPException(status_code=400, detail="date format error")

    filters = {
        "name__contains": name.replace("contains__", "") if name else None,
        "sid__contains": sid.replace("contains__", "") if sid else None,
        "birth_date": birth_date,
        "sex": sex,
        "memo__contains": memo.replace("contains__", "") if memo else None,
    }
    filters = dict([(k, v) for k, v in filters.items() if v is not None and v != []])
    filter_expr = models.Subject.filter_expr(**filters)
    if number:
        filter_expr.append(
            cast(models.Subject.number, String).ilike(
                f'%{number.replace("contains__", "")}%',
            ),
        )
    sort_expr = sort_expr.split(",") if sort_expr else ["-last_measure_time"]
    sort_expr = [e.replace("+", "") for e in sort_expr]
    order_expr = models.Subject.order_expr(*sort_expr)

    time_filters = get_filters(
        {
            "measure_time__ge": start_date,
            "measure_time__le": end_date,
        },
    )
    org_fileters = get_filters(
        {
            "org_id": current_user.org_id,
        },
    )
    org_expressions = models.MeasureInfo.filter_expr(**org_fileters)
    time_expressions = models.MeasureInfo.filter_expr(**time_filters)
    if specific_months:
        time_expressions.append(
            extract("month", models.MeasureInfo.measure_time).in_(specific_months),
        )
    subquery = (
        select(models.Subject)
        .join(MeasureInfo)
        .where(*time_expressions, *org_expressions)
        .distinct()
        .subquery()
    )

    query = (
        select(models.Subject)
        .join(subquery, models.Subject.id == subquery.c.id)
        .where(*filter_expr)
        .options(
            selectinload(models.Subject.standard_measure_info),
        )
    )

    items = await crud.subject.get_multi(
        db_session=db_session,
        query=query,
        order_expr=order_expr,
        skip=(pagination.page - 1) * pagination.per_page,
        limit=pagination.per_page,
    )
    resp = await db_session.execute(select(func.count()).select_from(query.subquery()))
    total_count = resp.scalar_one()

    return SubjectListResponse(
        subject=await pagination.paginate2(total_count, items),
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
    org_id: Optional[List[str]] = Query(
        [],
        title="檢測單位",
    ),
    measure_operator: Optional[List[str]] = Query(
        [],
        title="檢測人員",
        alias="measure_operator[]",
    ),
    consult_dr: Optional[List[str]] = Query(
        [],
        title="諮詢醫師",
        alias="consult_dr[]",
    ),  # judge_dr
    irregular_hr: Optional[List[bool]] = Query(
        [],
        title="節律標記",
        alias="irregular_hr[]",
    ),
    proj_num: Optional[str] = Query(None, title="計畫編號"),
    has_memos: Optional[str] = Query(None, title="檢測標記"),
    has_bcqs: Optional[str] = Query(None, title="BCQ 檢測"),
    age: Optional[List[str]] = Query([], regex="(ge|le)__", title="年齡", alias="age[]"),
    bmi: Optional[List[str]] = Query([], regex="(ge|le)__", title="BMI", alias="bmi[]"),
    not_include_low_pass_rates: Optional[List[bool]] = Query(
        [],
        title="排除通過率低項目",
        alias="not_include_low_pass_rates[]",
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
    has_memos = (
        [True if e == "true" else False for e in has_memos.split(",")]
        if has_memos
        else []
    )
    has_bcqs = (
        [True if e == "true" else False for e in has_bcqs.split(",")]
        if has_bcqs
        else []
    )
    start_date, end_date = dateutils.get_dates()
    age_start = py_.head(list(filter(lambda x: x.startswith("ge"), age)))
    age_end = py_.head(list(filter(lambda x: x.startswith("le"), age)))
    bmi_start = py_.head(list(filter(lambda x: x.startswith("ge"), bmi)))
    bmi_end = py_.head(list(filter(lambda x: x.startswith("le"), bmi)))
    irregular_hr = (
        [0 if e == False else 1 for e in irregular_hr] if irregular_hr else []
    )
    has_low_pass_rate = [not x for x in not_include_low_pass_rates]
    expressions = []
    filters = get_filters(
        {
            "subject_id": subject_id,
            "measure_time__ge": start_date,
            "measure_time__le": end_date,
            "age__ge": age_start and int(age_start.replace("ge__", "")),
            "age__le": age_end and int(age_end.replace("le__", "")),
            "bmi__ge": bmi_start and int(bmi_start.replace("ge__", "")),
            "bmi__le": bmi_end and int(bmi_end.replace("le__", "")),
            # TODO: filter org_id by user permission
            "org_id__in": org_id,
            "measure_operator__in": measure_operator,
            "judge_dr__in": consult_dr,
            "irregular_hr__in": irregular_hr,
            "proj_num": proj_num,
            "has_memo__in": has_memos,
            "has_bcq__in": has_bcqs,
            "has_low_pass_rate__in": has_low_pass_rate,
            "org_id": current_user.org_id,
        },
    )
    print("filters", filters)
    expressions = models.MeasureInfo.filter_expr(**filters)
    org_expressions = []
    print("expressions", expressions)
    if specific_months:
        expressions.append(
            extract("month", models.MeasureInfo.measure_time).in_(specific_months),
        )
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
            bcq=measure.has_bcq,
            is_standard_measure=(subject.standard_measure_id == measure.id),
        )
        for measure in measures
    ]

    resp = await db_session.execute(select(func.count()).select_from(query.subquery()))
    total_count = resp.scalar_one()
    page_result = await pagination.paginate2(total_count, measures)

    # TODO: user, division mapping
    org_names = [{"value": current_user.org.id, "key": current_user.org.name}]

    measure_operators_query = select(
        func.distinct(MeasureInfo.measure_operator),
    ).select_from(base_query.subquery())
    measure_operators_result = await db_session.execute(measure_operators_query)
    measure_operators = [
        {"value": operator[0], "key": operator[0]}
        for operator in measure_operators_result.fetchall()
        if operator[0]
    ]

    consult_dr_query = select(func.distinct(MeasureInfo.judge_dr)).select_from(
        base_query.subquery(),
    )
    consult_drs_result = await db_session.execute(consult_dr_query)
    consult_drs = [
        {"value": consult_dr[0], "key": consult_dr[0]}
        for consult_dr in consult_drs_result.fetchall()
        if consult_dr[0]
    ]

    proj_nums_query = select(func.distinct(MeasureInfo.proj_num)).select_from(
        base_query.subquery(),
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
        consult_drs=consult_drs,
        irregular_hrs=[{"value": False, "key": "規律"}, {"value": True, "key": "不規律"}],
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
    # TODO: check all measure ids are valid: owned by the subject
    measures_infos = await crud.measure_info.get_by_ids(
        db_session=db_session,
        list_ids=measure_ids,
        relations=["bcq"],
    )

    measures_infos = py_.sort(
        measures_infos,
        key=lambda item: item.measure_time,
        reverse=True,
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
            hr_l_type=get_hr_type(measure.hr_l),
            hr_r=measure.hr_r,
            hr_r_type=get_hr_type(measure.hr_r),
            mean_prop_range_max_l_cu=measure.mean_prop_range_max_l_cu,
            mean_prop_range_max_l_qu=measure.mean_prop_range_max_l_qu,
            mean_prop_range_max_l_ch=measure.mean_prop_range_max_l_ch,
            mean_prop_range_max_r_cu=measure.mean_prop_range_max_r_cu,
            mean_prop_range_max_r_qu=measure.mean_prop_range_max_r_qu,
            mean_prop_range_max_r_ch=measure.mean_prop_range_max_r_ch,
            max_amp_depth_of_range_l_cu=measure.max_amp_depth_of_range_l_cu,
            max_amp_depth_of_range_l_qu=measure.max_amp_depth_of_range_l_qu,
            max_amp_depth_of_range_l_ch=measure.max_amp_depth_of_range_l_ch,
            max_amp_depth_of_range_r_cu=measure.max_amp_depth_of_range_r_cu,
            max_amp_depth_of_range_r_qu=measure.max_amp_depth_of_range_r_qu,
            max_amp_depth_of_range_r_ch=measure.max_amp_depth_of_range_r_ch,
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
            h1_l_cu=mean_statistic_model_dict[measure.id].h1_l_cu,
            h1_l_qu=mean_statistic_model_dict[measure.id].h1_l_qu,
            h1_l_ch=mean_statistic_model_dict[measure.id].h1_l_ch,
            h1_r_cu=mean_statistic_model_dict[measure.id].h1_r_cu,
            h1_r_qu=mean_statistic_model_dict[measure.id].h1_r_qu,
            h1_r_ch=mean_statistic_model_dict[measure.id].h1_r_ch,
            h1_div_t1_l_cu=safe_divide(
                mean_statistic_model_dict[measure.id].h1_div_t1_l_cu,
                1000,
            ),
            h1_div_t1_l_qu=safe_divide(
                mean_statistic_model_dict[measure.id].h1_div_t1_l_qu,
                1000,
            ),
            h1_div_t1_l_ch=safe_divide(
                mean_statistic_model_dict[measure.id].h1_div_t1_l_ch,
                1000,
            ),
            h1_div_t1_r_cu=safe_divide(
                mean_statistic_model_dict[measure.id].h1_div_t1_r_cu,
                1000,
            ),
            h1_div_t1_r_qu=safe_divide(
                mean_statistic_model_dict[measure.id].h1_div_t1_r_qu,
                1000,
            ),
            h1_div_t1_r_ch=safe_divide(
                mean_statistic_model_dict[measure.id].h1_div_t1_r_ch,
                1000,
            ),
            pr_l_cu=mean_statistic_model_dict[measure.id].pr_l_cu,
            pr_l_qu=mean_statistic_model_dict[measure.id].pr_l_qu,
            pr_l_ch=mean_statistic_model_dict[measure.id].pr_l_ch,
            pr_r_cu=mean_statistic_model_dict[measure.id].pr_r_cu,
            pr_r_qu=mean_statistic_model_dict[measure.id].pr_r_qu,
            pr_r_ch=mean_statistic_model_dict[measure.id].pr_r_ch,
            w1_l_cu=mean_statistic_model_dict[measure.id].w1_l_cu,
            w1_l_qu=mean_statistic_model_dict[measure.id].w1_l_qu,
            w1_l_ch=mean_statistic_model_dict[measure.id].w1_l_ch,
            w1_r_cu=mean_statistic_model_dict[measure.id].w1_r_cu,
            w1_r_qu=mean_statistic_model_dict[measure.id].w1_r_qu,
            w1_r_ch=mean_statistic_model_dict[measure.id].w1_r_ch,
            w1_div_t_l_cu=mean_statistic_model_dict[measure.id].w1_div_t_l_cu,
            w1_div_t_l_qu=mean_statistic_model_dict[measure.id].w1_div_t_l_qu,
            w1_div_t_l_ch=mean_statistic_model_dict[measure.id].w1_div_t_l_ch,
            w1_div_t_r_cu=mean_statistic_model_dict[measure.id].w1_div_t_r_cu,
            w1_div_t_r_qu=mean_statistic_model_dict[measure.id].w1_div_t_r_qu,
            w1_div_t_r_ch=mean_statistic_model_dict[measure.id].w1_div_t_r_ch,
            t1_div_t_l_cu=mean_statistic_model_dict[measure.id].t1_div_t_l_cu,
            t1_div_t_l_qu=mean_statistic_model_dict[measure.id].t1_div_t_l_qu,
            t1_div_t_l_ch=mean_statistic_model_dict[measure.id].t1_div_t_l_ch,
            t1_div_t_r_cu=mean_statistic_model_dict[measure.id].t1_div_t_r_cu,
            t1_div_t_r_qu=mean_statistic_model_dict[measure.id].t1_div_t_r_qu,
            t1_div_t_r_ch=mean_statistic_model_dict[measure.id].t1_div_t_r_ch,
            pw_l_cu=mean_statistic_model_dict[measure.id].pw_l_cu,
            pw_l_qu=mean_statistic_model_dict[measure.id].pw_l_qu,
            pw_l_ch=mean_statistic_model_dict[measure.id].pw_l_ch,
            pw_r_cu=mean_statistic_model_dict[measure.id].pw_r_cu,
            pw_r_qu=mean_statistic_model_dict[measure.id].pw_r_qu,
            pw_r_ch=mean_statistic_model_dict[measure.id].pw_r_ch,
            pwcv_l_cu=cv_statistic_model_dict[measure.id].pw_l_cu,
            pwcv_l_qu=cv_statistic_model_dict[measure.id].pw_l_qu,
            pwcv_l_ch=cv_statistic_model_dict[measure.id].pw_l_ch,
            pwcv_r_cu=cv_statistic_model_dict[measure.id].pw_r_cu,
            pwcv_r_qu=cv_statistic_model_dict[measure.id].pw_r_qu,
            pwcv_r_ch=cv_statistic_model_dict[measure.id].pw_r_ch,
            a0_l_cu=mean_statistic_model_dict[measure.id].a0_l_cu,
            a0_l_qu=mean_statistic_model_dict[measure.id].a0_l_qu,
            a0_l_ch=mean_statistic_model_dict[measure.id].a0_l_ch,
            a0_r_cu=mean_statistic_model_dict[measure.id].a0_r_cu,
            a0_r_qu=mean_statistic_model_dict[measure.id].a0_r_qu,
            a0_r_ch=mean_statistic_model_dict[measure.id].a0_r_ch,
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
                score_yang_head=measure.bcq.percentage_yang_head
                if measure.bcq
                else None,
                score_yang_chest=measure.bcq.percentage_yang_chest
                if measure.bcq
                else None,
                score_yang_limbs=measure.bcq.percentage_yang_limbs
                if measure.bcq
                else None,
                score_yang_abdomen=measure.bcq.percentage_yang_abdomen
                if measure.bcq
                else None,
                score_yang_surface=measure.bcq.percentage_yang_surface
                if measure.bcq
                else None,
                score_yin_head=measure.bcq.percentage_yin_head if measure.bcq else None,
                score_yin_limbs=measure.bcq.percentage_yin_limbs
                if measure.bcq
                else None,
                score_yin_gt=measure.bcq.percentage_yin_gt if measure.bcq else None,
                score_yin_surface=measure.bcq.percentage_yin_surface
                if measure.bcq
                else None,
                score_yin_abdomen=measure.bcq.percentage_yin_abdomen
                if measure.bcq
                else None,
                score_phlegm_trunk=measure.bcq.percentage_phlegm_trunk
                if measure.bcq
                else None,
                score_phlegm_surface=measure.bcq.percentage_phlegm_surface
                if measure.bcq
                else None,
                score_phlegm_head=measure.bcq.percentage_phlegm_head
                if measure.bcq
                else None,
                score_phlegm_gt=measure.bcq.percentage_phlegm_gt
                if measure.bcq
                else None,
                percentage_yang=measure.bcq.percentage_yang if measure.bcq else None,
                percentage_yin=measure.bcq.percentage_yin if measure.bcq else None,
                percentage_phlegm=measure.bcq.percentage_phlegm
                if measure.bcq
                else None,
                percentage_yang_head=measure.bcq.percentage_yang_head
                if measure.bcq
                else None,
                percentage_yang_chest=measure.bcq.percentage_yang_chest
                if measure.bcq
                else None,
                percentage_yang_limbs=measure.bcq.percentage_yang_limbs
                if measure.bcq
                else None,
                percentage_yang_abdomen=measure.bcq.percentage_yang_abdomen
                if measure.bcq
                else None,
                percentage_yang_surface=measure.bcq.percentage_yang_surface
                if measure.bcq
                else None,
                percentage_yin_head=measure.bcq.percentage_yin_head
                if measure.bcq
                else None,
                percentage_yin_limbs=measure.bcq.percentage_yin_limbs
                if measure.bcq
                else None,
                percentage_yin_gt=measure.bcq.percentage_yin_gt
                if measure.bcq
                else None,
                percentage_yin_surface=measure.bcq.percentage_yin_surface
                if measure.bcq
                else None,
                percentage_yin_abdomen=measure.bcq.percentage_yin_abdomen
                if measure.bcq
                else None,
                percentage_phlegm_trunk=measure.bcq.percentage_phlegm_trunk
                if measure.bcq
                else None,
                percentage_phlegm_surface=measure.bcq.percentage_phlegm_surface
                if measure.bcq
                else None,
                percentage_phlegm_head=measure.bcq.percentage_phlegm_head
                if measure.bcq
                else None,
                percentage_phlegm_gt=measure.bcq.percentage_phlegm_gt
                if measure.bcq
                else None,
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
        subject=schemas.SubjectRead(
            **jsonable_encoder(subject),
            standard_measure_info=standard_measure_info,
        ),
        measures=measures,
        normal_spec=normal_spec,
    )
