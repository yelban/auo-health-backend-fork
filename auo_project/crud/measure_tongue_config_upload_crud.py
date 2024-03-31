from io import BytesIO
from pathlib import Path
from typing import Optional
from uuid import UUID
from zipfile import ZipFile

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.core import azure
from auo_project.core.config import settings
from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_tongue_config_upload_model import (
    MeasureTongueConfigUpload,
)
from auo_project.schemas.measure_tongue_config_upload_schema import (
    MeasureTongueConfigUploadCreate,
    MeasureTongueConfigUploadUpdate,
)


class CRUDMeasureTongueConfigUpload(
    CRUDBase[
        MeasureTongueConfigUpload,
        MeasureTongueConfigUploadCreate,
        MeasureTongueConfigUploadUpdate,
    ],
):
    async def get_by_color_hash(
        self,
        db_session: AsyncSession,
        org_id: UUID,
        color_hash: str,
    ) -> Optional[MeasureTongueConfigUpload]:
        response = await db_session.execute(
            select(MeasureTongueConfigUpload)
            .where(
                MeasureTongueConfigUpload.org_id == org_id,
                MeasureTongueConfigUpload.color_hash == color_hash,
            )
            .order_by(MeasureTongueConfigUpload.created_at.desc()),
        )
        return response.scalars().first()

    async def get_cc_pickle_content(
        self,
        db_session: AsyncSession,
        org_id: UUID,
        color_hash: str,
    ) -> Optional[bytes]:
        config_upload = await self.get_by_color_hash(
            db_session=db_session,
            org_id=org_id,
            color_hash=color_hash,
        )
        if config_upload is None:
            return None

        zip_bytes = azure.download_file(
            blob_service_client=azure.private_blob_service,
            category=settings.AZURE_STORAGE_CONTAINER_TONGUE_CONFIG,
            file_path=config_upload.file_loc,
        )

        zip_file = BytesIO(zip_bytes.readall())

        with ZipFile(zip_file, mode="r") as config_zip:
            infolist = config_zip.infolist()
            for file in infolist:
                filepath = Path(file.filename)
                filename = filepath.name
                if filename == "color_correction.pkl":
                    with config_zip.open(str(filepath), mode="r") as f:
                        pickle_content = f.read()
                        return pickle_content

        return None


measure_tongue_config_upload = CRUDMeasureTongueConfigUpload(MeasureTongueConfigUpload)
