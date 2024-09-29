from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from auo_project.core.config import settings
from auo_project.models.user_model import UserBase
from auo_project.schemas.user_branch_schema import AuthOrgBranches


class UserRead(UserBase):
    id: UUID
    org: Optional["OrgRead"] = None
    subscription: Optional["SubscriptionRead"] = None
    roles: List["RoleRead"] = []
    groups: List["GroupRead"] = []
    auth_org_branches: List[AuthOrgBranches] = Field(default=[], title="有權限查看的組織與分支機構。")

    menus: List[str] = Field(default=[], title="有權限查看的側邊欄。")
    rows_per_page: int = Field(default=settings.ROWS_PER_PAGE, title="列表一頁呈現幾筆資料。")
    max_size_per_file: int = Field(
        default=settings.MAX_SIZE_PER_FILE,
        title="單一檔案大小限制，單位為 MB。",
    )
    max_size_per_upload: int = Field(
        default=settings.MAX_SIZE_PER_UPLOAD,
        title="每次上傳最大檔案數。",
    )
    max_upload_concurrency: int = Field(
        default=settings.MAX_UPLOAD_CONCURRENCY,
        title="最大同時上傳檔案數。",
    )


class UserReadWithUploads(UserRead):
    uploads: List["Upload"] = []


class UserWithName(UserBase):
    id: UUID
    full_name: str


class UserCreate(BaseModel):
    org_id: UUID
    username: str
    full_name: str
    mobile: str
    email: EmailStr
    is_active: bool
    is_superuser: bool
    password: str  # TODO: SecretStr


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserRecoverPassword(BaseModel):
    email: EmailStr
    token: str
    new_password: str
    confirm_password: str


class UserResetPassword(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str
