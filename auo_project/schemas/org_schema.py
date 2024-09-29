from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from auo_project.models.org_model import OrgBase


class OrgRead(OrgBase):
    id: UUID


class OrgCreate(OrgBase):
    pass


class OrgUpdate(BaseModel):
    name: Optional[str] = Field(None, title="機構名稱")
    description: Optional[str] = Field(None, title="機構描述")
    country: Optional[str] = Field(None, title="機構國家")
    address: Optional[str] = Field(None, title="機構地址")
    contact_name: Optional[str] = Field(None, title="機構聯絡人姓名")
    contact_phone: Optional[str] = Field(None, title="機構聯絡人電話")
    contact_email: Optional[str] = Field(None, title="機構聯絡人信箱")
    sales_name: Optional[str] = Field(None, title="機構負責業務姓名")
    sales_phone: Optional[str] = Field(None, title="機構負責業務電話")
    sales_email: Optional[str] = Field(None, title="機構負責業務信箱")
