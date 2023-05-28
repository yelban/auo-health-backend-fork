from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_parameter_option_model import MeasureParameterOption
from auo_project.schemas.measure_parameter_option_schema import (
    MeasureParameterOptionCreate,
    MeasureParameterOptionUpdate,
)


class CRUDMeasureParameterOption(
    CRUDBase[
        MeasureParameterOption,
        MeasureParameterOptionCreate,
        MeasureParameterOptionUpdate,
    ],
):
    pass


measure_parameter_option = CRUDMeasureParameterOption(MeasureParameterOption)
