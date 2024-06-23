from sqlmodel import Field

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class SubjectTagBase(BaseModel):
    tag_type: str = Field(
        nullable=False,
        title="標籤類型",
    )
    name: str = Field(
        nullable=False,
        title="標籤名稱",
    )
    description: str = Field(
        nullable=True,
        title="標籤描述",
    )


class SubjectTag(BaseUUIDModel, BaseTimestampModel, SubjectTagBase, table=True):
    __tablename__ = "subject_tags"
    __table_args__ = {"schema": "measure"}
