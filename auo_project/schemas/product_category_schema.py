from uuid import UUID

from pydantic import BaseModel

from auo_project.models.product_category_model import ProductCategoryBase


class ProductCategoryRead(ProductCategoryBase):
    id: UUID


class ProductCategoryCreate(ProductCategoryBase):
    pass


class ProductCategoryUpdate(BaseModel):
    pass
