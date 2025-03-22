from uuid import UUID

from pydantic import BaseModel, Field

from auo_project.models.deleted_subject_model import DeletedSubjectBase


class DeletedSubjectReadBase(DeletedSubjectBase):
    id: UUID = Field(title="編號")


class DeletedSubjectRead(DeletedSubjectReadBase):
    pass



class DeletedSubjectCreate(DeletedSubjectBase):
    pass


class DeletedSubjectUpdate(BaseModel):
    pass

