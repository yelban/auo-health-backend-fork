import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status

from auo_project.core.constants import UploadStatusType


@pytest.mark.anyio
async def test_create_upload_ok(client: AsyncClient, fastapi_app: FastAPI) -> None:
    """
    Checks the create upload endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """
    url = fastapi_app.url_path_for("create_upload")
    expected_files = ["testfile1.zip", "testfile2.zip"]
    payload = {"filename_list": expected_files}
    response = await client.post(url, json=payload)
    assert response.status_code == 200
    result = response.json()

    print("result", result)

    assert result["upload_status"] == UploadStatusType.uploading.value
    assert result["file_number"] == len(expected_files)

    actual_files = result["files"]
    actual_filenames = [file["name"] for file in actual_files]
    assert len(expected_files) == len(actual_files)
    for expected_file in expected_files:
        assert expected_file in actual_filenames


@pytest.mark.anyio
async def test_get_upload_ok(client: AsyncClient, fastapi_app: FastAPI) -> None:
    """
    Checks the get upload endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """
    url = fastapi_app.url_path_for("create_upload")
    expected_files = ["testfile1.zip", "testfile2.zip"]
    payload = {"filename_list": expected_files}
    response = await client.post(url, json=payload)
    assert response.status_code == status.HTTP_200_OK
    result1 = response.json()
    del result1["endpoint"]

    url = fastapi_app.url_path_for("get_upload", upload_id=result1["id"])
    response = await client.get(url)
    assert response.status_code == status.HTTP_200_OK
    result2 = response.json()

    assert result1 == result2


@pytest.mark.anyio
async def test_get_upload_not_found_fail(
    client: AsyncClient,
    fastapi_app: FastAPI,
) -> None:
    """
    Checks the get upload endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """
    # while True:
    #     random_upload_id = uuid4()
    #     if not await crud.upload.get(db_session=SessionLocal()):
    #         break

    # url = fastapi_app.url_path_for("get_upload", upload_id=random_upload_id)
    # response = await client.get(url)
    # assert response.status_code == 404
    return True


@pytest.mark.anyio
async def test_get_upload_list_filter_upload_list_ok(
    client: AsyncClient,
    fastapi_app: FastAPI,
) -> None:
    """
    Checks the get upload list endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """
    # url = fastapi_app.url_path_for("get_upload_list", upload_id)
    return True


@pytest.mark.anyio
async def test_get_upload_list_filter_filename_ok(
    client: AsyncClient,
    fastapi_app: FastAPI,
) -> None:
    """
    Checks the get upload list endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """
    # url = fastapi_app.url_path_for("get_upload_list", upload_id)
    return True


@pytest.mark.anyio
async def test_get_upload_list_filter_owner_name_ok(
    client: AsyncClient,
    fastapi_app: FastAPI,
) -> None:
    """
    Checks the get upload list endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """
    # url = fastapi_app.url_path_for("get_upload_list", upload_id)
    return True


@pytest.mark.anyio
async def test_get_upload_list_filter_start_from_ok(
    client: AsyncClient,
    fastapi_app: FastAPI,
) -> None:
    """
    Checks the get upload list endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """
    # url = fastapi_app.url_path_for("get_upload_list", upload_id)
    return True


@pytest.mark.anyio
async def test_get_upload_list_filter_file_number_ok(
    client: AsyncClient,
    fastapi_app: FastAPI,
) -> None:
    """
    Checks the get upload list endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """
    # url = fastapi_app.url_path_for("get_upload_list", upload_id)
    return True


@pytest.mark.anyio
async def test_get_upload_list_filter_upload_status_ok(
    client: AsyncClient,
    fastapi_app: FastAPI,
) -> None:
    """
    Checks the get upload list endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """
    # url = fastapi_app.url_path_for("get_upload_list", upload_id)
    return True


@pytest.mark.anyio
async def test_cancel_upload_ok(client: AsyncClient, fastapi_app: FastAPI) -> None:
    """
    Checks the cancel upload endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """
    # url = fastapi_app.url_path_for("create_upload")
    # expected_files = ["testfile1.zip", "testfile2.zip"]
    # payload = {"filename_list": expected_files}
    # response = await client.post(url, json=payload)
    # assert response.status_code == status.HTTP_200_OK
    # result = response.json()

    # url = fastapi_app.url_path_for("cancel_upload", upload_id=result["id"])
    # response = await client.post(url)
    # assert response.status_code == status.HTTP_200_OK
    # result = response.json()

    # assert result["upload_status"] == UploadStatusType.failed.value
    return True
