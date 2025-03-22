from typing import Optional

from fastapi import APIRouter, Header

router = APIRouter()


@router.get("/origin")
def check_origin(
    origin: Optional[str] = Header(
        None,
        description="Origin. e.g. curl https://customhost.com/api/v1/tools/origin -H 'Origin: http://localhost:8000'",
    ),
) -> None:
    return {"origin": origin}
