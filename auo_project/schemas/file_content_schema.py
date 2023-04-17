from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, validator

from auo_project.core.utils import switch_strength_value


class FileInfos(BaseModel):
    """infos.txt"""

    uid: str = Field(None)
    name: str
    id: str
    birthday: str = Field(None)
    birth_date: datetime = Field(None)  # extra
    number: str
    measure: int
    bcq: bool = Field(None, title="BCQ")  #
    tongue: bool = Field(None, title="")  #
    measure_time: datetime
    measure_operator: str = Field(None, title="")  #
    select_index_l_cu: int = Field(None)
    range_length_l_cu: float = Field(None)  # int
    max_ampt_index_l_cu: int = Field(None)
    max_ampt_value_l_cu: float = Field(None)
    irregular_hr_l_cu: bool = Field(None)
    select_index_l_qu: int = Field(None)
    range_length_l_qu: float = Field(None)
    max_ampt_index_l_qu: int = Field(None)
    max_ampt_value_l_qu: float = Field(None)
    irregular_hr_l_qu: bool = Field(None)
    select_index_l_ch: int = Field(None)
    range_length_l_ch: float = Field(None)  # int
    max_ampt_index_l_ch: int = Field(None)
    max_ampt_value_l_ch: float = Field(None)
    irregular_hr_l_ch: bool = Field(None)
    select_index_r_cu: int = Field(None)
    range_length_r_cu: float = Field(None)  # int
    max_ampt_index_r_cu: int = Field(None)
    max_ampt_value_r_cu: float = Field(None)
    irregular_hr_r_cu: bool = Field(None)
    select_index_r_qu: int = Field(None)
    range_length_r_qu: float = Field(None)  # int
    max_ampt_index_r_qu: int = Field(None)
    max_ampt_value_r_qu: float = Field(None)
    irregular_hr_r_qu: bool = Field(None)
    select_index_r_ch: int = Field(None)
    range_length_r_ch: float = Field(None)
    max_ampt_index_r_ch: int = Field(None)
    max_ampt_value_r_ch: float = Field(None)
    irregular_hr_r_ch: bool = Field(None)
    sex: int = Field(None)
    height: int = Field(None)
    weight: int = Field(None)
    # BMI: float
    sbp: int = Field(None)  # SBP
    dbp: int = Field(None)  # DBP
    judge_time: datetime = Field(None)
    judge_dr: str = Field(None)
    hr_l: int = Field(None, title="左脈率 HR_L")  # TODO: check 遲/正常/數 區間
    hr_r: int = Field(None, title="右脈率 HR_R")
    select_static_l_cu: int = Field(None)
    select_static_l_qu: int = Field(None)
    select_static_l_ch: int = Field(None)
    select_static_r_cu: int = Field(None)
    select_static_r_qu: int = Field(None)
    select_static_r_ch: int = Field(None)
    depth_l_cu: int = Field(None)
    depth_l_qu: int = Field(None)
    depth_l_ch: int = Field(None)
    depth_r_cu: int = Field(None)
    depth_r_qu: int = Field(None)
    depth_r_ch: int = Field(None)
    strength_l_cu: int = Field(None)
    strength_l_qu: int = Field(None)
    strength_l_ch: int = Field(None)
    strength_r_cu: int = Field(None)
    strength_r_qu: int = Field(None)
    strength_r_ch: int = Field(None)
    special_l: str = Field(None)
    special_r: str = Field(None)
    comment: str = Field(None)

    @validator("birth_date", pre=True)
    def convert_birth_date(cls, v, values):
        if values.get("birthday"):
            try:
                birth_date = datetime.strptime(values.get("birthday"), "%Y/%m/%d")
                return birth_date
            except:
                print(f"parse birthday error: {values.get('birthday')}")
        return v

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

    @validator(
        "strength_l_cu",
        "strength_l_qu",
        "strength_l_ch",
        "strength_r_cu",
        "strength_r_qu",
        "strength_r_ch",
        pre=True,
    )
    def switch_value(cls, v):
        return switch_strength_value(v)


