from sqlmodel import Field, UniqueConstraint

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class MeasureDiseaseOptionBase(BaseModel):
    category_id: str = Field(
        index=True,
        nullable=False,
    )
    category_name: str = Field(
        index=False,
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


class MeasureDiseaseOption(
    BaseUUIDModel,
    BaseTimestampModel,
    MeasureDiseaseOptionBase,
    table=True,
):
    __tablename__ = "disease_options"
    __table_args__ = (
        UniqueConstraint(
            "category_id",
            "value",
            name="measure_disease_options_category_id_value_key",
        ),
        {"schema": "measure"},
    )
