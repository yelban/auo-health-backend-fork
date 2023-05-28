from sqlmodel import Field, UniqueConstraint

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class MeasureQuestionOptionBase(BaseModel):
    category_id: str = Field(
        index=True,
        nullable=False,
    )
    value: str = Field(
        index=True,
        nullable=False,
    )
    label: str = Field(
        index=False,
        nullable=False,
    )
    component: str = Field(
        index=False,
        nullable=False,
    )
    memo: str = Field(
        index=False,
        nullable=False,
    )


class MeasureQuestionOption(
    BaseUUIDModel,
    BaseTimestampModel,
    MeasureQuestionOptionBase,
    table=True,
):
    __tablename__ = "question_options"
    __table_args__ = (
        UniqueConstraint(
            "category_id",
            "value",
            name="measure_question_options_category_id_value_key",
        ),
        {"schema": "measure"},
    )
