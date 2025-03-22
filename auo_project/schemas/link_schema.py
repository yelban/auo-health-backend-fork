from uuid import UUID

from pydantic import BaseModel


class LinkRead(BaseModel):
    pass


class LinkCreate(BaseModel):
    pass


class LinkUpdate(BaseModel):
    pass


class LinkBranchProductCreate(BaseModel):
    branch_id: UUID
    product_id: UUID
