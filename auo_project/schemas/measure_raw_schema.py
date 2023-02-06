from uuid import UUID

from auo_project.models.measure_raw_model import MeasureRawBase


class MeasureRawRead(MeasureRawBase):
    id: UUID


class MeasureRawCreate(MeasureRawBase):
    pass


class MeasureRawUpdate(MeasureRawBase):
    pass
