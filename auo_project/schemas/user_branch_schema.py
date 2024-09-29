from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from auo_project.models.user_branch_model import UserBranchBase
from auo_project.schemas.branch_schema import SimpleBranchRead


class UserBranchRead(UserBranchBase):
    id: UUID


class UserBranchCreate(UserBranchBase):
    pass


class UserBranchUpdate(BaseModel):
    is_active: Optional[bool] = None


class AuthOrgBranches(BaseModel):
    org_id: UUID
    org_name: str
    org_description: str
    branches: List[SimpleBranchRead] = []
