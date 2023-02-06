import uuid as uuid_pkg
from datetime import datetime
from typing import Optional

from sqlalchemy import text

# from sqlmodel import Field
from sqlalchemy_mixins import AllFeaturesMixin
from sqlmodel import Field, SQLModel

from auo_project.core.translation import i18n as _
from auo_project.db.session import mixins_session


class BaseUUIDModel(SQLModel):
    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
        sa_column_kwargs={"server_default": text("gen_random_uuid()"), "unique": True},
        title="編號",
    )


class BaseJoinUUIDModel(SQLModel):
    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
        sa_column_kwargs={"server_default": text("gen_random_uuid()"), "unique": True},
        title="編號",
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        title=_("Create Time"),
    )


class BaseTimestampModel(SQLModel):
    created_at: datetime = Field(
        index=True,
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("current_timestamp(0)")},
    )

    updated_at: datetime = Field(
        index=True,
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={
            "server_default": text("current_timestamp(0)"),
            "onupdate": text("current_timestamp(0)"),
        },
    )


class BaseModel(SQLModel, AllFeaturesMixin):
    __abstract__ = True


BaseModel.set_session(mixins_session)
