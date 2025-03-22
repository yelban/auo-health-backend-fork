from uuid import UUID
from sqlmodel import or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.core import azure
from auo_project.core.config import settings
from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_tongue_upload_model import MeasureTongueUpload
from auo_project.schemas.measure_tongue_upload_schema import (
    MeasureTongueUploadCreate,
    MeasureTongueUploadUpdate,
)


class CRUDMeasureTongueUpload(
    CRUDBase[MeasureTongueUpload, MeasureTongueUploadCreate, MeasureTongueUploadUpdate],
):
    async def get_by_subject_id(
        self, db_session: AsyncSession, subject_id: UUID
    ) -> list[MeasureTongueUpload]:
        response = await db_session.execute(
            select(MeasureTongueUpload).where(
                MeasureTongueUpload.subject_id == subject_id
            ),
        )

        return response.scalars().all()

    async def get_unprocessed_rows(
        self,
        db_session: AsyncSession,
    ) -> list[MeasureTongueUpload]:
        response = await db_session.execute(
            select(MeasureTongueUpload).where(
                or_(
                    MeasureTongueUpload.tongue_front_corrected_loc.is_(None),
                    MeasureTongueUpload.tongue_back_corrected_loc.is_(None),
                ),
            ),
        )

        return response.scalars().all()

    def get_container_name(self) -> str:
        return settings.AZURE_STORAGE_CONTAINER_INTERNET_IMAGE

    def get_blob_prefix(self) -> str:
        return "tongue"

    def get_image_content(self, image_loc: str) -> bytes:
        downloader = azure.download_file(
            azure.internet_blob_service,
            category=self.get_container_name(),
            file_path=image_loc,
        )
        return downloader.readall()

    def get_original_images(self, upload: MeasureTongueUpload) -> tuple[bytes, bytes]:
        tongue_front = self.get_image_content(upload.tongue_front_original_loc)
        tongue_back = self.get_image_content(upload.tongue_back_original_loc)

        return tongue_front, tongue_back

    def upload_image(self, image_loc: str, image_content: bytes):
        return azure.upload_blob_file(
            azure.internet_blob_service,
            self.get_container_name(),
            image_loc,
            image_content,
        )


measure_tongue_upload = CRUDMeasureTongueUpload(MeasureTongueUpload)
