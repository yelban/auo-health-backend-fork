from typing import List
from uuid import UUID

import sqlalchemy as sa
from sqlmodel import ARRAY, AutoString, Column, Field, Relationship, UniqueConstraint

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class MeasureAdvancedTongue2Base(BaseModel):
    measure_id: UUID = Field(
        default=None,
        index=True,
        nullable=True,
        foreign_key="measure.tongue_uploads.id",
    )
    info_id: UUID = Field(
        default=None,
        index=True,
        nullable=True,
        foreign_key="measure.infos.id",
    )
    owner_id: UUID = Field(
        index=True,
        nullable=False,
        foreign_key="app.auth_users.id",
    )
    tongue_tip: List[str] = Field([], sa_column=Column(ARRAY(AutoString)), title="舌尖")
    tongue_tip_disease_map: dict = Field({}, sa_column=Column(sa.JSON), title="舌尖證型對應表")
    tongue_color: List[str] = Field([], sa_column=Column(ARRAY(AutoString)), title="舌色")
    tongue_color_disease_map: dict = Field(
        {},
        sa_column=Column(sa.JSON),
        title="舌色證型對應表",
    )
    tongue_shap: List[str] = Field(
        [],
        sa_column=Column(ARRAY(AutoString)),
        title="舌形",
    )
    tongue_shap_level_map: dict = Field({}, sa_column=Column(sa.JSON), title="舌形等級對應表")
    tongue_shap_disease_map: dict = Field(
        {},
        sa_column=Column(sa.JSON),
        title="舌形證型對應表",
    )
    tongue_status1: List[str] = Field(
        [],
        sa_column=Column(ARRAY(AutoString)),
        title="舌態",
    )
    tongue_status1_disease_map: dict = Field(
        {},
        sa_column=Column(sa.JSON),
        title="舌態證型對應表",
    )
    tongue_status2: List[str] = Field(
        [],
        sa_column=Column(ARRAY(AutoString)),
        title="舌神",
    )
    tongue_status2_level_map: dict = Field(
        {},
        sa_column=Column(sa.JSON),
        title="舌神等級對應表",
    )
    tongue_status2_disease_map: dict = Field(
        {},
        sa_column=Column(sa.JSON),
        title="舌神證型對應表",
    )
    tongue_coating_color: List[str] = Field(
        [],
        sa_column=Column(ARRAY(AutoString)),
        title="苔色",
    )
    tongue_coating_color_level_map: dict = Field(
        {},
        sa_column=Column(sa.JSON),
        title="苔色等級對應表",
    )
    tongue_coating_color_disease_map: dict = Field(
        {},
        sa_column=Column(sa.JSON),
        title="苔色證型對應表",
    )
    tongue_coating_status: List[str] = Field(
        [],
        sa_column=Column(ARRAY(AutoString)),
        title="苔質",
    )
    tongue_coating_status_level_map: dict = Field(
        {},
        sa_column=Column(sa.JSON),
        title="苔質等級對應表",
    )
    tongue_coating_status_disease_map: dict = Field(
        {},
        sa_column=Column(sa.JSON),
        title="苔質證型對應表",
    )
    tongue_coating_bottom: List[str] = Field(
        [],
        sa_column=Column(ARRAY(AutoString)),
        title="舌下脈絡",
    )
    tongue_coating_bottom_level_map: dict = Field(
        {},
        sa_column=Column(sa.JSON),
        title="舌下脈絡等級對應表",
    )
    tongue_coating_bottom_disease_map: dict = Field(
        {},
        sa_column=Column(sa.JSON),
        title="舌下脈絡證型對應表",
    )
    tongue_summary: str = Field(default=None, nullable=True, title="舌象概要")
    tongue_memo: str = Field(default=None, nullable=True, title="檢測標記")
    has_tongue_label: bool = Field(default=False, nullable=True, title="是否有舌象標記")

    class Config:
        arbitrary_types_allowed = True


class MeasureAdvancedTongue2(
    BaseUUIDModel,
    BaseTimestampModel,
    MeasureAdvancedTongue2Base,
    table=True,
):
    __tablename__ = "advanced_tongues2"
    __table_args__ = (
        UniqueConstraint(
            "measure_id",
            "owner_id",
            name="advanced_tongues_measure_id_owner_id_key",
        ),
        {"schema": "measure"},
    )

    tongue_upload: "MeasureTongueUpload" = Relationship(
        back_populates="advanced_tongue2",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    measure_info: "MeasureInfo" = Relationship(
        back_populates="advanced_tongue2",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
