from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_question_option_model import MeasureQuestionOption
from auo_project.schemas.measure_question_option_schema import (
    MeasureQuestionOptionCreate,
    MeasureQuestionOptionUpdate,
)


class CRUDMeasureQuestionOption(
    CRUDBase[
        MeasureQuestionOption,
        MeasureQuestionOptionCreate,
        MeasureQuestionOptionUpdate,
    ],
):
    pass


measure_question_option = CRUDMeasureQuestionOption(MeasureQuestionOption)
