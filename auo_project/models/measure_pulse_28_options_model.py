from sqlmodel import Field

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class MeasurePulse28OptionBase(BaseModel):
    name: str = Field(
        nullable=False,
        title="名稱",
    )
    description: str = Field(
        nullable=True,
        title="描述",
    )


class MeasurePulse28Option(
    BaseUUIDModel,
    BaseTimestampModel,
    MeasurePulse28OptionBase,
    table=True,
):
    __tablename__ = "pulse_28_options"
    __table_args__ = ({"schema": "measure"},)