class FileInfosAnalyze(BaseModel):
    """infos_analyze.txt"""

    range_start_index_l_cu: float = Field(None)  # int
    range_1_3_index_l_cu: float = Field(None)  # int
    range_2_3_index_l_cu: float = Field(None)  # int
    range_end_index_l_cu: float = Field(None)  # int
    max_amp_value_l_cu: float = Field(None)
    max_amp_depth_l_cu: float = Field(None)
    sum_range_1_l_cu: float = Field(None)
    sum_range_2_l_cu: float = Field(None)
    sum_range_3_l_cu: float = Field(None)
    mean_range_1_l_cu: float = Field(None, title="左寸-前段範圍振幅平均值")
    mean_range_2_l_cu: float = Field(None)
    mean_range_3_l_cu: float = Field(None)
    max_slop_l_cu: float = Field(None)
    range_start_index_l_qu: float = Field(None)  # int
    range_1_3_index_l_qu: float = Field(None)  # int
    range_2_3_index_l_qu: float = Field(None)  # int
    range_end_index_l_qu: float = Field(None)  # int
    max_amp_value_l_qu: float = Field(None)
    max_amp_depth_l_qu: float = Field(None)
    sum_range_1_l_qu: float = Field(None)
    sum_range_2_l_qu: float = Field(None)
    sum_range_3_l_qu: float = Field(None)
    mean_range_1_l_qu: float = Field(None)
    mean_range_2_l_qu: float = Field(None)
    mean_range_3_l_qu: float = Field(None)
    max_slop_l_qu: float = Field(None)
    range_start_index_l_ch: float = Field(None)  # int
    range_1_3_index_l_ch: float = Field(None)  # int
    range_2_3_index_l_ch: float = Field(None)  # int
    range_end_index_l_ch: float = Field(None)  # int
    max_amp_value_l_ch: float = Field(None)
    max_amp_depth_l_ch: float = Field(None)
    sum_range_1_l_ch: float = Field(None)
    sum_range_2_l_ch: float = Field(None)
    sum_range_3_l_ch: float = Field(None)
    mean_range_1_l_ch: float = Field(None)
    mean_range_2_l_ch: float = Field(None)
    mean_range_3_l_ch: float = Field(None)
    max_slop_l_ch: float = Field(None)
    range_start_index_r_cu: float = Field(None)  # int
    range_1_3_index_r_cu: float = Field(None)  # int
    range_2_3_index_r_cu: float = Field(None)  # int
    range_end_index_r_cu: float = Field(None)  # int
    max_amp_value_r_cu: float = Field(None)
    max_amp_depth_r_cu: float = Field(None)
    sum_range_1_r_cu: float = Field(None)
    sum_range_2_r_cu: float = Field(None)
    sum_range_3_r_cu: float = Field(None)
    mean_range_1_r_cu: float = Field(None)
    mean_range_2_r_cu: float = Field(None)
    mean_range_3_r_cu: float = Field(None)
    max_slop_r_cu: float = Field(None)
    range_start_index_r_qu: float = Field(None)  # int
    range_1_3_index_r_qu: float = Field(None)  # int
    range_2_3_index_r_qu: float = Field(None)  # int
    range_end_index_r_qu: float = Field(None)  # int
    max_amp_value_r_qu: float = Field(None)
    max_amp_depth_r_qu: float = Field(None)
    sum_range_1_r_qu: float = Field(None)
    sum_range_2_r_qu: float = Field(None)
    sum_range_3_r_qu: float = Field(None)
    mean_range_1_r_qu: float = Field(None)
    mean_range_2_r_qu: float = Field(None)
    mean_range_3_r_qu: float = Field(None)
    max_slop_r_qu: float = Field(None)
    range_start_index_r_ch: float = Field(None)  # int
    range_1_3_index_r_ch: float = Field(None)  # int
    range_2_3_index_r_ch: float = Field(None)  # int
    range_end_index_r_ch: float = Field(None)  # int
    max_amp_value_r_ch: float = Field(None)
    max_amp_depth_r_ch: float = Field(None)
    sum_range_1_r_ch: float = Field(None)
    sum_range_2_r_ch: float = Field(None)
    sum_range_3_r_ch: float = Field(None)
    mean_range_1_r_ch: float = Field(None)
    mean_range_2_r_ch: float = Field(None)
    mean_range_3_r_ch: float = Field(None)
    max_slop_r_ch: float = Field(None)
    static_range_start_l_cu: float = Field(None)
    static_range_1_3_l_cu: float = Field(None)
    static_range_2_3_l_cu: float = Field(None)
    static_range_end_l_cu: float = Field(None)
    static_max_amp_l_cu: float = Field(None)
    static_sum_range_1_l_cu: float = Field(None)
    static_sum_range_2_l_cu: float = Field(None)
    static_sum_range_3_l_cu: float = Field(None)
    static_mean_range_1_l_cu: float = Field(None)
    static_mean_range_2_l_cu: float = Field(None)
    static_mean_range_3_l_cu: float = Field(None)
    static_range_start_l_qu: float = Field(None)
    static_range_1_3_l_qu: float = Field(None)
    static_range_2_3_l_qu: float = Field(None)
    static_range_end_l_qu: float = Field(None)
    static_max_amp_l_qu: float = Field(None)
    static_sum_range_1_l_qu: float = Field(None)
    static_sum_range_2_l_qu: float = Field(None)
    static_sum_range_3_l_qu: float = Field(None)
    static_mean_range_1_l_qu: float = Field(None)
    static_mean_range_2_l_qu: float = Field(None)
    static_mean_range_3_l_qu: float = Field(None)
    static_range_start_l_ch: float = Field(None)
    static_range_1_3_l_ch: float = Field(None)
    static_range_2_3_l_ch: float = Field(None)
    static_range_end_l_ch: float = Field(None)
    static_max_amp_l_ch: float = Field(None)
    static_sum_range_1_l_ch: float = Field(None)
    static_sum_range_2_l_ch: float = Field(None)
    static_sum_range_3_l_ch: float = Field(None)
    static_mean_range_1_l_ch: float = Field(None)
    static_mean_range_2_l_ch: float = Field(None)
    static_mean_range_3_l_ch: float = Field(None)
    static_range_start_r_cu: float = Field(None)
    static_range_1_3_r_cu: float = Field(None)
    static_range_2_3_r_cu: float = Field(None)
    static_range_end_r_cu: float = Field(None)
    static_max_amp_r_cu: float = Field(None)
    static_sum_range_1_r_cu: float = Field(None)
    static_sum_range_2_r_cu: float = Field(None)
    static_sum_range_3_r_cu: float = Field(None)
    static_mean_range_1_r_cu: float = Field(None)
    static_mean_range_2_r_cu: float = Field(None)
    static_mean_range_3_r_cu: float = Field(None)
    static_range_start_r_qu: float = Field(None)
    static_range_1_3_r_qu: float = Field(None)
    static_range_2_3_r_qu: float = Field(None)
    static_range_end_r_qu: float = Field(None)
    static_max_amp_r_qu: float = Field(None)
    static_sum_range_1_r_qu: float = Field(None)
    static_sum_range_2_r_qu: float = Field(None)
    static_sum_range_3_r_qu: float = Field(None)
    static_mean_range_1_r_qu: float = Field(None)
    static_mean_range_2_r_qu: float = Field(None)
    static_mean_range_3_r_qu: float = Field(None)
    static_range_start_r_ch: float = Field(None)
    static_range_1_3_r_ch: float = Field(None)
    static_range_2_3_r_ch: float = Field(None)
    static_range_end_r_ch: float = Field(None)
    static_max_amp_r_ch: float = Field(None)
    static_sum_range_1_r_ch: float = Field(None)
    static_sum_range_2_r_ch: float = Field(None)
    static_sum_range_3_r_ch: float = Field(None)
    static_mean_range_1_r_ch: float = Field(None)
    static_mean_range_2_r_ch: float = Field(None)
    static_mean_range_3_r_ch: float = Field(None)


