from uuid import UUID

from sqlmodel import Field

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class DeletedSubjectBase(BaseModel):
    org_id: UUID = Field(nullable=False, title="組織編號")
    number: str = Field(default=None, nullable=True)
    operator_id: UUID = Field(nullable=False, title="刪除者使用者 ID")

class DeletedSubject(BaseUUIDModel, BaseTimestampModel, DeletedSubjectBase, table=True):
    __tablename__ = "deleted_subjects"
    __table_args__ = {"schema": "measure"}
