from datetime import datetime
from uuid import UUID

from sqlmodel import Field, Relationship

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class BranchFieldBase(BaseModel):
    branch_id: UUID = Field(
        index=True,
        nullable=False,
        foreign_key="app.auth_branches.id",
    )
    name: str = Field(
        max_length=64,
        unique=True,
        index=True,
        nullable=False,
    )
    address: str = Field(
        max_length=200,
        unique=False,
        index=False,
        nullable=False,
    )
    city: str = Field(
        max_length=100,
        unique=False,
        index=False,
        nullable=False,
    )
    state: str = Field(
        max_length=100,
        unique=False,
        index=False,
        nullable=False,
    )
    country: str = Field(
        max_length=100,
        unique=False,
        index=False,
        nullable=False,
    )
    zip_code: str = Field(
        max_length=20,
        unique=False,
        index=False,
        nullable=False,
    )
    contact_name: str = Field(
        max_length=100,
        unique=False,
        index=False,
        nullable=False,
    )
    contact_email: str = Field(
        max_length=100,
        unique=False,
        index=False,
        nullable=False,
    )
    contact_phone: str = Field(
        max_length=20,
        unique=False,
        index=False,
        nullable=False,
    )
    valid_from: datetime = Field(
        nullable=False,
    )
    valid_to: datetime = Field(
        nullable=False,
    )
    is_active: bool = Field(
        default=True,
        nullable=False,
    )


class BranchField(BaseUUIDModel, BaseTimestampModel, BranchFieldBase, table=True):
    __tablename__ = "fields"
    __table_args__ = {"schema": "app"}
    branch: "Branch" = Relationship(
        back_populates="fields",
        sa_relationship_kwargs={"lazy": "select"},
    )
    tongue_cc_config: "TongueCCConfig" = Relationship(
        back_populates="field",
        sa_relationship_kwargs={"lazy": "select", "uselist": False},
    )
