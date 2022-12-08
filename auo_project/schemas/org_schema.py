from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from auo_project.models.org_model import OrgBase


class OrgRead(OrgBase):
    id: UUID


class OrgCreate(OrgBase):
    pass


class OrgUpdate(BaseModel):
    description: Optional[str] = None
