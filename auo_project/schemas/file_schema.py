from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from auo_project.core.constants import FILE_STATUS_TYPE_LABEL, FileStatusType
from auo_project.core.pagination import Link
from auo_project.models.file_model import FileBase
from auo_project.schemas.user_schema import UserWithName


class FileRead(FileBase):
    id: UUID = Field(title="編號")
    file_status_name: str = Field(default=None, title="檔案狀態名稱")
    file_status_label: str = Field(default=None, title="檔案狀態標籤")
    is_valid_label: Optional[str] = Field(default=None, title="驗證狀態標籤")
    created_at: Optional[datetime] = Field(default=None, title="建立時間 UTC+0")
    created_at_utc8: Optional[str] = Field(default=None, title="建立時間 UTC+8 (長度 16)")
    updated_at: Optional[datetime] = Field(default=None, title="更新時間")
    owner: Optional[UserWithName] = Field(default=None, title="上傳者")

    @validator("file_status_name", always=True)
    def get_file_status_name(cls, _, values):
        return FileStatusType(values["file_status"]).name

    @validator("file_status_label", always=True)
    def get_file_status_label(cls, _, values):
        return FILE_STATUS_TYPE_LABEL.get(values["file_status_name"])

    @validator("created_at_utc8", always=True)
    def get_created_at_utc8(cls, _, values):
        return (
            (values["created_at"] + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
            if values["created_at"]
            else None
        )

    @validator("is_valid_label", always=True)
    def get_is_valid_label(cls, _, values):
        return "驗證成功" if values["is_valid"] else "驗證失敗"


class FileCreate(FileBase):
    upload_id: UUID


class FileUpdate(BaseModel):
    file_status: Optional[int] = None
    location: Optional[str] = None
    size: Optional[float] = None
    is_valid: Optional[bool] = None
    memo: Optional[str] = None


class FileReadWithSimple(BaseModel):
    name: str
    file_status: int
    is_valid: bool


class FileListPage(BaseModel):
    page: int
    per_page: int
    page_count: int
    total_count: int
    link: Link
    items: List[FileRead] = Field(
        default=[],
        title="檔案列表",
    )
