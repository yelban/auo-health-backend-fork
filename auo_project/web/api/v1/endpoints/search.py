from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Query
from fastapi.param_functions import Depends
from fastapi.encoders import jsonable_encoder
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy import func


from auo_project import crud, models
from auo_project.web.api import deps
from auo_project.core.utils import get_filters

router = APIRouter()


@router.get("/subject_id")
async def search_subject_id(
    keyword: Optional[str] = Query(None, title="搜尋關鍵字"),
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Search by sid
    """
    if keyword is None or keyword == "":
        return []
    subject_sids = await crud.subject.get_sid_by_keyword(
        db_session=db_session,
        org_id=current_user.org_id,
        keyword=keyword,
        user=current_user,
    )
    return subject_sids


@router.get("/consult_dr")
async def search_dr(
    keyword: str = Query(None, title="搜尋關鍵字"),
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Search by consult_dr
    """
    if keyword is None or keyword == "":
        doctors = await crud.doctor.get_all_by_org_id(
            db_session=db_session,
            org_id=current_user.org_id,
        )
        return crud.doctor.format_options(doctors=doctors, add_all=True)
    doctors = await crud.doctor.get_list_by_name(
        db_session=db_session,
        org_id=current_user.org_id,
        name=keyword,
    )
    return crud.doctor.format_options(doctors=doctors, add_all=False)


@router.get("/subject", response_model=list[models.Subject])
async def search_subject(
    keyword: str = Query(..., title="搜尋關鍵字"),
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Search subject by keyword using colunms: sid, name, number
    When keyword length is 8 and start with 8 number, it will convert the number to yyyymmdd and search subjects measured at the date.
    """
    # print(len(keyword), keyword[0] == "D", all(
    #     map(lambda x: isinstance(x, str) and x.isdigit(), keyword[1:])
    # ))
    # 搜尋身分證字號、護照號碼、病歷編號、姓名
    if len(keyword) == 8 and all(
        map(lambda x: isinstance(x, str) and x.isdigit(), keyword),
    ):
        try:
            measure_date = datetime.strptime(keyword, "%Y%m%d")
            start_date = measure_date
            end_date = measure_date + timedelta(hours=24) + timedelta(microseconds=-1)
            measure_filters = get_filters(
                {
                    "is_active": True,
                    "org_id": current_user.org_id,
                    "measure_time__ge": start_date,
                    "measure_time__le": end_date,
                    "branch_id__in": crud.user.get_branches_list(user=current_user),
                },
            )
            measure_expressions = models.MeasureInfo.filter_expr(**measure_filters)
            subquery = (
                select(models.Subject.id, func.max(models.MeasureInfo.measure_time).label("measure_time"))
                .join(models.MeasureInfo)
                .where(*measure_expressions)
                .group_by(models.Subject.id)
                .subquery()
            )
            query = (
                select(models.Subject, subquery.c.measure_time)
                .join(subquery, models.Subject.id == subquery.c.id)
                .order_by(subquery.c.measure_time.asc())
            )
            response = await db_session.execute(query)
            subjects = response.all()
            # update last_measure_time as keyword
            subjects = [
                {**jsonable_encoder(subject), "last_measure_time": measure_time}
                for subject, measure_time in subjects
            ]
            if subjects:
                return subjects
        except Exception as e:
            print(f"error: {e}")

    subjects = await crud.subject.get_all_by_keyword(
        db_session=db_session,
        org_id=current_user.org_id,
        keyword=keyword,
        user=current_user,
    )
    return subjects
