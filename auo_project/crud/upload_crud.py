from typing import List, Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud
from auo_project.core.constants import FileStatusType, UploadStatusType
from auo_project.crud.base_crud import CRUDBase
from auo_project.models.file_model import File
from auo_project.models.upload_model import Upload
from auo_project.schemas.upload_schema import UploadCreate, UploadUpdate


class CRUDUpload(CRUDBase[Upload, UploadCreate, UploadUpdate]):
    async def add_files_to_upload(
        self, *, db_session: AsyncSession, files: List[File], upload_id: UUID
    ) -> Optional[Upload]:
        upload = await super().get(db_session=db_session, id=upload_id)
        if not upload:
            raise Exception(f"not found upload_id {upload_id}")
        new_files = [
            await crud.file.create(db_session=db_session, obj_in=file, autocommit=False)
            for file in files
        ]
        # upload.files.extend(new_files)
        # db_session.add(upload)
        await db_session.commit()
        await db_session.refresh(upload)
        return upload

    async def cancel(self, *, db_session: Optional[AsyncSession], upload_id: UUID):
        upload = await super().get(
            db_session=db_session,
            id=upload_id,
            relations=["all_files"],
        )
        if not upload:
            return
        for file in upload.all_files:
            if file.file_status == FileStatusType.uploading.value:
                file.file_status = FileStatusType.canceled.value
                db_session.add(file)
        upload.upload_status = UploadStatusType.failed.value
        db_session.add(upload)
        await db_session.commit()
        await db_session.refresh(upload)
        return upload

    async def is_files_all_success(
        self,
        db_session: AsyncSession,
        upload_id: UUID,
    ) -> bool:
        upload = await super().get(
            db_session=db_session,
            id=upload_id,
            relations=["all_files"],
        )
        if not upload:
            return False
        return all(
            [
                file.file_status == FileStatusType.success.value
                for file in upload.all_files
                if not (file.is_dup and file.file_status == FileStatusType.init.value)
                and not file.file_status in (FileStatusType.canceled.value,)
            ],
        )

    async def is_files_all_failed(
        self,
        db_session: AsyncSession,
        upload_id: UUID,
    ) -> bool:
        upload = await super().get(
            db_session=db_session,
            id=upload_id,
            relations=["all_files"],
        )
        if not upload:
            return False
        return all(
            [
                file.file_status == FileStatusType.failed.value
                for file in upload.all_files
                if not (file.is_dup and file.file_status == FileStatusType.init.value)
                and not file.file_status in (FileStatusType.canceled.value,)
            ],
        )

    async def is_files_all_complete(
        self,
        db_session: AsyncSession,
        upload_id: UUID,
    ) -> bool:
        upload = await super().get(
            db_session=db_session,
            id=upload_id,
            relations=["all_files"],
        )
        if not upload:
            return False

        all_files = upload.all_files
        return len(upload.all_files) == (
            sum(
                [
                    (file.is_dup and file.file_status == FileStatusType.init.value)
                    for file in all_files
                ],
            )
            + sum(
                [
                    file.file_status
                    in (
                        FileStatusType.success.value,
                        FileStatusType.failed.value,
                        FileStatusType.canceled.value,
                    )
                    for file in all_files
                ],
            )
        )

    async def get_display_file_number(self, db_session: AsyncSession, upload_id: UUID):
        upload = await super().get(
            db_session=db_session,
            id=upload_id,
            relations=["all_files"],
        )
        if not upload:
            return 0
        return sum(
            [
                file.file_status
                in (FileStatusType.success.value, FileStatusType.uploading.value)
                for file in upload.all_files
                if not (file.is_dup and file.file_status == FileStatusType.init.value)
                and not file.file_status in (FileStatusType.canceled.value,)
            ],
        )

    async def get_uploading_upload(self, db_session: AsyncSession):
        query = select(self.model).where(
            self.model.upload_status == UploadStatusType.uploading.value,
        )
        response = await db_session.execute(query)
        return response.scalars().all()


upload = CRUDUpload(Upload)
