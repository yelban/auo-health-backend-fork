from typing import Dict, List, Union
from uuid import UUID

from pydantic import BaseModel, Field


class Memo(BaseModel):
    content: str = Field(None, title="內容")


class Link(BaseModel):
    self: str
    next: str = None
    prev: str = None


class BatchRequestBody(BaseModel):
    ids: List[UUID]


class BatchResponse(BaseModel):
    success: List[Dict[str, Union[UUID, str]]]
    failure: List[Dict[str, Union[UUID, str]]]
