from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from auo_project.models.subscription_model import SubscriptionBase


class SubscriptionRead(SubscriptionBase):
    id: UUID


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionUpdate(BaseModel):
    description: Optional[str] = None
    start_from: Optional[datetime] = None
    end_to: Optional[datetime] = None
    is_active: Optional[bool] = None
