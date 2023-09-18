from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, UniqueConstraint

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class MeasureSurveyResultBase(BaseModel):
    survey_id: UUID = Field(
        index=True,
        nullable=False,
        foreign_key="measure.surveys.id",
    )
    number: str = Field(default="", nullable=False, max_length=128)
    subject_id: UUID = Field(
        default=None,
        index=True,
        nullable=True,
        foreign_key="measure.subjects.id",
    )
    measure_id: UUID = Field(
        default=None,
        index=True,
        nullable=True,
        foreign_key="measure.infos.id",
    )
    value: dict = Field(default={}, nullable=True, sa_column=Column(JSON))
    survey_at: datetime = Field(default=None, nullable=True)
    is_active: bool = Field(default=True, nullable=False)


class MeasureSurveyResult(
    BaseUUIDModel,
    BaseTimestampModel,
    MeasureSurveyResultBase,
    table=True,
):
    __tablename__ = "survey_results"
    __table_args__ = (
        UniqueConstraint(
            "survey_id",
            "number",
            "survey_at",
            name="measure_survey_results_survey_id_number_survey_at_key",
        ),
        {"schema": "measure"},
    )
    measure_survey: Optional["MeasureSurvey"] = Relationship(
        back_populates="measure_survey_result",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    subject: Optional["Subject"] = Relationship(
        back_populates="measure_survey_result",
        sa_relationship_kwargs={"lazy": "select"},
    )
    measure_info: Optional["MeasureInfo"] = Relationship(
        back_populates="measure_survey_result",
        sa_relationship_kwargs={"lazy": "select"},
    )
    # statistics: "MeasureStatistic" = Relationship(
    #     back_populates="measure_survey_result",
    #     sa_relationship_kwargs={
    #         "lazy": "select",
    #         "primaryjoin": "MeasureStatistic.measure_id == MeasureSurveyResult.measure_id",
    #         "uselist": True,
    #         "foreign_keys": "MeasureSurveyResult.measure_id",
    #         "remote_side": "MeasureStatistic.measure_id",
    #     },
    # )
