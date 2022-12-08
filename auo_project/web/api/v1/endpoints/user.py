from typing import Any

from fastapi import APIRouter
from fastapi.param_functions import Depends

from auo_project import schemas
from auo_project.web.api import deps

router = APIRouter()


@router.get("/me", response_model=schemas.UserRead)
def read_user_me(
    *,
    current_user: schemas.UserRead = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Get current user information, permission and configs.
    """
    return current_user


@router.get("/test", response_model=schemas.UserRead)
async def test_user_perm(
    current_user: schemas.UserRead = Depends(
        deps.get_current_user_with_perm(required_groups=["user"]),
    ),
) -> Any:
    return current_user
