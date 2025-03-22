from datetime import datetime
from uuid import UUID

from sqlmodel import Field, UniqueConstraint

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class RecoveryTokenBase(BaseModel):
    user_id: UUID = Field(
        unique=False,
        index=True,
        nullable=False,
        foreign_key="app.auth_users.id",
    )
    token: str = Field(
        max_length=128,
        unique=False,
        index=True,
        nullable=False,
    )
    expired_at: datetime = Field(
        unique=False,
        index=False,
        nullable=False,
    )
    is_active: bool = Field(
        default=True,
        unique=False,
        index=True,
        nullable=False,
    )


class RecoveryToken(BaseUUIDModel, BaseTimestampModel, RecoveryTokenBase, table=True):
    __tablename__ = "auth_recovery_token"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "token",
            name="auth_recovery_token_user_id_token_key",
        ),
        {"schema": "app"},
    )
