from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_tongue_symptom_disease_model import (
    MeasureTongueSymptomDisease,
)
from auo_project.schemas.measure_tongue_symptom_disease_schema import (
    MeasureTongueSymptomDiseaseCreate,
    MeasureTongueSymptomDiseaseUpdate,
)


class CRUDMeasureTongueSymptomDisease(
    CRUDBase[
        MeasureTongueSymptomDisease,
        MeasureTongueSymptomDiseaseCreate,
        MeasureTongueSymptomDiseaseUpdate,
    ],
):
    pass


measure_tongue_symptom_disease = CRUDMeasureTongueSymptomDisease(
    MeasureTongueSymptomDisease,
)
