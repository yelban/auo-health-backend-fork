from typing import List
from uuid import UUID

from sqlalchemy.orm import joinedload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.user_branch_model import UserBranch
from auo_project.schemas.user_branch_schema import (
    AuthOrgBranches,
    UserBranchCreate,
    UserBranchUpdate,
)


class CRUDUserBranch(CRUDBase[UserBranch, UserBranchCreate, UserBranchUpdate]):
    async def get_by_user_id(
        self,
        db_session: AsyncSession,
        user_id: UUID,
    ) -> List[UserBranch]:
        user_branch = await db_session.execute(
            select(UserBranch)
            .where(
                UserBranch.user_id == user_id,
                UserBranch.is_active == True,
            )
            .order_by(UserBranch.created_at.asc(), UserBranch.branch_id.asc())
            .options(joinedload(UserBranch.branch), joinedload(UserBranch.org)),
        )
        return user_branch.scalars().all()

    async def get_auth_org_branches(
        self,
        db_session: AsyncSession,
        user_id: UUID,
    ) -> List[AuthOrgBranches]:
        user_branches = await self.get_by_user_id(
            db_session=db_session,
            user_id=user_id,
        )
        result = {}
        for user_branch in user_branches:
            if user_branch.org_id not in result:
                result[user_branch.org_id] = {
                    "org_id": user_branch.org_id,
                    "org_name": user_branch.org.name,
                    "org_description": user_branch.org.description,
                    "branches": [],
                }
            result[user_branch.org_id]["branches"].append(user_branch.branch)
        output = [AuthOrgBranches(**value) for _, value in result.items()]
        return output


user_branch = CRUDUserBranch(UserBranch)
