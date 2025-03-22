from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.links_model import LinkBranchProduct
from auo_project.schemas.link_schema import LinkBranchProductCreate, LinkUpdate


class CRUDLinkBranchProduct(
    CRUDBase[LinkBranchProduct, LinkBranchProductCreate, LinkUpdate],
):
    async def get_by_branch_id_and_product_id(
        self,
        db_session: AsyncSession,
        branch_id: int,
        product_id: int,
    ) -> LinkBranchProduct:
        link = await db_session.execute(
            select(LinkBranchProduct)
            .where(LinkBranchProduct.branch_id == branch_id)
            .where(LinkBranchProduct.product_id == product_id),
        )
        return link.scalar_one_or_none()


link_branch_product = CRUDLinkBranchProduct(LinkBranchProduct)
