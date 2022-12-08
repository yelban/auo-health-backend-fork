from datetime import timedelta
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud, schemas
from auo_project.core.config import settings
from auo_project.core.security import AuthJWT
from auo_project.web.api import deps

router = APIRouter()


@router.post("/token/login", response_model=schemas.LoginResponseToken)
async def login_access_token(
    db_session: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
    Authorize: AuthJWT = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await crud.user.authenticate(
        db_session=db_session,
        email=form_data.username,
        password=form_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect account name or password",
        )
    elif not (crud.user.is_active(user)):
        raise HTTPException(status_code=400, detail="Inactive user")
    sub = user.username

    access_token = Authorize.create_access_token(
        subject=sub,
        expires_delta=timedelta(settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    csrf_access_token = Authorize.csrf_token
    Authorize.set_access_cookies(
        access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    refresh_token = Authorize.create_refresh_token(
        subject=sub,
        expires_delta=timedelta(settings.REFRESH_TOKEN_EXPIRE_MINUTES),
    )
    csrf_refresh_token = Authorize.csrf_token
    Authorize.set_refresh_cookies(
        refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        # "csrf_access_token": csrf_access_token,
        # "csrf_refresh_token": csrf_refresh_token,
        "token_type": "bearer",
    }


@router.post("/token/refresh", response_model=schemas.Token)
async def refresh_access_token(
    db_session: AsyncSession = Depends(deps.get_db),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
    Authorize: AuthJWT = Depends(deps.require_jwt_token_refresh),
) -> Any:
    subject = Authorize.get_jwt_subject()
    user = await crud.user.get_by_username(db_session=db_session, username=subject)
    if user and user.is_active:
        new_access_token = Authorize.create_access_token(
            subject=user.username,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        Authorize.set_access_cookies(new_access_token)
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
        }
    else:
        raise HTTPException(status_code=404, detail="Inactive user")
