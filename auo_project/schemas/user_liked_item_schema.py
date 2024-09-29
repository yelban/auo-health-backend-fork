from uuid import UUID

from pydantic import BaseModel, validator

from auo_project.core.constants import LikeItemType
from auo_project.models.user_liked_item_model import UserLikedItemBase


class UserLikedItemRead(UserLikedItemBase):
    id: UUID


class UserLikedItemCreate(UserLikedItemBase):
    pass


class UserLikedItemUpdate(UserLikedItemBase):
    pass


class UserLikeItemInput(BaseModel):
    item_type: LikeItemType
    item_ids: list[UUID]

    @validator("item_ids")
    def check_item_ids(cls, v):
        if not v:
            raise ValueError("item_ids cannot be empty")
        return v
