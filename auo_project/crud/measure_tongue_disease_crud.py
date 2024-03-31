from auo_project.crud.base_crud import CRUDBase
from auo_project.models.measure_tongue_disease_model import MeasureTongueDisease
from auo_project.schemas.measure_tongue_disease_schema import (
    MeasureTongueDiseaseCreate,
    MeasureTongueDiseaseUpdate,
)


class CRUDMeasureTongueDisease(
    CRUDBase[
        MeasureTongueDisease,
        MeasureTongueDiseaseCreate,
        MeasureTongueDiseaseUpdate,
    ],
):
    pass


measure_tongue_disease = CRUDMeasureTongueDisease(MeasureTongueDisease)
