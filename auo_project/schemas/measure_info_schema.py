from datetime import datetime
from enum import IntEnum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator

from auo_project.models.measure_info_model import MeasureInfoBase
from auo_project.schemas.subject_schema import SubjectRead


class SideType(IntEnum):
    """
    左 left = 0
    右 right = 1
    """

    left = 0
    right = 1


class IrregularHRType(IntEnum):
    """
    止無定數 = 0
    止有定數 = 1
    """

    unfixed = 0
    fixed = 1


class IrregularHR(BaseModel):
    side: SideType = Field(title="左右手; 左:0/右:1")
    type: IrregularHRType = Field(title="異常狀態; 止無定數:0/止有定數:1")


class TongueInfo(BaseModel):
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


class TongueImage(BaseModel):
    front: Any = Field(None, title="舌面")
    back: Any = Field(None, title="舌背")


class Tongue(BaseModel):
    exist: bool = Field(False, title="是否有舌象資訊")
    info: TongueInfo = Field({}, title="舌象資訊")
    image: TongueImage = Field({}, title="舌頭圖片")


class BCQ(BaseModel):
    exist: bool = Field(False, title="是否有 BCQ 結果")
    yang_state_spec: Dict[str, Any] = Field(
        {"good": [0, 13], "fair": [14, 29], "serious": [30, 100]},
        title="嚴重程度; 良好 good 0-13/普通 fair 14-29/嚴重 serious 30-100",
    )
    yin_state_spec: Dict[str, Any] = Field(
        {"good": [0, 13], "fair": [14, 29], "serious": [30, 100]},
        title="嚴重程度; 良好 good 0-13/普通 fair 14-29/嚴重 serious 30-100",
    )
    phlegm_state_spec: Dict[str, Any] = Field(
        {"good": [0, 16], "fair": [17, 29], "serious": [30, 100]},
        title="嚴重程度; 良好 good 0-16/普通 fair 17-29/嚴重 serious 30-100",
    )
    yang_second_state_spec: Dict[str, Any] = Field(
        {"good": [0, 100], "fair": [101, 102], "serious": [103, 104]},
        title="嚴重程度; 未定義",
    )
    yin_second_state_spec: Dict[str, Any] = Field(
        {"good": [0, 100], "fair": [101, 102], "serious": [103, 104]},
        title="嚴重程度; 未定義",
    )
    phlegm_second_state_spec: Dict[str, Any] = Field(
        {"good": [0, 100], "fair": [101, 102], "serious": [103, 104]},
        title="嚴重程度; 未定義",
    )
    score_yang: int = Field(None, title="總分-陽(int)")
    score_yin: int = Field(None, title="總分-陰(int)")
    score_phlegm: int = Field(None, title="總分-痰瘀(int)")
    score_yang_head: int = Field(None, title="總分-陽-頭部(int)")
    score_yang_chest: int = Field(None, title="總分-陽-胸部(int)")
    score_yang_limbs: int = Field(None, title="總分-陽-四肢(int)")
    score_yang_abdomen: int = Field(None, title="總分-陽-腹腔(int)")
    score_yang_surface: int = Field(None, title="總分-陽-體表(int)")
    score_yin_head: int = Field(None, title="總分-陰-頭部(int)")
    score_yin_limbs: int = Field(None, title="總分-陰-四肢(int)")
    score_yin_gt: int = Field(None, title="總分-陰-腸胃道(int)")
    score_yin_surface: int = Field(None, title="總分-陰-體表(int)")
    score_yin_abdomen: int = Field(None, title="總分-陰-腹腔(int)")
    score_phlegm_trunk: int = Field(None, title="總分-痰瘀-軀幹(int)")
    score_phlegm_surface: int = Field(None, title="總分-痰瘀-體表(int)")
    score_phlegm_head: int = Field(None, title="總分-痰瘀-頭部(int)")
    score_phlegm_gt: int = Field(None, title="總分-痰瘀-腸胃道(int)")
    percentage_yang: int = Field(None, title="百分比-陽(int)")
    percentage_yin: int = Field(None, title="百分比-陰(int)")
    percentage_phlegm: int = Field(None, title="百分比-痰瘀(int)")
    percentage_yang_head: int = Field(None, title="百分比-陽-頭部(int)")
    percentage_yang_chest: int = Field(None, title="百分比-陽-胸部(int)")
    percentage_yang_limbs: int = Field(None, title="百分比-陽-四肢(int)")
    percentage_yang_abdomen: int = Field(None, title="百分比-陽-腹腔(int)")
    percentage_yang_surface: int = Field(None, title="百分比-陽-體表(int)")
    percentage_yin_head: int = Field(None, title="百分比-陰-頭部(int)")
    percentage_yin_limbs: int = Field(None, title="百分比-陰-四肢(int)")
    percentage_yin_gt: int = Field(None, title="百分比-陰-腸胃道(int)")
    percentage_yin_surface: int = Field(None, title="百分比-陰-體表(int)")
    percentage_yin_abdomen: int = Field(None, title="百分比-陰-腹腔(int)")
    percentage_phlegm_trunk: int = Field(None, title="百分比-痰瘀-軀幹(int)")
    percentage_phlegm_surface: int = Field(None, title="百分比-痰瘀-體表(int)")
    percentage_phlegm_head: int = Field(None, title="百分比-痰瘀-頭部(int)")
    percentage_phlegm_gt: int = Field(None, title="百分比-痰瘀-腸胃道(int)")


