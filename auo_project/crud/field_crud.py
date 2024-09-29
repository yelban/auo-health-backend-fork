from typing import Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.field_model import BranchField
from auo_project.models.tongue_cc_configs_model import TongueCCConfig
from auo_project.schemas.field_schema import BranchFieldCreate, BranchFieldUpdate


class CRUDBrnachField(CRUDBase[BranchField, BranchFieldCreate, BranchFieldUpdate]):
    async def get_all_by_branch_id(
        self,
        db_session: AsyncSession,
        branch_id: UUID,
    ) -> list[BranchField]:
        fields = await db_session.execute(
            select(BranchField).where(BranchField.branch_id == branch_id),
        )
        return fields.scalars().all()

    async def get_by_branch_id_and_name(
        self,
        db_session: AsyncSession,
        branch_id: UUID,
        name: str,
    ) -> Optional[BranchField]:
        field = await db_session.execute(
            select(BranchField)
            .where(BranchField.branch_id == branch_id)
            .where(BranchField.name == name),
        )
        return field.scalar_one_or_none()

    def is_deletable(self, tongue_cc_config: TongueCCConfig) -> bool:
        if tongue_cc_config is None:
            return True
        if tongue_cc_config.device_id or tongue_cc_config.pad_id:
            return False
        return True


branch_field = CRUDBrnachField(BranchField)
