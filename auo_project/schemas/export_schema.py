from typing import List

from pydantic import BaseModel, Field


class DF1Schema(BaseModel):
    measure_time: str = Field(default=None, alias="受測時間")
    number: str = Field(default=None, alias="受測者編號")
    birth_date: str = Field(default=None, alias="生日")
    sex_label: str = Field(default=None, alias="性別")
    bmi: float = Field(default=None, alias="BMI")
    pass_rate: float = Field(default=None, alias="通過率")
    hand: str = Field(default=None, alias="左右")
    position: str = Field(default=None, alias="寸關尺")
    hr: float = Field(default=None, alias="脈率")
    range: str = Field(default=None, alias="浮沈")
    static_max_amp: float = Field(default=None, alias="振幅")
    max_slope_value: float = Field(default=None, alias="斜率")
    width: float = Field(default=None, alias="時間")
    h1: float = Field(default=None, alias="h1")
    h1_div_t1: float = Field(default=None, alias="h1/t1")
    w1: float = Field(default=None, alias="w1")
    w1_div_t: float = Field(default=None, alias="w1/t")
    t1_div_t: float = Field(default=None, alias="t1/t")
    pw: float = Field(default=None, alias="pw")
    pwcv: float = Field(default=None, alias="pwcv")
    a0: float = Field(default=None, alias="a0")
    c1_mean: float = Field(default=None, alias="c1_mean")
    c2_mean: float = Field(default=None, alias="c2_mean")
    c3_mean: float = Field(default=None, alias="c3_mean")
    c4_mean: float = Field(default=None, alias="c4_mean")
    c5_mean: float = Field(default=None, alias="c5_mean")
    c6_mean: float = Field(default=None, alias="c6_mean")
    c7_mean: float = Field(default=None, alias="c7_mean")
    c8_mean: float = Field(default=None, alias="c8_mean")
    c9_mean: float = Field(default=None, alias="c9_mean")
    c10_mean: float = Field(default=None, alias="c10_mean")
    c11_mean: float = Field(default=None, alias="c11_mean")
    c1_cv: float = Field(default=None, alias="c1_cv")
    c2_cv: float = Field(default=None, alias="c2_cv")
    c3_cv: float = Field(default=None, alias="c3_cv")
    c4_cv: float = Field(default=None, alias="c4_cv")
    c5_cv: float = Field(default=None, alias="c5_cv")
    c6_cv: float = Field(default=None, alias="c6_cv")
    c7_cv: float = Field(default=None, alias="c7_cv")
    c8_cv: float = Field(default=None, alias="c8_cv")
    c9_cv: float = Field(default=None, alias="c9_cv")
    c10_cv: float = Field(default=None, alias="c10_cv")
    c11_cv: float = Field(default=None, alias="c11_cv")
    p1_mean: float = Field(default=None, alias="p1_mean")
    p2_mean: float = Field(default=None, alias="p2_mean")
    p3_mean: float = Field(default=None, alias="p3_mean")
    p4_mean: float = Field(default=None, alias="p4_mean")
    p5_mean: float = Field(default=None, alias="p5_mean")
    p6_mean: float = Field(default=None, alias="p6_mean")
    p7_mean: float = Field(default=None, alias="p7_mean")
    p8_mean: float = Field(default=None, alias="p8_mean")
    p9_mean: float = Field(default=None, alias="p9_mean")
    p10_mean: float = Field(default=None, alias="p10_mean")
    p11_mean: float = Field(default=None, alias="p11_mean")
    p1_std: float = Field(default=None, alias="p1_std")
    p2_std: float = Field(default=None, alias="p2_std")
    p3_std: float = Field(default=None, alias="p3_std")
    p4_std: float = Field(default=None, alias="p4_std")
    p5_std: float = Field(default=None, alias="p5_std")
    p6_std: float = Field(default=None, alias="p6_std")
    p7_std: float = Field(default=None, alias="p7_std")
    p8_std: float = Field(default=None, alias="p8_std")
    p9_std: float = Field(default=None, alias="p9_std")
    p10_std: float = Field(default=None, alias="p10_std")
    p11_std: float = Field(default=None, alias="p11_std")

    class Config:
        allow_population_by_field_name = True


class DF2Schema(BaseModel):
    measure_time: str = Field(default=None, alias="受測時間")
    number: str = Field(default=None, alias="受測者編號")
    item_type: str = Field(default=None, alias="體質")
    position: str = Field(default=None, alias="位置")
    score: int = Field(default=None, alias="得分")
    percentage: int = Field(default=None, alias="正規化得分")

    class Config:
        allow_population_by_field_name = True


class MultiExportFile(BaseModel):
    filename: str
    rows: List[dict]
