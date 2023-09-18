from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Json

from auo_project.models.measure_survey_result_model import MeasureSurveyResultBase


class MeasureSurveyResultRead(MeasureSurveyResultBase):
    id: UUID


class MeasureSurveyResultCreate(MeasureSurveyResultBase):
    survey_id: UUID
    number: str
    subject_id: Optional[UUID] = None
    measure_id: Optional[UUID] = None
    value: Json
    survey_at: datetime


class MeasureSurveyResultUpdate(BaseModel):
    subject_id: Optional[UUID] = None
    measure_id: Optional[UUID] = None
    value: Optional[Json] = None
