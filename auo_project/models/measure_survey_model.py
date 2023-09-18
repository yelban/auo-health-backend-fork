from typing import List, Optional
from uuid import UUID

from sqlmodel import Field, Relationship, UniqueConstraint

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class MeasureSurveyBase(BaseModel):
    org_id: UUID = Field(index=True, nullable=False, foreign_key="app.auth_orgs.id")
    name: str = Field(default="", nullable=False, max_length=128)
    description: str = Field(default="", nullable=True, max_length=256)


class MeasureSurvey(
    BaseUUIDModel,
    BaseTimestampModel,
    MeasureSurveyBase,
    table=True,
):
    __tablename__ = "surveys"
    __table_args__ = (
        UniqueConstraint(
            "org_id",
            "name",
            name="measure_surveys_org_id_name_key",
        ),
        {"schema": "measure"},
    )
    org: Optional["Org"] = Relationship(
        back_populates="measure_survey",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    measure_survey_result: List["MeasureSurveyResult"] = Relationship(
        back_populates="measure_survey",
        sa_relationship_kwargs={"lazy": "select"},
    )
