from typing import Optional
from uuid import UUID

from sqlmodel import Field

from auo_project.models.base_model import BaseJoinUUIDModel


class LinkGroupUser(BaseJoinUUIDModel, table=True):
    __tablename__ = "auth_group_users"
    __table_args__ = {"schema": "app"}
    group_id: Optional[UUID] = Field(
        default=None,
        nullable=False,
        foreign_key="app.auth_groups.id",
        primary_key=True,
    )
    user_id: Optional[UUID] = Field(
        default=None,
        nullable=False,
        foreign_key="app.auth_users.id",
        primary_key=True,
    )


class LinkUserAction(BaseJoinUUIDModel, table=True):
    __tablename__ = "auth_user_actions"
    __table_args__ = {"schema": "app"}
    user_id: Optional[UUID] = Field(
        default=None,
        nullable=False,
        foreign_key="app.auth_users.id",
        primary_key=True,
    )
    action_id: Optional[UUID] = Field(
        default=None,
        nullable=False,
        foreign_key="app.auth_actions.id",
        primary_key=True,
    )


class LinkRoleAction(BaseJoinUUIDModel, table=True):
    __tablename__ = "auth_role_actions"
    __table_args__ = {"schema": "app"}
    role_id: Optional[UUID] = Field(
        default=None,
        nullable=False,
        foreign_key="app.auth_roles.id",
        primary_key=True,
    )
    action_id: Optional[UUID] = Field(
        default=None,
        nullable=False,
        foreign_key="app.auth_actions.id",
        primary_key=True,
    )


class LinkUserRole(BaseJoinUUIDModel, table=True):
    __tablename__ = "auth_user_roles"
    __table_args__ = {"schema": "app"}
    user_id: Optional[UUID] = Field(
        default=None,
        nullable=False,
        foreign_key="app.auth_users.id",
        primary_key=True,
    )
    role_id: Optional[UUID] = Field(
        default=None,
        nullable=False,
        foreign_key="app.auth_roles.id",
        primary_key=True,
    )


class LinkGroupRole(BaseJoinUUIDModel, table=True):
    __tablename__ = "auth_group_roles"
    __table_args__ = {"schema": "app"}
    group_id: Optional[UUID] = Field(
        default=None,
        nullable=False,
        foreign_key="app.auth_groups.id",
        primary_key=True,
    )
    role_id: Optional[UUID] = Field(
        default=None,
        nullable=False,
        foreign_key="app.auth_roles.id",
        primary_key=True,
    )
