from http.cookies import SimpleCookie
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud, models
from auo_project.core.config import settings
from auo_project.core.security import AuthJWT, decode_jwt_token
from auo_project.db.session import SessionLocal, async_session_factory, engine
from auo_project.models.user_model import User
from auo_project.services.celery import celery_app

# TODO: merge
JSONObject = Dict[str, Any]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


import contextlib


@contextlib.asynccontextmanager
async def get_db2() -> AsyncGenerator[AsyncSession, None]:
    try:
        db = async_session_factory()
        yield db
    finally:
        await db.close()
        await engine.dispose()


def get_celery_app():
    return celery_app


# def get_current_user2() -> User:
#     async def current_user(
#         db_session: AsyncSession = Depends(get_db),
#         Authorize: AuthJWT = Depends(),
#         required_groups: List[str] = None,
#         required_roles: List[str] = None,
#         required_actions: List[str] = None,
#     ) -> User:
#         try:
#             Authorize.jwt_access_token_required()
#             payload = Authorize.get_raw_jwt

#         except (jwt.JWTError, ValidationError):
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Could not validate credentials",
#             )
#         user: User = await crud.user.get_by_username(
#             db_session=db_session, username=payload["sub"]
#         )
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")

#         if not user.is_active:
#             raise HTTPException(status_code=400, detail="Inactive user")

#         if not crud.user.has_requires(
#             db_session=db_session,
#             user=user,
#             groups=required_groups,
#             roles=required_roles,
#             actions=required_actions,
#         ):
#             raise HTTPException(
#                 status_code=403,
#                 detail=f'The action requires Group "{required_groups}" / Role "{required_roles}" / Action "{required_actions}"',
#             )

#         return user

#     return current_user


# # def get_current_user(required_groups: List[str] = None, required_roles: List[str] = None, required_actions: List[str] = None) -> User:
# def get_current_user() -> User:
#     async def current_user(db_session: AsyncSession = Depends(get_db), Authorize: AuthJWT = Depends()) -> User:
#         try:
#             # payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
#             Authorize.jwt_access_token_required()
#             payload = Authorize.get_raw_jwt()

#         except (jwt.JWTError, ValidationError):
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Could not validate credentials",
#             )
#         user: User = await crud.user.get_by_username(db_session=db_session, name=payload["sub"])
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")

#         if not user.is_active:
#             raise HTTPException(status_code=400, detail="Inactive user")

#         # if not crud.user.has_requires(db_session=db_session, user=user, groups=required_groups, roles=required_roles, actions=required_actions):
#         #     raise HTTPException(
#         #         status_code=403,
#         #         detail=f'The action requires Group "{required_groups}" / Role "{required_roles}" / Action "{required_actions}"',
#         #     )

#         return user

#     return current_user


async def get_current_user(
    db_session: AsyncSession = Depends(get_db),
    Authorize: AuthJWT = Depends(),
) -> User:
    try:
        Authorize.jwt_access_token_required()
        payload = Authorize.get_raw_jwt

    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user: User = await crud.user.get_by_username(
        db_session=db_session,
        username=payload["sub"],
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_user_with_perm(
    required_groups: List[str] = None,
    required_roles: List[str] = None,
    required_actions: List[str] = None,
) -> Callable:
    async def has_requires(user) -> bool:
        return crud.user.has_requires(
            user=user,
            groups=required_groups,
            roles=required_roles,
            actions=required_actions,
        )

    async def depend(
        user=Depends(get_current_active_user),
    ) -> Optional[User]:
        if not await has_requires(user):
            items = [
                ("Group", required_groups),
                ("Role", required_roles),
                ("Action", required_actions),
            ]
            content = " or ".join(
                [item[0] + ": " + ",".join(item[1]) for item in items if item[1]],
            )
            raise HTTPException(
                status_code=403,
                detail=f"The request requires {content}",
            )
        return user

    return depend


def get_ip_allowed(cf_ipcountry: Optional[str] = Header("")):
    if not "TW" in cf_ipcountry:
        print("The IP is not allowed.")
    else:
        print("The IP is allowed.")
    #     raise HTTPException(
    #         status_code=403,
    #         detail=f"The IP is not allowed.",
    #     )
    return True


# check referer and origin header as a CSRF protection
# ref: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html#identifying-source-origin-via-originreferer-header
def check_allowed_headers(
    origin: Optional[str] = Header(""),
    referer: Optional[str] = Header(""),
):
    # if not origin:
    #     raise HTTPException()
    #     if origin
    print(origin, referer)


def require_jwt_token_refresh(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()
    return Authorize


def get_raw_jwt_access_token(Authorize: AuthJWT = Depends()):
    Authorize.jwt_access_token_required()
    return Authorize.get_raw_jwt


async def get_current_active_user_for_tus(
    arbitrary_json: JSONObject = None,
    db_session: AsyncSession = Depends(get_db),
) -> models.User:
    # TODO: replace with pydash
    cookies_str: str = arbitrary_json["HTTPRequest"]["Header"]["Cookie"][0]
    if not cookies_str:
        raise HTTPException(status_code=400, detail="Missing cookie")

    cookie = SimpleCookie(cookies_str)
    encoded_token = cookie.get("access_token_cookie")
    if not encoded_token:
        raise HTTPException(
            status_code=400,
            detail="Missing access_token_cookie of cookie",
        )
    payload = decode_jwt_token(encoded_token.value, settings.SECRET_KEY)
    user: models.User = await crud.user.get_by_username(
        db_session=db_session,
        username=payload["sub"],
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user
