from services.cosmos_db import CosmosDBService
from apps.products.models import Product
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

CONTAINER = 'products'


class ProductService:

    @staticmethod
    def create(data: dict) -> dict:
        # Ensure default values for optional fields
        if 'status' not in data:
            data['status'] = 'active'
            
        product = Product(**data)
        saved = CosmosDBService.upsert(CONTAINER, product.to_dict())

        try:
            from services.rag_search import RagSearchService
            RagSearchService.index_product(saved)
        except Exception as e:
            logger.warning(f"Failed to RAG index product {saved['id']}: {e}")

        return saved

    @staticmethod
    def get(product_id: str, shop_id: str) -> dict:
        return CosmosDBService.get_by_id(CONTAINER, product_id, shop_id)

    @staticmethod
    def list_all(user_id: str, page: int = 1, page_size: int = 20) -> tuple[list, int]:
        offset = (page - 1) * page_size
        query = """
            SELECT * FROM c
            WHERE c.status = 'active' AND c.user_id = @user_id
            ORDER BY c.created_at DESC
            OFFSET @offset LIMIT @limit
        """
        count_query = "SELECT VALUE COUNT(1) FROM c WHERE c.status = 'active' AND c.user_id = @user_id"
        params = [
            {"name": "@user_id", "value": user_id},
            {"name": "@offset", "value": offset},
            {"name": "@limit", "value": page_size},
        ]
        items = CosmosDBService.query(CONTAINER, query, params)
        counts = CosmosDBService.query(CONTAINER, count_query, [{"name": "@user_id", "value": user_id}])
        total = counts[0] if counts else 0
        return items, total

    @staticmethod
    def update(product_id: str, shop_id: str, data: dict) -> dict:
        existing = CosmosDBService.get_by_id(CONTAINER, product_id, shop_id)
        existing.update(data)
        existing['updated_at'] = datetime.now(timezone.utc).isoformat()
        return CosmosDBService.upsert(CONTAINER, existing)

    @staticmethod
    def delete(product_id: str, shop_id: str) -> None:
        existing = CosmosDBService.get_by_id(CONTAINER, product_id, shop_id)
        existing['status'] = 'deleted'
        existing['updated_at'] = datetime.now(timezone.utc).isoformat()
        CosmosDBService.upsert(CONTAINER, existing)