class MeasureInfoCreate(MeasureInfoBase):
    pass


class MeasureInfoCreateFromFile(MeasureInfoBase):
    subject_id: Optional[UUID] = None
    file_id: Optional[UUID] = None
    bmi: Optional[float] = None
    irregular_hr: Optional[float] = None

    @validator("measure_time", pre=True)
    def parse_measure_time(cls, v):
        if isinstance(v, str):
            dt = datetime.strptime(v, "%Y/%m/%d\u3000%H:%M")
            return dt
        return v

    @validator("judge_time", pre=True)
    def parse_judge_time(cls, v):
        if isinstance(v, str):
            dt = datetime.strptime(v, "%Y/%m/%d\u3000%H:%M")
            return dt
        return v

    @validator("irregular_hr", always=True)
    def check_irregular_hr(cls, _, values):
        check_list = (
            "irregular_hr_l_cu",
            "irregular_hr_l_qu",
            "irregular_hr_l_ch",
            "irregular_hr_r_cu",
            "irregular_hr_r_qu",
            "irregular_hr_r_ch",
        )
        return any([values.get(field) for field in check_list])

    @validator("bmi", always=True)
    def cal_bmi(cls, _, values):
        if values["height"] and values["weight"]:
            return values["weight"] / (values["height"] / 100) ** 2


class MeasureInfoReadByList(BaseModel):
    id: UUID = Field(default=None, title="檢測編號")
    measure_time: datetime = Field(default=None, title="檢測時間")
    measure_operator: str = Field(
        default=None,
        max_length=128,
        nullable=True,
        title="檢測人員名稱",
    )
    # TODO: 檢測單位 is org_name?
    org_name: str = Field(default=None, title="檢測單位")
    irregular_hr: int = Field(default=None, nullable=True, title="節律標記")
    proj_num: str = Field(default=None, title="計畫編號")  # from report.txt
    memo: str = Field(default=None, title="檢測標記")
    has_memo: bool = Field(default=False, title="是否有檢測標記")
    age: int = Field(default=None, title="年齡")
    bcq: bool = Field(default=None, title="BCQ檢測")
    bmi: float = Field(default=None, title="BMI")
    is_standard_measure: bool = Field(default=False, title="是否為基準值")

    @validator("bmi", always=True)
    def round_bmi(cls, v):
        if v:
            return round(v, 1)
        return v


