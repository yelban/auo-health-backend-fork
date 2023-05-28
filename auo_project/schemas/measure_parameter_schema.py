from pydantic import BaseModel

from auo_project.models.measure_parameter_model import MeasureParameterBase


class MeasureParameterCreate(MeasureParameterBase):
    pass


class MeasureParameterUpdate(BaseModel):
    pass
