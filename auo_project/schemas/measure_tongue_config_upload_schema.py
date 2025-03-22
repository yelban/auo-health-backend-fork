from uuid import UUID

from auo_project.models.measure_tongue_config_upload_model import (
    MeasureTongueConfigUploadBase,
)


class MeasureTongueConfigUploadRead(MeasureTongueConfigUploadBase):
    id: UUID


class MeasureTongueConfigUploadCreate(MeasureTongueConfigUploadBase):
    pass


class MeasureTongueConfigUploadUpdate(MeasureTongueConfigUploadBase):
    pass