class MeasureInDB(MeasureInfoBase):
    irregular_hr: bool = Field(
        title="有任一個 true 就是異常：irregular_hr_l_cu, irregular_hr_l_qu, irregular_hr_l_ch, irregular_hr_r_cu, irregular_hr_r_qu, irregular_hr_r_ch",
    )


class MeasureInfoRead(MeasureInfoBase):
    pass


class SimpleMeasureInfo(BaseModel):
    id: UUID
    measure_time: datetime
    measure_operator: str


class MeasureInfoUpdate(BaseModel):
    irregular_hr_type_l: int = Field(
        default=None,
        title="左手節律異常類型; 無:null/止無定數:0/止有定數:1",
    )
    irregular_hr_type_r: int = Field(
        default=None,
        title="右手節律異常類型; 無:null/止無定數:0/止有定數:1",
    )
    memo: str = Field(default=None, max_length=1024, title="檢測標記")
    has_memo: bool = Field(default=None, title="是否有檢測標記")
    has_bcq: bool = Field(default=None, title="是否有BCQ檢測")
    comment: str = Field(
        default=None,
        max_length=1024,
        title="診斷內容",
    )


# TODO: 討論預設值
class MeasureDetailRead(BaseModel):
    org_name: str = Field(default=None, title="檢測單位")  # TODO
    measure_time: datetime = Field(default=None, title="檢測時間")
    measure_operator: str = Field(
        default=None,
        max_length=128,
        nullable=True,
        title="檢測人員名稱",
    )
    proj_num: str = Field(default=None, title="計畫編號")  # from report.txt
    sbp: int = Field(None, title="收縮壓")
    dbp: int = Field(None, title="舒張壓")
    memo: str = Field(None, title="檢測標記")
    age: int = Field(None, title="年齡")
    height: float = Field(None, title="身高")
    weight: float = Field(None, title="體重")
    bmi: float = Field(None, title="BMI")
    irregular_hr_l: int = Field(None, title="左手節律是否異常; 正常:0/異常:1")
    irregular_hr_type_l: int = Field(None, title="左手節律異常類型; 無:null/止無定數:0/止有定數:1")
    irregular_hr_r: int = Field(None, title="右手節律是否異常; 正常:0/異常:1")
    irregular_hr_type_r: int = Field(None, title="右手節律異常類型; 無:null/止無定數:0/止有定數:1")
    hr_l: int = Field(None, title="左手脈率數值")
    hr_l_type: int = Field(None, title="左手脈率類型; 無:null/遲:0/正常:1/數:2")  # TODO 確認遲/正常/數區間
    hr_r: int = Field(None, title="右手脈率數值")
    hr_r_type: int = Field(None, title="右手脈率類型; 無:null/遲:0/正常:1/數:2")  # TODO 確認遲/正常/數區間
    # infos_analyze
    mean_prop_range_1_l_cu: float = Field(None, title="左寸浮振幅平均值佔比")
    mean_prop_range_2_l_cu: float = Field(None, title="左寸中振幅平均值佔比")
    mean_prop_range_3_l_cu: float = Field(None, title="左寸沉振幅平均值佔比")
    mean_prop_range_1_l_qu: float = Field(None, title="左關浮振幅平均值佔比")
    mean_prop_range_2_l_qu: float = Field(None, title="左關中振幅平均值佔比")
    mean_prop_range_3_l_qu: float = Field(None, title="左關沉振幅平均值佔比")
    mean_prop_range_1_l_ch: float = Field(None, title="左尺浮振幅平均值佔比")
    mean_prop_range_2_l_ch: float = Field(None, title="左尺中振幅平均值佔比")
    mean_prop_range_3_l_ch: float = Field(None, title="左尺沉振幅平均值佔比")
    mean_prop_range_1_r_cu: float = Field(None, title="右寸浮振幅平均值佔比")
    mean_prop_range_2_r_cu: float = Field(None, title="右寸中振幅平均值佔比")
    mean_prop_range_3_r_cu: float = Field(None, title="右寸沉振幅平均值佔比")
    mean_prop_range_1_r_qu: float = Field(None, title="右關浮振幅平均值佔比")
    mean_prop_range_2_r_qu: float = Field(None, title="右關中振幅平均值佔比")
    mean_prop_range_3_r_qu: float = Field(None, title="右關沉振幅平均值佔比")
    mean_prop_range_1_r_ch: float = Field(None, title="右尺浮振幅平均值佔比")
    mean_prop_range_2_r_ch: float = Field(None, title="右尺中振幅平均值佔比")
    mean_prop_range_3_r_ch: float = Field(None, title="右尺沉振幅平均值佔比")

    mean_prop_range_max_l_cu: int = Field(None, title="左寸浮沉振幅平均佔比最大值區塊; 浮:0/中:1/沉:2")
    mean_prop_range_max_l_qu: int = Field(None, title="左關浮沉振幅平均佔比最大值區塊; 浮:0/中:1/沉:2")
    mean_prop_range_max_l_ch: int = Field(None, title="左尺浮沉振幅平均佔比最大值區塊; 浮:0/中:1/沉:2")
    mean_prop_range_max_r_cu: int = Field(None, title="右寸浮沉振幅平均佔比最大值區塊; 浮:0/中:1/沉:2")
    mean_prop_range_max_r_qu: int = Field(None, title="右關浮沉振幅平均佔比最大值區塊; 浮:0/中:1/沉:2")
    mean_prop_range_max_r_ch: int = Field(None, title="右尺浮沉振幅平均佔比最大值區塊; 浮:0/中:1/沉:2")

    # infos_analyze
    # TODO: check 最大值落點怎麼算：是不是看 max_amp_depth_L_qu 落在哪一區 range_start_index_L_qu/range_1_3_index_L_qu/range_2_3_index_L_qu/range_end_index_L_qu::
    max_amp_depth_of_range_l_cu: int = Field(None, title="左寸浮沉振幅最大值落點區塊; 浮:0/中:1/沉:2")
    max_amp_depth_of_range_l_qu: int = Field(None, title="左關浮沉振幅最大值落點區塊; 浮:0/中:1/沉:2")
    max_amp_depth_of_range_l_ch: int = Field(None, title="左尺浮沉振幅最大值落點區塊; 浮:0/中:1/沉:2")
    max_amp_depth_of_range_r_cu: int = Field(None, title="右寸浮沉振幅最大值落點區塊; 浮:0/中:1/沉:2")
    max_amp_depth_of_range_r_qu: int = Field(None, title="右關浮沉振幅最大值落點區塊; 浮:0/中:1/沉:2")
    max_amp_depth_of_range_r_ch: int = Field(None, title="右尺浮沉振幅最大值落點區塊; 浮:0/中:1/沉:2")

    # infos_analyze
    max_amp_value_l_cu: float = Field(None, title="左寸-有效範圍內最大振幅值")
    max_amp_value_l_qu: float = Field(None, title="左關-有效範圍內最大振幅值")
    max_amp_value_l_ch: float = Field(None, title="左尺-有效範圍內最大振幅值")
    max_amp_value_r_cu: float = Field(None, title="右寸-有效範圍內最大振幅值")
    max_amp_value_r_qu: float = Field(None, title="右關-有效範圍內最大振幅值")
    max_amp_value_r_ch: float = Field(None, title="右尺-有效範圍內最大振幅值")

    # analyze_raw
    max_slope_value_l_cu: float = Field(None, title="左寸斜率最大值")
    max_slope_value_l_qu: float = Field(None, title="左關斜率最大值")
    max_slope_value_l_ch: float = Field(None, title="左尺斜率最大值")
    max_slope_value_r_cu: float = Field(None, title="右寸斜率最大值")
    max_slope_value_r_qu: float = Field(None, title="右關斜率最大值")
    max_slope_value_r_ch: float = Field(None, title="右尺斜率最大值")

    # report / info
    strength_l_cu: int = Field(None, title="左寸力量; 無:null/無力:0/正常:1/有力:2")
    strength_l_qu: int = Field(None, title="左關力量; 無:null/無力:0/正常:1/有力:2")
    strength_l_ch: int = Field(None, title="左尺力量; 無:null/無力:0/正常:1/有力:2")
    strength_r_cu: int = Field(None, title="右寸力量; 無:null/無力:0/正常:1/有力:2")
    strength_r_qu: int = Field(None, title="右關力量; 無:null/無力:0/正常:1/有力:2")
    strength_r_ch: int = Field(None, title="右尺力量; 無:null/無力:0/正常:1/有力:2")

    # report / info
    width_l_cu: int = Field(None, title="左寸虛實; 無:null/虛:0/正常:1/實:2")
    width_l_qu: int = Field(None, title="左關虛實; 無:null/虛:0/正常:1/實:2")
    width_l_ch: int = Field(None, title="左尺虛實; 無:null/虛:0/正常:1/實:2")
    width_r_cu: int = Field(None, title="右寸虛實; 無:null/虛:0/正常:1/實:2")
    width_r_qu: int = Field(None, title="右關虛實; 無:null/虛:0/正常:1/實:2")
    width_r_ch: int = Field(None, title="右尺虛實; 無:null/虛:0/正常:1/實:2")

    width_value_l_cu: float = Field(None, title="左寸虛實值(時間，單位為秒)")
    width_value_l_qu: float = Field(None, title="左關虛實值(時間，單位為秒)")
    width_value_l_ch: float = Field(None, title="左尺虛實值(時間，單位為秒)")
    width_value_r_cu: float = Field(None, title="右寸虛實值(時間，單位為秒)")
    width_value_r_qu: float = Field(None, title="右關虛實值(時間，單位為秒)")
    width_value_r_ch: float = Field(None, title="右尺虛實值(時間，單位為秒)")

    # tongue
    tongue: Tongue = Field({}, title="舌象資訊與圖片")

    ### bcq.txt
    bcq: BCQ = Field({}, title="BCQ 資訊")

    # 檢測紀錄
    comment: str = Field(None, title="檢測紀錄評論")
    # 全段脈波
    all_sec: Dict[str, Any] = Field({}, title="全段脈波")
    # CN
    cn: Dict[str, Any] = Field({}, title="CN: C1-C11; 如果 standard_value 為空畫面不可選")
    cn_state_spec: Dict[str, Any] = Field(
        {
            "pos": {"good": [0, 49], "fair": [50, 69], "serious": [70]},
            "neg": {"good": [-14, -1], "fair": [-69, -15], "serious": [-70]},
        },
        title="嚴重程度; 類型分成正值 pos 和負值 neg，狀態良好 good, fair 數值區間皆為左右包含; serious 正值為大於等於，負值為小於等於",
    )


