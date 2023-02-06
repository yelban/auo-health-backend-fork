from azure.storage.blob import BlobServiceClient

from auo_project.core.config import settings

blob_service = BlobServiceClient(
    account_url=f"https://{settings.AZURE_STORAGE_ACCOUNT}.blob.core.windows.net",
    credential={
        "account_name": settings.AZURE_STORAGE_ACCOUNT,
        "account_key": settings.AZURE_STORAGE_KEY,
    },
)

internet_blob_service = BlobServiceClient(
    account_url=f"https://{settings.AZURE_STORAGE_ACCOUNT_INTERNET}.blob.core.windows.net",
    credential={
        "account_name": settings.AZURE_STORAGE_ACCOUNT_INTERNET,
        "account_key": settings.AZURE_STORAGE_KEY_INTERNET,
    },
)


def upload_internet_file(
    blob_service_client,
    category,
    file_path,
    object,
    overwrite=True,
):
    blob_client = blob_service_client.get_blob_client(
        container=category,
        blob=file_path,
    )
    blob_client.upload_blob(object, overwrite=overwrite)
    return file_path


def download_zip_file(blob_service_client, file_path):
    blob_client = blob_service_client.get_blob_client(
        container=settings.AZURE_STORAGE_CONTAINER_RAW_ZIP,
        blob=file_path,
    )
    return blob_client.download_blob()
