from uuid import UUID

from sqlmodel import select

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.recipe_model import Recipe
from auo_project.schemas.recipe_schema import RecipeCreate, RecipeUpdate


class CRUDRecipe(CRUDBase[Recipe, RecipeCreate, RecipeUpdate]):
    async def get_active_by_owner(self, db_session, *, owner_id: UUID):
        query = select(self.model).where(
            self.model.owner_id == owner_id,
            self.model.is_active == True,
        )
        response = await db_session.execute(query)
        return response.scalars().all()


recipe = CRUDRecipe(Recipe)
