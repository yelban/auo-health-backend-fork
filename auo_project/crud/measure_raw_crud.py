from typing import Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_raw_model import MeasureRaw
from auo_project.schemas.measure_raw_schema import MeasureRawCreate, MeasureRawUpdate


class CRUDMeasureRaw(CRUDBase[MeasureRaw, MeasureRawCreate, MeasureRawUpdate]):
    async def get_by_measure_id(
        self, db_session: AsyncSession, *, measure_id: UUID
    ) -> Optional[MeasureRaw]:
        measure_raw = await db_session.execute(
            select(MeasureRaw).where(MeasureRaw.measure_id == measure_id),
        )
        return measure_raw.scalar_one_or_none()


measure_raw = CRUDMeasureRaw(MeasureRaw)
