import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from auo_project.core.config import settings


@pytest.mark.anyio
async def test_user_me(client: AsyncClient, fastapi_app: FastAPI) -> None:
    """
    Checks the user me endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """
    url = fastapi_app.url_path_for("read_user_me")
    response = await client.get(url)
    assert response.status_code == 200
    result = response.json()
    assert settings.FIRST_SUPERUSER_EMAIL == result["email"]