class MultiMeasureDetailRead(BaseModel):
    id: UUID = Field(default=None, title="檢測編號")
    tn: str = Field(default=None, title="T1-T20")
    measure_time: datetime = Field(default=None, title="檢測時間")
    hr_l: int = Field(None, title="左手脈率數值")
    hr_l_type: int = Field(None, title="左手脈率類型; 無:null/遲:0/正常:1/數:2")  # TODO 確認遲/正常/數區間
    hr_r: int = Field(None, title="右手脈率數值")
    hr_r_type: int = Field(None, title="右手脈率類型; 無:null/遲:0/正常:1/數:2")  # TODO 確認遲/正常/數區間

    # TODO: check
    mean_prop_range_max_l_cu: int = Field(None, title="左寸浮沉振幅平均佔比最大值區塊; 浮:0/中:1/沉:2")
    mean_prop_range_max_l_qu: int = Field(None, title="左關浮沉振幅平均佔比最大值區塊; 浮:0/中:1/沉:2")
    mean_prop_range_max_l_ch: int = Field(None, title="左尺浮沉振幅平均佔比最大值區塊; 浮:0/中:1/沉:2")
    mean_prop_range_max_r_cu: int = Field(None, title="右寸浮沉振幅平均佔比最大值區塊; 浮:0/中:1/沉:2")
    mean_prop_range_max_r_qu: int = Field(None, title="右關浮沉振幅平均佔比最大值區塊; 浮:0/中:1/沉:2")
    mean_prop_range_max_r_ch: int = Field(None, title="右尺浮沉振幅平均佔比最大值區塊; 浮:0/中:1/沉:2")

    # TODO: check

    # TODO: check 最大值落點怎麼算：是不是看 max_amp_depth_L_qu 落在哪一區 range_start_index_L_qu/range_1_3_index_L_qu/range_2_3_index_L_qu/range_end_index_L_qu::
    max_amp_depth_of_range_l_cu: int = Field(None, title="左寸浮沉振幅最大值落點區塊; 浮:0/中:1/沉:2")
    max_amp_depth_of_range_l_qu: int = Field(None, title="左關浮沉振幅最大值落點區塊; 浮:0/中:1/沉:2")
    max_amp_depth_of_range_l_ch: int = Field(None, title="左尺浮沉振幅最大值落點區塊; 浮:0/中:1/沉:2")
    max_amp_depth_of_range_r_cu: int = Field(None, title="右寸浮沉振幅最大值落點區塊; 浮:0/中:1/沉:2")
    max_amp_depth_of_range_r_qu: int = Field(None, title="右關浮沉振幅最大值落點區塊; 浮:0/中:1/沉:2")
    max_amp_depth_of_range_r_ch: int = Field(None, title="右尺浮沉振幅最大值落點區塊; 浮:0/中:1/沉:2")

    # TODO: check
    max_amp_value_l_cu: float = Field(None, title="左寸-有效範圍內最大振幅值")
    max_amp_value_l_qu: float = Field(None, title="左關-有效範圍內最大振幅值")
    max_amp_value_l_ch: float = Field(None, title="左尺-有效範圍內最大振幅值")
    max_amp_value_r_cu: float = Field(None, title="右寸-有效範圍內最大振幅值")
    max_amp_value_r_qu: float = Field(None, title="右關-有效範圍內最大振幅值")
    max_amp_value_r_ch: float = Field(None, title="右尺-有效範圍內最大振幅值")

    # TODO: check
    max_slope_value_l_cu: float = Field(None, title="左寸斜率最大值")
    max_slope_value_l_qu: float = Field(None, title="左關斜率最大值")
    max_slope_value_l_ch: float = Field(None, title="左尺斜率最大值")
    max_slope_value_r_cu: float = Field(None, title="右寸斜率最大值")
    max_slope_value_r_qu: float = Field(None, title="右關斜率最大值")
    max_slope_value_r_ch: float = Field(None, title="右尺斜率最大值")

    # TODO 行程
    xingcheng_l_cu: float = Field(None, title="左寸行程")
    xingcheng_l_qu: float = Field(None, title="左關行程")
    xingcheng_l_ch: float = Field(None, title="左尺行程")
    xingcheng_r_cu: float = Field(None, title="右寸行程")
    xingcheng_r_qu: float = Field(None, title="右關行程")
    xingcheng_r_ch: float = Field(None, title="右尺行程")

    # statistics
    h1_l_cu: float = Field(None, title="左寸 h1")
    h1_l_qu: float = Field(None, title="左關 h1")
    h1_l_ch: float = Field(None, title="左尺 h1")
    h1_r_cu: float = Field(None, title="右寸 h1")
    h1_r_qu: float = Field(None, title="右關 h1")
    h1_r_ch: float = Field(None, title="右尺 h1")

    h1_div_t1_l_cu: float = Field(None, title="左寸 h1/t1")
    h1_div_t1_l_qu: float = Field(None, title="左關 h1/t1")
    h1_div_t1_l_ch: float = Field(None, title="左尺 h1/t1")
    h1_div_t1_r_cu: float = Field(None, title="右寸 h1/t1")
    h1_div_t1_r_qu: float = Field(None, title="右關 h1/t1")
    h1_div_t1_r_ch: float = Field(None, title="右尺 h1/t1")

    pr_l_cu: float = Field(None, title="左寸 pr")
    pr_l_qu: float = Field(None, title="左關 pr")
    pr_l_ch: float = Field(None, title="左尺 pr")
    pr_r_cu: float = Field(None, title="右寸 pr")
    pr_r_qu: float = Field(None, title="右關 pr")
    pr_r_ch: float = Field(None, title="右尺 pr")

    w1_l_cu: float = Field(None, title="左寸 w1")
    w1_l_qu: float = Field(None, title="左關 w1")
    w1_l_ch: float = Field(None, title="左尺 w1")
    w1_r_cu: float = Field(None, title="右寸 w1")
    w1_r_qu: float = Field(None, title="右關 w1")
    w1_r_ch: float = Field(None, title="右尺 w1")

    w1_div_t_l_cu: float = Field(None, title="左寸 w1/t")
    w1_div_t_l_qu: float = Field(None, title="左關 w1/t")
    w1_div_t_l_ch: float = Field(None, title="左尺 w1/t")
    w1_div_t_r_cu: float = Field(None, title="右寸 w1/t")
    w1_div_t_r_qu: float = Field(None, title="右關 w1/t")
    w1_div_t_r_ch: float = Field(None, title="右尺 w1/t")

    t1_div_t_l_cu: float = Field(None, title="左寸 t1/t")
    t1_div_t_l_qu: float = Field(None, title="左關 t1/t")
    t1_div_t_l_ch: float = Field(None, title="左尺 t1/t")
    t1_div_t_r_cu: float = Field(None, title="右寸 t1/t")
    t1_div_t_r_qu: float = Field(None, title="右關 t1/t")
    t1_div_t_r_ch: float = Field(None, title="右尺 t1/t")

    pw_l_cu: float = Field(None, title="左寸 pw")
    pw_l_qu: float = Field(None, title="左關 pw")
    pw_l_ch: float = Field(None, title="左尺 pw")
    pw_r_cu: float = Field(None, title="右寸 pw")
    pw_r_qu: float = Field(None, title="右關 pw")
    pw_r_ch: float = Field(None, title="右尺 pw")

    pwcv_l_cu: float = Field(None, title="左寸 pwcv")
    pwcv_l_qu: float = Field(None, title="左關 pwcv")
    pwcv_l_ch: float = Field(None, title="左尺 pwcv")
    pwcv_r_cu: float = Field(None, title="右寸 pwcv")
    pwcv_r_qu: float = Field(None, title="右關 pwcv")
    pwcv_r_ch: float = Field(None, title="右尺 pwcv")

    a0_l_cu: float = Field(None, title="左寸 a0")
    a0_l_qu: float = Field(None, title="左關 a0")
    a0_l_ch: float = Field(None, title="左尺 a0")
    a0_r_cu: float = Field(None, title="右寸 a0")
    a0_r_qu: float = Field(None, title="右關 a0")
    a0_r_ch: float = Field(None, title="右尺 a0")

    # CN
    cn: Dict[str, Any] = Field({}, title="CN: C1-C11; 如果 standard_value 為空畫面不可選")
    # TODO: cncv, pn, pnsd 對應資料
    cncv: Dict[str, Any] = Field({}, title="CNCV: C1-C11; 如果 standard_value 為空畫面不可選")
    pn: Dict[str, Any] = Field({}, title="PN: C1-C11; 如果 standard_value 為空畫面不可選")
    pnsd: Dict[str, Any] = Field({}, title="PNSD: C1-C11; 如果 standard_value 為空畫面不可選")

    ### bcq.txt
    bcq: BCQ = Field({}, title="BCQ 資訊")


