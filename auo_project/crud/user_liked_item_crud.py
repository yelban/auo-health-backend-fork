from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.user_liked_item_model import UserLikedItem
from auo_project.schemas.user_liked_item_schema import (
    UserLikedItemCreate,
    UserLikedItemUpdate,
)


class CRUDUserLikedItem(
    CRUDBase[UserLikedItem, UserLikedItemCreate, UserLikedItemUpdate],
):
    async def get_by_user_id(
        self,
        db_session: AsyncSession,
        user_id: UUID,
    ) -> list[UserLikedItem]:
        items = await db_session.execute(
            select(UserLikedItem).where(UserLikedItem.user_id == user_id),
        )
        return items.scalars().all()

    async def get_by_item_type(
        self,
        db_session: AsyncSession,
        user_id: UUID,
        item_type: str,
        is_active: bool = None,
    ) -> list[UserLikedItem]:
        conds = [
            UserLikedItem.user_id == user_id,
            UserLikedItem.item_type == item_type,
        ]
        if is_active is not None:
            conds.append(UserLikedItem.is_active == is_active)
        items = await db_session.execute(select(UserLikedItem).where(*conds))
        return items.scalars().all()

    async def get_by_item_type_and_ids(
        self,
        db_session: AsyncSession,
        user_id: UUID,
        item_type: str,
        item_ids: list[UUID],
        is_active: bool = None,
    ) -> list[UserLikedItem]:
        conds = [
            UserLikedItem.user_id == user_id,
            UserLikedItem.item_type == item_type,
            UserLikedItem.item_id.in_(item_ids),
        ]
        if is_active is not None:
            conds.append(UserLikedItem.is_active == is_active)
        items = await db_session.execute(select(UserLikedItem).where(*conds))
        return items.scalars().all()


user_liked_item = CRUDUserLikedItem(UserLikedItem)
