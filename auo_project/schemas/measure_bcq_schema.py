from uuid import UUID

from auo_project.models.measure_bcq_model import BCQBase


class BCQRead(BCQBase):
    id: UUID


class BCQCreate(BCQBase):
    pass


class BCQUpdate(BCQBase):
    pass
