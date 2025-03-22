from datetime import date
from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class MeasureTongueUploadBase(BaseModel):
    measure_id: UUID = Field(
        index=True,
        unique=True,
        nullable=False,
        foreign_key="measure.infos.id",
    )
    org_id: UUID = Field(
        index=True,
        nullable=False,
        foreign_key="app.auth_orgs.id",
    )
    owner_id: UUID = Field(
        index=False,
        nullable=False,
        foreign_key="app.auth_users.id",
    )
    subject_id: UUID = Field(
        index=True,
        nullable=False,
        foreign_key="measure.subjects.id",
    )
    branch_id: Optional[UUID] = Field(
        default=None,
        index=True,
        nullable=True,
        foreign_key="app.auth_branches.id",
    )
    field_id: Optional[UUID] = Field(
        default=None,
        index=True,
        nullable=True,
        foreign_key="app.fields.id",
    )
    device_id: str = Field(None, title="舌診擷取設備編號", nullable=True)
    pad_id: str = Field(None, title="平板編號", nullable=True)
    name: str = Field(None, title="平板名稱", nullable=True)
    sid: str = Field(None, title="身分證字號", nullable=True)
    birth_date: date = Field(None, title="", nullable=True)
    age: int = Field(title="年齡", nullable=False)
    sex: int = Field(title="性別", nullable=False)
    number: str = Field(title="檢測編號", nullable=False)
    measure_operator: str = Field(title="檢測人員", nullable=False)
    color_hash: str = Field(title="sha256", nullable=False)
    tongue_front_original_loc: str = Field(title="原始舌面照片位置", nullable=False)
    tongue_back_original_loc: str = Field(title="原始舌背照片位置", nullable=False)
    tongue_front_corrected_loc: str = Field(None, title="校色舌面照片位置", nullable=True)
    tongue_back_corrected_loc: str = Field(None, title="校色舌面照片位置", nullable=True)
    doctor_id: Optional[UUID] = Field(
        index=True,
        nullable=True,
        foreign_key="app.doctors.id",
        title="醫師編號",
    )
    proj_num: str = Field(None, title="Project number", nullable=True)


class MeasureTongueUpload(
    BaseUUIDModel,
    BaseTimestampModel,
    MeasureTongueUploadBase,
    table=True,
):
    __tablename__ = "tongue_uploads"
    __table_args__ = {"schema": "measure"}

    org: "Org" = Relationship(
        sa_relationship_kwargs={
            "lazy": "select",
            "uselist": False,
        },
    )
    owner: "User" = Relationship(
        sa_relationship_kwargs={
            "lazy": "selectin",
            "uselist": False,
        },
    )
    subject: "Subject" = Relationship(
        sa_relationship_kwargs={
            "lazy": "selectin",
            "uselist": False,
        },
    )
    measure_info: "MeasureInfo" = Relationship(
        back_populates="tongue_upload",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    advanced_tongue2: "MeasureAdvancedTongue2" = Relationship(
        back_populates="tongue_upload",
        sa_relationship_kwargs={"lazy": "select", "uselist": False},
    )
