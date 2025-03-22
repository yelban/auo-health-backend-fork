from typing import List
from uuid import UUID

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_pulse_28_options_model import MeasurePulse28Option
from auo_project.schemas.measure_info_schema import Pulse28Elmenet
from auo_project.schemas.measure_pulse_28_options_schema import (
    MeasurePulse28OptionCreate,
    MeasurePulse28OptionUpdate,
)


class CRUDPulse28Option(
    CRUDBase[
        MeasurePulse28Option,
        MeasurePulse28OptionCreate,
        MeasurePulse28OptionUpdate,
    ],
):
    async def get_options(self, db_session):
        options = await self.get_all(db_session=db_session)
        return self.format_options(options)

    def format_options(
        self,
        options: List[MeasurePulse28Option],
        selected_ids: List[UUID],
    ) -> List[Pulse28Elmenet]:
        return [
            {
                "value": option.id,
                "label": option.name,
                "description": option.description,
                "selected": option.id in selected_ids if selected_ids else False,
            }
            for option in options
        ]


measure_pulse_28_option = CRUDPulse28Option(MeasurePulse28Option)
