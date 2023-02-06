from typing import Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_bcq_model import BCQ
from auo_project.schemas.measure_bcq_schema import BCQCreate, BCQUpdate


class CRUDBCQ(CRUDBase[BCQ, BCQCreate, BCQUpdate]):
    async def get_by_measure_id(
        self, db_session: AsyncSession, *, measure_id: UUID
    ) -> Optional[BCQ]:
        bcq = await db_session.execute(select(BCQ).where(BCQ.measure_id == measure_id))
        return bcq.scalar_one_or_none()


measure_bcq = CRUDBCQ(BCQ)
