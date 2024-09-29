from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.org_model import Org
from auo_project.schemas.org_schema import OrgCreate, OrgUpdate


class CRUDOrg(CRUDBase[Org, OrgCreate, OrgUpdate]):
    async def get_sales_names(self, db_session: AsyncSession) -> list[str]:
        res = await db_session.execute(select(Org.sales_name).distinct())
        result = res.fetchall()
        names = sorted([row[0] for row in result])
        return names


org = CRUDOrg(Org)
