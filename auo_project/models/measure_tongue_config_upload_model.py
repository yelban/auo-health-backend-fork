from uuid import UUID

from sqlmodel import Field

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class MeasureTongueConfigUploadBase(BaseModel):
    org_id: UUID = Field(
        index=True,
        nullable=False,
        foreign_key="app.auth_orgs.id",
    )
    user_id: UUID = Field(
        index=True,
        nullable=False,
        foreign_key="app.auth_users.id",
    )
    color_correction_pkl: str = Field(title="")
    color_ini: str = Field(title="")
    file_loc: str = Field(title="")
    color_hash: str = Field(title="sha256")

    class Config:
        arbitrary_types_allowed = True


class MeasureTongueConfigUpload(
    BaseUUIDModel,
    BaseTimestampModel,
    MeasureTongueConfigUploadBase,
    table=True,
):
    __tablename__ = "tongue_config_uploads"
    __table_args__ = {"schema": "measure"}