class FileBCQ(BaseModel):
    """BCQ.txt"""

    score_yang: int
    score_yin: int
    score_phlegm: int
    score_yanghead: int
    score_yangchest: int
    score_yanglimbs: int
    score_yangabdomen: int
    score_yangsurface: int
    score_yinhead: int
    score_yinlimbs: int
    score_yingt: int
    score_yinsurface: int
    score_yinabdomen: int
    score_phlegmtrunk: int
    score_phlegmsurface: int
    score_phlegmhead: int
    score_phlegmgt: int
    percentage_yang: int
    percentage_yin: int
    percentage_phlegm: int
    percentage_yanghead: int
    percentage_yangchest: int
    percentage_yanglimbs: int
    percentage_yangabdomen: int
    percentage_yangsurface: int
    percentage_yinhead: int
    percentage_yinlimbs: int
    percentage_yingt: int
    percentage_yinsurface: int
    percentage_yinabdomen: int
    percentage_phlegmtrunk: int
    percentage_phlegmsurface: int
    percentage_phlegmhead: int
    percentage_phlegmgt: int
    q1_select: int
    q2_select: int
    q3_select: int
    q4_select: int
    q5_select: int
    q6_select: int
    q7_select: int
    q8_select: int
    q9_select: int
    q10_select: int
    q11_select: int
    q12_select: int
    q13_select: int
    q14_select: int
    q15_select: int
    q16_select: int
    q17_select: int
    q18_select: int
    q19_select: int
    q20_select: int
    q21_select: int
    q22_select: int
    q23_select: int
    q24_select: int
    q25_select: int
    q26_select: int
    q27_select: int
    q28_select: int
    q29_select: int
    q30_select: int
    q31_select: int
    q32_select: int
    q33_select: int
    q34_select: int
    q35_select: int
    q36_select: int
    q37_select: int
    q38_select: int
    q39_select: int
    q40_select: int
    q41_select: int
    q42_select: int
    q43_select: int
    q44_select: int


