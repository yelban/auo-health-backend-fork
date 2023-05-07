from sqlmodel import Field, UniqueConstraint

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class MeasureMeanBase(BaseModel):
    hand: str = Field(
        index=True,
        nullable=False,
        max_length=10,
    )
    position: str = Field(index=True, nullable=False, max_length=2)
    sex: int = Field(index=True, nullable=False)
    cnt: int = Field(nullable=False)
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


class MeasureMean(
    BaseUUIDModel,
    BaseTimestampModel,
    MeasureMeanBase,
    table=True,
):
    __tablename__ = "overall_means"
    __table_args__ = (
        UniqueConstraint(
            "hand",
            "position",
            "sex",
            name="measure_overall_means_hand_position_sex_key",
        ),
        {"schema": "measure"},
    )
