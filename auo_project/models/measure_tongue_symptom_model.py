from typing import List

from sqlmodel import ARRAY, INTEGER, Column, Field, Relationship, UniqueConstraint

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class MeasureTongueSymptomBase(BaseModel):
    item_id: str = Field(
        index=True,
        nullable=False,
    )
    item_name: str = Field(
        index=True,
        nullable=False,
    )
    group_id: str = Field(
        index=True,
        nullable=True,
        foreign_key="measure.tongue_group_symptoms.id",
    )
    symptom_id: str = Field(
        index=True,
        nullable=False,
    )
    symptom_name: str = Field(
        index=True,
        nullable=False,
    )
    symptom_description: str = Field(
        default="",
        nullable=True,
    )
    symptom_levels: List[int] = Field(
        sa_column=Column(ARRAY(INTEGER)),
        default=[],
        nullable=True,
    )
    is_default: bool = Field(
        default=False,
        nullable=True,
    )
    is_normal: bool = Field(
        default=False,
        nullable=True,
    )
    order: int = Field(
        default=0,
        nullable=False,
    )

    class Config:
        arbitrary_types_allowed = True


class MeasureTongueSymptom(
    BaseUUIDModel,
    BaseTimestampModel,
    MeasureTongueSymptomBase,
    table=True,
):
    __tablename__ = "tongue_symptoms"
    __table_args__ = (
        UniqueConstraint(
            "item_id",
            "symptom_id",
            name="measure_tongue_symptoms_item_id_symptom_id_key",
        ),
        {"schema": "measure"},
    )
    # group_symptom: "MeasureTongueGroupSymptom" = Relationship(
    #     back_populates="tongue_symptom",
    #     sa_relationship_kwargs={"lazy": "selectin"},
    # )
    tongue_symptom_disease: "MeasureTongueSymptomDisease" = Relationship(
        back_populates="tongue_symptom",
        sa_relationship_kwargs={
            "lazy": "select",
            "primaryjoin": f"and_(foreign(MeasureTongueSymptom.item_id) == MeasureTongueSymptomDisease.item_id, MeasureTongueSymptomDisease.symptom_id == MeasureTongueSymptom.symptom_id)",
            "uselist": False,
        },
    )
