from datetime import datetime
from itertools import chain
from typing import Any, Dict, List, Optional, Sequence, Union
from uuid import UUID

from fastapi_async_sqlalchemy import db
from pydantic.networks import EmailStr
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.core.security import get_password_hash, verify_password
from auo_project.crud.base_crud import CRUDBase
from auo_project.models.user_model import User
from auo_project.schemas.user_schema import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(
        self,
        db_session: AsyncSession,
        email: str,
    ) -> Optional[User]:
        users = await db_session.execute(select(User).where(User.email == email))
        return users.scalar_one_or_none()

    async def get_user_by_id(
        self,
        db_session: AsyncSession,
        id: UUID,
    ) -> Optional[User]:
        return await super().get(id=id, db_session=db_session)

    async def get_by_username(
        self,
        db_session: AsyncSession,
        username: str,
        relations: List[Any] = [],
    ) -> Optional[User]:
        options = []
        for relation in relations:
            if isinstance(relation, str):
                options.append(selectinload(getattr(self.model, relation)))
            else:
                options.append(selectinload(relation))
        users = await db_session.execute(
            select(User).where(User.username == username).options(*options),
        )
        return users.scalar_one_or_none()

    async def create(
        self,
        *,
        db_session: AsyncSession,
        obj_in: UserCreate,
        autocommit: bool = True,
    ) -> User:
        db_obj = User(
            org_id=obj_in.org_id,
            username=obj_in.username,
            full_name=obj_in.full_name,
            mobile=obj_in.mobile,
            email=obj_in.email,
            is_superuser=obj_in.is_superuser,
            hashed_password=get_password_hash(obj_in.password),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(db_obj)
        if autocommit:
            await db_session.commit()
            await db_session.refresh(db_obj)
        return db_obj

    async def create_with_role(
        self,
        *,
        db_session: AsyncSession,
        obj_in: UserCreate,
    ) -> User:
        db_obj = User(
            username=obj_in.username,
            full_name=obj_in.full_name,
            mobile=obj_in.mobile,
            email=obj_in.email,
            is_superuser=obj_in.is_superuser,
            hashed_password=get_password_hash(obj_in.password),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(db_obj)
        # TODO: add role
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj

    def update(
        self,
        *,
        db_session: AsyncSession,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]],
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(
            db_session=db_session,
            obj_current=db_obj,
            obj_new=update_data,
        )

    async def update_is_active(
        self,
        *,
        db_session: AsyncSession,
        db_obj: List[User],
        obj_in: Union[int, str, Dict[str, Any]],
    ) -> Union[User, None]:
        response = None
        for x in db_obj:
            setattr(x, "is_active", obj_in.is_active)
            setattr(x, "updated_at", datetime.utcnow())
            db.session.add(x)
            await db.session.commit()
            await db.session.refresh(x)
            response.append(x)
        return response

    async def authenticate(
        self,
        *,
        db_session: AsyncSession,
        email: EmailStr,
        password: str,
    ) -> Optional[User]:
        user = await self.get_by_email(email=email, db_session=db_session)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def has_requires(
        self,
        *,
        user: User,
        groups: Sequence[str] = [],
        roles: Sequence[str] = [],
        actions: Sequence[str] = [],
    ) -> bool:
        """
        Check user exist required permission
        """
        if not groups and not roles and not actions:
            return True

        own_group_names = [group.name for group in user.groups]
        role_names = [role.name for role in user.roles]
        action_names = [action.name for action in user.actions]

        if groups and set(groups) & set(own_group_names):
            return True

        if roles and set(roles) & set(role_names):
            return True

        if actions and set(actions) & set(action_names):
            return True

        own_group_roles = list(
            chain.from_iterable([group.roles for group in user.groups]),
        )
        own_roles = user.roles + own_group_roles
        own_role_names = set([role.name for role in own_roles])
        if roles and set(roles) & set(own_role_names):
            return True

        own_actions = chain.from_iterable(
            [user.actions, chain.from_iterable([role.actions for role in own_roles])],
        )
        own_action_names = set([action.name for action in own_actions])
        if actions and set(actions) & set(own_action_names):
            return True

        return False

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_org_manager(self, user: User) -> bool:
        return self.has_requires(
            user=user,
            roles=["MeasureManager"],
        )

    def get_branches_list(self, user: User) -> list[str]:
        """
        when the user is superuser or org manager, the list will return [].
        """
        return (
            []
            if self.is_org_manager(user=user) or user.is_superuser
            else [x.branch_id for x in user.user_branches]
        )


user = CRUDUser(User)
