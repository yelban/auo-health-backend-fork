from typing import List
from uuid import UUID

from pydantic import BaseModel, Field

from auo_project.models.subject_tag_model import SubjectTagBase


class SubjectTagReadBase(SubjectTagBase):
    id: UUID = Field(title="編號")
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


class SubjectTagRead(SubjectTagReadBase):
    pass


class SubjectTagCreate(SubjectTagBase):
    pass


class SubjectTagUpdate(BaseModel):
    pass


class SubjectTagUpdateInput(BaseModel):
    tag_ids: List[UUID] = Field(
        nullable=False,
        title="標籤編號",
    )
