from pydantic import BaseModel

from auo_project.models.measure_pulse_28_options_model import MeasurePulse28OptionBase


class MeasurePulse28OptionRead(MeasurePulse28OptionBase):
    pass


class MeasurePulse28OptionCreate(MeasurePulse28OptionBase):
    pass


class MeasurePulse28OptionUpdate(BaseModel):
    pass
