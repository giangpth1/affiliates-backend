import httpx
import uuid
from azure.storage.blob import BlobServiceClient, ContentSettings
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class AzureStorageService:
    _client = None

    @classmethod
    def get_client(cls) -> BlobServiceClient:
        if cls._client is None:
            cls._client = BlobServiceClient.from_connection_string(
                settings.AZURE_STORAGE_CONNECTION_STRING
            )
        return cls._client

    @classmethod
    async def upload_image_from_url(cls, image_url: str) -> str:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(image_url)
            response.raise_for_status()
            content_type = response.headers.get('content-type', 'image/jpeg')
            image_data = response.content

        blob_name = f"{uuid.uuid4()}.jpg"
        blob_client = cls.get_client().get_blob_client(
            container=settings.AZURE_STORAGE_CONTAINER,
            blob=blob_name
        )

        blob_client.upload_blob(
            image_data,
            content_settings=ContentSettings(content_type=content_type),
            overwrite=True
        )

        return blob_client.url
