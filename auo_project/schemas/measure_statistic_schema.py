from uuid import UUID

from auo_project.models.measure_statistic_model import MeasureStatisticBase


class MeasureStatisticRead(MeasureStatisticBase):
    id: UUID


class MeasureStatisticCreate(MeasureStatisticBase):
    pass


class MeasureStatisticUpdate(MeasureStatisticBase):
    pass
