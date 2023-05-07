from uuid import UUID

from pydantic import BaseModel

from auo_project.models.measure_mean_model import MeasureMeanBase


class MeasureMeanRead(MeasureMeanBase):
    id: UUID


class MeasureMeanCreate(MeasureMeanBase):
    pass


class MeasureMeanUpdate(BaseModel):
    pass
