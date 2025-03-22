from uuid import UUID

from sqlmodel import Field, Relationship, UniqueConstraint

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel
from auo_project.models.branch_model import Branch
from auo_project.models.org_model import Org
from auo_project.models.user_model import User


class UserBranchBase(BaseModel):
    user_id: UUID = Field(
        index=True,
        nullable=False,
        foreign_key="app.auth_users.id",
        title="使用者編號",
    )
    org_id: UUID = Field(
        index=True,
        nullable=False,
        foreign_key="app.auth_orgs.id",
        title="組織編號",
    )
    branch_id: UUID = Field(
        index=True,
        nullable=True,
        foreign_key="app.auth_branches.id",
        title="分店編號",
    )
    is_active: bool = Field(
        index=False,
        nullable=False,
        default=True,
        title="是否啟用",
    )


class UserBranch(BaseUUIDModel, BaseTimestampModel, UserBranchBase, table=True):
    __tablename__ = "auth_user_branches"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "org_id",
            "branch_id",
            name="user_branch_user_id_org_id_branch_id_key",
        ),
        {
            "schema": "app",
        },
    )
    user: User = Relationship(
        back_populates="user_branches",
        sa_relationship_kwargs={"lazy": "joined"},
    )
    org: Org = Relationship(
        back_populates="user_branches",
        sa_relationship_kwargs={"lazy": "joined"},
    )
    branch: Branch = Relationship(
        back_populates="user_branches",
        sa_relationship_kwargs={"lazy": "joined"},
    )
