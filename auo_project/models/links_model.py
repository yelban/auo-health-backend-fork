from typing import Optional
from uuid import UUID

from sqlmodel import Field, UniqueConstraint

from auo_project.models.base_model import BaseJoinUUIDModel


class LinkGroupUser(BaseJoinUUIDModel, table=True):
    __tablename__ = "auth_group_users"
    __table_args__ = (
        UniqueConstraint(
            "group_id",
            "user_id",
            name="auth_group_users_group_id_user_id_key",
        ),
        {"schema": "app"},
    )
    group_id: Optional[UUID] = Field(
        default=None,
        nullable=False,
        foreign_key="app.auth_groups.id",
        primary_key=False,
        index=True,
    )
    user_id: Optional[UUID] = Field(
        default=None,
        nullable=False,
        foreign_key="app.auth_users.id",
        primary_key=False,
        index=True,
    )


class LinkUserAction(BaseJoinUUIDModel, table=True):
    __tablename__ = "auth_user_actions"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "action_id",
            name="auth_user_actions_user_id_action_id_key",
        ),
        {"schema": "app"},
    )
    user_id: Optional[UUID] = Field(
        default=None,
        nullable=False,
        foreign_key="app.auth_users.id",
        primary_key=False,
        index=True,
    )
    action_id: Optional[UUID] = Field(
        default=None,
        nullable=False,
        foreign_key="app.auth_actions.id",
        primary_key=False,
        index=True,
    )


class LinkRoleAction(BaseJoinUUIDModel, table=True):
    __tablename__ = "auth_role_actions"
    __table_args__ = (
        UniqueConstraint(
            "role_id",
            "action_id",
            name="auth_role_actions_role_id_action_id_key",
        ),
        {"schema": "app"},
    )
    role_id: Optional[UUID] = Field(
        default=None,
        nullable=False,
        foreign_key="app.auth_roles.id",
        primary_key=False,
        index=True,
    )
    action_id: Optional[UUID] = Field(
        default=None,
        nullable=False,
        foreign_key="app.auth_actions.id",
        primary_key=False,
        index=True,
    )


class LinkUserRole(BaseJoinUUIDModel, table=True):
    __tablename__ = "auth_user_roles"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "role_id",
            name="auth_user_roles_user_id_role_id_key",
        ),
        {"schema": "app"},
    )
    user_id: Optional[UUID] = Field(
        default=None,
        nullable=False,
        foreign_key="app.auth_users.id",
        primary_key=False,
        index=True,
    )
    role_id: Optional[UUID] = Field(
        default=None,
        nullable=False,
        foreign_key="app.auth_roles.id",
        primary_key=False,
        index=True,
    )


class LinkGroupRole(BaseJoinUUIDModel, table=True):
    __tablename__ = "auth_group_roles"
    __table_args__ = (
        UniqueConstraint(
            "group_id",
            "role_id",
            name="auth_group_roles_user_id_role_id_key",
        ),
        {"schema": "app"},
    )
    group_id: Optional[UUID] = Field(
        default=None,
        nullable=False,
        foreign_key="app.auth_groups.id",
        primary_key=False,
        index=True,
    )
    role_id: Optional[UUID] = Field(
        default=None,
        nullable=False,
        foreign_key="app.auth_roles.id",
        primary_key=False,
        index=True,
    )
