from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from auo_project.models.role_model import RoleBase


class ActionItem(BaseModel):
    key: str = Field(title="功能代號與名稱")
    value: dict = Field(title="授權功能")


class RoleRead(RoleBase):
    id: UUID
    action_items: Optional[list[ActionItem]] = Field(default=[])
    liked: Optional[bool] = False


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    is_active: Optional[bool] = None
    description: Optional[str] = None


class RoleActionsUpdate(BaseModel):
    action_items: list[dict]
