from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator
from sqlmodel import Field

from auo_project.core.config import settings
from auo_project.models.upload_model import UploadBase


class UploadCreateReqBody(BaseModel):
    filename_list: List[str]


# cannot replace with Upload
class UploadRead(UploadBase):
    id: UUID = Field(title="編號")
    all_files: List["FileRead"] = []
    owner: "User" = None
    owner_name: str = Field(default="", title="上傳者")

    @validator("owner_name", always=True)
    def get_owner_name(cls, _, values):
        if values["owner"]:
            return values["owner"].full_name

    class Config:
        fields = {
            "owner": {"exclude": True},
            "file_number": {"exclude": True},
            "all_files": "files",
        }
        allow_population_by_field_name = True


class UploadReadWithEndpoint(UploadRead):
    endpoint: str = Field(
        default=f"https://{settings.DOMAIN}/files/",
        title="TUS 伺服器上傳端點",
    )


class UploadReadWithFilteredFile(UploadBase):
    id: UUID = Field(title="編號")
    owner: "User" = None
    owner_name: str = Field(default="", title="上傳者")
    filtered_files: List["FileRead"] = Field(
        default=[],
        title="檔案清單只保留上傳中、成功",
        alias="files",
    )

    @validator("owner_name", always=True)
    def get_owner_name(cls, _, values):
        if values["owner"]:
            return values["owner"].full_name

    class Config:
        fields = {
            "owner": {"exclude": True},
            "file_number": {"exclude": True},
        }
        allow_population_by_field_name = True


# class UploadReadWithFilteredFile(UploadRead):
#     filtered_files: List["FileRead"] = Field(default=[], title="檔案清單只保留上傳中、成功")

#     class Config:
#         fields = {
#             "owner": {"exclude": True},
#             "file_number": {"exclude": True},
#             "files": {"exclude": True},
#             "filtered_files": "files",
#         }


class UploadCreate(UploadBase):
    pass


class UploadUpdate(BaseModel):
    upload_status: Optional[int] = None
    file_number: Optional[int] = None
    start_from: Optional[datetime] = None
    end_to: Optional[datetime] = None
    is_active: Optional[bool] = None


class UploadListResponse(BaseModel):
    count: int
    data: List["UploadRead"]
