from uuid import UUID

from sqlmodel import Field, UniqueConstraint

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class DoctorBase(BaseModel):
    org_id: UUID = Field(
        unique=False,
        index=True,
        nullable=False,
        foreign_key="app.auth_orgs.id",
    )
    employee_id: str = Field(
        max_length=128,
        unique=False,
        index=True,
        nullable=False,
    )
    name: str = Field(
        max_length=128,
        unique=False,
        index=True,
        nullable=False,
    )
    is_active: bool = Field(
        default=True,
        index=False,
        nullable=False,
    )


class Doctor(BaseUUIDModel, BaseTimestampModel, DoctorBase, table=True):
    __tablename__ = "doctors"
    __table_args__ = (
        UniqueConstraint(
            "org_id",
            "employee_id",
            name="doctors_org_id_employee_id_key",
        ),
        {"schema": "app"},
    )
