from typing import Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_survey_model import MeasureSurvey
from auo_project.schemas.measure_survey_schema import (
    MeasureSurveyCreate,
    MeasureSurveyUpdate,
)


class CRUDMeasureSurvey(
    CRUDBase[MeasureSurvey, MeasureSurveyCreate, MeasureSurveyUpdate],
):
    async def get_by_measure_id(
        self, db_session: AsyncSession, *, measure_id: UUID
    ) -> Optional[MeasureSurvey]:
        measure_survey = await db_session.execute(
            select(MeasureSurvey.id).where(MeasureSurvey.measure_id == measure_id),
        )
        return measure_survey.scalar_one_or_none()


measure_survey = CRUDMeasureSurvey(MeasureSurvey)
