from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from auo_project.models.action_model import ActionBase


class ActionRead(ActionBase):
    id: UUID


class ActionCreate(ActionBase):
    pass


class ActionUpdate(BaseModel):
    description: Optional[str] = None
