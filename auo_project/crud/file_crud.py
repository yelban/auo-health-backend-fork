from auo_project.crud.base_crud import CRUDBase
from auo_project.models.file_model import File
from auo_project.schemas.file_schema import FileCreate, FileUpdate


class CRUDFile(CRUDBase[File, FileCreate, FileUpdate]):
    pass


file = CRUDFile(File)
