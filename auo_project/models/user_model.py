from typing import List, Optional
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import Column, Field, Relationship, String

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel
from auo_project.models.links_model import LinkGroupUser, LinkUserAction, LinkUserRole


class UserBase(BaseModel):
    org_id: Optional[UUID] = Field(
        index=True,
        nullable=False,
        foreign_key="app.auth_orgs.id",
    )
    subscription_id: Optional[UUID] = Field(
        default=None,
        foreign_key="app.subscriptions.id",
    )
    username: str = Field(
        max_length=64,
        unique=True,
        index=True,
        nullable=False,
    )
    full_name: str = Field(
        max_length=64,
        unique=False,
        index=False,
        nullable=False,
        title="用戶顯示名稱。",
    )
    mobile: str = Field(
        max_length=64,
        unique=False,
        index=False,
        nullable=False,
    )
    email: EmailStr = Field(
        nullable=True,
        unique=True,
        index=True,
        sa_column=Column(String(128), unique=True, index=True),
    )
    is_active: bool = Field(index=True, nullable=False, default=True)
    is_superuser: bool = Field(index=True, nullable=False, default=False)


class User(BaseUUIDModel, BaseTimestampModel, UserBase, table=True):
    __tablename__ = "auth_users"
    __table_args__ = {"schema": "app"}
    hashed_password: str = Field(max_length=100, nullable=False, index=False)
    org: Optional["Org"] = Relationship(
        back_populates="users",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    actions: List["Action"] = Relationship(
        back_populates="users",
        link_model=LinkUserAction,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    roles: List["Role"] = Relationship(
        back_populates="users",
        link_model=LinkUserRole,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    groups: List["Group"] = Relationship(
        back_populates="users",
        link_model=LinkGroupUser,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    subscription: Optional["Subscription"] = Relationship(
        back_populates="users",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    uploads: List["Upload"] = Relationship(back_populates="owner")
    all_files: List["File"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    recipes: List["Recipe"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"lazy": "select"},
    )
