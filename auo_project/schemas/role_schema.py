from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from auo_project.models.role_model import RoleBase


class RoleRead(RoleBase):
    id: UUID


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    description: Optional[str] = None
