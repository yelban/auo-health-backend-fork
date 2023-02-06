from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from auo_project.models.base_model import BaseTimestampModel, BaseUUIDModel


class MeasureRawBase(SQLModel):
    measure_id: UUID = Field(
        index=True,
        unique=True,
        nullable=False,
        foreign_key="measure.infos.id",
    )
    six_sec_l_cu: str = Field(default=None, index=False, nullable=True)
    six_sec_l_qu: str = Field(default=None, index=False, nullable=True)
    six_sec_l_ch: str = Field(default=None, index=False, nullable=True)
    six_sec_r_cu: str = Field(default=None, index=False, nullable=True)
    six_sec_r_qu: str = Field(default=None, index=False, nullable=True)
    six_sec_r_ch: str = Field(default=None, index=False, nullable=True)
    all_sec_analyze_raw_l_cu: str = Field(default=None, index=False, nullable=True)
    all_sec_analyze_raw_l_qu: str = Field(default=None, index=False, nullable=True)
    all_sec_analyze_raw_l_ch: str = Field(default=None, index=False, nullable=True)
    all_sec_analyze_raw_r_cu: str = Field(default=None, index=False, nullable=True)
    all_sec_analyze_raw_r_qu: str = Field(default=None, index=False, nullable=True)
    all_sec_analyze_raw_r_ch: str = Field(default=None, index=False, nullable=True)


class MeasureRaw(BaseUUIDModel, BaseTimestampModel, MeasureRawBase, table=True):
    __tablename__ = "raw_data"
    __table_args__ = {"schema": "measure"}
    measure_info: "MeasureInfo" = Relationship(
        back_populates="raw",
        sa_relationship_kwargs={"lazy": "select"},
    )
