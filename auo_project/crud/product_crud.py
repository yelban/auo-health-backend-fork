from sqlmodel import select

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.product_model import Product
from auo_project.schemas.product_schema import ProductCreate, ProductUpdate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    async def get_product_names(self, db_session) -> list[str]:
        res = await db_session.execute(
            select(Product.name).where(Product.is_active == True).distinct(),
        )
        result = res.fetchall()
        names = [row[0] for row in result]
        return names

    async def get_product_versions(self, db_session) -> list[str]:
        res = await db_session.execute(select(Product.product_version).distinct())
        result = res.fetchall()
        versions = [row[0] for row in result]
        return versions


product = CRUDProduct(Product)
