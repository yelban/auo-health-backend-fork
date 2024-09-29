from datetime import datetime
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.recovery_token_model import RecoveryToken
from auo_project.schemas.recovery_token_schema import (
    RecoveryTokenCreate,
    RecoveryTokenUpdate,
)


class CRUDRecoveryToken(
    CRUDBase[RecoveryToken, RecoveryTokenCreate, RecoveryTokenUpdate],
):
    async def get_by_token(
        self,
        db_session: AsyncSession,
        user_id: UUID,
        token: str,
    ) -> RecoveryToken:
        res = await db_session.execute(
            select(RecoveryToken).where(
                RecoveryToken.user_id == user_id,
                RecoveryToken.token == token,
            ),
        )
        return res.scalar_one_or_none()

    async def get_tokens(self, db_session: AsyncSession, user_id: UUID) -> list[str]:
        res = await db_session.execute(
            select(RecoveryToken)
            .where(RecoveryToken.user_id == user_id)
            .order_by(RecoveryToken.created_at.desc()),
        )
        return res.scalars().all()

    async def get_active_tokens(
        self,
        db_session: AsyncSession,
        user_id: UUID,
    ) -> list[str]:
        res = await db_session.execute(
            select(RecoveryToken).where(
                RecoveryToken.user_id == user_id,
                RecoveryToken.is_active == True,
            ),
        )
        return res.scalars().all()

    async def get_valid_tokens(
        self,
        db_session: AsyncSession,
        user_id: UUID,
    ) -> list[str]:
        res = await db_session.execute(
            select(RecoveryToken)
            .where(
                RecoveryToken.user_id == user_id,
                RecoveryToken.is_active == True,
                RecoveryToken.expired_at > datetime.utcnow(),
            )
            .order_by(RecoveryToken.created_at.desc()),
        )
        return res.scalars().all()


recovery_token = CRUDRecoveryToken(RecoveryToken)
