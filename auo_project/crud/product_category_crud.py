from auo_project.crud.base_crud import CRUDBase
from auo_project.models.product_category_model import ProductCategory
from auo_project.schemas.product_category_schema import (
    ProductCategoryCreate,
    ProductCategoryUpdate,
)


class CRUDProductCategory(
    CRUDBase[ProductCategory, ProductCategoryCreate, ProductCategoryUpdate],
):
    def format_options(self, options: list[ProductCategory]) -> list[dict]:
        return [
            {
                "value": raw_category.id,
                "label": raw_category.name,
            }
            for raw_category in options
        ]


product_category = CRUDProductCategory(ProductCategory)
