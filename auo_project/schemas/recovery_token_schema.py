from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from auo_project.models.recovery_token_model import RecoveryTokenBase


class RecoveryTokenRead(RecoveryTokenBase):
    id: UUID


class RecoveryTokenCreate(RecoveryTokenBase):
    pass


class RecoveryTokenUpdate(BaseModel):
    is_active: Optional[bool] = None
