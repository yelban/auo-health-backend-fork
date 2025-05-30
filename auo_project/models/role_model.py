from typing import List

from sqlmodel import Field, Relationship

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel
from auo_project.models.links_model import LinkGroupRole, LinkRoleAction, LinkUserRole


class RoleBase(BaseModel):
    name: str = Field(
        max_length=64,
        unique=True,
        index=True,
        nullable=False,
    )
    name_zh: str = Field(
        max_length=64,
        unique=True,
        index=True,
        nullable=False,
    )
    description: str = Field(
        max_length=128,
        unique=False,
        index=False,
        nullable=False,
    )
    is_active: bool = Field(index=True, nullable=False, default=True)


class Role(BaseUUIDModel, BaseTimestampModel, RoleBase, table=True):
    __tablename__ = "auth_roles"
    __table_args__ = {"schema": "app"}
    users: List["User"] = Relationship(
        back_populates="roles",
        link_model=LinkUserRole,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    actions: List["Action"] = Relationship(
        back_populates="roles",
        link_model=LinkRoleAction,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    groups: List["Group"] = Relationship(
        back_populates="roles",
        link_model=LinkGroupRole,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
