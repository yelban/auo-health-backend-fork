from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from auo_project.core.constants import FILE_STATUS_TYPE_LABEL, FileStatusType
from auo_project.models.file_model import FileBase


class FileRead(FileBase):
    id: UUID = Field(title="編號")
    file_status_name: str = Field(default=None, title="檔案狀態名稱")
    file_status_label: str = Field(default=None, title="檔案狀態標籤")

    @validator("file_status_name", always=True)
    def get_file_status_name(cls, _, values):
        return FileStatusType(values["file_status"]).name

    @validator("file_status_label", always=True)
    def get_file_status_label(cls, _, values):
        return FILE_STATUS_TYPE_LABEL.get(values["file_status_name"])

    # @validator("size", always=True)
    # def round_size(cls, v):
    #     return round(v, 2)


class FileCreate(FileBase):
    upload_id: UUID


class FileUpdate(BaseModel):
    file_status: Optional[int] = None
    location: Optional[str] = None
    size: Optional[float] = None
    is_valid: Optional[bool] = None


class FileReadWithSimple(BaseModel):
    name: str
    file_status: int
