from typing import Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.action_model import Action
from auo_project.models.group_model import Group
from auo_project.models.role_model import Role
from auo_project.models.user_model import User
from auo_project.schemas.role_schema import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    async def get_by_name(
        self, *, db_session: AsyncSession, name: str
    ) -> Optional[Role]:
        role = await db_session.execute(select(Role).where(Role.name == name))
        return role.scalar_one_or_none()

    async def get_by_names(
        self, *, db_session: AsyncSession, names: list[str]
    ) -> list[Role]:
        role = await db_session.execute(select(Role).where(Role.name.in_(names)))
        return role.scalars().all()

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

    async def remove_action_from_role(
        self,
        *,
        db_session: AsyncSession,
        action: Action,
        role_id: UUID,
    ) -> Optional[Role]:
        role = await super().get(db_session=db_session, id=role_id)
        if not role:
            raise Exception(f"role_id {role_id} not exists.")
        role.actions.remove(action)
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

    async def remove_role_from_user(
        self, *, db_session: AsyncSession, user: User, role_id: UUID
    ) -> Optional[Role]:
        role = await super().get(db_session=db_session, id=role_id)
        if not role:
            raise Exception(f"role_id {role_id} not exists.")
        role.users.remove(user)
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

    async def get_name_zhs(self, db_session: AsyncSession) -> list[str]:
        response = await db_session.execute(select(Role.name_zh).distinct())
        result = response.fetchall()
        return sorted([row[0] for row in result])


role = CRUDRole(Role)
