from typing import Any, List, Optional, Sequence
from uuid import UUID

import dateutil.parser
import sqlmodel
from fastapi import APIRouter, HTTPException, Query
from fastapi.param_functions import Depends
from pydantic import BaseModel
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import operators
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud, models, schemas
from auo_project.core.config import settings
from auo_project.core.constants import FileStatusType, UploadStatusType
from auo_project.core.pagination import Pagination
from auo_project.core.query import OPERATOR_SPLITTER, OPERATORS
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
    upload_id: Optional[str] = Query(None, regex="exact__", title="上傳編號"),
    filename: Optional[str] = Query(None, regex="contains__", title="檔案名稱"),
    owner_name: Optional[str] = Query(None, regex="contains__", title="上傳者"),
    start_from: Optional[List[str]] = Query([], regex="(ge|le)__", title="上傳時間"),
    upload_status: Optional[str] = Query(
        None,
        regex="in__",
        title="上傳狀態。請以,隔開值，例如: in__0,1,2",
    ),
    file_status: Optional[str] = Query(
        None,
        regex="in__",
        title="檔案狀態。請以,隔開值，例如: in__0,1,2",
    ),
    is_valid: Optional[str] = Query(
        None,
        regex="in__",
        title="檔案驗證是否成功。請以,隔開值，例如: in__true,false",
    ),
    pagniation: Pagination = Depends(),
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
    # TODO: filter dup file

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
    filter_list = [
        (Upload.id, upload_id),
        (File.name, filename),
        (User.full_name, owner_name),
        *[(Upload.start_from, exp) for exp in start_from],
        (Upload.display_file_number, "gt__0"),
        (Upload.upload_status, upload_status),
        (File.file_status, file_status),
        (File.is_valid, is_valid),
    ]

    expressions = []
    for filter in filter_list:
        print("filter ", filter)
        col = filter[0]
        op_name_value = filter[1]
        if not op_name_value:
            continue
        if OPERATOR_SPLITTER in op_name_value:
            op_name, value = op_name_value.rsplit(OPERATOR_SPLITTER, 1)
            # TODO: fixme
            if isinstance(col.expression.type, sqlmodel.sql.sqltypes.GUID):
                if not isinstance(value, UUID):
                    import sqlalchemy as sa
                    from sqlalchemy.sql.expression import cast

                    col = cast(col, sa.String)
            elif col.expression.name in ("display_file_number"):
                value = int(value)
            elif col.expression.name in ("start_from"):
                try:
                    value = dateutil.parser.parse(value)
                except Exception as e:
                    print(e)
                    raise HTTPException(422, "dateformat is not valid")
            elif col.expression.name in ("upload_status", "file_status"):
                import sqlalchemy as sa

                value = [
                    int(x) if isinstance(col.expression.type, sa.Integer) else x
                    for x in value.split(",")
                ]
            elif col.expression.name in ("is_valid"):
                new_value = []
                if "true" in value:
                    new_value += [True]
                if "false" in value:
                    new_value += [False]
                value = new_value
            op = OPERATORS.get(op_name)
            if not op:
                raise Exception(f"cannot handle op {op}")
        else:
            op = operators.eq
            value = op_name_value
        print(op, col, type(col), value)
        expressions.append(op(col, value))

    auth_cond = []
    group_names = [group.name for group in current_user.groups]
    print("group_names", group_names)
    if "admin" in group_names:
        auth_cond = []
    elif "manager" in group_names:
        auth_cond.append(User.org_id == current_user.org_id)
    elif "user" in group_names or "subject" in group_names:
        auth_cond.append(User.id == current_user.id)

    expressions += auth_cond
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
        skip=(pagniation.page - 1) * pagniation.per_page,
        limit=pagniation.per_page,
    )
    # TODO: FIXME
    resp = await db_session.execute(select(func.count()).select_from(query.subquery()))
    total_count = resp.scalar_one()
    result = await pagniation.paginate2(total_count, items)
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
