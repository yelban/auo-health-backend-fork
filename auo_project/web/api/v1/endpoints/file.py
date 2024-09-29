from datetime import timedelta
from typing import Any, List, Optional, Sequence

import pydash as py_
from fastapi import APIRouter, HTTPException, Query
from fastapi.param_functions import Depends
from sqlalchemy.orm import joinedload
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud, models, schemas
from auo_project.core.constants import FileStatusType, UploadStatusType
from auo_project.core.pagination import Pagination
from auo_project.core.utils import get_filters, safe_parse_dt
from auo_project.web.api import deps

router = APIRouter()


@router.get("/", response_model=schemas.FileListPage)
async def get_files(
    filename: Optional[str] = Query(None, regex="contains__", title="檔案名稱"),
    owner_name: Optional[str] = Query(None, regex="contains__", title="上傳者"),
    created_at: Optional[List[str]] = Query(
        [],
        regex="(ge|le)__",
        title="上傳時間",
        alias="created_at[]",
    ),
    is_valid: Optional[List[bool]] = Query(
        [],
        title="檔案驗證是否成功。",
        alias="is_valid[]",
    ),
    sort_expr: Optional[str] = Query(
        "-created_at",
        title="created_at 代表由小到大排。-created_at 代表由大到小排。",
    ),
    pagination: Pagination = Depends(),
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Get file list.
    """
    sort_expr = sort_expr.split(",") if sort_expr else ["-created_at"]
    sort_expr = [e.replace("+", "") for e in sort_expr]
    order_expr = models.File.order_expr(*sort_expr)

    auth_filter_expr = []
    group_names = [group.name for group in current_user.groups]
    if "admin" in group_names:
        auth_filter_expr = []
    elif "manager" in group_names:
        auth_filter_expr.append(models.User.org_id == current_user.org_id)
    elif "user" in group_names or "subject" in group_names:
        auth_filter_expr.append(models.User.id == current_user.id)

    created_at_start_str = py_.head(
        list(filter(lambda x: x.startswith("ge"), created_at)),
    )
    created_at_end_str = py_.head(
        list(filter(lambda x: x.startswith("le"), created_at)),
    )
    created_at_start_utc8 = (
        safe_parse_dt(created_at_start_str.replace("ge__", ""))
        if created_at_start_str
        else None
    )
    created_at_end_utc8 = (
        safe_parse_dt(created_at_end_str.replace("le__", ""))
        if created_at_end_str
        else None
    )
    created_at_start_utc0 = (
        created_at_start_utc8 - timedelta(hours=8) if created_at_start_utc8 else None
    )
    created_at_end_utc0 = (
        created_at_end_utc8 - timedelta(hours=8) if created_at_end_utc8 else None
    )

    file_filters = {
        "is_dup": False,
        "name__contains": filename.replace("contains__", "") if filename else None,
        "created_at__ge": created_at_start_utc0,
        "created_at__le": created_at_end_utc0,
        "is_valid__in": is_valid,
        "file_status__in": [FileStatusType.success.value, FileStatusType.failed.value],
    }
    owner_filters = {
        "full_name__contains": (
            owner_name.replace("contains__", "") if owner_name else None
        ),
    }

    file_filter_expr = models.File.filter_expr(**get_filters(file_filters))
    user_filter_expr = models.User.filter_expr(**get_filters(owner_filters))
    expressions = [
        *file_filter_expr,
        *user_filter_expr,
        *auth_filter_expr,
    ]

    query = (
        select(models.File)
        .join(models.Upload)
        .join(models.User)
        .options(joinedload(models.File.owner))
        .where(*expressions)
        .distinct()
    )
    items: Sequence[schemas.FileRead] = await crud.file.get_multi(
        db_session=db_session,
        query=query,
        order_expr=order_expr,
        unique=False,
        skip=(pagination.page - 1) * pagination.per_page,
        limit=pagination.per_page,
    )
    resp = await db_session.execute(select(func.count()).select_from(query.subquery()))
    total_count = resp.scalar_one()
    result = await pagination.paginate2(total_count, items)
    return result


@router.get("/{file_id}")
async def get_upload_file(
    file_id: str,
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Get upload file.
    """
    file = await crud.file.get(db_session=db_session, id=file_id)
    if not file:
        raise HTTPException(status_code=404, detail=f"Not found file id: {file_id}")

    return file


@router.post("/cancel-upload/{file_id}")
async def cancel_upload_file(
    file_id: str,
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Cancel upload file.
    """
    file = await crud.file.get(db_session=db_session, id=file_id)
    if not file:
        raise HTTPException(status_code=404, detail=f"Not found file id: {file_id}")
    file.file_status = FileStatusType.canceled.value
    db_session.add(file)
    await db_session.commit()

    if await crud.upload.is_files_all_complete(
        db_session=db_session,
        upload_id=file.upload_id,
    ):
        file.upload.upload_status = UploadStatusType.success.value
        db_session.add(file.upload)
        await db_session.commit()

    return file_id


@router.post("/resume-upload/{file_id}")
async def resume_upload_file(
    file_id: str,
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Cancel upload file.
    """
    file = await crud.file.get(db_session=db_session, id=file_id)
    if not file:
        raise HTTPException(status_code=404, detail=f"Not found file id: {file_id}")

    if await crud.upload.is_files_all_complete(
        db_session=db_session,
        upload_id=file.upload_id,
    ):
        file.upload.upload_status = UploadStatusType.uploading.value
        db_session.add(file.upload)
        await db_session.commit()

    file.file_status = FileStatusType.uploading.value
    db_session.add(file)
    await db_session.commit()

    return file_id
