from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import select

from auo_project import crud
from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_info_model import MeasureInfo
from auo_project.schemas.measure_info_schema import MeasureInfoCreate, MeasureInfoUpdate


class CRUDMeasureInfo(CRUDBase[MeasureInfo, MeasureInfoCreate, MeasureInfoUpdate]):
    async def get_exist_measure(
        self, db_session, *, sid: str, measure_time: datetime
    ) -> Optional[MeasureInfo]:
        subject = await crud.subject.get_by_sid(db_session=db_session, sid=sid)
        if not subject:
            return
        measure = await db_session.execute(
            select(MeasureInfo).where(
                MeasureInfo.subject_id == subject.id,
                MeasureInfo.measure_time == measure_time,
            ),
        )
        return measure.scalar_one_or_none()

    async def get(
        self, db_session, *, id: UUID, relations: List[Any] = []
    ) -> Optional[MeasureInfo]:
        options = []
        for relation in relations:
            if isinstance(relation, str):
                options.append(selectinload(getattr(self.model, relation)))
            else:
                options.append(selectinload(relation))
        measure = await db_session.execute(
            select(MeasureInfo).where(MeasureInfo.id == id).options(*options),
        )
        return measure.scalar_one_or_none()


measure_info = CRUDMeasureInfo(MeasureInfo)
