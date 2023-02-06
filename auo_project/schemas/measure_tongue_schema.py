from typing import List
from uuid import UUID

from pydantic import BaseModel, Field
from sqlmodel import Field

from auo_project.models.measure_tongue_model import MeasureTongueBase


class MeasureTongueRead(MeasureTongueBase):
    id: UUID


class MeasureTongueCreate(MeasureTongueBase):
    pass


class MeasureTongueUpdate(BaseModel):
    tongue_color: int = Field(None, title="舌色; 無:null/淡白:0/淡紅:1/紅:2/絳:3/青紫:4")
    tongue_shap: List[int] = Field(
        [],
        title="舌形; 無:null/正常:0/老:1/嫩:2/胖大:3/瘦薄:4/點刺:5/裂紋:6/齒痕:7",
    )
    tongue_status1: List[int] = Field(
        [],
        title="舌態; 無:null/正常:0/痿軟:1/強硬:2/歪斜:3/顫動:4/吐弄:5/短縮:6",
    )
    tongue_status2: int = Field(None, title="舌神; 無:null/榮舌:0/枯舌:1")
    tongue_coating_color: int = Field(None, title="苔色; 無:null/正常:0/白:1/黃:2/灰黑:3")
    tongue_coating_status: List[int] = Field(
        [],
        title="苔質/舌苔; 無:null/正常:0/厚:1/薄:2/潤:3/燥:4/滑:5/糙:6/少:7/膩:8/腐:9/花剝:10/光剝:11",
    )
    tongue_coating_bottom: int = Field(None, title="舌下脈絡; 無:null/正常:0/怒張:1")
