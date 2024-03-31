from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from auo_project.models.measure_tongue_upload_model import MeasureTongueUploadBase


class MeasureTongueUploadRead(MeasureTongueUploadBase):
    id: UUID


class MeasureTongueUploadCreate(MeasureTongueUploadBase):
    pass


class MeasureTongueUploadUpdate(BaseModel):
    tongue_front_original_loc: Optional[str] = None
    tongue_back_original_loc: Optional[str] = None
    tongue_front_corrected_loc: Optional[str] = None
    tongue_back_corrected_loc: Optional[str] = None
