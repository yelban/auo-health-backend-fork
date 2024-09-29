from typing import Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.tongue_cc_configs_model import TongueCCConfig
from auo_project.schemas.tongue_cc_config_schema import (
    TongueCCConfigCreate,
    TongueCCConfigUpdate,
)


class CRUDTongueCCConfig(
    CRUDBase[TongueCCConfig, TongueCCConfigCreate, TongueCCConfigUpdate],
):
    async def get_device_ids(self, db_session: AsyncSession) -> list[str]:
        response = await db_session.execute(select(TongueCCConfig.device_id).distinct())
        return sorted(response.scalars().all())

    async def get_by_device_id(
        self,
        db_session: AsyncSession,
        org_id: UUID,
        device_id: str,
    ) -> Optional[TongueCCConfig]:
        response = await db_session.execute(
            select(TongueCCConfig).where(
                TongueCCConfig.org_id == org_id,
                TongueCCConfig.device_id == device_id,
            ),
        )
        return response.scalar_one_or_none()

    async def get_by_field_id(
        self,
        db_session: AsyncSession,
        field_id: UUID,
    ) -> Optional[TongueCCConfig]:
        response = await db_session.execute(
            select(TongueCCConfig).where(TongueCCConfig.field_id == field_id),
        )
        return response.scalar_one_or_none()

    async def get_by_field_ids(
        self,
        db_session: AsyncSession,
        field_ids: list[UUID],
    ) -> list[TongueCCConfig]:
        response = await db_session.execute(
            select(TongueCCConfig).where(TongueCCConfig.field_id.in_(field_ids)),
        )
        return response.scalars().all()


tongue_cc_config = CRUDTongueCCConfig(TongueCCConfig)
