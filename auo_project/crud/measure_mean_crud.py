from typing import Any, Dict, List, Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_mean_model import MeasureMean
from auo_project.schemas.measure_mean_schema import MeasureMeanCreate, MeasureMeanUpdate


class CRUDMeasureMean(
    CRUDBase[MeasureMean, MeasureMeanCreate, MeasureMeanUpdate],
):
    async def get_by_uniq_keys(
        self, db_session: AsyncSession, *, hand: str, position: str, sex: int
    ) -> Optional[MeasureMean]:
        cn_mean = await db_session.execute(
            select(MeasureMean).where(
                MeasureMean.hand == hand,
                MeasureMean.position == position,
                MeasureMean.sex == sex,
            ),
        )
        return cn_mean.scalar_one_or_none()

    async def get_by_sex(
        self, db_session: AsyncSession, *, sex: int
    ) -> List[MeasureMean]:
        cn_means = await db_session.execute(
            select(MeasureMean).where(MeasureMean.sex == sex),
        )
        return cn_means.scalars().all()

    async def get_dict_by_sex(
        self, db_session: AsyncSession, *, sex: int
    ) -> Dict[str, Any]:
        if sex is None:
            cn_means = await self.get_all(db_session=db_session)
        else:
            cn_means = await self.get_by_sex(db_session=db_session, sex=sex)
        return dict(
            [
                (
                    f'{"l" if cn_mean.hand == "Left" else "r"}_{cn_mean.position.lower()}',
                    cn_mean,
                )
                for cn_mean in cn_means
            ],
        )


measure_cn_mean = CRUDMeasureMean(MeasureMean)
