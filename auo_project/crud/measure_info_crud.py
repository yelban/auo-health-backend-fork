from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud
from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_info_model import MeasureInfo
from auo_project.models.org_model import Org
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

    async def get_by_file_id(
        self, db_session, *, file_id: UUID
    ) -> Optional[MeasureInfo]:
        response = await db_session.execute(
            select(MeasureInfo).where(MeasureInfo.file_id == file_id),
        )
        return response.scalar_one_or_none()

    # TODO: add permission filter
    async def get_proj_num(
        self,
        db_session,
        user=None,
    ) -> List[str]:
        base_query = select(MeasureInfo)
        proj_nums_query = select(func.distinct(MeasureInfo.proj_num)).select_from(
            base_query.subquery(),
        )
        proj_nums_result = await db_session.execute(proj_nums_query)
        proj_nums = [
            {"value": proj_num[0], "label": proj_num[0]}
            for proj_num in proj_nums_result.fetchall()
            if proj_num[0]
        ]
        return proj_nums

    async def get_consult_dr(
        self,
        db_session,
        user=None,
    ) -> List[str]:
        base_query = select(MeasureInfo)
        query = select(func.distinct(MeasureInfo.judge_dr)).select_from(
            base_query.subquery(),
        )
        result = await db_session.execute(query)
        result = [{"value": e[0], "label": e[0]} for e in result.fetchall() if e[0]]
        return result

    async def get_measure_operator(
        self,
        db_session,
        user=None,
    ) -> List[str]:
        base_query = select(MeasureInfo)
        query = select(func.distinct(MeasureInfo.measure_operator)).select_from(
            base_query.subquery(),
        )
        result = await db_session.execute(query)
        result = [{"value": e[0], "label": e[0]} for e in result.fetchall() if e[0]]
        return result

    async def get_org_name(
        self,
        db_session,
        user=None,
    ) -> List[str]:
        base_query = select(MeasureInfo)
        org_id_query = select(func.distinct(MeasureInfo.org_id)).select_from(
            base_query.subquery(),
        )
        query = select(Org).where(Org.id.in_(org_id_query))
        result = await db_session.execute(query)
        result = [
            {"value": str(e[0].id), "label": e[0].description}
            for e in result.fetchall()
            if e[0]
        ]
        return result

    async def get_by_numbers(
        self,
        *,
        list_ids: List[str],
        relations: List[Any] = [],
        db_session: AsyncSession,
    ) -> Optional[List[MeasureInfo]]:
        options = []
        for relation in relations:
            if isinstance(relation, str):
                options.append(selectinload(getattr(self.model, relation)))
            else:
                options.append(selectinload(relation))
        response = await db_session.execute(
            select(self.model).where(self.model.number.in_(list_ids)).options(*options),
        )
        return response.scalars().all()

    async def get_all_by_measure_time(
        self, db_session, *, measure_time: datetime
    ) -> Optional[List[MeasureInfo]]:
        response = await db_session.execute(
            select(MeasureInfo).where(
                MeasureInfo.measure_time >= measure_time,
            ),
        )
        return response.scalars().all()

    async def get_closest_by_survey_at(
        self, db_session: AsyncSession, *, subject_id: UUID, survey_at: datetime
    ) -> Optional[MeasureInfo]:
        response = await db_session.execute(
            select(MeasureInfo)
            .where(MeasureInfo.subject_id == subject_id)
            .order_by(
                func.abs(
                    func.extract("epoch", MeasureInfo.measure_time - survey_at),
                ).asc(),
            )
            .limit(1),
        )
        return response.scalar_one_or_none()


measure_info = CRUDMeasureInfo(MeasureInfo)
