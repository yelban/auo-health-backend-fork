from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from auo_project.models.doctor_model import DoctorBase


class DoctorRead(DoctorBase):
    id: UUID


class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
