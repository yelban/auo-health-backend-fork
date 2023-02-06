from datetime import date
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from auo_project.core.constants import SEX_TYPE_LABEL
from auo_project.core.utils import mask_credential_name, mask_crediential_sid
from auo_project.models.subject_model import SubjectBase


class SubjectReadBase(SubjectBase):
    id: UUID = Field(title="編號")
    sex_label: Optional[str] = Field(default=None, title="性別")
    standard_measure_info: Optional["SimpleMeasureInfo"] = Field(
        title="基準值檢測",
        default=None,
    )

    @validator("sex_label", always=True)
    def get_sex_label(cls, _, values):
        return SEX_TYPE_LABEL.get(values.get("sex"))


class SubjectRead(SubjectReadBase):
    pass


class SubjectSecretRead(SubjectReadBase):
    @validator("sid", always=True)
    def mask_sid(cls, value):
        return mask_crediential_sid(value)

    @validator("name", always=True)
    def mask_name(cls, value):
        return mask_credential_name(value)


class Link(BaseModel):
    self: str
    next: str = None
    prev: str = None


class MeasureListPage(BaseModel):
    page: int
    per_page: int
    page_count: int
    total_count: int
    link: Link
    items: List["MeasureInfoReadByList"] = Field(
        default=[],
        title="檢測紀錄",
    )


class SubjectReadWithMeasures(BaseModel):
    subject: SubjectRead
    measure: MeasureListPage
    measure_times: List[Dict[str, Any]] = Field([], title="選項：檢測時間")
    org_names: List[Dict[str, Any]] = Field([], title="選項：檢測單位")
    measure_operators: List[Dict[str, Any]] = Field(title="選項：檢測人員")
    irregular_hrs: List[Dict[str, Any]] = Field(title="選項：節律標記")
    proj_nums: List[Dict[str, Any]] = Field(title="選項：計畫編號")
    has_memos: List[Dict[str, Any]] = Field(title="選項：檢測標記")
    not_include_low_pass_rates: List[Dict[str, Any]] = Field(title="選項：排除脈波通過率過低項目")


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(SubjectBase):
    birth_date: date = Field(default=None, title="出生年月日")
    sex: int = Field(default=None, title="性別編號")
    memo: str = Field(default=None, max_length=1024, title="受測者標記")
    standard_measure_id: UUID = Field(
        title="基準值檢測編號",
        default=None,
    )
