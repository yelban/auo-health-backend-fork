from pydantic import BaseModel

from auo_project.models.measure_parameter_option_model import MeasureParameterOptionBase


class MeasureParameterOptionCreate(MeasureParameterOptionBase):
    pass


class MeasureParameterOptionUpdate(BaseModel):
    pass
