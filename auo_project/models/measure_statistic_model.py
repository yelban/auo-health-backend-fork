from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from auo_project.models.base_model import BaseTimestampModel, BaseUUIDModel


class MeasureStatisticBase(SQLModel):
    measure_id: UUID = Field(index=True, nullable=False, foreign_key="measure.infos.id")
    statistic: str = Field(
        index=True,
        nullable=False,
        max_length=10,
    )
    hand: str = Field(
        index=True,
        nullable=False,
        max_length=10,
    )
    position: str = Field(index=True, nullable=False, max_length=2)
    a0: float = Field(default=None, nullable=True, title="")
    c1: float = Field(default=None, nullable=True)
    c2: float = Field(default=None, nullable=True)
    c3: float = Field(default=None, nullable=True)
    c4: float = Field(default=None, nullable=True)
    c5: float = Field(default=None, nullable=True)
    c6: float = Field(default=None, nullable=True)
    c7: float = Field(default=None, nullable=True)
    c8: float = Field(default=None, nullable=True)
    c9: float = Field(default=None, nullable=True)
    c10: float = Field(default=None, nullable=True)
    c11: float = Field(default=None, nullable=True)
    p1: float = Field(default=None, nullable=True)
    p2: float = Field(default=None, nullable=True)
    p3: float = Field(default=None, nullable=True)
    p4: float = Field(default=None, nullable=True)
    p5: float = Field(default=None, nullable=True)
    p6: float = Field(default=None, nullable=True)
    p7: float = Field(default=None, nullable=True)
    p8: float = Field(default=None, nullable=True)
    p9: float = Field(default=None, nullable=True)
    p10: float = Field(default=None, nullable=True)
    p11: float = Field(default=None, nullable=True)
    h1: float = Field(default=None, nullable=True)
    t1: float = Field(default=None, nullable=True)
    t: float = Field(default=None, nullable=True)
    pw: float = Field(default=None, nullable=True)
    w1: float = Field(default=None, nullable=True)
    w1_div_t: float = Field(default=None, nullable=True)
    h1_div_t1: float = Field(default=None, nullable=True)
    t1_div_t: float = Field(default=None, nullable=True)
    hr: int = Field(default=None, nullable=True)
    pass_num: int = Field(default=None, nullable=True)
    all_num: int = Field(default=None, nullable=True)
    pass_rate: float = Field(default=None, nullable=True)


class MeasureStatistic(
    BaseUUIDModel,
    BaseTimestampModel,
    MeasureStatisticBase,
    table=True,
):
    __tablename__ = "statistics"
    __table_args__ = (
        UniqueConstraint(
            "measure_id",
            "statistic",
            "hand",
            "position",
            name="measure_statistics_measure_id_statistic_hand_position_key",
        ),
        {"schema": "measure"},
    )
    measure_info: "MeasureInfo" = Relationship(
        back_populates="statistics",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
