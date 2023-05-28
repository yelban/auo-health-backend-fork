from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel

from auo_project.models.recipe_model import RecipeBase
from auo_project.schemas.chart_schema import Chart


class RecipeBaseRead(RecipeBase):
    id: UUID


class RecipeRead(RecipeBaseRead):
    pass


class RecipeCreate(BaseModel):
    owner_id: UUID
    name: Optional[str] = None
    stage: str
    is_active: bool
    subject_num_snapshot: Optional[int] = None
    snapshot_at: Optional[datetime] = None
    is_active: bool = False


class RecipeUpdate(BaseModel):
    name: Optional[str] = None
    stage: Optional[str] = None
    subject_num_snapshot: Optional[int] = None
    snapshot_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class RecipeListResponse(BaseModel):
    data: List[RecipeRead]
    total: int


class RecipeWithAnalyticalParamsResponse(BaseModel):
    recipe: RecipeRead
    parameters: Dict[str, Any]


class RecipeWithParamsResponse(BaseModel):
    recipe: RecipeRead
    parameters: Any


class RecipeWithChartsResponse(BaseModel):
    recipe: RecipeRead
    charts: Chart
