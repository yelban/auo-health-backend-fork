from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status

from auo_project.core.constants import FileStatusType, UploadStatusType


@pytest.mark.anyio
async def test_cancel_file_ok(client: AsyncClient, fastapi_app: FastAPI) -> None:
    """
    Checks the cancel file endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """
    url = fastapi_app.url_path_for("create_upload")
    expected_files = ["testfile1.zip", "testfile2.zip"]
    payload = {"filename_list": expected_files}
    response = await client.post(url, json=payload)
    assert response.status_code == status.HTTP_200_OK
    result = response.json()

    for file in result["files"]:
        url = fastapi_app.url_path_for("cancel_upload_file", file_id=file["id"])
        response = await client.post(url)
        assert response.status_code == status.HTTP_200_OK

    url = fastapi_app.url_path_for("get_upload", upload_id=result["id"])
    response = await client.get(url)
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    for file in result["files"]:
        assert file["file_status"] == FileStatusType.canceled.value

    assert result["upload_status"] == UploadStatusType.success.value


@pytest.mark.anyio
async def test_cancel_file_not_found_fail(
    client: AsyncClient,
    fastapi_app: FastAPI,
) -> None:
    """
    Checks the cancel file endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """
    random_file_id = uuid4()
    while True:
        random_file_id = uuid4()
        url = fastapi_app.url_path_for("get_upload_file", file_id=random_file_id)
        response = await client.get(url)
        if response.status_code == status.HTTP_404_NOT_FOUND:
            break
    url = fastapi_app.url_path_for("cancel_upload_file", file_id=random_file_id)
    response = await client.post(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
