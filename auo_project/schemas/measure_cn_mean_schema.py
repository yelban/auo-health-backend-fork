from uuid import UUID

from pydantic import BaseModel

from auo_project.models.measure_cn_mean_model import MeasureCNMeanBase


class MeasureCNMeanRead(MeasureCNMeanBase):
    id: UUID


class MeasureCNMeanCreate(MeasureCNMeanBase):
    pass


class MeasureCNMeanUpdate(BaseModel):
    pass
