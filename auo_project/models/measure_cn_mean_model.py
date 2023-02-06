from sqlmodel import Field, SQLModel, UniqueConstraint

from auo_project.models.base_model import BaseTimestampModel, BaseUUIDModel


class MeasureCNMeanBase(SQLModel):
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


class MeasureCNMean(
    BaseUUIDModel,
    BaseTimestampModel,
    MeasureCNMeanBase,
    table=True,
):
    __tablename__ = "cn_means"
    __table_args__ = (
        UniqueConstraint(
            "hand",
            "position",
            "sex",
            name="measure_cn_means_hand_position_sex_key",
        ),
        {"schema": "measure"},
    )
