from typing import List
from uuid import UUID

from sqlmodel import ARRAY, INTEGER, Column, Field, Relationship

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class MeasureTongueBase(BaseModel):
    measure_id: UUID = Field(
        index=True,
        unique=True,
        nullable=False,
        foreign_key="measure.infos.id",
    )
    tongue_color: int = Field(None, title="舌色; 無:null/淡白:0/淡紅:1/紅:2/絳:3/青紫:4")
    tongue_shap: List[int] = Field(
        [],
        sa_column=Column(ARRAY(INTEGER)),
        title="舌形; 無:null/正常:0/老:1/嫩:2/胖大:3/瘦薄:4/點刺:5/裂紋:6/齒痕:7",
    )
    tongue_status1: List[int] = Field(
        [],
        sa_column=Column(ARRAY(INTEGER)),
        title="舌態; 無:null/正常:0/痿軟:1/強硬:2/歪斜:3/顫動:4/吐弄:5/短縮:6",
    )
    tongue_status2: int = Field(None, title="舌神; 無:null/榮舌:0/枯舌:1")
    tongue_coating_color: int = Field(None, title="苔色; 無:null/正常:0/白:1/黃:2/灰黑:3")
    tongue_coating_status: List[int] = Field(
        [],
        sa_column=Column(ARRAY(INTEGER)),
        title="苔質/舌苔; 無:null/正常:0/厚:1/薄:2/潤:3/燥:4/滑:5/糙:6/少:7/膩:8/腐:9/花剝:10/光剝:11",
    )
    tongue_coating_bottom: int = Field(None, title="舌下脈絡; 無:null/正常:0/怒張:1")
    up_img_uri: str = Field(default=None, nullable=True)
    down_img_uri: str = Field(default=None, nullable=True)
    up_img_cc_uri: str = Field(default=None, nullable=True)
    down_img_cc_uri: str = Field(default=None, nullable=True)
    class Config:
        arbitrary_types_allowed = True


class MeasureTongue(BaseUUIDModel, BaseTimestampModel, MeasureTongueBase, table=True):
    __tablename__ = "tongues"
    __table_args__ = {"schema": "measure"}
    measure_info: "MeasureInfo" = Relationship(
        back_populates="tongue",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
