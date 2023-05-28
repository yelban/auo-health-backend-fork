from sqlmodel import Field

from auo_project.models.base_model import BaseModel, BaseTimestampModel


class MeasureParameterBase(BaseModel):
    id: str = Field(
        primary_key=True,
        index=True,
        nullable=False,
    )
    p_type: str = Field(
        index=True,
        nullable=False,
    )
    label: str = Field(
        index=False,
        nullable=False,
    )
    has_childs: bool = Field(
        index=False,
        nullable=False,
    )
    parent_id: str = Field(
        index=True,
        nullable=False,
    )
    option_type: str = Field(
        index=False,
        nullable=False,
    )
    option_component: str = Field(
        index=False,
        nullable=False,
    )
    option_category_id: str = Field(
        index=True,
        nullable=False,
    )


class MeasureParameter(
    BaseTimestampModel,
    MeasureParameterBase,
    table=True,
):
    __tablename__ = "parameters"
    __table_args__ = ({"schema": "measure"},)
