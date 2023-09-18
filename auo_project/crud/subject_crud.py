from typing import Optional
from uuid import UUID

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.subject_model import Subject
from auo_project.schemas.subject_schema import SubjectCreate, SubjectUpdate


class CRUDSubject(CRUDBase[Subject, SubjectCreate, SubjectUpdate]):
    async def get_by_sid(
        self, *, db_session: AsyncSession, org_id: UUID, sid: str
    ) -> Optional[Subject]:
        subject = await db_session.execute(
            select(Subject).where(Subject.org_id == org_id, Subject.sid == sid),
        )
        return subject.scalar_one_or_none()

    async def get_by_sid_and_proj_num(
        self, *, db_session: AsyncSession, org_id: UUID, sid: str, proj_num: str = None
    ) -> Optional[Subject]:
        if proj_num:
            subject = await db_session.execute(
                select(Subject).where(
                    Subject.org_id == org_id,
                    Subject.sid == sid,
                    Subject.proj_num is None,
                ),
            )
        else:
            subject = await db_session.execute(
                select(Subject).where(
                    Subject.org_id == org_id,
                    Subject.sid == sid,
                    Subject.proj_num == proj_num,
                ),
            )
        return subject.scalar_one_or_none()

    async def get_by_number_and_org_id(
        self, *, db_session: AsyncSession, org_id: str, number: str
    ) -> Optional[Subject]:
        subject = await db_session.execute(
            select(Subject).where(
                Subject.org_id == org_id,
                func.upper(Subject.number) == number.upper(),
            ),
        )
        return subject.scalar_one_or_none()


subject = CRUDSubject(Subject)
