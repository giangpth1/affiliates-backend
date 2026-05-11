from azure.cosmos import CosmosClient, exceptions
from django.conf import settings
from apps.core.exceptions import DocumentNotFound, CosmosDBError
import logging

logger = logging.getLogger(__name__)


class CosmosDBService:
    _client = None
    _database = None

    @classmethod
    def get_client(cls) -> CosmosClient:
        if cls._client is None:
            cls._client = CosmosClient(
                url=settings.COSMOS_DB_URL,
                credential=settings.COSMOS_DB_KEY
            )
        return cls._client

    @classmethod
    def get_database(cls):
        if cls._database is None:
            cls._database = cls.get_client().get_database_client(
                settings.COSMOS_DB_DATABASE
            )
        return cls._database

    @classmethod
    def get_container(cls, container_name: str):
        return cls.get_database().get_container_client(container_name)

    @classmethod
    def upsert(cls, container_name: str, document: dict) -> dict:
        try:
            container = cls.get_container(container_name)
            return container.upsert_item(document)
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Cosmos DB upsert error: {e}")
            raise CosmosDBError(detail=str(e))

    @classmethod
    def get_by_id(cls, container_name: str, item_id: str, partition_key: str) -> dict:
        try:
            container = cls.get_container(container_name)
            return container.read_item(item=item_id, partition_key=partition_key)
        except exceptions.CosmosResourceNotFoundError:
            raise DocumentNotFound(detail=f"Document {item_id} not found.")
        except exceptions.CosmosHttpResponseError as e:
            raise CosmosDBError(detail=str(e))

    @classmethod
    def query(cls, container_name: str, query: str, parameters: list = None) -> list:
        try:
            container = cls.get_container(container_name)
            return list(container.query_items(
                query=query,
                parameters=parameters or [],
                enable_cross_partition_query=True
            ))
        except exceptions.CosmosHttpResponseError as e:
            raise CosmosDBError(detail=str(e))

    @classmethod
    def delete(cls, container_name: str, item_id: str, partition_key: str) -> None:
        try:
            container = cls.get_container(container_name)
            container.delete_item(item=item_id, partition_key=partition_key)
        except exceptions.CosmosResourceNotFoundError:
            raise DocumentNotFound(detail=f"Document {item_id} not found.")
