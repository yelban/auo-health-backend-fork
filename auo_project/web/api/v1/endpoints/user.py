from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud, schemas
from auo_project.core.exceptions import CustomHTTPException
from auo_project.web.api import deps

router = APIRouter()


def verify_password(new_password: str, confirmed_password: str) -> None:
    if new_password != confirmed_password:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match",
        )
    if len(new_password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters",
        )
    if not any(char.isdigit() for char in new_password) or not any(
        char.isalpha() for char in new_password
    ):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one letter and one number",
        )


@router.get("/me", response_model=schemas.UserRead)
async def read_user_me(
    *,
    current_user: schemas.UserRead = Depends(deps.get_current_active_user),
    db_session: AsyncSession = Depends(deps.get_db),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Get current user information, permission and configs.
    """
    auth_org_branches = await crud.user_branch.get_auth_org_branches(
        db_session=db_session,
        user_id=current_user.id,
    )
    return schemas.UserRead(
        **current_user.dict(),
        auth_org_branches=auth_org_branches,
        roles=current_user.roles,
    )


@router.get("/test", response_model=schemas.UserRead)
async def test_user_perm(
    current_user: schemas.UserRead = Depends(
        deps.get_current_user_with_perm(required_roles=["UploadCreator"]),
    ),
) -> Any:
    return current_user


@router.get("/list_item/like", response_model=list[schemas.UserLikedItemRead])
async def get_liked_items(
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: schemas.UserRead = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get liked items.
    """
    items = await crud.user_liked_item.get_by_user_id(
        db_session=db_session,
        user_id=current_user.id,
    )
    return items


@router.post("/list_item/like")
async def like_items(
    input_payload: schemas.UserLikeItemInput,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: schemas.UserRead = Depends(deps.get_current_active_user),
) -> Any:
    """
    Like items.
    """
    exist_items = await crud.user_liked_item.get_by_item_type_and_ids(
        db_session=db_session,
        user_id=current_user.id,
        item_type=input_payload.item_type,
        item_ids=input_payload.item_ids,
        is_active=None,
    )
    exist_item_ids_set = set([item.item_id for item in exist_items])
    user_like_items = [
        schemas.UserLikedItemCreate(
            user_id=current_user.id,
            item_type=input_payload.item_type,
            item_id=item_id,
            is_active=True,
        )
        for item_id in input_payload.item_ids
        if item_id not in exist_item_ids_set
    ]
    for user_like_item in user_like_items:
        await crud.user_liked_item.create(
            db_session=db_session,
            obj_in=user_like_item,
            autocommit=False,
        )
    await db_session.commit()
    return {"msg": "success"}


@router.post("/list_item/dislike")
async def dislike_items(
    input_payload: schemas.UserLikeItemInput,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: schemas.UserRead = Depends(deps.get_current_active_user),
) -> Any:
    """
    Dilike items.
    """
    exist_items = await crud.user_liked_item.get_by_item_type_and_ids(
        db_session=db_session,
        user_id=current_user.id,
        item_type=input_payload.item_type,
        item_ids=input_payload.item_ids,
        is_active=None,
    )
    for item in exist_items:
        await crud.user_liked_item.remove(
            db_session=db_session,
            id=item.id,
            autocommit=False,
        )
    await db_session.commit()
    return {"msg": "success"}


@router.post("/recover/password")
async def recover_password(
    input_payload: schemas.UserRecoverPassword,
    db_session: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Recover password when forget password.
    """
    user = await crud.user.get_by_email(
        db_session=db_session,
        email=input_payload.email,
    )
    if not user:
        # raise HTTPException(
        #     status_code=400,
        #     detail="User not found",
        # )
        raise CustomHTTPException(
            status_code=400,
            error_code="001",
            detail="User not found",
        )
    if not user.is_active:
        # raise HTTPException(
        #     status_code=400,
        #     detail="Inactive user",
        # )
        raise CustomHTTPException(
            status_code=400,
            error_code="002",
            detail="Inactive user",
        )

    verify_password(input_payload.new_password, input_payload.confirm_password)

    # TODO: verify token
    recovery_token = await crud.recovery_token.get_by_token(
        db_session=db_session,
        user_id=user.id,
        token=input_payload.token,
    )
    if not recovery_token:
        raise CustomHTTPException(
            status_code=400,
            error_code="003",
            detail="Token not found",
        )
    if recovery_token.is_active == False:
        raise CustomHTTPException(
            status_code=400,
            error_code="004",
            detail="Token is not active",
        )
    if recovery_token.expired_at < datetime.utcnow():
        raise CustomHTTPException(
            status_code=400,
            error_code="004",
            detail="Token is expired",
        )

    await crud.recovery_token.update(
        db_session=db_session,
        obj_current=recovery_token,
        obj_new=schemas.RecoveryTokenUpdate(is_active=False),
    )
    await crud.user.update(
        db_session=db_session,
        db_obj=user,
        obj_in=schemas.UserUpdate(password=input_payload.new_password),
    )

    # get active tokens and set them to inactive
    recovery_tokens = await crud.recovery_token.get_active_tokens(
        db_session=db_session,
        user_id=user.id,
    )
    for recovery_token in recovery_tokens:
        await crud.recovery_token.update(
            db_session=db_session,
            obj_current=recovery_token,
            obj_new=schemas.RecoveryTokenUpdate(is_active=False),
        )
    return {"msg": "success"}


@router.post("/reset/password")
async def reset_password(
    input_payload: schemas.UserResetPassword,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: schemas.UserRead = Depends(deps.get_current_active_user),
) -> Any:
    """
    Reset password when login.
    """
    verify_password(input_payload.new_password, input_payload.confirm_password)

    valid_user = await crud.user.authenticate(
        db_session=db_session,
        email=current_user.email,
        password=input_payload.old_password,
    )
    if valid_user is None:
        raise HTTPException(
            status_code=400,
            detail="Incorrect old password",
        )
    if valid_user and valid_user.id != current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Incorrect old password",
        )

    await crud.user.update(
        db_session=db_session,
        db_obj=current_user,
        obj_in=schemas.UserUpdate(password=input_payload.new_password),
    )
    return {"msg": "success"}
