from sqlmodel import Field, Relationship, UniqueConstraint

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


# tongue_symptom_diseases
class MeasureTongueSymptomDiseaseBase(BaseModel):
    item_id: str = Field(
        index=True,
        nullable=False,
    )
    symptom_id: str = Field(
        index=True,
        nullable=False,
    )
    disease_id: str = Field(
        index=True,
        nullable=False,
        foreign_key="measure.tongue_diseases.disease_id",
    )

    class Config:
        arbitrary_types_allowed = True


class MeasureTongueSymptomDisease(
    BaseUUIDModel,
    BaseTimestampModel,
    MeasureTongueSymptomDiseaseBase,
    table=True,
):
    __tablename__ = "tongue_symptom_diseases"
    __table_args__ = (
        UniqueConstraint(
            "item_id",
            "symptom_id",
            "disease_id",
            name="measure_tongue_symptom_disease_uniq_key",
        ),
        {
            "schema": "measure",
        },
    )
    tongue_symptom: "MeasureTongueSymptom" = Relationship(
        back_populates="tongue_symptom_disease",
        sa_relationship_kwargs={
            "lazy": "select",
            "primaryjoin": f"and_(foreign(MeasureTongueSymptom.item_id) == MeasureTongueSymptomDisease.item_id, MeasureTongueSymptomDisease.symptom_id == MeasureTongueSymptom.symptom_id)",
            "uselist": False,
        },
    )
    tongue_disease: "MeasureTongueDisease" = Relationship(
        back_populates="tongue_symptom_disease",
        sa_relationship_kwargs={"lazy": "select"},
    )
