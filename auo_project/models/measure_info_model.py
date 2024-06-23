from datetime import datetime
from typing import List, Optional
from uuid import UUID

import sqlmodel
from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Relationship, UniqueConstraint

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class MeasureInfoBase(BaseModel):
    subject_id: UUID = Field(
        index=True,
        nullable=False,
        foreign_key="measure.subjects.id",
        title="受測者資料庫編號",
    )
    file_id: UUID = Field(
        index=True,
        nullable=True,
        foreign_key="app.upload_files.id",
        title="檔案編號",
        default=None,
        unique=True,
    )
    org_id: UUID = Field(
        index=True,
        nullable=False,
        foreign_key="app.auth_orgs.id",
        title="檢測單位編號",
    )
    uid: str = Field(nullable=True, max_length=128, title="脈診儀 UID", default=None)
    number: str = Field(nullable=True, max_length=128, title="病歷號碼", default=None)
    has_measure: int = Field(nullable=True, index=True, title="脈象量測", default=None)
    has_bcq: bool = Field(nullable=True, index=True, title="BCQ體質量表", default=None)
    has_tongue: bool = Field(nullable=True, index=True, title="舌象", default=None)
    has_memo: bool = Field(nullable=True, index=True, title="是否有檢測標記", default=None)
    has_low_pass_rate: bool = Field(
        nullable=True,
        index=True,
        title="是否有脈波通過率過低項目",
        default=None,
    )
    measure_time: datetime = Field(
        default=None,
        nullable=True,
        index=True,
        title="檢測時間",
    )
    measure_operator: str = Field(
        default=None,
        max_length=128,
        index=True,
        nullable=True,
        title="檢測人員名稱",
    )
    mean_prop_range_1_l_cu: float = Field(default=None, title="左寸浮振幅平均值佔比")
    mean_prop_range_2_l_cu: float = Field(default=None, title="左寸中振幅平均值佔比")
    mean_prop_range_3_l_cu: float = Field(default=None, title="左寸沉振幅平均值佔比")
    mean_prop_range_1_l_qu: float = Field(default=None, title="左關浮振幅平均值佔比")
    mean_prop_range_2_l_qu: float = Field(default=None, title="左關中振幅平均值佔比")
    mean_prop_range_3_l_qu: float = Field(default=None, title="左關沉振幅平均值佔比")
    mean_prop_range_1_l_ch: float = Field(default=None, title="左尺浮振幅平均值佔比")
    mean_prop_range_2_l_ch: float = Field(default=None, title="左尺中振幅平均值佔比")
    mean_prop_range_3_l_ch: float = Field(default=None, title="左尺沉振幅平均值佔比")
    mean_prop_range_1_r_cu: float = Field(default=None, title="右寸浮振幅平均值佔比")
    mean_prop_range_2_r_cu: float = Field(default=None, title="右寸中振幅平均值佔比")
    mean_prop_range_3_r_cu: float = Field(default=None, title="右寸沉振幅平均值佔比")
    mean_prop_range_1_r_qu: float = Field(default=None, title="右關浮振幅平均值佔比")
    mean_prop_range_2_r_qu: float = Field(default=None, title="右關中振幅平均值佔比")
    mean_prop_range_3_r_qu: float = Field(default=None, title="右關沉振幅平均值佔比")
    mean_prop_range_1_r_ch: float = Field(default=None, title="右尺浮振幅平均值佔比")
    mean_prop_range_2_r_ch: float = Field(default=None, title="右尺中振幅平均值佔比")
    mean_prop_range_3_r_ch: float = Field(default=None, title="右尺沉振幅平均值佔比")
    mean_prop_range_max_l_cu: int = Field(
        default=None,
        title="左寸浮沉振幅平均佔比最大值區塊; 浮:2/中:1/沉:0",
    )
    mean_prop_range_max_l_qu: int = Field(
        default=None,
        title="左關浮沉振幅平均佔比最大值區塊; 浮:2/中:1/沉:0",
    )
    mean_prop_range_max_l_ch: int = Field(
        default=None,
        title="左尺浮沉振幅平均佔比最大值區塊; 浮:2/中:1/沉:0",
    )
    mean_prop_range_max_r_cu: int = Field(
        default=None,
        title="右寸浮沉振幅平均佔比最大值區塊; 浮:2/中:1/沉:0",
    )
    mean_prop_range_max_r_qu: int = Field(
        default=None,
        title="右關浮沉振幅平均佔比最大值區塊; 浮:2/中:1/沉:0",
    )
    mean_prop_range_max_r_ch: int = Field(
        default=None,
        title="右尺浮沉振幅平均佔比最大值區塊; 浮:2/中:1/沉:0",
    )
    max_amp_depth_of_range_l_cu: int = Field(
        default=None,
        title="左寸浮沉振幅最大值落點區塊; 浮:2/中:1/沉:0",
    )
    max_amp_depth_of_range_l_qu: int = Field(
        default=None,
        title="左關浮沉振幅最大值落點區塊; 浮:2/中:1/沉:0",
    )
    max_amp_depth_of_range_l_ch: int = Field(
        default=None,
        title="左尺浮沉振幅最大值落點區塊; 浮:2/中:1/沉:0",
    )
    max_amp_depth_of_range_r_cu: int = Field(
        default=None,
        title="右寸浮沉振幅最大值落點區塊; 浮:2/中:1/沉:0",
    )
    max_amp_depth_of_range_r_qu: int = Field(
        default=None,
        title="右關浮沉振幅最大值落點區塊; 浮:2/中:1/沉:0",
    )
    max_amp_depth_of_range_r_ch: int = Field(
        default=None,
        title="右尺浮沉振幅最大值落點區塊; 浮:2/中:1/沉:0",
    )
    max_amp_value_l_cu: float = Field(
        default=None,
        nullable=True,
        title="左寸-有效範圍內最大振幅值",
    )
    max_amp_value_l_qu: float = Field(
        default=None,
        nullable=True,
        title="左關-有效範圍內最大振幅值",
    )
    max_amp_value_l_ch: float = Field(
        default=None,
        nullable=True,
        title="左尺-有效範圍內最大振幅值",
    )
    max_amp_value_r_cu: float = Field(
        default=None,
        nullable=True,
        title="右寸-有效範圍內最大振幅值",
    )
    max_amp_value_r_qu: float = Field(
        default=None,
        nullable=True,
        title="右關-有效範圍內最大振幅值",
    )
    max_amp_value_r_ch: float = Field(
        default=None,
        nullable=True,
        title="右尺-有效範圍內最大振幅值",
    )
    select_static_l_cu: float = Field(
        default=None,
        nullable=True,
        title="左寸-點選的靜態壓值(單位:mmHg)",
    )
    select_static_l_qu: float = Field(
        default=None,
        nullable=True,
        title="左關-點選的靜態壓值(單位:mmHg)",
    )
    select_static_l_ch: float = Field(
        default=None,
        nullable=True,
        title="左尺-點選的靜態壓值(單位:mmHg)",
    )
    select_static_r_cu: float = Field(
        default=None,
        nullable=True,
        title="右寸-點選的靜態壓值(單位:mmHg)",
    )
    select_static_r_qu: float = Field(
        default=None,
        nullable=True,
        title="右關-點選的靜態壓值(單位:mmHg)",
    )
    select_static_r_ch: float = Field(
        default=None,
        nullable=True,
        title="右尺-點選的靜態壓值(單位:mmHg)",
    )
    irregular_hr_l_cu: bool = Field(default=None, nullable=True, title="左寸-有無脈律不整")
    irregular_hr_l_qu: bool = Field(default=None, nullable=True, title="左關-有無脈律不整")
    irregular_hr_l_ch: bool = Field(default=None, nullable=True, title="左尺-有無脈律不整")
    irregular_hr_r_cu: bool = Field(default=None, nullable=True, title="右寸-有無脈律不整")
    irregular_hr_r_qu: bool = Field(default=None, nullable=True, title="右關-有無脈律不整")
    irregular_hr_r_ch: bool = Field(default=None, nullable=True, title="右尺-有無脈律不整")
    irregular_hr_l: int = Field(default=None, title="左手節律是否異常; 正常:0/異常:1")
    irregular_hr_type_l: int = Field(
        default=None,
        title="左手節律異常類型; 無:null/止無定數:0/止有定數:1",
    )
    irregular_hr_r: int = Field(default=None, title="右手節律是否異常; 正常:0/異常:1")
    irregular_hr_type_r: int = Field(
        default=None,
        title="右手節律異常類型; 無:null/止無定數:0/止有定數:1",
    )
    irregular_hr: int = Field(
        default=None,
        nullable=True,
        index=True,
        title="節律標記：有任一個 true 就是異常：irregular_hr_L_cu, irregular_hr_L_qu, irregular_hr_L_ch, irregular_hr_R_cu, irregular_hr_R_qu, irregular_hr_R_ch",
    )
    max_slope_value_l_cu: float = Field(default=None, title="左寸斜率最大值")
    max_slope_value_l_qu: float = Field(default=None, title="左關斜率最大值")
    max_slope_value_l_ch: float = Field(default=None, title="左尺斜率最大值")
    max_slope_value_r_cu: float = Field(default=None, title="右寸斜率最大值")
    max_slope_value_r_qu: float = Field(default=None, title="右關斜率最大值")
    max_slope_value_r_ch: float = Field(default=None, title="右尺斜率最大值")

    strength_l_cu: int = Field(default=None, title="左寸力量; 無:null/無力:0/正常:1/有力:2")
    strength_l_qu: int = Field(default=None, title="左關力量; 無:null/無力:0/正常:1/有力:2")
    strength_l_ch: int = Field(default=None, title="左尺力量; 無:null/無力:0/正常:1/有力:2")
    strength_r_cu: int = Field(default=None, title="右寸力量; 無:null/無力:0/正常:1/有力:2")
    strength_r_qu: int = Field(default=None, title="右關力量; 無:null/無力:0/正常:1/有力:2")
    strength_r_ch: int = Field(default=None, title="右尺力量; 無:null/無力:0/正常:1/有力:2")

    range_length_l_cu: float = Field(default=None, title="左寸有效範圍長度(單位:mm)")
    range_length_l_qu: float = Field(default=None, title="左關有效範圍長度(單位:mm)")
    range_length_l_ch: float = Field(default=None, title="左尺有效範圍長度(單位:mm)")
    range_length_r_cu: float = Field(default=None, title="右寸有效範圍長度(單位:mm)")
    range_length_r_qu: float = Field(default=None, title="右關有效範圍長度(單位:mm)")
    range_length_r_ch: float = Field(default=None, title="右尺有效範圍長度(單位:mm)")

    width_l_cu: int = Field(default=None, title="左寸大細; 無:null/虛:0/正常:1/實:2")
    width_l_qu: int = Field(default=None, title="左關大細; 無:null/虛:0/正常:1/實:2")
    width_l_ch: int = Field(default=None, title="左尺大細; 無:null/虛:0/正常:1/實:2")
    width_r_cu: int = Field(default=None, title="右寸大細; 無:null/虛:0/正常:1/實:2")
    width_r_qu: int = Field(default=None, title="右關大細; 無:null/虛:0/正常:1/實:2")
    width_r_ch: int = Field(default=None, title="右尺大細; 無:null/虛:0/正常:1/實:2")

    static_max_amp_l_cu: float = Field(
        default=None,
        title="靜態壓有效範圍-左寸-最大振幅靜態壓值(單位:mmHg)",
    )
    static_max_amp_l_qu: float = Field(
        default=None,
        title="靜態壓有效範圍-左關-最大振幅靜態壓值(單位:mmHg)",
    )
    static_max_amp_l_ch: float = Field(
        default=None,
        title="靜態壓有效範圍-左尺-最大振幅靜態壓值(單位:mmHg)",
    )
    static_max_amp_r_cu: float = Field(
        default=None,
        title="靜態壓有效範圍-右寸-最大振幅靜態壓值(單位:mmHg)",
    )
    static_max_amp_r_qu: float = Field(
        default=None,
        title="靜態壓有效範圍-右關-最大振幅靜態壓值(單位:mmHg)",
    )
    static_max_amp_r_ch: float = Field(
        default=None,
        title="靜態壓有效範圍-右尺-最大振幅靜態壓值(單位:mmHg)",
    )
    static_range_start_l_cu: float = Field(
        default=None,
        title="靜態壓有效範圍-左寸-起點靜態壓值(單位:mmHg)",
    )
    static_range_start_l_qu: float = Field(
        default=None,
        title="靜態壓有效範圍-左關-起點靜態壓值(單位:mmHg)",
    )
    static_range_start_l_ch: float = Field(
        default=None,
        title="靜態壓有效範圍-左尺-起點靜態壓值(單位:mmHg)",
    )
    static_range_start_r_cu: float = Field(
        default=None,
        title="靜態壓有效範圍-右寸-起點靜態壓值(單位:mmHg)",
    )
    static_range_start_r_qu: float = Field(
        default=None,
        title="靜態壓有效範圍-右關-起點靜態壓值(單位:mmHg)",
    )
    static_range_start_r_ch: float = Field(
        default=None,
        title="靜態壓有效範圍-右尺-起點靜態壓值(單位:mmHg)",
    )
    static_range_end_l_cu: float = Field(
        default=None,
        title="靜態壓有效範圍-左寸-終點靜態壓值(單位:mmHg)",
    )
    static_range_end_l_qu: float = Field(
        default=None,
        title="靜態壓有效範圍-左關-終點靜態壓值(單位:mmHg)",
    )
    static_range_end_l_ch: float = Field(
        default=None,
        title="靜態壓有效範圍-左尺-終點靜態壓值(單位:mmHg)",
    )
    static_range_end_r_cu: float = Field(
        default=None,
        title="靜態壓有效範圍-右寸-終點靜態壓值(單位:mmHg)",
    )
    static_range_end_r_qu: float = Field(
        default=None,
        title="靜態壓有效範圍-右關-終點靜態壓值(單位:mmHg)",
    )
    static_range_end_r_ch: float = Field(
        default=None,
        title="靜態壓有效範圍-右尺-終點靜態壓值(單位:mmHg)",
    )
    xingcheng_l_cu: float = Field(default=None, title="行程-左寸-起點終點相差深度(單位:mm)")
    xingcheng_l_qu: float = Field(default=None, title="行程-左關-起點終點相差深度(單位:mm)")
    xingcheng_l_ch: float = Field(default=None, title="行程-左尺-起點終點相差深度(單位:mm)")
    xingcheng_r_cu: float = Field(default=None, title="行程-右寸-起點終點相差深度(單位:mm)")
    xingcheng_r_qu: float = Field(default=None, title="行程-右關-起點終點相差深度(單位:mm)")
    xingcheng_r_ch: float = Field(default=None, title="行程-右尺-起點終點相差深度(單位:mm)")

    pass_rate_l_cu: float = Field(default=None, title="左寸-通過率 0-100")
    pass_rate_l_qu: float = Field(default=None, title="左關-通過率 0-100")
    pass_rate_l_ch: float = Field(default=None, title="左尺-通過率 0-100")
    pass_rate_r_cu: float = Field(default=None, title="右寸-通過率 0-100")
    pass_rate_r_qu: float = Field(default=None, title="右關-通過率 0-100")
    pass_rate_r_ch: float = Field(default=None, title="右尺-通過率 0-100")

    sex: int = Field(default=None, nullable=True, title="性別")
    age: int = Field(default=None, nullable=True, title="檢測時年齡")
    height: int = Field(default=None, nullable=True, title="身高")
    weight: int = Field(default=None, nullable=True, title="體重")
    bmi: float = Field(
        default=None,
        index=True,
        nullable=True,
        title="BMI=weight/(height/100)^2",
    )

    sbp: int = Field(default=None, nullable=True, title="收縮壓")
    dbp: int = Field(default=None, nullable=True, title="舒張壓")
    judge_time: datetime = Field(default=None, nullable=True, title="診斷時間")
    judge_dr: str = Field(default=None, max_length=128, nullable=True, title="診斷醫師")

    hr_l: int = Field(default=None, nullable=True, title="左脈率")  # TODO: check 遲/正常/數 區間
    hr_r: int = Field(default=None, nullable=True, title="右脈率")
    special_l: str = Field(default=None, max_length=10, nullable=True, title="左手特殊脈")
    special_r: str = Field(default=None, max_length=10, nullable=True, title="右手特殊脈")

    comment: str = Field(
        default=None,
        max_length=1024,
        nullable=True,
        title="診斷內容",
    )  # TODO: handle multiple lines issue
    memo: str = Field(default=None, max_length=1024, nullable=True, title="檢測標記")
    proj_num: str = Field(
        default=None,
        index=True,
        nullable=True,
        title="計畫編號",
    )  # from report.txt

    six_sec_pw_valid_l_cu: bool = Field(default=True, title="左寸六秒脈波有效")
    six_sec_pw_valid_l_qu: bool = Field(default=True, title="左關六秒脈波有效")
    six_sec_pw_valid_l_ch: bool = Field(default=True, title="左尺六秒脈波有效")
    six_sec_pw_valid_r_cu: bool = Field(default=True, title="右寸六秒脈波有效")
    six_sec_pw_valid_r_qu: bool = Field(default=True, title="右關六秒脈波有效")
    six_sec_pw_valid_r_ch: bool = Field(default=True, title="右尺六秒脈波有效")

    pulse_28_ids_l_overall: List[UUID] = Field(
        default=[],
        sa_column=Column(postgresql.ARRAY(sqlmodel.sql.sqltypes.GUID())),
        title="左手總按28脈 UUID",
    )
    pulse_28_ids_l_cu: List[UUID] = Field(
        default=[],
        sa_column=Column(postgresql.ARRAY(sqlmodel.sql.sqltypes.GUID())),
        title="左寸28脈 UUID",
    )
    pulse_28_ids_l_qu: List[UUID] = Field(
        default=[],
        sa_column=Column(postgresql.ARRAY(sqlmodel.sql.sqltypes.GUID())),
        title="左關28脈 UUID",
    )
    pulse_28_ids_l_ch: List[UUID] = Field(
        default=[],
        sa_column=Column(postgresql.ARRAY(sqlmodel.sql.sqltypes.GUID())),
        title="左尺28脈 UUID",
    )
    pulse_28_ids_r_overall: List[UUID] = Field(
        default=[],
        sa_column=Column(postgresql.ARRAY(sqlmodel.sql.sqltypes.GUID())),
        title="右手總按28脈 UUID",
    )
    pulse_28_ids_r_cu: List[UUID] = Field(
        default=[],
        sa_column=Column(postgresql.ARRAY(sqlmodel.sql.sqltypes.GUID())),
        title="右寸28脈 UUID",
    )
    pulse_28_ids_r_qu: List[UUID] = Field(
        default=[],
        sa_column=Column(postgresql.ARRAY(sqlmodel.sql.sqltypes.GUID())),
        title="右關28脈 UUID",
    )
    pulse_28_ids_r_ch: List[UUID] = Field(
        default=[],
        sa_column=Column(postgresql.ARRAY(sqlmodel.sql.sqltypes.GUID())),
        title="右尺28脈 UUID",
    )

    pulse_memo: str = Field(default="", title="脈象標記")

    ver: str = Field(default=None, max_length=100, nullable=True, title="ver.ini")

    is_active: bool = Field(index=True, nullable=False, default=True)


