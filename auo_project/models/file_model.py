from typing import Optional
from uuid import UUID

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from auo_project.core.constants import FileStatusType
from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel

# from sqlalchemy_utils import ChoiceType


class FileBase(BaseModel):
    # TODO: composite unique key
    name: str = Field(
        max_length=128,
        # unique=True,
        index=True,
        nullable=False,
        title="檔案名稱",
    )
    owner_id: UUID = Field(
        index=True,
        nullable=False,
        foreign_key="app.auth_users.id",
        title="擁有者編號",
    )
    upload_id: UUID = Field(nullable=False, foreign_key="app.uploads.id", title="上傳編號")
    file_status: FileStatusType = Field(default=FileStatusType.init.value, title="檔案狀態")
    size: float = Field(0, title="檔案大小，單位為 MB。")
    location: str = Field(
        default="",
        max_length=128,
        unique=False,
        index=True,
        nullable=False,
        title="檔案儲存相對路徑。",
    )
    is_dup: bool = Field(default=False, nullable=False, title="檔案名稱是否重複。")
    is_valid: bool = Field(default=False, nullable=False, title="檔案是否驗證成功。")
    memo: str = Field(
        default="",
        max_length=128,
        index=False,
        nullable=False,
        title="備註",
    )


class File(BaseUUIDModel, BaseTimestampModel, FileBase, table=True):
    __tablename__ = "upload_files"
    __table_args__ = (UniqueConstraint("upload_id", "name"), {"schema": "app"})
    upload: Optional["Upload"] = Relationship(
        back_populates="all_files",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    owner: Optional["User"] = Relationship(
        back_populates="all_files",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
