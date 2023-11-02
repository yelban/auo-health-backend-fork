from typing import List
from uuid import UUID

import sqlalchemy as sa
from sqlmodel import ARRAY, INTEGER, Column, Field, UniqueConstraint

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class MeasureAdvancedTongueBase(BaseModel):
    measure_id: UUID = Field(
        index=True,
        nullable=False,
        foreign_key="measure.infos.id",
    )
    owner_id: UUID = Field(
        index=True,
        nullable=False,
        foreign_key="app.auth_users.id",
    )
    tongue_tip: List[int] = Field([], sa_column=Column(ARRAY(INTEGER)), title="舌尖; 紅:1")
    tongue_color: int = Field(None, title="舌色; 無:null/淡白:0/淡紅:1/紅:2/絳:3/青紫:4")
    tongue_shap: List[int] = Field(
        [],
        sa_column=Column(ARRAY(INTEGER)),
        title="舌形; 正常:0/老:1/嫩:2/胖大:3/瘦薄:4/點刺:5/裂紋:6/齒痕:7/瘀點:8/瘀斑:9/朱點:10",
    )
    tongue_shap_level_map: dict = Field({}, sa_column=Column(sa.JSON), title="舌形等級對應表")
    tongue_status1: List[int] = Field(
        [],
        sa_column=Column(ARRAY(INTEGER)),
        title="舌態; 無:null/正常:0/歪斜:3/萎軟:1/顫動:4/吐弄:5/短縮:6/強硬:2",
    )
    tongue_status2: int = Field(None, title="舌神; 無:null/榮舌:0/枯舌:1")
    tongue_status2_level_map: dict = Field(
        {},
        sa_column=Column(sa.JSON),
        title="舌神等級對應表",
    )
    tongue_coating_color: List[int] = Field(
        [],
        sa_column=Column(ARRAY(INTEGER)),
        title="苔色; 無:null/正常:0/白:1/黃:2/灰:3/黑:4/染苔:5",
    )
    tongue_coating_color_level_map: dict = Field(
        {},
        sa_column=Column(sa.JSON),
        title="苔色等級對應表",
    )
    tongue_coating_status: List[int] = Field(
        [],
        sa_column=Column(ARRAY(INTEGER)),
        title="苔質; 無:-1/正常:0/厚:1/薄:2/潤:3/燥:4/滑:5/糙:6/少:7/膩:8/腐:9/花剝:10/光剝:11",
    )
    tongue_coating_status_level_map: dict = Field(
        {},
        sa_column=Column(sa.JSON),
        title="苔質等級對應表",
    )
    tongue_coating_bottom: List[int] = Field(
        [],
        sa_column=Column(ARRAY(INTEGER)),
        title="舌下脈絡; 無:null/正常:0/怒張:1/血管超過舌長3/5:2/青紫絲:3/瘀斑:4/囊泡:5/囊柱:6/分枝:7",
    )
    tongue_coating_bottom_level_map: dict = Field(
        {},
        sa_column=Column(sa.JSON),
        title="舌下脈絡等級對應表",
    )
    tongue_memo: str = Field(default=None, nullable=True, title="特殊註記")
    has_tongue_label: bool = Field(default=False, nullable=True, title="是否有舌象標記")

    class Config:
        arbitrary_types_allowed = True


class MeasureAdvancedTongue(
    BaseUUIDModel,
    BaseTimestampModel,
    MeasureAdvancedTongueBase,
    table=True,
):
    __tablename__ = "advanced_tongues"
    __table_args__ = (
        UniqueConstraint(
            "measure_id",
            "owner_id",
            name="advanced_tongues_measure_id_owner_id_key",
        ),
        {"schema": "measure"},
    )
