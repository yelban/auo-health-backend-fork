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

    async def get_recipe_parameter(
        self,
        db_session: AsyncSession,
        *,
        recipe_id: UUID,
        parameter_id: str,
    ):
        response = await db_session.execute(
            select(self.model)
            .where(
                self.model.recipe_id == recipe_id,
                self.model.parameter_id == parameter_id,
            )
            .order_by(self.model.id),
        )
        records = response.scalar_one_or_none()
        return records

    async def remove_recipe_paramter(
        self,
        db_session: AsyncSession,
        *,
        recipe_id: UUID,
        parameter_id: str,
        autocommit: bool,
    ):
        response = await db_session.execute(
            select(self.model).where(
                self.model.recipe_id == recipe_id,
                self.model.parameter_id == parameter_id,
            ),
        )
        recipe_param = response.scalar_one_or_none()
        if recipe_param:
            await self.remove(
                db_session=db_session,
                id=recipe_param.id,
                autocommit=autocommit,
            )


recipe_parameter = CRUDRecipe(RecipeParameter)
