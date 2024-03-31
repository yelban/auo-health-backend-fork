from typing import Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_advanced_tongue2_model import MeasureAdvancedTongue2
from auo_project.schemas.measure_advanced_tongue2_schema import (
    MeasureAdvancedTongue2Create,
    MeasureAdvancedTongue2Update,
)


class CRUDMeasureAdvancedTongue2(
    CRUDBase[
        MeasureAdvancedTongue2,
        MeasureAdvancedTongue2Create,
        MeasureAdvancedTongue2Update,
    ],
):
    async def get_by_measure_id(
        self, db_session: AsyncSession, *, measure_id: UUID, owner_id: UUID
    ) -> Optional[MeasureAdvancedTongue2]:
        tongue = await db_session.execute(
            select(MeasureAdvancedTongue2).where(
                MeasureAdvancedTongue2.measure_id == measure_id,
                MeasureAdvancedTongue2.owner_id == owner_id,
            ),
        )
        return tongue.scalar_one_or_none()


measure_advanced_tongue2 = CRUDMeasureAdvancedTongue2(MeasureAdvancedTongue2)
