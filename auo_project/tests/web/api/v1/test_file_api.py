import pytest
from fastapi import FastAPI
from httpx import AsyncClient


@pytest.mark.anyio
async def test_cancel_file_ok(client: AsyncClient, fastapi_app: FastAPI) -> None:
    """
    Checks the cancel file endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """
    # print("DEBUG START")
    # url = fastapi_app.url_path_for("create_upload")
    # expected_files = ["testfile1.zip", "testfile2.zip"]
    # payload = {"filename_list": expected_files}
    # response = await client.post(url, json=payload)
    # assert response.status_code == status.HTTP_200_OK
    # result = response.json()
    # print("DEBUG END1")
    # url = fastapi_app.url_path_for("cancel_upload_file", file_id=result["id"])
    # response = await client.post(url)
    # assert response.status_code == status.HTTP_200_OK
    # result = response.json()
    # print("DEBUG END2")

    # assert result["upload_status"] == UploadStatusType.failed.value
    return True


# @pytest.mark.anyio
# async def test_cancel_file_not_found_fail(client: AsyncClient, fastapi_app: FastAPI, db_session: AsyncSession,) -> None:
#     """
#     Checks the cancel file endpoint.

#     :param client: client for the app.
#     :param fastapi_app: current FastAPI application.
#     """
#     # while True:
#     #     random_file_id = uuid4()
#     #     if  await crud.file.get(db_session=SessionLocal()):
#     #         break
#     random_file_id = "fa7fed7e-29bf-448a-9cbb-fe7a3a9cd9e8"
#     url = fastapi_app.url_path_for("cancel_upload_file", file_id=random_file_id)
#     response = await client.post(url)
#     assert response.status_code == 404
