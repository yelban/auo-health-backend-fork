from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from auo_project.models.group_model import GroupBase


class GroupRead(GroupBase):
    id: UUID


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    description: Optional[str] = None
