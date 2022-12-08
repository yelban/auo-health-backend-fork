from auo_project.schemas.file_schema import FileRead
from auo_project.schemas.group_schema import GroupRead
from auo_project.schemas.org_schema import OrgRead
from auo_project.schemas.role_schema import RoleRead
from auo_project.schemas.subscription_schema import SubscriptionRead
from auo_project.schemas.upload_schema import (
    UploadListResponse,
    UploadRead,
    UploadReadWithEndpoint,
    UploadReadWithFilteredFile,
)
from auo_project.schemas.user_schema import UserRead, UserReadWithUploads, UserWithName

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
