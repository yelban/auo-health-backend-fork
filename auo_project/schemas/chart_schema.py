from typing import Any, Dict, List

from pydantic import BaseModel, Field


class Chart(BaseModel):
    data: Dict[str, Any] = Field(title="圖表資料")
    setting: List[Dict[str, Any]] = Field(title="圖表設定（需顯示圖表）")
