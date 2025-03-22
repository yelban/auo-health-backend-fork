from uuid import UUID

from pydantic import BaseModel

from auo_project.models.measure_tongue_symptom_disease_model import (
    MeasureTongueSymptomDiseaseBase,
)


class MeasureTongueSymptomDiseaseRead(MeasureTongueSymptomDiseaseBase):
    id: UUID


class MeasureTongueSymptomDiseaseCreate(MeasureTongueSymptomDiseaseBase):
    pass


class MeasureTongueSymptomDiseaseUpdate(BaseModel):
    pass
