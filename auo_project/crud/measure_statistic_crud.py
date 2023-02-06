from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_statistic_model import MeasureStatistic
from auo_project.schemas.measure_statistic_schema import (
    MeasureStatisticCreate,
    MeasureStatisticUpdate,
)


class CRUDMeasureStatistic(
    CRUDBase[MeasureStatistic, MeasureStatisticCreate, MeasureStatisticUpdate],
):
    async def get_by_uniq_keys(
        self,
        db_session: AsyncSession,
        *,
        measure_id: UUID,
        statistic: str,
        hand: str,
        position: str,
    ) -> Optional[MeasureStatistic]:
        statistic = await db_session.execute(
            select(MeasureStatistic).where(
                MeasureStatistic.measure_id == measure_id,
                MeasureStatistic.statistic == statistic,
                MeasureStatistic.hand == hand,
                MeasureStatistic.position == position,
            ),
        )
        return statistic.scalar_one_or_none()

    async def get_means(
        self, db_session: AsyncSession, *, measure_id: UUID
    ) -> List[MeasureStatistic]:
        statistics = await db_session.execute(
            select(MeasureStatistic).where(
                MeasureStatistic.measure_id == measure_id,
                MeasureStatistic.statistic == "MEAN",
            ),
        )
        return statistics.scalars().all()

    async def get_means_dict(
        self, db_session: AsyncSession, *, measure_id: UUID
    ) -> Dict[str, Any]:
        means = await self.get_means(db_session=db_session, measure_id=measure_id)
        return dict(
            [
                (
                    f'{"l" if mean.hand == "Left" else "r"}_{mean.position.lower()}',
                    mean,
                )
                for mean in means
            ],
        )


measure_statistic = CRUDMeasureStatistic(MeasureStatistic)
