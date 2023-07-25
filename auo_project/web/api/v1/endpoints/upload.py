from datetime import datetime
from typing import Any, List, Optional, Sequence
from uuid import UUID

import sqlalchemy as sa
from fastapi import APIRouter, HTTPException, Query
from fastapi.param_functions import Depends
from pydantic import BaseModel
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import cast
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud, models, schemas
from auo_project.core.config import settings
from auo_project.core.constants import FileStatusType, UploadStatusType
from auo_project.core.pagination import Pagination
from auo_project.core.utils import safe_int, safe_parse_dt
from auo_project.models import File, Upload, User
from auo_project.web.api import deps

router = APIRouter()


@router.post("/", response_model=schemas.UploadReadWithEndpoint)
async def create_upload(
    *,
    body: schemas.UploadCreateReqBody,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Create new upload.
    """
    filename_list = body.filename_list
    if len(filename_list) > settings.MAX_SIZE_PER_UPLOAD:
        raise HTTPException(
            status_code=400,
            detail=f"Max size per upload is {settings.MAX_SIZE_PER_UPLOAD}",
        )

    for filename in filename_list:
        if ".zip" not in filename:
            raise HTTPException(status_code=400, detail=f"Invalid filename {filename}")

    all_files = await crud.file.get_all_by_owner_id(
        db_session=db_session,
        owner_id=current_user.id,
    )
    owned_file_list = [
        schemas.FileRead.parse_obj({**file.dict(), "is_dup": True})
        for file in all_files
        if file.file_status
        in (FileStatusType.uploading, FileStatusType.success, FileStatusType.failed)
    ]
    owned_filename_list = [file.name for file in owned_file_list]
    matched_filename_set = set(owned_filename_list) & set(filename_list)

    upload_in = schemas.UploadCreate(
        owner_id=current_user.id,
        upload_status=UploadStatusType.uploading.value,
        file_number=len(filename_list) - len(matched_filename_set),
    )
    upload = await crud.upload.create(db_session=db_session, obj_in=upload_in)
    files_in = [
        schemas.FileCreate(
            name=filename,
            owner_id=current_user.id,
            upload_id=upload.id,
            is_dup=filename in matched_filename_set,
        )
        for filename in filename_list
    ]

    upload = await crud.upload.add_files_to_upload(
        db_session=db_session,
        files=files_in,
        upload_id=upload.id,
    )

    return upload


@router.get("/{upload_id}", response_model=schemas.UploadRead)
async def get_upload(
    upload_id: UUID,
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Get upload detail.
    """
    upload = await crud.upload.get(db_session=db_session, id=upload_id)
    if not upload:
        raise HTTPException(status_code=404, detail=f"Not found upload id: {upload_id}")
    return upload


from typing import Any, TypeVar

T = TypeVar("T")


class Link(BaseModel):
    self: str
    next: str = None
    prev: str = None


class PageToBeFixed(BaseModel):
    page: int
    per_page: int
    page_count: int
    total_count: int
    link: Link
    items: List[schemas.UploadReadWithFilteredFile]


@router.get("/", response_model=PageToBeFixed)
async def get_upload_list(
    upload_id: Optional[str] = Query(None, regex="(exact__|contains__)", title="上傳編號"),
    filename: Optional[str] = Query(None, regex="contains__", title="檔案名稱"),
    owner_name: Optional[str] = Query(None, regex="contains__", title="上傳者"),
    start_from: Optional[List[str]] = Query([], regex="(ge|le)__", title="上傳時間"),
    upload_status: Optional[str] = Query(
        None,
        regex="in__",
        title="上傳狀態。請以,隔開值，例如: in__0,1,2",
    ),
    is_valid: Optional[str] = Query(
        None,
        regex="in__",
        title="檔案驗證是否成功。請以,隔開值，例如: in__true,false",
    ),
    pagination: Pagination = Depends(),
    sort_expr: Optional[str] = Query(
        "-start_from",
        title="排序。start_from 代表由小到大排。-start_from 代表由大到小排。",
    ),
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Get upload list.
    """

    # TODO: upload_id change to contains
    if upload_id:
        upload_id = upload_id.replace("exact__", "contains__")

    order_expr = None
    sort_model = None
    order_by = "desc"
    if sort_expr and "-" not in sort_expr:
        order_by = "asc"
    base_sort_expr = sort_expr and sort_expr.replace("-", "")
    if base_sort_expr:
        d = {
            "upload_id": Upload.id,
            "filename": File.name,
            "owner_name": User.full_name,
            "start_from": Upload.start_from,
            "file_number": Upload.file_number,
            "upload_status": Upload.upload_status,
            "file_status": File.file_status,
            "is_valid": File.is_valid,
        }
        sort_model = d.get(base_sort_expr, Upload.created_at)
    if sort_model:
        order_expr = (getattr(sort_model, order_by)(),)

    expressions = []

    start_from_ge_list = [exp for exp in start_from if "ge__" in exp]
    start_from_le_list = [exp for exp in start_from if "le__" in exp]
    start_from_ge = start_from_ge_list and start_from_ge_list[0].replace("ge__", "")
    start_from_le = start_from_le_list and start_from_le_list[0].replace("le__", "")

    upload_filters = {
        "display_file_number__gt": 0,
        "upload_status__in": list(
            filter(
                lambda x: x,
                map(safe_int, upload_status.replace("in__", "").split(",")),
            ),
        )
        if upload_status
        else None,
        "start_from__ge": safe_parse_dt(start_from_ge),
        "start_from__le": safe_parse_dt(start_from_le),
    }
    upload_filters = dict(
        [(k, v) for k, v in upload_filters.items() if v is not None and v != []],
    )
    upload_filter_expr = models.Upload.filter_expr(**upload_filters)
    if upload_id:
        upload_filter_expr.append(
            cast(Upload.id, sa.String).contains(upload_id.replace("contains__", "")),
        )

    user_filters = {
        "full_name__contains": owner_name.replace("contains__", "")
        if owner_name
        else None,
    }
    user_filters = dict(
        [(k, v) for k, v in user_filters.items() if v is not None and v != []],
    )
    user_filter_expr = models.User.filter_expr(**user_filters)

    file_filters = {
        "name__contains": filename.replace("contains__", "") if filename else None,
    }
    file_filters = dict(
        [(k, v) for k, v in file_filters.items() if v is not None and v != []],
    )
    file_filter_expr = models.File.filter_expr(**file_filters)
    if is_valid:
        true_cond = File.is_valid == True
        false_cond = and_(File.is_valid == False, File.is_dup == False).self_group()
        if "true" in is_valid and "false" in is_valid:
            file_filter_expr.append(or_(true_cond, false_cond))
        elif "true" in is_valid:
            file_filter_expr.append(true_cond)
        elif "false" in is_valid:
            file_filter_expr.append(false_cond)

    auth_cond = []
    group_names = [group.name for group in current_user.groups]
    print("group_names", group_names)
    if "admin" in group_names:
        auth_cond = []
    elif "manager" in group_names:
        auth_cond.append(User.org_id == current_user.org_id)
    elif "user" in group_names or "subject" in group_names:
        auth_cond.append(User.id == current_user.id)

    expressions = [
        *upload_filter_expr,
        *file_filter_expr,
        *user_filter_expr,
        *auth_cond,
    ]
    print("expressions", expressions)

    query = (
        select(Upload)
        .join(File)
        .join(User)
        .options(joinedload(Upload.owner))
        .where(*expressions)
        .distinct()
    )

    print("order_expr", order_expr)
    items: Sequence[schemas.UploadReadWithFilteredFile] = await crud.upload.get_multi(
        db_session=db_session,
        query=query,
        order_expr=order_expr,
        unique=False,
        skip=(pagination.page - 1) * pagination.per_page,
        limit=pagination.per_page,
    )
    # TODO: FIXME
    resp = await db_session.execute(select(func.count()).select_from(query.subquery()))
    total_count = resp.scalar_one()
    result = await pagination.paginate2(total_count, items)
    return result


@router.post("/beacon/cancel-upload/{upload_id}", response_model=schemas.UploadRead)
async def cancel_upload(
    upload_id: UUID,
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Cancel upload.
    """
    # TODO: cancel uploading status file
    upload = await crud.upload.get(db_session=db_session, id=upload_id)
    if not upload:
        raise HTTPException(status_code=404, detail=f"Not found upload id: {upload_id}")

    is_all_files_success = await crud.upload.is_files_all_success(
        db_session=db_session,
        upload_id=upload.id,
    )
    display_file_number = await crud.upload.get_display_file_number(
        db_session=db_session,
        upload_id=upload.id,
    )
    if is_all_files_success:
        upload_in = schemas.UploadUpdate(
            upload_status=UploadStatusType.success.value,
            end_to=datetime.utcnow(),
            display_file_number=display_file_number,
        )
        await crud.upload.update(
            db_session=db_session,
            obj_current=upload,
            obj_new=upload_in,
        )
    else:
        upload = await crud.upload.cancel(db_session=db_session, upload_id=upload_id)
    return upload
