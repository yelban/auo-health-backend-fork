from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.branch_model import Branch
from auo_project.schemas.branch_schema import BranchCreate, BranchUpdate


class CRUDBranch(CRUDBase[Branch, BranchCreate, BranchUpdate]):
    async def get_names(self, db_session: AsyncSession) -> list[str]:
        response = await db_session.execute(select(Branch.name).distinct())
        return sorted(response.scalars().all())

    async def get_vatids(self, db_session: AsyncSession) -> list[str]:
        response = await db_session.execute(select(Branch.vatid).distinct())
        return sorted(response.scalars().all())

    async def get_by_org_id_and_name(
        self,
        db_session: AsyncSession,
        org_id: str,
        name: str,
    ) -> Optional[Branch]:
        query = select(Branch).where(Branch.org_id == org_id).where(Branch.name == name)
        response = await db_session.execute(query)
        return response.scalar_one_or_none()


branch = CRUDBranch(Branch)
