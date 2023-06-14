from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, UniqueConstraint

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class RecipeBase(BaseModel):
    owner_id: UUID = Field(
        index=True,
        unique=False,
        nullable=False,
        foreign_key="app.auth_users.id",
    )
    name: str = Field(None, title="名稱")
    stage: str = Field(title="階段")
    subject_num_snapshot: int = Field(None, nullable=True, title="受試人數快照")
    snapshot_at: datetime = Field(None, nullable=True, title="快照時間")
    is_active: bool = Field(False, title="是否啟用")
    chart_settings: Optional[List[Dict[str, Any]]] = Field(
        None,
        title="圖表設定",
        sa_column=Column(JSON),
    )


class Recipe(BaseUUIDModel, BaseTimestampModel, RecipeBase, table=True):
    __tablename__ = "recipes"
    __table_args__ = (
        UniqueConstraint(
            "owner_id",
            "name",
            name="measure_recipes_owner_id_name_key",
        ),
        {"schema": "measure"},
    )
    owner: Optional["User"] = Relationship(
        back_populates="recipes",
        sa_relationship_kwargs={"lazy": "select"},
    )
    parameters: Optional["RecipeParameter"] = Relationship(
        back_populates="recipe",
        sa_relationship_kwargs={"lazy": "select"},
    )
