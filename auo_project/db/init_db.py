from typing import Any, List

from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud, models
from auo_project.core.config import settings
from auo_project.schemas.action_schema import ActionCreate
from auo_project.schemas.group_schema import GroupCreate
from auo_project.schemas.org_schema import OrgCreate
from auo_project.schemas.role_schema import RoleCreate
from auo_project.schemas.user_schema import UserCreate


async def init_sample_data(db_session: AsyncSession) -> None:
    # create product categories
    product_categories = [
        models.ProductCategory(
            name="舌診",
            description="舌診產品類別",
            is_active=True,
        ),
        models.ProductCategory(
            name="脈診",
            description="脈診產品類別",
            is_active=True,
        ),
    ]
    db_session.add_all(product_categories)
    await db_session.commit()


async def init_db(db_session: AsyncSession) -> None:
    print("init db start")

    file_create = "file:create"
    file_read = "file:read"
    file_update = "file:update"
    file_delete = "file:delete"
    file_upload = "file:upload"
    upload_create = "upload:create"
    upload_read = "upload:read"
    upload_update = "upload:update"
    upload_delete = "upload:delete"
    tongue_app_upload = "tongue_app:upload"
    pulse_app_upload = "pulse_app:upload"
    tongue_cc_config_create = "tongue_cc_config_mgmt:create"
    tongue_cc_config_read = "tongue_cc_config_mgmt:read"
    tongue_cc_config_update = "tongue_cc_config_mgmt:update"
    tongue_cc_config_delete = "tongue_cc_config_mgmt:delete"
    tongue_cc_config_upload = "tongue_cc_config_mgmt:upload"
    product_mgmt_create = "product_mgmt:create"
    product_mgmt_read = "product_mgmt:read"
    product_mgmt_update = "product_mgmt:update"
    product_mgmt_delete = "product_mgmt:delete"
    org_mgmt_create = "org_mgmt:create"
    org_mgmt_read = "org_mgmt:read"
    org_mgmt_update = "org_mgmt:update"
    org_mgmt_delete = "org_mgmt:delete"
    branch_mgmt_create = "branch_mgmt:create"
    branch_mgmt_read = "branch_mgmt:read"
    branch_mgmt_update = "branch_mgmt:update"
    branch_mgmt_delete = "branch_mgmt:delete"
    branch_mgmt_upload = "branch_mgmt:upload"
    field_mgmt_create = "field_mgmt:create"
    field_mgmt_read = "field_mgmt:read"
    field_mgmt_update = "field_mgmt:update"
    field_mgmt_delete = "field_mgmt:delete"
    permission_mgmt_create = "permission_mgmt:create"
    permission_mgmt_read = "permission_mgmt:read"
    permission_mgmt_update = "permission_mgmt:update"
    permission_mgmt_delete = "permission_mgmt:delete"
    account_mgmt_create = "account_mgmt:create"
    account_mgmt_read = "account_mgmt:read"
    account_mgmt_update = "account_mgmt:update"
    account_mgmt_delete = "account_mgmt:delete"

    upload_owner = "UploadOwner"
    upload_creator = "UploadCreator"
    upload_reader = "UploadReader"
    role_fae = "FAE"
    role_measure_operator = "MeasureOperator"
    role_admin = "ConsoleManager"

    actions: List[ActionCreate] = [
        ActionCreate(name=file_create, description=""),
        ActionCreate(name=file_read, description=""),
        ActionCreate(name=file_update, description=""),
        ActionCreate(name=file_delete, description=""),
        ActionCreate(name=file_upload, description=""),
        ActionCreate(name=upload_create, description=""),
        ActionCreate(name=upload_read, description=""),
        ActionCreate(name=upload_update, description=""),
        ActionCreate(name=upload_delete, description=""),
        ActionCreate(name=tongue_app_upload, description=""),
        ActionCreate(name=pulse_app_upload, description=""),
        ActionCreate(name=tongue_cc_config_create, description=""),
        ActionCreate(name=tongue_cc_config_read, description=""),
        ActionCreate(name=tongue_cc_config_update, description=""),
        ActionCreate(name=tongue_cc_config_delete, description=""),
        ActionCreate(name=tongue_cc_config_upload, description=""),
        ActionCreate(name=product_mgmt_create, description=""),
        ActionCreate(name=product_mgmt_read, description=""),
        ActionCreate(name=product_mgmt_update, description=""),
        ActionCreate(name=product_mgmt_delete, description=""),
        ActionCreate(name=org_mgmt_create, description=""),
        ActionCreate(name=org_mgmt_read, description=""),
        ActionCreate(name=org_mgmt_update, description=""),
        ActionCreate(name=org_mgmt_delete, description=""),
        ActionCreate(name=branch_mgmt_create, description=""),
        ActionCreate(name=branch_mgmt_read, description=""),
        ActionCreate(name=branch_mgmt_update, description=""),
        ActionCreate(name=branch_mgmt_delete, description=""),
        ActionCreate(name=branch_mgmt_upload, description=""),
        ActionCreate(name=field_mgmt_create, description=""),
        ActionCreate(name=field_mgmt_read, description=""),
        ActionCreate(name=field_mgmt_update, description=""),
        ActionCreate(name=field_mgmt_delete, description=""),
        ActionCreate(name=permission_mgmt_create, description=""),
        ActionCreate(name=permission_mgmt_read, description=""),
        ActionCreate(name=permission_mgmt_update, description=""),
        ActionCreate(name=permission_mgmt_delete, description=""),
        ActionCreate(name=account_mgmt_create, description=""),
        ActionCreate(name=account_mgmt_read, description=""),
        ActionCreate(name=account_mgmt_update, description=""),
        ActionCreate(name=account_mgmt_delete, description=""),
    ]

    roles: List[Any] = [
        {
            "data": {
                "name_zh": "檔案管理人員",
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
                "name_zh": "檔案上傳人員",
                "description": "",
                "actions": [file_create, file_read, file_update, upload_create],
            },
            "name": upload_creator,
        },
        {
            "data": {
                "name_zh": "檔案讀取人員",
                "description": "",
                "actions": [file_read, upload_reader],
            },
            "name": upload_reader,
        },
        {
            "data": {
                "name_zh": "裝機人員",
                "description": "",
                "actions": [
                    tongue_cc_config_create,
                    tongue_cc_config_read,
                    tongue_cc_config_update,
                    tongue_cc_config_delete,
                    tongue_cc_config_upload,
                    org_mgmt_read,
                    branch_mgmt_read,
                    field_mgmt_read,
                ],
            },
            "name": role_fae,
        },
        {
            "data": {
                "name_zh": "量測人員",
                "description": "",
                "actions": [
                    tongue_app_upload,
                    pulse_app_upload,
                    tongue_cc_config_read,
                    tongue_cc_config_update,
                    tongue_cc_config_upload,
                ],
            },
            "name": role_measure_operator,
        },
        {
            "data": {
                "name_zh": "後台管理員",
                "description": "",
                "actions": [
                    product_mgmt_create,
                    product_mgmt_read,
                    product_mgmt_update,
                    product_mgmt_delete,
                    org_mgmt_create,
                    org_mgmt_read,
                    org_mgmt_update,
                    org_mgmt_delete,
                    branch_mgmt_create,
                    branch_mgmt_read,
                    branch_mgmt_update,
                    branch_mgmt_delete,
                    branch_mgmt_upload,
                    field_mgmt_create,
                    field_mgmt_read,
                    field_mgmt_update,
                    field_mgmt_delete,
                    permission_mgmt_create,
                    permission_mgmt_read,
                    permission_mgmt_update,
                    permission_mgmt_delete,
                    account_mgmt_create,
                    account_mgmt_read,
                    account_mgmt_update,
                    account_mgmt_delete,
                ],
            },
            "name": role_admin,
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
        OrgCreate(name="tph", description="部北醫院"),
        OrgCreate(name="tongue_label", description="舌象標記專用"),
        OrgCreate(name="nricm", description="國家中醫藥所"),
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
                    name_zh=role["data"]["name_zh"],
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
                username="auo_health_admin_user",
                password=settings.FIRST_SUPERUSER_PASSWORD,
                org_id=current_orgs[0].id,
                full_name="最高管理員",
                mobile="",
                email="admin@auohealth.com",
                is_active=True,
                is_superuser=True,
            ),
            "group_name": "admin",
        },
        {
            "data": UserCreate(
                username="manager_user",
                password=settings.USER_DEFAULT_PASSWORD,
                org_id=current_orgs[1].id,
                full_name="X 中心管理員",
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
                password=settings.USER_DEFAULT_PASSWORD,
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
                password=settings.USER_DEFAULT_PASSWORD,
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
                password=settings.USER_PASSWORD1,
                org_id=current_orgs[3].id,
                full_name="Y 中心管理員",
                mobile="",
                email="manager_user@ymedicalcenter.com.tw",
                is_active=True,
                is_superuser=False,
            ),
            "group_name": "manager",
        },
        {
            "data": UserCreate(
                username="helen.hua@auo.com",
                password=settings.USER_PASSWORD2,
                org_id=current_orgs[0].id,
                full_name="Helen",
                mobile="",
                email="helen.hua@auo.com",
                is_active=True,
                is_superuser=False,
            ),
            "group_name": "manager",
        },
        {
            "data": UserCreate(
                username="chief@tph.tw",
                password=settings.TPH_PASSWORD,
                org_id=current_orgs[4].id,
                full_name="TPH 管理員",
                mobile="",
                email="chief@tph.tw",
                is_active=True,
                is_superuser=False,
            ),
            "group_name": "manager",
        },
        {
            "data": UserCreate(
                username="lan@tph.tw",
                password="8s379Czji8TI7owf5NksdhivAHktq73k",
                org_id=current_orgs[4].id,
                full_name="TPH 醫師",
                mobile="",
                email="lan@tph.tw",
                is_active=True,
                is_superuser=False,
            ),
            "group_name": "user",
        },
        {
            "data": UserCreate(
                username="user1@tonguelabel.tw",
                password=settings.TONGUE_LABEL_PASSWORD1,
                org_id=current_orgs[5].id,
                full_name="舌象標記人員1",
                mobile="",
                email="user1@tonguelabel.tw",
                is_active=True,
                is_superuser=False,
            ),
            "group_name": "manager",
        },
        {
            "data": UserCreate(
                username="user2@tonguelabel.tw",
                password=settings.TONGUE_LABEL_PASSWORD2,
                org_id=current_orgs[5].id,
                full_name="舌象標記人員2",
                mobile="",
                email="user2@tonguelabel.tw",
                is_active=True,
                is_superuser=False,
            ),
            "group_name": "manager",
        },
        {
            "data": UserCreate(
                username="user3@tonguelabel.tw",
                password=settings.TONGUE_LABEL_PASSWORD3,
                org_id=current_orgs[5].id,
                full_name="舌象標記人員3",
                mobile="",
                email="user3@tonguelabel.tw",
                is_active=True,
                is_superuser=False,
            ),
            "group_name": "manager",
        },
        {
            "data": UserCreate(
                username="chief@nricm.org.tw",
                password=settings.NRICM_PASSWORD,
                org_id=current_orgs[6].id,
                full_name="NRICM 管理員",
                mobile="",
                email="chief@nricm.org.tw",
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
