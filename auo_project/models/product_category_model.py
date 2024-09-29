from typing import List

from sqlmodel import Field, Relationship

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class ProductCategoryBase(BaseModel):
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
    is_active: bool = Field(
        default=True,
        unique=False,
        index=False,
        nullable=False,
    )


class ProductCategory(
    BaseUUIDModel,
    BaseTimestampModel,
    ProductCategoryBase,
    table=True,
):
    __tablename__ = "product_categories"
    __table_args__ = {"schema": "app"}
    products: List["Product"] = Relationship(
        back_populates="product_category",
        sa_relationship_kwargs={"lazy": "select"},
    )
