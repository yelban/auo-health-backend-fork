from uuid import UUID

from sqlmodel import Field

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class MeasureTongueConfigBase(BaseModel):
    org_id: UUID = Field(
        index=True,
        nullable=False,
        unique=True,
    )
    upload_id: UUID = Field(
        index=True,
        nullable=False,
        foreign_key="measure.tongue_config_uploads.id",
    )


class MeasureTongueConfig(
    BaseUUIDModel,
    BaseTimestampModel,
    MeasureTongueConfigBase,
    table=True,
):
    __tablename__ = "tongue_configs"
    __table_args__ = {"schema": "measure"}
