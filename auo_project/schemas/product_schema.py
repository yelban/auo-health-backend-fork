from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from auo_project.models.product_model import ProductBase


class SimpleProductRead(ProductBase):
    id: UUID

    valid_from: str = Field(title="有效日期之起始日", description="格式: YYYY-MM-DD")
    valid_to: str = Field(title="有效日期之起始日", description="格式: YYYY-MM-DD")

    product_category: Optional["ProductCategoryRead"] = Field(
        default=None,
        title="產品類別",
    )

    @validator("valid_from", "valid_to", pre=True)
    def datetime_to_str(cls, v):
        if v:
            if isinstance(v, datetime):
                return v.strftime("%Y-%m-%d")
            elif isinstance(v, str):
                return v[:10]
        return v


class ProductRead(ProductBase):
    id: UUID
    has_data: Optional[bool] = Field(title="是否有量測資料")
    liked: Optional[bool] = Field(title="是否已加星號")

    valid_from: str = Field(title="有效日期之起始日", description="格式: YYYY-MM-DD")
    valid_to: str = Field(title="有效日期之起始日", description="格式: YYYY-MM-DD")

    product_category: Optional["ProductCategoryRead"] = Field(
        default=None,
        title="產品類別",
    )

    @validator("valid_from", "valid_to", pre=True)
    def datetime_to_str(cls, v):
        if v:
            if isinstance(v, datetime):
                return v.strftime("%Y-%m-%d")
            elif isinstance(v, str):
                return v[:10]
        return v


class ProductCreate(ProductBase):
    pass


class ProductUpdateInput(BaseModel):
    name: Optional[str] = Field(title="產品名稱")
    category_id: Optional[UUID] = Field(title="產品類別編號")
    product_version: Optional[str] = Field(title="產品版本")
    app_version: Optional[str] = Field(title="軟體版本")
    valid_from: Optional[datetime] = Field(title="有效日期之起始日")
    valid_to: Optional[datetime] = Field(title="有效日期之結束日")


class ProductUpdate(ProductUpdateInput):
    is_active: Optional[bool] = Field(title="是否啟用")


class ProductCreateInput(BaseModel):
    name: str = Field(title="產品名稱")
    category_id: UUID = Field(title="產品類別編號")
    product_version: str = Field(title="產品版本")
    app_version: str = Field(title="軟體版本")
    valid_from: datetime = Field(title="有效日期之起始日")
    valid_to: datetime = Field(title="有效日期之結束日")
