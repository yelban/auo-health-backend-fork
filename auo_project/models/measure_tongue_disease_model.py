from sqlmodel import Field, Relationship

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


# tongue_diseases
class MeasureTongueDiseaseBase(BaseModel):
    disease_id: str = Field(
        index=True,
        nullable=False,
        unique=True,
    )
    disease_name: str = Field(
        index=True,
        nullable=False,
    )

    class Config:
        arbitrary_types_allowed = True


class MeasureTongueDisease(
    BaseUUIDModel,
    BaseTimestampModel,
    MeasureTongueDiseaseBase,
    table=True,
):
    __tablename__ = "tongue_diseases"
    __table_args__ = {"schema": "measure"}

    tongue_symptom_disease: "MeasureTongueSymptomDisease" = Relationship(
        back_populates="tongue_disease",
        sa_relationship_kwargs={"lazy": "select"},
    )
