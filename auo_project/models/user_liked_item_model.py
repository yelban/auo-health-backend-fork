from uuid import UUID

from auo_project.models.base_model import BaseModel, BaseTimestampModel, BaseUUIDModel

# revision identifiers, used by Alembic.
revision = "3eed9d8e701e"
down_revision = "574d2034f1d6"
branch_labels = None
depends_on = None


class UserLikedItemBase(BaseModel):
    user_id: UUID = Field(
        index=True,
        nullable=False,
        title="使用者編號",
    )
    item_type: str = Field(
        index=True,
        nullable=False,
        max_length=50,
        title="項目類型",
    )
    item_id: UUID = Field(
        index=True,
        nullable=False,
        title="項目編號",
    )
    is_active: bool = Field(
        index=False,
        nullable=False,
        title="是否啟用",
    )


class UserLikedItem(
    BaseUUIDModel,
    BaseTimestampModel,
    UserLikedItemBase,
    table=True,
):
    __tablename__ = "user_liked_items"
    __table_args__ = ({"schema": "app"},)
