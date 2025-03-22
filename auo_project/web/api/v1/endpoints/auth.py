import random
import string
from datetime import datetime, timedelta
from typing import Any, Optional

from azure.communication.email import EmailClient
from fastapi import APIRouter, Form, HTTPException, Response
from fastapi.param_functions import Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud, schemas
from auo_project.core.config import settings
from auo_project.core.exceptions import CustomHTTPException
from auo_project.core.security import AuthJWT
from auo_project.web.api import deps


@dataclass
class AdditionalUserDataForm:
    pad_id: Optional[str] = Form(None, title="平板編號")
    device_id: Optional[str] = Form(None, title="舌診擷取設備編號")


class RecoveryRequestInputPayload(BaseModel):
    email: str = Field(..., title="Email")


class RecoveryVerifyInputPayload(BaseModel):
    email: str = Field(..., title="Email")
    token: str = Field(..., title="Token")


router = APIRouter()


@router.post("/token/login", response_model=schemas.LoginResponseToken)
async def login_access_token(
    db_session: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
    Authorize: AuthJWT = Depends(),
    allowed_header: bool = Depends(deps.check_allowed_headers),
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
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    csrf_access_token = Authorize.csrf_token
    Authorize.set_access_cookies(
        access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    refresh_token = Authorize.create_refresh_token(
        subject=sub,
        expires_delta=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
    )
    csrf_refresh_token = Authorize.csrf_token
    Authorize.set_refresh_cookies(
        refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "csrf_access_token": csrf_access_token,
        "csrf_refresh_token": csrf_refresh_token,
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


@router.post("/token/logout", response_model=schemas.LogoutResponse)
async def logout_token(
    response: Response,
    db_session: AsyncSession = Depends(deps.get_db),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
    allowed_header: bool = Depends(deps.check_allowed_headers),
) -> Any:
    """Logout and reset cookies"""
    response.delete_cookie("refresh_token_cookie")
    response.delete_cookie("access_token_cookie")
    response.delete_cookie("csrf_access_token")
    response.delete_cookie("csrf_refresh_token")

    return {"status": "success"}


@router.post("/token/recovery_request")
async def request_recovery_token(
    input_payload: RecoveryRequestInputPayload,
    db_session: AsyncSession = Depends(deps.get_db),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    """
    Request recovery token with 10 minutes expiration
    """
    N = 6
    user = await crud.user.get_by_email(
        db_session=db_session,
        email=input_payload.email,
    )
    if not user:
        raise CustomHTTPException(
            status_code=404,
            error_code="001",
            detail="User not found",
        )
    if not user.is_active:
        raise CustomHTTPException(
            status_code=400,
            error_code="002",
            detail="Inactive user",
        )
    if user:
        # create and save token
        while True:
            token = "".join(random.choices(string.ascii_uppercase + string.digits, k=N))
            exist = await crud.recovery_token.get_by_token(
                db_session=db_session,
                user_id=user.id,
                token=token,
            )
            if not exist:
                break

        # update active tokens to inactive
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

        expired_at = datetime.utcnow() + timedelta(minutes=10)
        recovery_token = await crud.recovery_token.create(
            db_session=db_session,
            obj_in=schemas.RecoveryTokenCreate(
                user_id=user.id,
                token=token,
                expired_at=expired_at,
                is_active=True,
            ),
        )
        # send email
        mail_status = ""
        try:
            email_client = EmailClient.from_connection_string(
                "endpoint=https://auohealthacs.asiapacific.communication.azure.com/;accesskey=AwrNMPEch11WsFr6AXsQ9Y5wPBnh7SqvfBHd5sScUDFnlupiAUGJJQQJ99AIACULyCpBm7CoAAAAAZCSPfj8",
            )
            message = {
                "content": {
                    "subject": "密碼重設驗證碼",
                    "html": f"<html><div>您好 {user.username},<br/>請輸入您的驗證碼:<br/><strong>{recovery_token.token}</strong></div></html>",
                },
                "recipients": {
                    "to": [{"address": user.email, "displayName": user.username}],
                },
                "senderAddress": "<donotreply@service.auohealth.com>",
            }
            poller = email_client.begin_send(message)
            mail_status = str(poller.result())
        except Exception as e:
            print(e)
            mail_status = f"failed: {e}"

        return {
            "status": "success",
            "token": recovery_token.token,  # TODO: remove token field
            "mail_status": mail_status,
        }


@router.post("/token/recovery_verify")
async def verify_recovery_token(
    input_payload: RecoveryVerifyInputPayload,
    db_session: AsyncSession = Depends(deps.get_db),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    """
    Verify recovery token validity
    """
    # get user by email
    user = await crud.user.get_by_email(
        db_session=db_session,
        email=input_payload.email,
    )
    if not user:
        raise CustomHTTPException(
            status_code=404,
            error_code="001",
            detail="User not found",
        )
    if not user.is_active:
        raise CustomHTTPException(
            status_code=400,
            error_code="002",
            detail="Inactive user",
        )

    # check token by user id
    recovery_token = await crud.recovery_token.get_by_token(
        db_session=db_session,
        user_id=user.id,
        token=input_payload.token,
    )
    if not recovery_token:
        raise CustomHTTPException(
            status_code=404,
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

    return {"status": "success"}
