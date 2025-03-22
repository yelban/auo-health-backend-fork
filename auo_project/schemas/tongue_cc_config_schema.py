from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from auo_project.core.constants import TongueSideType
from auo_project.models.tongue_cc_configs_model import TongueCCConfigBase


class TongueCCConfigRead(TongueCCConfigBase):
    id: UUID


class TongueCCConfigCreate(TongueCCConfigBase):
    pass


class TongueCCConfigUpdate(BaseModel):
    cc_status: Optional[int] = Field(default=None, title="校色狀態")
    pad_name: Optional[str] = Field(default=None, title="平板名稱")
    front_contrast: Optional[int] = Field(default=None, title="舌面對比度", example=0)
    front_brightness: Optional[int] = Field(default=None, title="舌面亮度", example=0)
    front_saturation: Optional[int] = Field(default=None, title="舌面飽和度", example=0)
    front_hue: Optional[int] = Field(default=None, title="舌面色調", example=0)
    front_contrast_stretch_black_point: Optional[float] = Field(
        default=None,
        title="舌面對比拉伸 - 黑點",
        example=0,
    )
    front_contrast_stretch_white_point: Optional[float] = Field(
        default=None,
        title="舌面對比拉伸 - 白點",
        example=100,
    )
    front_gamma: Optional[float] = Field(
        default=None,
        title="舌面Gamma值",
        example=1.0,
        ge=0.1,
        le=2.0,
    )
    back_contrast: Optional[int] = Field(default=None, title="舌背對比度", example=0)
    back_brightness: Optional[int] = Field(default=None, title="舌背亮度", example=0)
    back_saturation: Optional[int] = Field(default=None, title="舌背飽和度", example=0)
    back_hue: Optional[int] = Field(default=None, title="舌背色調", example=0)
    back_contrast_stretch_black_point: Optional[float] = Field(
        default=None,
        title="舌背對比拉伸 - 黑點",
        example=100,
    )
    back_contrast_stretch_white_point: Optional[float] = Field(
        default=None,
        title="舌背對比拉伸 - 白點",
        example=100,
    )
    back_gamma: Optional[float] = Field(
        default=None,
        title="舌背Gamma值",
        example=1.0,
        ge=0.1,
        le=2.0,
    )
    is_active: Optional[bool] = Field(default=None, example=True)
    front_img_loc: Optional[str] = Field(default=None, title="原始舌面圖片")
    back_img_loc: Optional[str] = Field(default=None, title="原始舌背圖片")
    cc_front_img_loc: Optional[str] = Field(default=None, title="校色舌面圖片")
    cc_back_img_loc: Optional[str] = Field(default=None, title="校色舌背圖片")
    cc_front_saved: Optional[bool] = Field(default=None, title="舌面校色是否已儲存")
    cc_back_saved: Optional[bool] = Field(default=None, title="舌背校色是否已儲存")
    device_id: Optional[str] = Field(default=None, title="舌診擷取設備編號")
    pad_id: Optional[str] = Field(default=None, title="平板編號")
    pad_name: Optional[str] = Field(default=None, title="平板名稱")


class TongueCCConfigCreateInput(BaseModel):
    pass


class TongueCCConfigPreviewInput(BaseModel):
    front_or_back: TongueSideType = Field(
        title="舌面或舌背",
        description="front 舌面，back 舌背",
        example="front",
    )
    contrast: int = Field(title="對比度", example=0, ge=-100, le=100)
    brightness: int = Field(title="亮度", example=0, ge=-100, le=100)
    saturation: int = Field(title="飽和度", example=0, ge=-100, le=100)
    hue: int = Field(title="色調", example=0, ge=-100, le=100)
    contrast_stretch_black_point: float = Field(
        title="對比拉伸 - 黑點",
        example=0,
        ge=0,
        le=100,
    )
    contrast_stretch_white_point: float = Field(
        title="對比拉伸 - 白點",
        example=100,
        ge=0,
        le=100,
    )
    gamma: float = Field(title="Gamma值", example=1.0, ge=0.1, le=2.0)


class TongueCCConfigPreviewOutput(BaseModel):
    preview_cc_image_url: str


class TongueCCConfigUpdateInput(BaseModel):
    front_contrast: Optional[int] = Field(default=None, title="舌面對比度", example=0)
    front_brightness: Optional[int] = Field(default=None, title="舌面亮度", example=0)
    front_saturation: Optional[int] = Field(default=None, title="舌面飽和度", example=0)
    front_hue: Optional[int] = Field(default=None, title="舌面色調", example=0)
    front_contrast_stretch_black_point: Optional[float] = Field(
        default=None,
        title="舌面對比拉伸 - 黑點",
        example=0,
    )
    front_contrast_stretch_white_point: Optional[float] = Field(
        default=None,
        title="舌面對比拉伸 - 白點",
        example=100,
    )
    front_gamma: Optional[float] = Field(
        default=None,
        title="舌面Gamma值",
        example=1.0,
        ge=0.1,
        le=2.0,
    )
    back_contrast: Optional[int] = Field(default=None, title="舌背對比度", example=0)
    back_brightness: Optional[int] = Field(default=None, title="舌背亮度", example=0)
    back_saturation: Optional[int] = Field(default=None, title="舌背飽和度", example=0)
    back_hue: Optional[int] = Field(default=None, title="舌背色調", example=0)
    back_contrast_stretch_black_point: Optional[float] = Field(
        default=None,
        title="舌背對比拉伸 - 黑點",
        example=100,
    )
    back_contrast_stretch_white_point: Optional[float] = Field(
        default=None,
        title="舌背對比拉伸 - 白點",
        example=100,
    )
    back_gamma: Optional[float] = Field(
        default=None,
        title="舌背Gamma值",
        example=1.0,
        ge=0.1,
        le=2.0,
    )


class TongueCCConfigUpdateCCStatusInput(BaseModel):
    cc_status: int = Field(
        ...,
        title="校色狀態",
    )
