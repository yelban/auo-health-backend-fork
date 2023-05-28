from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship, UniqueConstraint

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class RecipeParameterBase(BaseModel):
    recipe_id: UUID = Field(
        index=True,
        unique=False,
        nullable=False,
        foreign_key="measure.recipes.id",
    )
    parameter_id: str = Field(
        index=False,
        unique=False,
        nullable=False,
        foreign_key="measure.parameters.id",
    )
    value: str = Field(nullable=False, title="值")


class RecipeParameter(
    BaseUUIDModel,
    BaseTimestampModel,
    RecipeParameterBase,
    table=True,
):
    __tablename__ = "recipe_parameters"
    __table_args__ = (
        UniqueConstraint(
            "recipe_id",
            "parameter_id",
            name="measure_recipe_paramters_recipe_id_parameter_id_key",
        ),
        {"schema": "measure"},
    )
    recipe: Optional["Recipe"] = Relationship(
        back_populates="parameters",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
