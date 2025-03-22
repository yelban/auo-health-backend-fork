from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_tongue_symptom_model import MeasureTongueSymptom


class CRUDMeasureTongueSymptom(
    CRUDBase[MeasureTongueSymptom, MeasureTongueSymptom, MeasureTongueSymptom],
):
    pass


measure_tongue_symptom = CRUDMeasureTongueSymptom(MeasureTongueSymptom)
