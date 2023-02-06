from typing import List
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.file_model import File
from auo_project.schemas.file_schema import FileCreate, FileUpdate


class CRUDFile(CRUDBase[File, FileCreate, FileUpdate]):
    async def get_all_by_owner_id(
        self,
        db_session: AsyncSession,
        owner_id: UUID,
    ) -> List[File]:
        response = await db_session.execute(
            select(File).where(File.owner_id == owner_id),
        )
        return response.scalars().all()


file = CRUDFile(File)
