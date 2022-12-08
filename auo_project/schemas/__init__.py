from auo_project.schemas.file_schema import (
    FileCreate,
    FileRead,
    FileReadWithSimple,
    FileUpdate,
)
from auo_project.schemas.group_schema import GroupCreate, GroupRead, GroupUpdate
from auo_project.schemas.measure_infos_schema import MeasureInfos
from auo_project.schemas.org_schema import OrgCreate, OrgRead, OrgUpdate
from auo_project.schemas.role_schema import RoleCreate, RoleRead, RoleUpdate
from auo_project.schemas.subject_schema import Subject
from auo_project.schemas.subscription_schema import (
    SubscriptionCreate,
    SubscriptionRead,
    SubscriptionUpdate,
)
from auo_project.schemas.token_schema import LoginResponseToken, Token
from auo_project.schemas.upload_schema import (
    UploadCreate,
    UploadCreateReqBody,
    UploadListResponse,
    UploadRead,
    UploadReadWithEndpoint,
    UploadReadWithFilteredFile,
    UploadUpdate,
)
from auo_project.schemas.user_schema import (
    UserCreate,
    UserRead,
    UserReadWithUploads,
    UserUpdate,
    UserWithName,
)

# https://lightrun.com/answers/tiangolo-sqlmodel-are-many-to-many-link-supported-with-fastapi
UserRead.update_forward_refs(
    OrgRead=OrgRead,
    SubscriptionRead=SubscriptionRead,
    RoleRead=RoleRead,
    GroupRead=GroupRead,
)

UploadRead.update_forward_refs(
    File=FileRead,
    FileRead=FileRead,
    User=UserRead,
    UserWithName=UserWithName,
)

UploadReadWithEndpoint.update_forward_refs(
    File=FileRead,
    FileRead=FileRead,
    User=UserRead,
)

UploadReadWithFilteredFile.update_forward_refs(
    File=FileRead,
    FileRead=FileRead,
    User=UserRead,
)

UserReadWithUploads.update_forward_refs(
    OrgRead=OrgRead,
    SubscriptionRead=SubscriptionRead,
    RoleRead=RoleRead,
    GroupRead=GroupRead,
    Upload=UploadRead,
    UserWithName=UserWithName,
)

UploadListResponse.update_forward_refs(
    UploadRead=UploadRead,
    UserWithName=UserWithName,
    UploadReadWithFilteredFile=UploadReadWithFilteredFile,
)
