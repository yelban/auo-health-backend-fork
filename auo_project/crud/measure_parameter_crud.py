from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.core.constants import ParameterType
from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_parameter_model import MeasureParameter
from auo_project.schemas.measure_parameter_schema import (
    MeasureParameterCreate,
    MeasureParameterUpdate,
)


class CRUDMeasureParameter(
    CRUDBase[MeasureParameter, MeasureParameterCreate, MeasureParameterUpdate],
):
    async def get_options_by_p_type(
        self, db_session: AsyncSession, *, p_type: ParameterType
    ):
        response = await db_session.execute(
            select(self.model).where(
                self.model.p_type == p_type.value,
            ),
        )
        options = [
            {
                "value": e.id,
                "label": e.label,
                "parent_id": e.parent_id,
                "has_childs": e.has_childs,
            }
            for e in response.scalars().all()
        ]
        option_labels_dict = {e["value"]: e["label"] for e in options}
        options = [
            {
                "value": e["value"],
                "label": f"{option_labels_dict.get(e['parent_id'])} - {e['label']}"
                if e["parent_id"] in option_labels_dict
                else e["label"],
            }
            for e in options
            if not e["has_childs"]
        ]
        sorted_options = sorted(options, key=lambda x: x["value"])

        return sorted_options


measure_parameter = CRUDMeasureParameter(MeasureParameter)
