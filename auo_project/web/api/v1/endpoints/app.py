from typing import Any

from fastapi import APIRouter
from fastapi.param_functions import Depends

from auo_project import schemas
from auo_project.web.api import deps

router = APIRouter()


@router.get("/copyright")
async def get_copyright_info(
    current_user: schemas.UserRead = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get copyright
    """
    return {
        "content": """本網站內所有資料之著作權、所有權與智慧財產權，包括文字、圖片、聲音、影像、軟體…等，均為麥書原創作品或依法向原作者或代理人機構取得合法重製授權。未經許可，禁止任何形式的複製、重製，直接或間接做為商業用途使用。© 2024 AUO. All rights reserved.""",
    }


@router.get("/contact")
async def get_contact_info(
    current_user: schemas.UserRead = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get contact
    """
    return "聯絡我們範例聯絡我們範例，聯絡我們範例聯絡我們範例，聯絡我們範例聯絡我們範例聯絡我們範例，聯絡我們範例。"


@router.get("/countries")
async def get_countries(
    current_user: schemas.UserRead = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get countries
    """
    return [
        {"label": "台灣"},
        {"label": "日本"},
        {"label": "美國"},
    ]
