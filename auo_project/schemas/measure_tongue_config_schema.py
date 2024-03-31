from uuid import UUID

from pydantic import BaseModel

from auo_project.models.measure_tongue_config_model import MeasureTongueConfigBase


class MeasureTongueConfigRead(MeasureTongueConfigBase):
    id: UUID


class MeasureTongueConfigCreate(MeasureTongueConfigBase):
    pass


class MeasureTongueConfigUpdate(BaseModel):
    upload_id: UUID
