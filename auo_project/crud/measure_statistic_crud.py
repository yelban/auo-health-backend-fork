from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_statistic_model import MeasureStatistic
from auo_project.schemas.measure_statistic_schema import (
    MeasureStatisticCreate,
    MeasureStatisticFlat,
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

    async def get_by_measure_id_list(
        self, db_session: AsyncSession, *, measure_id_list: List[UUID]
    ) -> List[MeasureStatistic]:
        statistics = await db_session.execute(
            select(MeasureStatistic).where(
                MeasureStatistic.measure_id.in_(measure_id_list),
            ),
        )
        return statistics.scalars().all()

    async def get_by_id_and_statistic(
        self, db_session: AsyncSession, *, measure_id: UUID, statistic: str
    ) -> List[MeasureStatistic]:
        statistics = await db_session.execute(
            select(MeasureStatistic).where(
                MeasureStatistic.measure_id == measure_id,
                MeasureStatistic.statistic == statistic,
            ),
        )
        return statistics.scalars().all()

    async def get_by_ids_and_statistic(
        self, db_session: AsyncSession, *, measure_ids: List[UUID], statistic_name: str
    ) -> List[MeasureStatistic]:
        statistics = await db_session.execute(
            select(MeasureStatistic).where(
                MeasureStatistic.measure_id.in_(measure_ids),
                MeasureStatistic.statistic == statistic_name,
            ),
        )
        return statistics.scalars().all()

    # TODO: refactor
    def get_flat_statistic_dict(self, statistics: List[MeasureStatistic]) -> dict:
        return dict(
            [
                (
                    f'{"l" if statistic.hand == "Left" else "r"}_{statistic.position.lower()}',
                    statistic,
                )
                for statistic in statistics
            ],
        )

    def get_flat_statistic_model(
        self,
        statistics: List[MeasureStatistic],
    ) -> MeasureStatisticFlat:
        statistic_dict = self.get_flat_statistic_dict(statistics=statistics)
        cols = ("h1",)
        result = {}
        for hand_pos, statistic in statistic_dict.items():
            for col in cols:
                result[f"{col}_{hand_pos}"] = getattr(statistic, col)
        return MeasureStatisticFlat(**result)

    def get_flat_statistic_model2(self, statistic_dict: dict) -> MeasureStatisticFlat:
        cols = (
            [
                "pass_rate",
                "h1",
                "h1_div_t1",
                "w1",
                "w1_div_t",
                "t1_div_t",
                "pw",
                "a0",
                "hr",
            ]
            + [f"c{i}" for i in range(1, 12)]
            + [f"p{i}" for i in range(1, 12)]
        )
        result = {}
        for hand_pos, statistic in statistic_dict.items():
            for col in cols:
                if col == "hr":
                    result[f"pr_{hand_pos}"] = getattr(statistic, col)
                else:
                    result[f"{col}_{hand_pos}"] = getattr(statistic, col)
        return MeasureStatisticFlat(**result)

    async def get_means_dict(
        self, db_session: AsyncSession, *, measure_id: UUID
    ) -> Dict[str, Any]:
        means = await self.get_means(db_session=db_session, measure_id=measure_id)
        return self.get_flat_statistic_dict(means)

    async def get_means_by_ids(
        self, db_session: AsyncSession, *, measure_ids: List[UUID]
    ) -> List[MeasureStatistic]:
        statistics = await db_session.execute(
            select(MeasureStatistic).where(
                MeasureStatistic.measure_id.in_(measure_ids),
                MeasureStatistic.statistic == "MEAN",
            ),
        )
        return statistics.scalars().all()

    async def get_flat_dict_by_ids_and_statistics(
        self, db_session: AsyncSession, *, measure_ids: List[UUID], statistic_name: str
    ) -> Dict[str, Any]:
        statistics = await self.get_by_ids_and_statistic(
            db_session=db_session,
            measure_ids=measure_ids,
            statistic_name=statistic_name,
        )
        result = {}
        result2 = {}
        for statistic in statistics:
            result.setdefault(statistic.measure_id, [])
            result[statistic.measure_id].append(statistic)
        for key, val in result.items():
            result2[key] = self.get_flat_statistic_dict(val)
        return result2

    async def get_flat_model_dict_by_ids_and_statistics(
        self, db_session: AsyncSession, *, measure_ids: List[UUID], statistic_name: str
    ) -> Dict[str, MeasureStatisticFlat]:
        statistics = await self.get_by_ids_and_statistic(
            db_session=db_session,
            measure_ids=measure_ids,
            statistic_name=statistic_name,
        )
        result = {}
        result2 = {}
        for statistic in statistics:
            result.setdefault(statistic.measure_id, [])
            result[statistic.measure_id].append(statistic)
        for key, val in result.items():
            result2[key] = self.get_flat_statistic_model(val)
        return result2


measure_statistic = CRUDMeasureStatistic(MeasureStatistic)
