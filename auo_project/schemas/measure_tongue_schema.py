from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field
from sqlmodel import Field

from auo_project.models.measure_tongue_model import MeasureTongueBase
from auo_project.schemas.common_schema import Link
from auo_project.schemas.subject_schema import SubjectRead, SubjectSecretRead


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


class TongueMeasure(BaseModel):
    id: UUID
    measure_time: str
    tongue: Dict[str, Any]


class TongueItem(BaseModel):
    subject: Union[SubjectRead, SubjectSecretRead]
    measure: TongueMeasure


class TongueListPage(BaseModel):
    page: int
    per_page: int
    page_count: int
    total_count: int
    link: Link
    items: List[TongueItem] = Field(
        default=[],
        title="舌象紀錄",
    )


class TongueListOutput(BaseModel):
    measure_times: List[dict]
    tongue: TongueListPage


class Disease(BaseModel):
    """證型"""

    value: Union[str, UUID]
    label: str
    selected: bool = False


class LevelOption(BaseModel):
    value: int
    label: str
    selected: bool = False


class ComponentChild(BaseModel):
    id: Union[str, UUID] = Field(None, title="症狀/特徵流水號")
    symptom_id: str = Field(None, title="症狀/特徵易讀編號")
    symptom_name: str = Field(None, title="症狀/特徵名稱")
    symptom_description: str = Field(None, title="症狀/特徵描述")
    level_options: List[LevelOption] = Field([], title="程度選項：輕/中/重")
    # is_default: bool = Field(False, title="是否為預設值")
    is_normal: bool = Field(
        False,
        title="是否為正常，若為正常需把 item 底下正常以外選項清空",
    )
    selected: bool = Field(False, title="是否選擇")
    diseases: List[Disease] = Field([], title="證型列表")


class Component(BaseModel):
    item_id: str
    component_id: str
    component_type: str = Field("radio", title="UI 元件類型")
    children: List[ComponentChild]


class SymptomItem(BaseModel):
    """症狀/特徵"""

    item_id: str
    item_name: str
    symptoms: List[Component]


class TongueSampleImage(BaseModel):
    front: str = None
    back: str = None


class TongueSampleMeasure(BaseModel):
    image: TongueSampleImage = Field(None, title="舌象圖片")
    measure_time: str = Field(None, title="拍攝時間")
    symptom: List[SymptomItem] = Field([], title="症狀/特徵列表")
    summary: str = Field(None, title="舌象概要")
    memo: str = Field(None, title="檢測標記")
    age: Optional[int] = Field(None, title="受測時年齡")
    measure_operator: Optional[str] = Field(None, title="檢測人員")


class AdvancedTongueOutput(BaseModel):
    subject: Union[SubjectRead, SubjectSecretRead]
    measure_tongue: TongueSampleMeasure


class TongueConfigUploadResponse(BaseModel):
    msg: str = Field(title="訊息")
    upload_id: UUID = Field(title="上傳 ID")
    color_hash: str = Field(title="校色 pickle 檔 SHA256")