class NormalRange(BaseModel):
    lower: Union[int, float] = Field(None, title="下界(包含)")
    upper: Union[int, float] = Field(None, title="上界(不包含)")


class MeasureNormalRange(BaseModel):
    hr: NormalRange = Field(title="脈率")
    mean_prop_range_max: NormalRange = Field(title="浮沉振幅平均佔比最大值區塊")
    max_amp_depth_of_range: NormalRange = Field(title="浮沉振幅最大值落點區塊")
    # TODO: rename
    max_empt_value: NormalRange = Field(title="有效範圍內最大振幅值")
    max_slope_value: NormalRange = Field(title="斜率最大值")
    xingcheng: NormalRange = Field(title="行程")
    h1: NormalRange = Field(title="h1")
    h1_div_t1: NormalRange = Field(title="h1/t1")
    pr: NormalRange = Field(title="pr")
    w1: NormalRange = Field(title="w1")
    w1_div_t: NormalRange = Field(title="w1/t")
    t1_div_t: NormalRange = Field(title="t1/t")
    pw: NormalRange = Field(title="pw")
    pwcv: NormalRange = Field(title="pwcv")
    a0: NormalRange = Field(title="a0")
    cn: NormalRange = Field(title="cn")
    cncv: NormalRange = Field(title="cncv")
    pn: NormalRange = Field(title="pn")
    pnsd: NormalRange = Field(title="pnsd")


