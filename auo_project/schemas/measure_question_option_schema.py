from pydantic import BaseModel

from auo_project.models.measure_question_option_model import MeasureQuestionOptionBase


class MeasureQuestionOptionCreate(MeasureQuestionOptionBase):
    pass


class MeasureQuestionOptionUpdate(BaseModel):
    pass
