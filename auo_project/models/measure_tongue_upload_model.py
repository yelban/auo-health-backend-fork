from datetime import date
from uuid import UUID

from sqlmodel import Field, Relationship

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class MeasureTongueUploadBase(BaseModel):
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
    name: str = Field(None, title="", nullable=True)
    sid: str = Field(None, title="", nullable=True)
    birth_date: date = Field(None, title="", nullable=True)
    age: int = Field(title="", nullable=False)
    sex: int = Field(title="", nullable=False)
    number: str = Field(title="", nullable=False)
    measure_operator: str = Field(title="", nullable=False)
    color_hash: str = Field(title="sha256", nullable=False)
    tongue_front_original_loc: str = Field(title="", nullable=False)
    tongue_back_original_loc: str = Field(title="", nullable=False)
    tongue_front_corrected_loc: str = Field(None, title="", nullable=True)
    tongue_back_corrected_loc: str = Field(None, title="", nullable=True)


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
    advanced_tongue2: "MeasureAdvancedTongue2" = Relationship(
        back_populates="tongue_upload",
        sa_relationship_kwargs={"lazy": "select", "uselist": False},
    )
