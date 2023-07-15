import pydash as py_
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_disease_option_model import MeasureDiseaseOption
from auo_project.schemas.measure_disease_option_schema import (
    MeasureDiseaseOptionCreate,
    MeasureDiseaseOptionUpdate,
)


class CRUDMeasureDiseaseOption(
    CRUDBase[
        MeasureDiseaseOption,
        MeasureDiseaseOptionCreate,
        MeasureDiseaseOptionUpdate,
    ],
):
    async def get_disease_options_dict(self, db_session: AsyncSession):
        records = await self.get_all(db_session=db_session)
        return {f"{record.category_id}:{record.value}": record for record in records}

    async def get_disease_level_options(
        self,
        db_session: AsyncSession,
        level_by="category_id",
    ):
        values = await self.get_all(db_session=db_session)
        transformed = (
            py_.chain(values)
            .group_by(level_by)
            .map_(
                lambda value: {
                    "category_id": value[0].category_id,
                    "category_name": value[0].category_name,
                    "diseases": [
                        {
                            "value": f"{value[0].category_id}:{e.value}",
                            "label": e.label,
                        }
                        for e in value
                    ],
                },
            )
            .value()
        )
        return transformed


measure_disease_option = CRUDMeasureDiseaseOption(MeasureDiseaseOption)
