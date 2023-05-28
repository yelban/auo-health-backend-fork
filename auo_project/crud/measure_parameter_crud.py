from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_parameter_model import MeasureParameter
from auo_project.schemas.measure_parameter_schema import (
    MeasureParameterCreate,
    MeasureParameterUpdate,
)


class CRUDMeasureParameter(
    CRUDBase[MeasureParameter, MeasureParameterCreate, MeasureParameterUpdate],
):
    pass


measure_parameter = CRUDMeasureParameter(MeasureParameter)
