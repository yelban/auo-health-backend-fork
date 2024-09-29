from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, Field, validator

from auo_project.core.constants import SEX_TYPE_LABEL
from auo_project.core.utils import mask_credential_name, mask_crediential_sid
from auo_project.models.subject_model import SubjectBase


class SubjectReadBase(SubjectBase):
    id: UUID = Field(title="編號")
    org_id: UUID = Field(title="組織編號")
    sex_label: Optional[str] = Field(default=None, title="生理性別")
    age: Optional[int] = Field(default=None, title="年齡")
    standard_measure_info: Optional["SimpleMeasureInfo"] = Field(
        title="基準值檢測",
        default=None,
    )
    tag_ids: List[UUID] = Field(default=[], title="受測者標籤編號")
    tags: List[Dict[str, Any]] = Field(default=[], title="受測者標籤")
    proj_num: Optional[str] = Field(default=None, title="計畫編號")

    @validator("sex_label", always=True)
    def get_sex_label(cls, _, values):
        return SEX_TYPE_LABEL.get(values.get("sex"))

    @validator("age", always=True)
    def get_age(cls, _, values):
        birth_date = values.get("birth_date")
        if birth_date:
            today = datetime.utcnow().date() + timedelta(hours=8)
            return relativedelta(today, birth_date).years
        return None


class SubjectRead(SubjectReadBase):
    liked: Optional[bool] = Field(title="是否已加星號")


class SubjectSecretRead(SubjectReadBase):
    @validator("sid", always=True)
    def mask_sid(cls, value):
        return mask_crediential_sid(value)

    @validator("name", always=True)
    def mask_name(cls, value):
        return mask_credential_name(value)

    liked: Optional[bool] = Field(title="是否已加星號")


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
    subject: Union[SubjectRead, SubjectSecretRead]
    measure: MeasureListPage
    measure_times: List[Dict[str, Any]] = Field([], title="選項：檢測時間")
    irregular_hrs: List[Dict[str, Any]] = Field([], title="選項：節律標記")
    has_bcqs: List[Dict[str, Any]] = Field([], title="選項：體質量表 / BCQ")
    pass_rates: List[Dict[str, Any]] = Field([], title="選項：脈波通過率")
    subject_tags: List[Dict[str, Any]] = Field([], title="選項：受測者標籤")
    measure_operators: List[Dict[str, Any]] = Field(title="（待刪除）選項：檢測人員")
    normal_spec: List[Dict[str, Any]] = Field(
        title="正常值範圍，表示方式 [x, y]。當數值 < x 或 數值 >= y 時代表異常，需顯示紅色",
    )


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    birth_date: Optional[date] = Field(default=None, title="出生年月日")
    sex: Optional[int] = Field(default=None, title="生理性別")
    memo: Optional[str] = Field(default=None, max_length=1024, title="受測者標記")
    standard_measure_id: Optional[UUID] = Field(
        title="基準值檢測編號",
        default=None,
    )
    last_measure_time: Optional[datetime] = Field(default=None, title="最後檢測時間")
    sid: Optional[str] = Field(default=None, title="身分證字號")
    name: Optional[str] = Field(default=None, title="姓名")
    number: Optional[str] = Field(default=None, title="受測者編號")
    proj_num: Optional[str] = Field(default=None, title="計畫編號")
    deleted_mark: Optional[bool] = Field(default=None, title="刪除標記")
    is_active: Optional[bool] = Field(default=None, title="是否啟用")


class SubjectUpdateInput(BaseModel):
    sid: Optional[str] = Field(default=None, title="身分證字號")
    name: Optional[str] = Field(default=None, title="姓名")
    number: Optional[str] = Field(default=None, title="受測者編號")
    birth_date: Optional[date] = Field(default=None, title="出生年月日")
    proj_num: Optional[str] = Field(default=None, title="計畫編號")
    sex: Optional[int] = Field(default=None, title="生理性別")
    deleted_mark: Optional[bool] = Field(default=None, title="刪除標記")
