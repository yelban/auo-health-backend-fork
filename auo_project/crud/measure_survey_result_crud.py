from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_info_model import MeasureInfo
from auo_project.models.measure_survey_model import MeasureSurvey
from auo_project.models.measure_survey_result_model import MeasureSurveyResult
from auo_project.schemas.measure_survey_result_schema import (
    MeasureSurveyResultCreate,
    MeasureSurveyResultUpdate,
)


class CRUDMeasureSurveyResult(
    CRUDBase[MeasureSurveyResult, MeasureSurveyResultCreate, MeasureSurveyResultUpdate],
):
    async def get_by_measure_id(
        self, db_session: AsyncSession, *, measure_id: UUID
    ) -> Optional[MeasureSurveyResult]:
        response = await db_session.execute(
            select(MeasureSurveyResult).where(
                MeasureSurveyResult.measure_id == measure_id,
            ),
        )
        return response.scalar_one_or_none()

    async def get_by_number_survey_at(
        self, db_session: AsyncSession, *, number: str, survey_at: datetime
    ) -> Optional[MeasureSurveyResult]:
        response = await db_session.execute(
            select(MeasureSurveyResult).where(
                func.upper(MeasureSurveyResult.number) == number.upper(),
                MeasureSurveyResult.survey_at == survey_at,
            ),
        )
        return response.scalar_one_or_none()

    async def get_by_org_id(
        self, db_session: AsyncSession, *, org_id: UUID
    ) -> List[MeasureSurveyResult]:
        measure_survey_result = await db_session.execute(
            select(MeasureSurveyResult).where(
                MeasureSurveyResult.survey_id.in_(
                    select(MeasureSurvey.id).where(MeasureSurvey.org_id == org_id),
                ),
            ),
        )
        return measure_survey_result.scalars().all()

    async def get_by_condition(
        self,
        db_session: AsyncSession,
        *,
        org_id: UUID,
        measure_time: List[str],
        survey_at: List[str],
        measure_operators: List[str],
        consult_drs: List[str],
        **kwargs,
    ) -> List[MeasureSurveyResult]:
        conditions = []

        if org_id:
            conditions.append(MeasureInfo.org_id == org_id)
        if measure_time:
            conditions.append(
                func.date(MeasureInfo.measure_time + timedelta(hours=8))
                >= measure_time[0],
            )
            conditions.append(
                func.date(MeasureInfo.measure_time + timedelta(hours=8))
                <= measure_time[1],
            )
        if survey_at:
            conditions.append(
                func.date(MeasureSurveyResult.survey_at + timedelta(hours=8))
                >= survey_at[0],
            )
            conditions.append(
                func.date(MeasureSurveyResult.survey_at + timedelta(hours=8))
                <= survey_at[1],
            )
        if measure_operators:
            conditions.append(MeasureInfo.measure_operator.in_(measure_operators))
        if consult_drs:
            conditions.append(MeasureInfo.judge_dr.in_(consult_drs))

        print("conditions", conditions)
        relations = kwargs.get("relations", [])
        print("relations", relations)
        from sqlalchemy.orm import selectinload

        relations = [selectinload(getattr(MeasureSurveyResult, "measure_info"))]
        measure_survey_result = await db_session.execute(
            select(MeasureSurveyResult)
            .where(
                MeasureSurveyResult.id.in_(
                    select(MeasureSurveyResult.id).where(
                        *conditions,
                    ),
                ),
            )
            .options(*relations),
        )
        return measure_survey_result.scalars().all()


measure_survey_result = CRUDMeasureSurveyResult(MeasureSurveyResult)
