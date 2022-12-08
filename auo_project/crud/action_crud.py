from auo_project.crud.base_crud import CRUDBase
from auo_project.models.action_model import Action
from auo_project.schemas.action_schema import ActionCreate, ActionUpdate


class CRUDAction(CRUDBase[Action, ActionCreate, ActionUpdate]):
    pass


action = CRUDAction(Action)
