from datetime import datetime
from typing import List
from uuid import UUID

from sqlmodel import Field, Relationship, UniqueConstraint

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel
from auo_project.models.field_model import BranchField
from auo_project.models.links_model import LinkBranchProduct
from auo_project.models.org_model import Org


class BranchBase(BaseModel):
    org_id: UUID = Field(
        unique=False,
        index=False,
        nullable=False,
        foreign_key="app.auth_orgs.id",
        title="組織編號",
    )
    name: str = Field(
        max_length=64,
        unique=True,
        index=True,
        nullable=False,
        title="分支機構名稱",
    )
    vatid: str = Field(
        max_length=20,
        unique=False,
        index=False,
        nullable=False,
        title="分支機構統一編號",
    )
    address: str = Field(
        max_length=200,
        unique=False,
        index=False,
        nullable=False,
        title="分支機構地址",
    )
    city: str = Field(
        max_length=100,
        unique=False,
        index=False,
        nullable=False,
    )
    state: str = Field(
        max_length=100,
        unique=False,
        index=False,
        nullable=False,
    )
    country: str = Field(
        max_length=100,
        unique=False,
        index=False,
        nullable=False,
        title="分支機構國家",
    )
    zip_code: str = Field(
        max_length=20,
        unique=False,
        index=False,
        nullable=False,
    )
    contact_name: str = Field(
        max_length=100,
        unique=False,
        index=False,
        nullable=False,
        title="分支機構聯絡人姓名",
    )
    contact_email: str = Field(
        max_length=100,
        unique=False,
        index=False,
        nullable=False,
        title="分支機構聯絡人信箱",
    )
    contact_phone: str = Field(
        max_length=20,
        unique=False,
        index=False,
        nullable=False,
        title="分支機構聯絡人電話",
    )
    sales_name: str = Field(
        max_length=100,
        unique=False,
        index=False,
        nullable=False,
        title="分支機構負責業務姓名",
    )
    sales_email: str = Field(
        max_length=100,
        unique=False,
        index=False,
        nullable=False,
        title="分支機構負責業務信箱",
    )
    sales_phone: str = Field(
        max_length=20,
        unique=False,
        index=False,
        nullable=False,
        title="分支機構負責業務電話",
    )
    has_inquiry_product: bool = Field(
        default=False,
        unique=False,
        index=False,
        nullable=False,
        title="是否購買問診產品",
    )
    has_tongue_product: bool = Field(
        default=False,
        unique=False,
        index=False,
        nullable=False,
        title="是否購買舌診產品",
    )
    has_pulse_product: bool = Field(
        default=False,
        unique=False,
        index=False,
        nullable=False,
        title="是否購買脈診產品",
    )
    valid_from: datetime = Field(
        default=datetime(1900, 1, 1, 0, 0, 0),
        unique=False,
        index=False,
        nullable=False,
        title="有效期間開始",
    )
    valid_to: datetime = Field(
        default=datetime(3001, 12, 31, 23, 59, 59),
        unique=False,
        index=False,
        nullable=False,
        title="有效期間結束",
    )
    is_active: bool = Field(
        default=True,
        unique=False,
        index=False,
        nullable=False,
        title="是否啟用",
    )


class Branch(BaseUUIDModel, BaseTimestampModel, BranchBase, table=True):
    __tablename__ = "auth_branches"
    __table_args__ = (
        UniqueConstraint("org_id", "name", name="auth_branches_org_id_name_key"),
        {"schema": "app"},
    )
    org: "Org" = Relationship(
        back_populates="branches",
        sa_relationship_kwargs={"lazy": "select"},
    )
    users: List["User"] = Relationship(
        back_populates="branch",
        sa_relationship_kwargs={"lazy": "select"},
    )
    fields: List["BranchField"] = Relationship(
        back_populates="branch",
        sa_relationship_kwargs={"lazy": "select"},
    )
    user_branches: List["UserBranch"] = Relationship(
        back_populates="branch",
        sa_relationship_kwargs={"lazy": "select"},
    )
    products: List["Product"] = Relationship(
        back_populates="branch",
        link_model=LinkBranchProduct,
        sa_relationship_kwargs={"lazy": "select"},
    )
