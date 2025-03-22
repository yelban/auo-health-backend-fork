from datetime import datetime
from uuid import UUID

from sqlmodel import Field, Relationship

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel
from auo_project.models.links_model import LinkBranchProduct


class ProductBase(BaseModel):
    category_id: UUID = Field(
        index=True,
        nullable=False,
        foreign_key="app.product_categories.id",
    )
    name: str = Field(
        max_length=64,
        unique=True,
        index=True,
        nullable=False,
        title="產品名稱",
    )
    description: str = Field(
        max_length=128,
        unique=False,
        index=False,
        nullable=False,
        title="產品描述",
    )
    product_version: str = Field(
        max_length=128,
        unique=False,
        index=False,
        nullable=False,
        title="產品版本",
    )
    app_version: str = Field(
        max_length=128,
        unique=False,
        index=False,
        nullable=False,
        title="軟體版本",
    )
    valid_from: datetime = Field(
        index=True,
        nullable=False,
        title="有效日期之起始日",
    )
    valid_to: datetime = Field(
        index=True,
        nullable=False,
        title="有效日期之結束日",
    )
    is_active: bool = Field(
        default=True,
        unique=False,
        index=False,
        nullable=False,
        title="是否啟用",
    )


class Product(BaseUUIDModel, BaseTimestampModel, ProductBase, table=True):
    __tablename__ = "products"
    __table_args__ = {"schema": "app"}
    product_category: "ProductCategory" = Relationship(
        back_populates="products",
        sa_relationship_kwargs={"lazy": "joined"},
    )
    branch: "Branch" = Relationship(
        back_populates="products",
        link_model=LinkBranchProduct,
        sa_relationship_kwargs={"lazy": "select"},
    )
