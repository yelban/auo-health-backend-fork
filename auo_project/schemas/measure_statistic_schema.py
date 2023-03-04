from uuid import UUID

from pydantic import BaseModel, Field

from auo_project.models.measure_statistic_model import MeasureStatisticBase


class MeasureStatisticRead(MeasureStatisticBase):
    id: UUID


class MeasureStatisticCreate(MeasureStatisticBase):
    pass


class MeasureStatisticUpdate(MeasureStatisticBase):
    pass


class MeasureStatisticFlat(BaseModel):

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

    w1_div_t_l_cu: float = Field(None, title="左寸 w1/t1")
    w1_div_t_l_qu: float = Field(None, title="左關 w1/t1")
    w1_div_t_l_ch: float = Field(None, title="左尺 w1/t1")
    w1_div_t_r_cu: float = Field(None, title="右寸 w1/t1")
    w1_div_t_r_qu: float = Field(None, title="右關 w1/t1")
    w1_div_t_r_ch: float = Field(None, title="右尺 w1/t1")

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
