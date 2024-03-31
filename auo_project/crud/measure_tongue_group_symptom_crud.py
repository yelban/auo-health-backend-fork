from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_tongue_group_symptom_model import (
    MeasureTongueGroupSymptom,
)


class CRUDMeasureTongueGroupSymptom(
    CRUDBase[
        MeasureTongueGroupSymptom,
        MeasureTongueGroupSymptom,
        MeasureTongueGroupSymptom,
    ],
):
    pass


measure_tongue_group_symptom = CRUDMeasureTongueGroupSymptom(MeasureTongueGroupSymptom)