class FileStatistics(BaseModel):
    """statistics.csv; need to remove extra comma of each line."""

    statistic: str = Field(None)
    id: str = Field(None)
    hand: str = Field(None)
    position: str = Field(None)
    a0: float = Field(None)
    c1: float = Field(None)
    c2: float = Field(None)
    c3: float = Field(None)
    c4: float = Field(None)
    c5: float = Field(None)
    c6: float = Field(None)
    c7: float = Field(None)
    c8: float = Field(None)
    c9: float = Field(None)
    c10: float = Field(None)
    c11: float = Field(None)
    p1: float = Field(None)
    p2: float = Field(None)
    p3: float = Field(None)
    p4: float = Field(None)
    p5: float = Field(None)
    p6: float = Field(None)
    p7: float = Field(None)
    p8: float = Field(None)
    p9: float = Field(None)
    p10: float = Field(None)
    p11: float = Field(None)
    h1: float = Field(None)
    t1: float = Field(None)
    t: float = Field(None)
    pw: float = Field(None)
    w1: float = Field(None)
    w1_div_t: float = Field(None)
    h1_div_t1: float = Field(None)
    t1_div_t: float = Field(None)
    hr: int = Field(None)
    pass_num: int = Field(None)
    all_num: int = Field(None)
    pass_rate: float = Field(None)


class FileReport(BaseModel):
    """report.txt"""

    name: str
    id: str
    birthday: str
    number: str
    measure_time: str
    measure_operator: str = Field(None)
    sex: int = Field(None)
    height: int = Field(None)
    weight: int = Field(None)
    sbp: int = Field(None, title="SBP")
    dbp: int = Field(None, title="DBP")
    judge_time: str = Field(None)
    judge_dr: str = Field(None)
    proj_num: str = Field(None)
    blood: int = Field(None)
    born_country: int = Field(None)
    born_tw_city: int = Field(None)
    born_tw_area: int = Field(None)
    born_foreign_addr: str = Field(None)
    live_country: int = Field(None)
    live_tw_city: int = Field(None)
    live_tw_area: int = Field(None)
    live_foreign_addr: str = Field(None)
    education: int = Field(None)
    job: str = Field(None)
    language: int = Field(None)
    other_language: str = Field(None)
    time_work: int = Field(None)
    time_work_start: int = Field(None)
    time_work_end: int = Field(None)
    time_weakup: int = Field(None)
    time_sleep: int = Field(None)
    stay_up: int = Field(None)
    stress: int = Field(None)
    favorite_tastes: str = Field(None)
    eat_cold: int = Field(None)
    eat_fried: int = Field(None)
    smoking: int = Field(None)
    drink: int = Field(None)
    areca_nut: int = Field(None)
    exercise: int = Field(None)
    disease: str = Field(None)
    other_disease: str = Field(None)
    surgery: int = Field(None)
    surgery_time_year: int = Field(None)
    surgery_time_month: int = Field(None)
    surgery_reason: str = Field(None)
    self_helth: int = Field(None)
    self_satisfy: int = Field(None)
    hr_l: int = Field(None, title="HR_L")
    hr_r: int = Field(None, title="HR_R")
    select_static_l_cu: int = Field(None)
    select_static_l_qu: int = Field(None)
    select_static_l_ch: int = Field(None)
    select_static_r_cu: int = Field(None)
    select_static_r_qu: int = Field(None)
    select_static_r_ch: int = Field(None)
    depth_l_cu: int = Field(None)
    depth_l_qu: int = Field(None)
    depth_l_ch: int = Field(None)
    depth_r_cu: int = Field(None)
    depth_r_qu: int = Field(None)
    depth_r_ch: int = Field(None)
    strength_l_cu: int = Field(None)
    strength_l_qu: int = Field(None)
    strength_l_ch: int = Field(None)
    strength_r_cu: int = Field(None)
    strength_r_qu: int = Field(None)
    strength_r_ch: int = Field(None)
    special_l: str = Field(None)  # special_L
    special_r: str = Field(None)  # special_R
    tongue_color: int = Field(None)
    tongue_shap: List[int] = Field([])
    tongue_status1: List[int] = Field([])
    tongue_status2: int = Field(None)
    tongue_coating_color: int = Field(None)
    tongue_coating_status: List[int] = Field([])
    tongue_coating_bottom: int = Field(
        None,
        title="tongue_coating_botton -> tongue_coating_bottom",
        alias="tongue_coating_botton",
    )
    bcq_yang: int = Field(None)
    bcq_yin: int = Field(None)
    bcq_phlegm: int = Field(None)
    comment: str = Field(None)

    @validator("tongue_shap", "tongue_status1", "tongue_coating_status", pre=True)
    def parse_int_list(cls, v):
        if isinstance(v, str):
            return [int(e) for e in v.split(",")]
        return v or []

    @validator(
        "strength_l_cu",
        "strength_l_qu",
        "strength_l_ch",
        "strength_r_cu",
        "strength_r_qu",
        "strength_r_ch",
        pre=True,
    )
    def switch_value(cls, v):
        return switch_strength_value(v)

    class Config:
        allow_population_by_field_name = True
