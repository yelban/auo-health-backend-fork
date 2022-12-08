from auo_project.crud.base_crud import CRUDBase
from auo_project.models.org_model import Org
from auo_project.schemas.org_schema import OrgCreate, OrgUpdate


class CRUDOrg(CRUDBase[Org, OrgCreate, OrgUpdate]):
    pass


org = CRUDOrg(Org)
