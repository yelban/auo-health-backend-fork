from datetime import datetime
from typing import List

from sqlmodel import Field, Relationship

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class OrgBase(BaseModel):
    name: str = Field(
        max_length=64,
        unique=True,
        index=True,
        nullable=False,
    )
    description: str = Field(
        max_length=128,
        unique=False,
        index=False,
        nullable=False,
    )
    vatid: str = Field(
        max_length=20,
        unique=False,
        index=False,
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
    sales_name: str = Field(
        max_length=100,
        unique=False,
        index=False,
        nullable=False,
    )
    sales_email: str = Field(
        max_length=100,
        unique=False,
        index=False,
        nullable=False,
    )
    sales_phone: str = Field(
        max_length=20,
        unique=False,
        index=False,
        nullable=False,
    )
    valid_from: datetime = Field(
        unique=False,
        index=False,
        nullable=False,
    )
    valid_to: datetime = Field(
        unique=False,
        index=False,
        nullable=False,
    )
    is_active: bool = Field(
        default=True,
        unique=False,
        index=False,
        nullable=False,
    )


class Org(BaseUUIDModel, BaseTimestampModel, OrgBase, table=True):
    __tablename__ = "auth_orgs"
    __table_args__ = {"schema": "app"}
    users: List["User"] = Relationship(
        back_populates="org",
        sa_relationship_kwargs={"lazy": "select"},
    )
    measure_info: List["MeasureInfo"] = Relationship(
        back_populates="org",
        sa_relationship_kwargs={"lazy": "select"},
    )
    measure_survey: List["MeasureSurvey"] = Relationship(
        back_populates="org",
        sa_relationship_kwargs={"lazy": "select"},
    )
    measure_tongue_upload: List["MeasureTongueUpload"] = Relationship(
        back_populates="org",
        sa_relationship_kwargs={"lazy": "select"},
    )
    branches: List["Branch"] = Relationship(
        back_populates="org",
        sa_relationship_kwargs={"lazy": "select"},
    )
    user_branches: List["UserBranch"] = Relationship(
        back_populates="org",
        sa_relationship_kwargs={"lazy": "select"},
    )
