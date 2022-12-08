from typing import List

from sqlmodel import Field, Relationship, SQLModel

from auo_project.models.base_model import BaseTimestampModel, BaseUUIDModel
from auo_project.models.links_model import LinkRoleAction, LinkUserAction


class ActionBase(SQLModel):
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


class Action(BaseUUIDModel, BaseTimestampModel, ActionBase, table=True):
    __tablename__ = "auth_actions"
    __table_args__ = {"schema": "app"}
    roles: List["Role"] = Relationship(
        back_populates="actions",
        link_model=LinkRoleAction,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    users: List["User"] = Relationship(
        back_populates="actions",
        link_model=LinkUserAction,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
