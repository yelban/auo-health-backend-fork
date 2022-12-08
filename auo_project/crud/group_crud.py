from typing import List, Optional
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.group_model import Group
from auo_project.models.user_model import User
from auo_project.schemas.group_schema import GroupCreate, GroupUpdate


class CRUDGroup(CRUDBase[Group, GroupCreate, GroupUpdate]):
    async def add_user_to_group(
        self,
        *,
        db_session: AsyncSession,
        user: User,
        group_id: UUID,
    ) -> Optional[Group]:
        group = await super().get(db_session=db_session, id=group_id)
        if not group:
            raise Exception(f"not found group_id {group_id}")
        group.users.append(user)
        db_session.add(group)
        await db_session.commit()
        await db_session.refresh(group)
        return group

    async def add_users_to_group(
        self,
        *,
        db_session: AsyncSession,
        users: List[User],
        group_id: UUID,
    ) -> Optional[Group]:
        group = await super().get(id=group_id, db_session=db_session)
        if not group:
            raise Exception(f"not found group_id {group_id}")
        group.users.extend(users)
        db_session.add(group)
        await db_session.commit()
        await db_session.refresh(group)
        return group


group = CRUDGroup(Group)
