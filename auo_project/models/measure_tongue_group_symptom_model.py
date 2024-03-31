from sqlmodel import Field

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


# tongue_group_symptoms
class MeasureTongueGroupSymptomBase(BaseModel):
    item_id: str = Field(
        index=True,
        nullable=False,
    )
    group_id: str = Field(
        index=True,
        nullable=True,
    )
    component_type: str = Field(
        index=True,
        nullable=False,
    )
    description: str = Field(
        default="",
        nullable=True,
    )

    class Config:
        arbitrary_types_allowed = True


class MeasureTongueGroupSymptom(
    BaseUUIDModel,
    BaseTimestampModel,
    MeasureTongueGroupSymptomBase,
    table=True,
):
    __tablename__ = "tongue_group_symptoms"
    __table_args__ = {"schema": "measure"}
