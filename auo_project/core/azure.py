from azure.storage.blob import BlobServiceClient

from auo_project.core.config import settings

blob_service = BlobServiceClient(
    account_url=f"https://{settings.AZURE_STORAGE_ACCOUNT}.blob.core.windows.net",
    credential={
        "account_name": settings.AZURE_STORAGE_ACCOUNT,
        "account_key": settings.AZURE_STORAGE_KEY,
    },
)
