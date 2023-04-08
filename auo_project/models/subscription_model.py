from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship

from auo_project.core.translation import i18n as _
from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class SubscriptionBase(BaseModel):
    name: str = Field(
        max_length=64,
        unique=True,
        index=True,
        nullable=False,
    )
    description: str = Field(
        max_length=128,
        unique=False,
        index=False,
        nullable=False,
    )
    start_from: Optional[datetime] = Field(
        default_factory=datetime.now,
        title=_("Start From"),
    )
    end_to: Optional[datetime] = Field(default_factory=datetime.now, title=_("End To"))
    is_active: bool = Field(default=True)


class Subscription(BaseUUIDModel, BaseTimestampModel, SubscriptionBase, table=True):
    __tablename__ = "subscriptions"
    __table_args__ = {"schema": "app"}
    users: Optional["User"] = Relationship(
        back_populates="subscription",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
