from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from auo_project.models.branch_model import BranchBase
from auo_project.schemas.field_schema import BranchFieldRead, SimpleBranchFieldRead


class BranchRead(BranchBase):
    id: UUID
    liked: Optional[bool] = Field(title="是否已加星號")
    deletable: Optional[bool] = Field(title="是否可刪除")
    org: Optional["OrgRead"] = None
    products: Optional[list["ProductRead"]] = []
    fields: list[BranchFieldRead] = []


class BranchCreate(BranchBase):
    pass


class BranchUpdate(BaseModel):
    name: Optional[str] = Field(title="分支機構名稱")
    vatid: Optional[str] = Field(None, title="分支機構統一編號")
    country: Optional[str] = Field(None, title="分支機構國家")
    address: Optional[str] = Field(None, title="分支機構地址")
    contact_name: Optional[str] = Field(None, title="分支機構聯絡人姓名")
    contact_phone: Optional[str] = Field(None, title="分支機構聯絡人電話")
    contact_email: Optional[str] = Field(None, title="分支機構聯絡人信箱")
    sales_name: Optional[str] = Field(None, title="分支機構負責業務姓名")
    sales_phone: Optional[str] = Field(None, title="分支機構負責業務電話")
    sales_email: Optional[str] = Field(None, title="分支機構負責業務信箱")
    is_active: Optional[bool] = Field(None, title="是否啟用")
    has_inquiry_product: Optional[bool] = Field(None, title="是否購買問診產品")
    has_tongue_product: Optional[bool] = Field(None, title="是否購買舌診產品")
    has_pulse_product: Optional[bool] = Field(None, title="是否購買脈診產品")


class SimpleBranchRead(BaseModel):
    id: UUID
    org_id: UUID
    name: str
    has_inquiry_product: bool = Field(title="是否購買問診產品")
    has_tongue_product: bool = Field(title="是否購買舌診產品")
    has_pulse_product: bool = Field(title="是否購買脈診產品")
    valid_to: datetime = Field(title="有效期間")
    fields: list[SimpleBranchFieldRead] = []
    org: Optional["SimpleOrgRead"] = None
