import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from auo_project.core.constants import UploadStatusType


@pytest.mark.anyio
async def test_cancel_file(client: AsyncClient, fastapi_app: FastAPI) -> None:
    """


    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """
    url = fastapi_app.url_path_for("create_upload")
    expected_files = ["testfile1.zip", "testfile2.zip"]
    payload = {"filename_list": expected_files}
    response = await client.post(url, json=payload)
    assert response.status_code == 200
    result = response.json()

    url = fastapi_app.url_path_for("cancel_upload", upload_id=result["id"])
    response = await client.post(url)
    assert response.status_code == 200
    result = response.json()

    assert result["upload_status"] == UploadStatusType.failed.value
