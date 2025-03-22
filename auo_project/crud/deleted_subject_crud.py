from auo_project.crud.base_crud import CRUDBase
from auo_project.models.deleted_subject_model import DeletedSubject
from auo_project.schemas.deleted_subject_schema import DeletedSubjectCreate, DeletedSubjectUpdate


class CRUDDeletedSubject(CRUDBase[DeletedSubject, DeletedSubjectCreate, DeletedSubjectUpdate]):
    pass

deleted_subject = CRUDDeletedSubject(DeletedSubject)
