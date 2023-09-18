from uuid import UUID

from auo_project.models.measure_survey_model import MeasureSurveyBase


class MeasureSurveyRead(MeasureSurveyBase):
    id: UUID


class MeasureSurveyCreate(MeasureSurveyBase):
    pass


class MeasureSurveyUpdate(MeasureSurveyBase):
    pass
