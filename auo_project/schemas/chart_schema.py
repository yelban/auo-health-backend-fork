from typing import Any, Dict, List

from pydantic import BaseModel, Field

from auo_project.core.constants import AdvanceChartType


class ChartSetting(BaseModel):
    chart_type: AdvanceChartType = Field(
        ...,
        description="圖表種類",
        example=AdvanceChartType.parameter_six_pulse.value,
    )
    x: str = Field(None, title="X 軸選項 value", description="X 軸，僅圖表類型二需要", example="")
    y: Dict[str, Any] = Field(
        ...,
        title="Y 軸選項 value",
        description="""Y 軸。不同圖表 y 的格式不同。
        圖表一 parameter_six_pulse：{
            "domain": ["time_domain", "h1"]
        }
        圖表二 parameter_cross：{
            "six_pulse": "l_cu",
            "domain": ["time_domain", "h1"]
        }
        圖表三 six_pulse_cn：{
            "six_pulse": "l_cu",
            "statistics": "mean"
        }
        """,
        example={"domain": ["time_domain", "h1"]},
    )
    z: str = Field(..., title="Z 軸選項 value", description="Z 軸", example="a004")


class Chart(BaseModel):
    settings: List[ChartSetting] = Field(title="圖表設定（需顯示圖表）")
    filters: List[Dict[str, Any]] = Field(title="圖表 X, Y, Z 軸選項")
