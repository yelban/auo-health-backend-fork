from typing import Optional
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.action_model import Action
from auo_project.models.group_model import Group
from auo_project.models.role_model import Role
from auo_project.models.user_model import User
from auo_project.schemas.role_schema import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    async def add_action_to_role(
        self,
        *,
        db_session: AsyncSession,
        action: Action,
        role_id: UUID,
    ) -> Optional[Role]:
        role = await super().get(db_session=db_session, id=role_id)
        if not role:
            raise Exception(f"role_id {role_id} not exists.")
        role.actions.append(action)
        db_session.add(role)
        await db_session.commit()
        await db_session.refresh(role)
        return role

    async def add_role_to_user(
        self, *, db_session: AsyncSession, user: User, role_id: UUID
    ) -> Optional[Role]:
        role = await super().get(db_session=db_session, id=role_id)
        if not role:
            raise Exception(f"role_id {role_id} not exists.")
        role.users.append(user)
        db_session.add(role)
        await db_session.commit()
        await db_session.refresh(role)
        return role

    async def add_role_to_group(
        self,
        *,
        db_session: AsyncSession,
        group: Group,
        role_id: UUID,
    ) -> Optional[Role]:
        role = await super().get(db_session=db_session, id=role_id)
        if not role:
            raise Exception(f"role_id {role_id} not exists.")
        role.groups.append(group)
        db_session.add(role)
        await db_session.commit()
        await db_session.refresh(role)
        return role


role = CRUDRole(Role)
