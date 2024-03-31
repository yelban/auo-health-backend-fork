from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, validator
from sqlmodel import Field

from auo_project.models.measure_advanced_tongue2_model import MeasureAdvancedTongue2Base


class MeasureAdvancedTongue2Read(MeasureAdvancedTongue2Base):
    id: UUID


class MeasureAdvancedTongue2Create(MeasureAdvancedTongue2Base):
    pass


class MeasureAdvancedTongue2UpdateInput(BaseModel):
    tongue_tip: List[str] = Field([], title="舌尖")
    tongue_tip_disease_map: dict = Field({}, title="舌尖證型對應表")
    tongue_color: List[str] = Field([], title="舌色")
    tongue_color_disease_map: dict = Field({}, title="舌色證型對應表")
    tongue_shap: List[str] = Field(
        [],
        title="舌形",
    )
    tongue_shap_level_map: dict = Field({}, title="舌形等級對應表")
    tongue_shap_disease_map: dict = Field({}, title="舌形證型對應表")
    tongue_status1: List[str] = Field(
        [],
        title="舌態",
    )
    tongue_status1_disease_map: dict = Field({}, title="舌態證型對應表")
    tongue_status2: List[str] = Field([], title="舌神")
    tongue_status2_level_map: dict = Field({}, title="舌神等級對應表")
    tongue_status2_disease_map: dict = Field({}, title="舌神證型對應表")
    tongue_coating_color: List[str] = Field(
        [],
        title="苔色",
    )
    tongue_coating_color_level_map: dict = Field({}, title="苔色等級對應表")
    tongue_coating_color_disease_map: dict = Field({}, title="苔色證型對應表")
    tongue_coating_status: List[str] = Field(
        [],
        title="苔質",
    )
    tongue_coating_status_level_map: dict = Field({}, title="苔質等級對應表")
    tongue_coating_status_disease_map: dict = Field({}, title="苔質證型對應表")
    tongue_coating_bottom: List[str] = Field(
        [],
        title="舌下脈絡",
    )
    tongue_coating_bottom_level_map: dict = Field({}, title="舌下脈絡等級對應表")
    tongue_coating_bottom_disease_map: dict = Field({}, title="舌下脈絡證型對應表")
    tongue_summary: str = Field(default=None, nullable=True, title="舌象概要")

    @validator(
        "tongue_tip",
        "tongue_color",
        "tongue_shap",
        "tongue_status1",
        "tongue_status2",
        "tongue_coating_color",
        "tongue_coating_status",
        "tongue_coating_bottom",
        pre=True,
    )
    def unique_item(cls, v):
        if isinstance(v, list):
            return list(map(lambda x: x, set(v)))
        return v


class MeasureAdvancedTongue2Update(MeasureAdvancedTongue2UpdateInput):
    tongue_memo: str = Field(default=None, title="舌象標記")
    has_tongue_label: bool = Field(
        default=False,
        nullable=True,
        exclude=True,
        title="是否有舌象標記",
    )
