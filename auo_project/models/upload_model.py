from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from auo_project.core.constants import FileStatusType, UploadStatusType
from auo_project.core.translation import i18n as _
from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class UploadBase(BaseModel):
    owner_id: UUID = Field(
        index=True,
        nullable=False,
        foreign_key="app.auth_users.id",
        title="擁有者編號",
    )
    upload_status: UploadStatusType = Field(default=0, title="上傳狀態")
    file_number: int = Field(default=0, title="檔案數量")
    display_file_number: int = Field(default=0, title="顯示檔案數量，僅包含上傳中與成功")
    start_from: Optional[datetime] = Field(
        index=True,
        nullable=False,
        default_factory=datetime.now,
        title=_("Start From"),
    )
    end_to: Optional[datetime] = Field(index=True, nullable=True, title=_("End To"))
    is_active: Optional[bool] = Field(default=True, title="是否有效")


class Upload(BaseUUIDModel, BaseTimestampModel, UploadBase, table=True):
    __tablename__ = "uploads"
    __table_args__ = {"schema": "app"}
    all_files: Optional[List["File"]] = Relationship(
        back_populates="upload",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    filtered_files: Optional[List["File"]] = Relationship(
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": f"and_(foreign(Upload.id) == File.upload_id, File.file_status.in_([{FileStatusType.uploading},{FileStatusType.success}]))",
            "uselist": True,
        },
    )
    owner: Optional["User"] = Relationship(
        back_populates="uploads",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
