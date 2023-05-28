from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.recipe_parameter_model import RecipeParameter
from auo_project.schemas.recipe_parameter_schema import (
    RecipeParameterCreate,
    RecipeParameterUpdate,
)


class CRUDRecipe(
    CRUDBase[RecipeParameter, RecipeParameterCreate, RecipeParameterUpdate],
):
    async def get_by_recipe_id(self, db_session: AsyncSession, *, recipe_id: UUID):
        response = await db_session.execute(
            select(self.model).where(self.model.recipe_id == recipe_id),
        )
        return response.scalars().all()

    async def get_dict_by_recipe_id(self, db_session: AsyncSession, *, recipe_id: UUID):
        recipe_params = await self.get_by_recipe_id(db_session, recipe_id=recipe_id)
        return {item.parameter_id: item for item in recipe_params}


recipe_parameter = CRUDRecipe(RecipeParameter)
