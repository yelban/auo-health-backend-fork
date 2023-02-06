from typing import Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_tongue_model import MeasureTongue
from auo_project.schemas.measure_tongue_schema import (
    MeasureTongueCreate,
    MeasureTongueUpdate,
)


class CRUDMeasureTongue(
    CRUDBase[MeasureTongue, MeasureTongueCreate, MeasureTongueUpdate],
):
    async def get_by_measure_id(
        self, db_session: AsyncSession, *, measure_id: UUID
    ) -> Optional[MeasureTongue]:
        tongue = await db_session.execute(
            select(MeasureTongue).where(MeasureTongue.measure_id == measure_id),
        )
        return tongue.scalar_one_or_none()


measure_tongue = CRUDMeasureTongue(MeasureTongue)
