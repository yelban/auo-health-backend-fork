from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud, models
from auo_project.core.constants import FileStatusType, UploadStatusType
from auo_project.web.api import deps

router = APIRouter()


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
