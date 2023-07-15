from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.subject_model import Subject
from auo_project.schemas.subject_schema import SubjectCreate, SubjectUpdate


class CRUDSubject(CRUDBase[Subject, SubjectCreate, SubjectUpdate]):
    async def get_by_sid(
        self, *, db_session: AsyncSession, sid: str
    ) -> Optional[Subject]:
        subject = await db_session.execute(select(Subject).where(Subject.sid == sid))
        return subject.scalar_one_or_none()

    async def get_by_sid_and_proj_num(
        self, *, db_session: AsyncSession, sid: str, proj_num: str = None
    ) -> Optional[Subject]:
        if proj_num:
            subject = await db_session.execute(
                select(Subject).where(Subject.sid == sid, Subject.proj_num is None),
            )
        else:
            subject = await db_session.execute(
                select(Subject).where(Subject.sid == sid, Subject.proj_num == proj_num),
            )
        return subject.scalar_one_or_none()


subject = CRUDSubject(Subject)
