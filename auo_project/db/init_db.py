from typing import Any, List

from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud
from auo_project.core.config import settings
from auo_project.schemas.action_schema import ActionCreate
from auo_project.schemas.group_schema import GroupCreate
from auo_project.schemas.org_schema import OrgCreate
from auo_project.schemas.role_schema import RoleCreate
from auo_project.schemas.user_schema import UserCreate


async def init_db(db_session: AsyncSession) -> None:
    print("init db start")

    file_create = "file:create"
    file_read = "file:read"
    file_update = "file:update"
    file_delete = "file:delete"
    upload_create = "upload:create"
    upload_read = "upload:read"
    upload_update = "upload:update"
    upload_delete = "upload:delete"

    upload_owner = "UploadOwner"
    upload_creator = "UploadCreator"
    upload_reader = "UploadReader"

    actions: List[ActionCreate] = [
        ActionCreate(name=file_create, description=""),
        ActionCreate(name=file_read, description=""),
        ActionCreate(name=file_update, description=""),
        ActionCreate(name=file_delete, description=""),
        ActionCreate(name=upload_create, description=""),
        ActionCreate(name=upload_read, description=""),
        ActionCreate(name=upload_update, description=""),
        ActionCreate(name=upload_delete, description=""),
    ]

    roles: List[Any] = [
        {
            "data": {
                "description": "",
                "actions": [
                    file_create,
                    file_read,
                    file_update,
                    file_delete,
                    upload_create,
                    upload_reader,
                    upload_update,
                    upload_delete,
                ],
            },
            "name": upload_owner,
        },
        {
            "data": {
                "description": "",
                "actions": [file_create, file_read, file_update, upload_create],
            },
            "name": upload_creator,
        },
        {
            "data": {
                "description": "",
                "actions": [file_read, upload_reader],
            },
            "name": upload_reader,
        },
    ]

    groups: List[GroupCreate] = [
        GroupCreate(name="admin", description="Admin group"),
        GroupCreate(name="manager", description="Manager group"),
        GroupCreate(name="user", description="User group"),
        GroupCreate(name="subject", description="Subject group"),
    ]

    group_roles = [
        ("admin", [upload_owner]),
        ("manager", [upload_owner]),
        ("user", [upload_creator, upload_reader]),
        ("subject", []),
    ]

    orgs: List[OrgCreate] = [
        OrgCreate(name="auo_health", description="AUO Health"),
        OrgCreate(name="x_medical_center", description="X Medical Center"),
        OrgCreate(name=settings.FIRST_SUPERUSER_ORG_NAME, description="First Org"),
        OrgCreate(name="y_medical_center", description="Y Medical Center"),
    ]

    for action in actions:
        action_current = await crud.action.get_by_name(
            db_session=db_session,
            name=action.name,
        )
        if not action_current:
            await crud.action.create(obj_in=action, db_session=db_session)

    for role in roles:
        role_current = await crud.role.get_by_name(
            db_session=db_session,
            name=role["name"],
        )
        if not role_current:
            role_current = await crud.role.create(
                obj_in=RoleCreate(
                    name=role["name"],
                    description=role["data"]["description"],
                ),
                db_session=db_session,
            )
        for role_action in role["data"]["actions"]:
            if role_action not in role_current.actions:
                action = await crud.action.get_by_name(
                    db_session=db_session,
                    name=role_action,
                )
                if action:
                    await crud.role.add_action_to_role(
                        db_session=db_session,
                        action=action,
                        role_id=role_current.id,
                    )

    for obj_in in groups:
        if not await crud.group.get_by_name(db_session=db_session, name=obj_in.name):
            await crud.group.create(db_session=db_session, obj_in=obj_in)
    current_groups = [
        await crud.group.get_by_name(db_session=db_session, name=obj_in.name)
        for obj_in in orgs
    ]

    for group_role in group_roles:
        current_group = await crud.group.get_by_name(
            db_session=db_session,
            name=group_role[0],
        )
        for require_role_name in group_role[1]:
            require_role = await crud.role.get_by_name(
                db_session=db_session,
                name=require_role_name,
            )
            if require_role not in current_group.roles:
                await crud.role.add_role_to_group(
                    db_session=db_session,
                    group=current_group,
                    role_id=require_role.id,
                )

    for obj_in in orgs:
        if not await crud.org.get_by_name(db_session=db_session, name=obj_in.name):
            await crud.org.create(db_session=db_session, obj_in=obj_in)
    current_orgs = [
        await crud.org.get_by_name(db_session=db_session, name=org_in.name)
        for org_in in orgs
    ]

    users: List[Any] = [
        {
            "data": UserCreate(
                username=settings.FIRST_SUPERUSER_EMAIL,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                org_id=current_orgs[2].id,
                full_name="最高管理員",
                mobile="",
                email=settings.FIRST_SUPERUSER_EMAIL,
                is_active=True,
                is_superuser=True,
            ),
            "group_name": "admin",
        },
        {
            "data": UserCreate(
                username="auo_health_admin_user",
                password="***REMOVED***",
                org_id=current_orgs[0].id,
                full_name="最高管理員",
                mobile="",
                email="admin@auo.com",
                is_active=True,
                is_superuser=True,
            ),
            "group_name": "admin",
        },
        {
            "data": UserCreate(
                username="manager_user",
                password="***REMOVED***",
                org_id=current_orgs[1].id,
                full_name="X醫療中心管理員",
                mobile="",
                email="manager_user@xmedicalcenter.com.tw",
                is_active=True,
                is_superuser=False,
            ),
            "group_name": "manager",
        },
        {
            "data": UserCreate(
                username="sample_user",
                password="***REMOVED***",
                org_id=current_orgs[1].id,
                full_name="X先生1號",
                mobile="",
                email="sample_user@xmedicalcenter.com.tw",
                is_active=True,
                is_superuser=False,
            ),
            "group_name": "user",
        },
        {
            "data": UserCreate(
                username="sample_subject",
                password="***REMOVED***",
                org_id=current_orgs[1].id,
                full_name="受測者1號",
                mobile="",
                email="sample_subject@xmedicalcenter.com.tw",
                is_active=True,
                is_superuser=False,
            ),
            "group_name": "subject",
        },
        {
            "data": UserCreate(
                username="manager_user@ymedicalcenter.com.tw",
                password="***REMOVED***",
                org_id=current_orgs[3].id,
                full_name="Y醫療中心管理員",
                mobile="",
                email="manager_user@ymedicalcenter.com.tw",
                is_active=True,
                is_superuser=False,
            ),
            "group_name": "manager",
        },
        {
            "data": UserCreate(
                username="hellen.hua@auo.com",
                password="***REMOVED***",
                org_id=current_orgs[0].id,
                full_name="Helen",
                mobile="",
                email="hellen.hua@auo.com",
                is_active=True,
                is_superuser=False,
            ),
            "group_name": "manager",
        },
    ]

    for user_in in users:
        user = await crud.user.get_by_email(
            email=user_in["data"].email,
            db_session=db_session,
        )
        if not user:
            await crud.user.create(obj_in=user_in["data"], db_session=db_session)
        else:
            await crud.user.update(
                db_session=db_session,
                db_obj=user,
                obj_in=user_in["data"],
            )
    for user_in in users:
        current_user = await crud.user.get_by_email(
            email=user_in["data"].email,
            db_session=db_session,
        )
        if not current_user.groups:
            current_group = await crud.group.get_by_name(
                name=user_in["group_name"],
                db_session=db_session,
            )
            await crud.group.add_user_to_group(
                user=current_user,
                group_id=current_group.id,
                db_session=db_session,
            )
    print("init db end")
