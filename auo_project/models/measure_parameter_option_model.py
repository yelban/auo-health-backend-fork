from uuid import UUID

from sqlmodel import Field, UniqueConstraint

from auo_project.models.base_model import BaseModel, BaseTimestampModel


class MeasureParameterOptionBase(BaseModel):
    id: UUID = Field(
        primary_key=True,
        index=True,
        nullable=False,
    )
    parent_id: str = Field(
        index=True,
        nullable=False,
    )
    value: str = Field(
        index=True,
        nullable=False,
    )
    label: str = Field(
        index=False,
        nullable=False,
    )
    label_suffix: str = Field(
        index=False,
        nullable=False,
    )
    option_type: str = Field(
        index=False,
        nullable=False,
    )
    option_component: str = Field(
        index=False,
        nullable=False,
    )
    option_category_id: str = Field(
        index=True,
        nullable=False,
    )
    memo: str = Field(
        index=False,
        nullable=False,
    )


class MeasureParameterOption(
    BaseTimestampModel,
    MeasureParameterOptionBase,
    table=True,
):
    __tablename__ = "parameter_options"
    __table_args__ = (
        UniqueConstraint(
            "parent_id",
            "value",
            name="measure_parameter_options_parent_id_value_key",
        ),
        {"schema": "measure"},
    )
