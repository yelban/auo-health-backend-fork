from datetime import datetime
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.recipe_model import Recipe
from auo_project.schemas.recipe_schema import RecipeCreate, RecipeUpdate


class CRUDRecipe(CRUDBase[Recipe, RecipeCreate, RecipeUpdate]):
    async def get_active_by_owner(self, db_session: AsyncSession, *, owner_id: UUID):
        query = select(self.model).where(
            self.model.owner_id == owner_id,
            self.model.is_active == True,
        )
        response = await db_session.execute(query)
        return response.scalars().all()

    async def get_inactive_by_datetime(
        self, db_session: AsyncSession, *, created_at: datetime
    ):
        query = select(self.model).where(
            self.model.created_at <= created_at,
            self.model.is_active == False,
        )
        response = await db_session.execute(query)
        return response.scalars().all()


recipe = CRUDRecipe(Recipe)
