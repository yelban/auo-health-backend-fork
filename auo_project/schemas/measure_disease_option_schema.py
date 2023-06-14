from pydantic import BaseModel

from auo_project.models.measure_disease_option_model import MeasureDiseaseOptionBase


class MeasureDiseaseOption(MeasureDiseaseOptionBase):
    pass


class MeasureDiseaseOptionCreate(MeasureDiseaseOptionBase):
    pass


class MeasureDiseaseOptionUpdate(BaseModel):
    pass
