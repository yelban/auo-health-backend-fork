from datetime import datetime
from uuid import UUID

from sqlmodel import Field, Relationship

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel


class TongueCCConfigBase(BaseModel):
    org_id: UUID = Field(
        index=True,
        nullable=False,
        foreign_key="app.auth_orgs.id",
        title="組織編號",
    )
    user_id: UUID = Field(
        index=True,
        nullable=False,
        foreign_key="app.auth_users.id",
        title="上傳者編號",
    )
    field_id: UUID = Field(
        index=True,
        nullable=False,
        unique=True,
        foreign_key="app.fields.id",
        title="場域編號",
    )
    device_id: str = Field(
        index=True,
        nullable=False,
        unique=True,
        title="舌診擷取設備編號",
    )
    pad_id: str = Field(
        index=True,
        nullable=False,
        title="平板編號",
    )
    pad_name: str = Field(
        index=False,
        nullable=False,
        title="平板名稱",
    )
    cc_status: int = Field(
        index=False,
        nullable=False,
        title="校色狀態",
    )
    front_img_loc: str = Field(
        index=False,
        nullable=True,
        title="原始舌面圖片",
    )
    back_img_loc: str = Field(
        index=False,
        nullable=True,
        title="原始舌背圖片",
    )
    cc_front_img_loc: str = Field(
        index=False,
        nullable=True,
        title="校色舌面圖片",
    )
    cc_back_img_loc: str = Field(
        index=False,
        nullable=True,
        title="校色舌背圖片",
    )
    front_contrast: int = Field(
        index=False,
        nullable=False,
        title="對比度",
    )
    front_brightness: int = Field(
        index=False,
        nullable=False,
        title="亮度",
    )
    front_saturation: int = Field(
        index=False,
        nullable=False,
        title="飽和度",
    )
    front_hue: int = Field(
        index=False,
        nullable=False,
        title="色調",
    )
    front_contrast_stretch_black_point: float = Field(
        index=False,
        nullable=False,
        title="對比拉伸 - 黑點",
    )
    front_contrast_stretch_white_point: float = Field(
        index=False,
        nullable=False,
        title="對比拉伸 - 白點",
    )
    front_gamma: float = Field(
        index=False,
        nullable=False,
        title="Gamma值",
    )
    back_contrast: int = Field(
        index=False,
        nullable=False,
        title="對比度",
    )
    back_brightness: int = Field(
        index=False,
        nullable=False,
        title="亮度",
    )
    back_saturation: int = Field(
        index=False,
        nullable=False,
        title="飽和度",
    )
    back_hue: int = Field(
        index=False,
        nullable=False,
        title="色調",
    )
    back_contrast_stretch_black_point: float = Field(
        index=False,
        nullable=False,
        title="對比拉伸 - 黑點",
    )
    back_contrast_stretch_white_point: float = Field(
        index=False,
        nullable=False,
        title="對比拉伸 - 白點",
    )
    back_gamma: float = Field(
        index=False,
        nullable=False,
        title="Gamma值",
    )
    upload_file_loc: str = Field(
        index=False,
        nullable=False,
    )
    last_uploaded_at: datetime = Field(index=False, nullable=True)
    color_hash: str = Field(
        index=True,
        nullable=False,
    )
    cc_front_saved: bool = Field(
        index=False,
        nullable=True,
        default=False,
    )
    cc_back_saved: bool = Field(
        index=False,
        nullable=True,
        default=False,
    )
    is_active: bool = Field(
        default=True,
        unique=False,
        index=False,
        nullable=False,
    )


class TongueCCConfig(BaseUUIDModel, BaseTimestampModel, TongueCCConfigBase, table=True):
    __tablename__ = "tongue_cc_configs"
    __table_args__ = {"schema": "measure"}

    field: "BranchField" = Relationship(
        back_populates="tongue_cc_config",
        sa_relationship_kwargs={"lazy": "select"},
    )
