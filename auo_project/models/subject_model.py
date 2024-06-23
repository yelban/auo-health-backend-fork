from datetime import date, datetime
from typing import List
from uuid import UUID

import sqlmodel
from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Relationship

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class SubjectBase(BaseModel):
    org_id: UUID = Field(index=True, nullable=False, title="組織編號")
    sid: str = Field(index=True, unique=True, nullable=False, title="身分證字號")
    name: str = Field(max_length=128, index=True, nullable=True, title="姓名")
    birth_date: date = Field(default=None, index=True, nullable=True, title="出生年月日")
    sex: int = Field(default=None, index=True, nullable=True, title="性別編號")
    memo: str = Field(
        default=None,
        max_length=1024,
        index=True,
        nullable=True,
        title="受測者標記",
    )
    standard_measure_id: UUID = Field(
        nullable=True,
        title="基準值檢測編號",
        default=None,
    )
    last_measure_time: datetime = Field(default=None, nullable=True)
    proj_num: str = Field(default=None, nullable=True)
    number: str = Field(default=None, nullable=True)
    tag_ids: List[UUID] = Field(
        default=[],
        sa_column=Column(postgresql.ARRAY(sqlmodel.sql.sqltypes.GUID())),
        nullable=True,
    )
    is_active: bool = Field(index=True, nullable=False, default=True)


class Subject(BaseUUIDModel, BaseTimestampModel, SubjectBase, table=True):
    __tablename__ = "subjects"
    __table_args__ = {"schema": "measure"}
    standard_measure_info: "MeasureInfo" = Relationship(
        sa_relationship_kwargs={
            "lazy": "select",
            "primaryjoin": "Subject.standard_measure_id == MeasureInfo.id",
            "uselist": False,
            "foreign_keys": "[Subject.standard_measure_id]",
        },
    )
    measure_survey_result: List["MeasureSurveyResult"] = Relationship(
        back_populates="subject",
        sa_relationship_kwargs={"lazy": "select"},
    )
