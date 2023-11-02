from typing import Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_advanced_tongue_model import MeasureAdvancedTongue
from auo_project.schemas.measure_advanced_tongue_schema import (
    MeasureAdvancedTongueCreate,
    MeasureAdvancedTongueUpdate,
)


class CRUDMeasureAdvancedTongue(
    CRUDBase[
        MeasureAdvancedTongue,
        MeasureAdvancedTongueCreate,
        MeasureAdvancedTongueUpdate,
    ],
):
    async def get_by_measure_id(
        self, db_session: AsyncSession, *, measure_id: UUID, owner_id: UUID
    ) -> Optional[MeasureAdvancedTongue]:
        tongue = await db_session.execute(
            select(MeasureAdvancedTongue).where(
                MeasureAdvancedTongue.measure_id == measure_id,
                MeasureAdvancedTongue.owner_id == owner_id,
            ),
        )
        return tongue.scalar_one_or_none()


measure_advanced_tongue = CRUDMeasureAdvancedTongue(MeasureAdvancedTongue)
