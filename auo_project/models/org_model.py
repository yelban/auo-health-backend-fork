from typing import List

from sqlmodel import Field, Relationship, SQLModel

from auo_project.models.base_model import BaseTimestampModel, BaseUUIDModel


class OrgBase(SQLModel):
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


class Org(BaseUUIDModel, BaseTimestampModel, OrgBase, table=True):
    __tablename__ = "auth_orgs"
    __table_args__ = {"schema": "app"}
    users: List["User"] = Relationship(
        back_populates="org",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
