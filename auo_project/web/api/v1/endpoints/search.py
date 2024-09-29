from typing import Any, Optional

from fastapi import APIRouter, Query
from fastapi.param_functions import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud, models
from auo_project.web.api import deps

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


@router.get("/subject")
async def search_subject(
    keyword: str = Query(..., title="搜尋關鍵字"),
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Search subject by keyword using colunms: sid, name, number
    """
    # 搜尋身分證字號、護照號碼、病歷編號、姓名
    subjects = await crud.subject.get_all_by_keyword(
        db_session=db_session,
        org_id=current_user.org_id,
        keyword=keyword,
    )
    return subjects