class MeasureInfoExtraInfo(BaseModel):
    mean_prop_range_1_l_cu: float = Field(None)
    mean_prop_range_2_l_cu: float = Field(None)
    mean_prop_range_3_l_cu: float = Field(None)
    mean_prop_range_1_l_qu: float = Field(None)
    mean_prop_range_2_l_qu: float = Field(None)
    mean_prop_range_3_l_qu: float = Field(None)
    mean_prop_range_1_l_ch: float = Field(None)
    mean_prop_range_2_l_ch: float = Field(None)
    mean_prop_range_3_l_ch: float = Field(None)
    mean_prop_range_1_r_cu: float = Field(None)
    mean_prop_range_2_r_cu: float = Field(None)
    mean_prop_range_3_r_cu: float = Field(None)
    mean_prop_range_1_r_qu: float = Field(None)
    mean_prop_range_2_r_qu: float = Field(None)
    mean_prop_range_3_r_qu: float = Field(None)
    mean_prop_range_1_r_ch: float = Field(None)
    mean_prop_range_2_r_ch: float = Field(None)
    mean_prop_range_3_r_ch: float = Field(None)
    mean_prop_range_max_l_cu: int = Field(None)
    mean_prop_range_max_l_qu: int = Field(None)
    mean_prop_range_max_l_ch: int = Field(None)
    mean_prop_range_max_r_cu: int = Field(None)
    mean_prop_range_max_r_qu: int = Field(None)
    mean_prop_range_max_r_ch: int = Field(None)
    max_amp_depth_of_range_l_cu: int = Field(None)
    max_amp_depth_of_range_l_qu: int = Field(None)
    max_amp_depth_of_range_l_ch: int = Field(None)
    max_amp_depth_of_range_r_cu: int = Field(None)
    max_amp_depth_of_range_r_qu: int = Field(None)
    max_amp_depth_of_range_r_ch: int = Field(None)


class MeasureDetailResponse(BaseModel):
    subject: SubjectRead
    measure: MeasureDetailRead


class MultiMeasureDetailResponse(BaseModel):
    subject: SubjectRead
    measures: List[MultiMeasureDetailRead]
    normal_spec: MeasureNormalRange
