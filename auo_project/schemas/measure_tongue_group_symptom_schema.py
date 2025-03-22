from uuid import UUID

from pydantic import BaseModel

from auo_project.models.measure_tongue_group_symptom_model import (
    MeasureTongueGroupSymptomBase,
)


class MeasureTongueGroupSymptomRead(MeasureTongueGroupSymptomBase):
    id: UUID


class MeasureTongueGroupSymptomCreate(MeasureTongueGroupSymptomBase):
    pass


class MeasureTongueGroupSymptomUpdate(BaseModel):
    pass
