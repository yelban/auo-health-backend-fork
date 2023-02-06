from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from auo_project.models.base_model import BaseTimestampModel, BaseUUIDModel


class BCQBase(SQLModel):
    measure_id: UUID = Field(
        index=True,
        unique=True,
        nullable=False,
        foreign_key="measure.infos.id",
    )
    score_yang: int = Field(None, title="總分-陽(int)")
    score_yin: int = Field(None, title="總分-陰(int)")
    score_phlegm: int = Field(None, title="總分-痰瘀(int)")
    score_yang_head: int = Field(None, title="總分-陽-頭部(int)")
    score_yang_chest: int = Field(None, title="總分-陽-胸部(int)")
    score_yang_limbs: int = Field(None, title="總分-陽-四肢(int)")
    score_yang_abdomen: int = Field(None, title="總分-陽-腹腔(int)")
    score_yang_surface: int = Field(None, title="總分-陽-體表(int)")
    score_yin_head: int = Field(None, title="總分-陰-頭部(int)")
    score_yin_limbs: int = Field(None, title="總分-陰-四肢(int)")
    score_yin_gt: int = Field(None, title="總分-陰-腸胃道(int)")
    score_yin_surface: int = Field(None, title="總分-陰-體表(int)")
    score_yin_abdomen: int = Field(None, title="總分-陰-腹腔(int)")
    score_phlegm_trunk: int = Field(None, title="總分-痰瘀-軀幹(int)")
    score_phlegm_surface: int = Field(None, title="總分-痰瘀-體表(int)")
    score_phlegm_head: int = Field(None, title="總分-痰瘀-頭部(int)")
    score_phlegm_gt: int = Field(None, title="總分-痰瘀-腸胃道(int)")
    percentage_yang: int = Field(None, title="百分比-陽(int)")
    percentage_yin: int = Field(None, title="百分比-陰(int)")
    percentage_phlegm: int = Field(None, title="百分比-痰瘀(int)")
    percentage_yang_head: int = Field(None, title="百分比-陽-頭部(int)")
    percentage_yang_chest: int = Field(None, title="百分比-陽-胸部(int)")
    percentage_yang_limbs: int = Field(None, title="百分比-陽-四肢(int)")
    percentage_yang_abdomen: int = Field(None, title="百分比-陽-腹腔(int)")
    percentage_yang_surface: int = Field(None, title="百分比-陽-體表(int)")
    percentage_yin_head: int = Field(None, title="百分比-陰-頭部(int)")
    percentage_yin_limbs: int = Field(None, title="百分比-陰-四肢(int)")
    percentage_yin_gt: int = Field(None, title="百分比-陰-腸胃道(int)")
    percentage_yin_surface: int = Field(None, title="百分比-陰-體表(int)")
    percentage_yin_abdomen: int = Field(None, title="百分比-陰-腹腔(int)")
    percentage_phlegm_trunk: int = Field(None, title="百分比-痰瘀-軀幹(int)")
    percentage_phlegm_surface: int = Field(None, title="百分比-痰瘀-體表(int)")
    percentage_phlegm_head: int = Field(None, title="百分比-痰瘀-頭部(int)")
    percentage_phlegm_gt: int = Field(None, title="百分比-痰瘀-腸胃道(int)")


class BCQ(BaseUUIDModel, BaseTimestampModel, BCQBase, table=True):
    __tablename__ = "bcqs"
    __table_args__ = {"schema": "measure"}
    measure_info: "MeasureInfo" = Relationship(
        back_populates="bcq",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