class MeasureInfo(BaseUUIDModel, BaseTimestampModel, MeasureInfoBase, table=True):
    __tablename__ = "infos"
    __table_args__ = (
        UniqueConstraint(
            "subject_id",
            "measure_time",
            name="measure_infos_subject_id_measure_time_key",
        ),
        {"schema": "measure"},
    )
    subject: "Subject" = Relationship(
        sa_relationship_kwargs={
            "lazy": "selectin",
            "uselist": False,
            "foreign_keys": "MeasureInfo.subject_id",
        },
    )
    bcq: "BCQ" = Relationship(
        back_populates="measure_info",
        sa_relationship_kwargs={
            "lazy": "select",
            "uselist": False,
            "cascade": "all, delete",
        },
    )
    raw: "MeasureRaw" = Relationship(
        back_populates="measure_info",
        sa_relationship_kwargs={
            "lazy": "select",
            "uselist": False,
            "cascade": "all, delete",
        },
    )
    statistics: "MeasureStatistic" = Relationship(
        back_populates="measure_info",
        sa_relationship_kwargs={
            "lazy": "select",
            "uselist": True,
            "cascade": "all, delete",
        },
    )
    tongue: "MeasureTongue" = Relationship(
        back_populates="measure_info",
        sa_relationship_kwargs={
            "lazy": "select",
            "uselist": False,
            "cascade": "all, delete",
        },
    )
    advanced_tongue: "MeasureAdvancedTongue" = Relationship(
        back_populates="measure_info",
        sa_relationship_kwargs={
            "lazy": "select",
            "uselist": False,
            "cascade": "all, delete",
        },
    )
    org: "Org" = Relationship(
        back_populates="measure_info",
        sa_relationship_kwargs={
            "lazy": "select",
            "uselist": False,
        },
    )
    measure_survey_result: Optional["MeasureSurveyResult"] = Relationship(
        back_populates="measure_info",
        sa_relationship_kwargs={
            "lazy": "select",
            "uselist": False,
        },
    )
    advanced_tongue2: "MeasureAdvancedTongue2" = Relationship(
        back_populates="measure_info",
        sa_relationship_kwargs={"lazy": "select", "uselist": True},
    )
