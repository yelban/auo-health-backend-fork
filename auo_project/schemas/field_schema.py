from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from auo_project.models.field_model import BranchFieldBase

# from auo_project.schemas.tongue_cc_config_schema import TongueCCConfigRead
# from auo_project.models.tongue_cc_configs_model import TongueCCConfig


class BranchFieldRead(BranchFieldBase):
    id: UUID
    # TODO: fixme
    tongue_cc_config: Optional[dict] = None
    deletable: Optional[bool] = Field(title="是否可刪除")


class BranchFieldCreate(BranchFieldBase):
    pass


class BranchFieldUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    address: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    is_active: Optional[bool] = None


class SimpleBranchFieldRead(BaseModel):
    id: UUID
    name: str
    tongue_cc_config: Optional[dict] = None
