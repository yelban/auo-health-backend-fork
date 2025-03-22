from uuid import UUID

from pydantic import BaseModel

from auo_project.models.measure_tongue_symptom_model import MeasureTongueSymptomBase


class MeasureTongueSymptomBase(MeasureTongueSymptomBase):
    id: UUID


class MeasureTongueSymptomCreate(MeasureTongueSymptomBase):
    pass


class MeasureTongueSymptomUpdate(BaseModel):
    pass
