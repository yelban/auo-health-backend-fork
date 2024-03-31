from uuid import UUID

from pydantic import BaseModel

from auo_project.models.measure_tongue_disease_model import MeasureTongueDiseaseBase


class MeasureTongueDiseaseRead(MeasureTongueDiseaseBase):
    id: UUID


class MeasureTongueDiseaseCreate(MeasureTongueDiseaseBase):
    pass


class MeasureTongueDiseaseUpdate(BaseModel):
    pass
