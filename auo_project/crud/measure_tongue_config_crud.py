from typing import Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_tongue_config_model import MeasureTongueConfig
from auo_project.schemas.measure_tongue_config_schema import (
    MeasureTongueConfigCreate,
    MeasureTongueConfigUpdate,
)


class CRUDMeasureTongueConfig(
    CRUDBase[MeasureTongueConfig, MeasureTongueConfigCreate, MeasureTongueConfigUpdate],
):
    async def get_by_org_id(
        self,
        db_session: AsyncSession,
        org_id: UUID,
    ) -> Optional[MeasureTongueConfig]:
        response = await db_session.execute(
            select(MeasureTongueConfig).where(MeasureTongueConfig.org_id == org_id),
        )
        return response.scalar_one_or_none()


measure_tongue_config = CRUDMeasureTongueConfig(MeasureTongueConfig)
