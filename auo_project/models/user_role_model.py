from typing import List
from uuid import UUID

from sqlmodel import Field, Relationship

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel
from auo_project.models.links_model import LinkUserRole


class UserRoleBase(BaseModel):
    user_id: UUID = Field(
        index=True,
        nullable=False,
        foreign_key="app.auth_users.id",
        title="使用者編號",
    )
    role_id: UUID = Field(
        index=True,
        nullable=False,
        foreign_key="app.auth_roles.id",
        title="角色編號",
    )


class UserRole(BaseUUIDModel, BaseTimestampModel, UserRoleBase, table=True):
    __tablename__ = "auth_user_roles"
    __table_args__ = {"schema": "app"}
    users: List["User"] = Relationship(
        back_populates="roles",
        link_model=LinkUserRole,
        sa_relationship_kwargs={"lazy": "select"},
    )
    roles: List["Role"] = Relationship(
        back_populates="users",
        link_model=LinkUserRole,
        sa_relationship_kwargs={"lazy": "select"},
    )
