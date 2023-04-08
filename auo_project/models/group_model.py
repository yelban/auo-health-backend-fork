from typing import List

from sqlmodel import Field, Relationship

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel

from .links_model import LinkGroupRole, LinkGroupUser


class GroupBase(BaseModel):
    name: str = Field(
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


class Group(BaseUUIDModel, BaseTimestampModel, GroupBase, table=True):
    __tablename__ = "auth_groups"
    __table_args__ = {"schema": "app"}
    users: List["User"] = Relationship(
        back_populates="groups",
        link_model=LinkGroupUser,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    roles: List["Role"] = Relationship(
        back_populates="groups",
        link_model=LinkGroupRole,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
