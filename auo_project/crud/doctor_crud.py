from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project.crud.base_crud import CRUDBase
from auo_project.models.doctor_model import Doctor
from auo_project.schemas.doctor_schema import DoctorCreate, DoctorUpdate


class CRUDDoctor(CRUDBase[Doctor, DoctorCreate, DoctorUpdate]):
    async def get_by_name(
        self,
        db_session: AsyncSession,
        org_id: UUID,
        name: str,
    ) -> Doctor:
        doctor = await db_session.execute(
            select(Doctor).where(
                Doctor.org_id == org_id,
                Doctor.name == name,
                Doctor.is_active == True,
            ),
        )
        return doctor.scalar.one()

    async def get_all_by_org_id(
        self,
        db_session: AsyncSession,
        org_id: UUID,
    ) -> list[Doctor]:
        doctors = await db_session.execute(
            select(Doctor).where(Doctor.org_id == org_id, Doctor.is_active == True),
        )
        return doctors.scalars().all()

    async def get_list_by_name(
        self,
        db_session: AsyncSession,
        org_id: UUID,
        name: str,
    ) -> list[Doctor]:
        doctors = await db_session.execute(
            select(Doctor).where(
                Doctor.org_id == org_id,
                Doctor.name == name,
                Doctor.is_active == True,
            ),
        )
        return doctors.scalars().all()

    def format_options(self, doctors: list[Doctor], add_all: bool) -> list[dict]:
        options = ([{"value": None, "label": "所有醫生"}] if add_all else []) + [
            {
                "value": doctor.id,
                "label": doctor.name,
            }
            for doctor in doctors
        ]

        return options


doctor = CRUDDoctor(Doctor)
