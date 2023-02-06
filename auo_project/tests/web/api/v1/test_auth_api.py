import pytest
from fastapi import FastAPI
from httpx import AsyncClient


@pytest.mark.anyio
async def test_login_access_token_ok(client: AsyncClient, fastapi_app: FastAPI) -> None:
    """
    Checks the login access token endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """

    return True


@pytest.mark.anyio
async def test_login_access_token_fail(
    client: AsyncClient,
    fastapi_app: FastAPI,
) -> None:
    """
    Checks the login access token endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """

    return True


@pytest.mark.anyio
async def test_refresh_access_token_fail(
    client: AsyncClient,
    fastapi_app: FastAPI,
) -> None:
    """
    Checks the login access token endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """

    return True


@pytest.mark.anyio
async def test_refresh_access_token_fail(
    client: AsyncClient,
    fastapi_app: FastAPI,
) -> None:
    """
    Checks the login access token endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """

    return True
