from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

_search_client = None


def get_search_client() -> SearchClient:
    global _search_client
    if _search_client is None:
        _search_client = SearchClient(
            endpoint=settings.AZURE_SEARCH_ENDPOINT,
            index_name=settings.AZURE_SEARCH_INDEX,
            credential=AzureKeyCredential(settings.AZURE_SEARCH_KEY)
        )
    return _search_client


class AzureSearchService:

    @staticmethod
    def index_product(product: dict) -> None:
        client = get_search_client()

        document = {
            'id': product['id'],
            'title': product.get('title', ''),
            'category': product.get('category', ''),
            'shop_id': product.get('shop_id', ''),
            'item_id': product.get('item_id', ''),
            'thumbnail_url': product.get('thumbnail_url', ''),
            'original_url': product.get('original_url', ''),
            'price': product.get('price'),
            'price_currency': product.get('price_currency', 'VND'),
            'created_at': product.get('created_at', ''),
        }

        result = client.upload_documents(documents=[document])
        if not result[0].succeeded:
            logger.error(f"Failed to index product {product['id']}: {result[0].errors}")

    @staticmethod
    def index_products_batch(products: list[dict]) -> None:
        if not products:
            return

        documents = []
        for product in products:
            documents.append({
                'id': product['id'],
                'title': product.get('title', ''),
                'category': product.get('category', ''),
                'shop_id': product.get('shop_id', ''),
                'item_id': product.get('item_id', ''),
                'thumbnail_url': product.get('thumbnail_url', ''),
                'original_url': product.get('original_url', ''),
                'price': product.get('price'),
                'price_currency': product.get('price_currency', 'VND'),
                'created_at': product.get('created_at', ''),
            })

        client = get_search_client()
        client.upload_documents(documents=documents)

    @staticmethod
    def semantic_search(
        query: str,
        top: int = 10,
        min_price: float = None,
        max_price: float = None,
    ) -> list[dict]:
        client = get_search_client()

        filters = []
        if min_price is not None:
            filters.append(f"price ge {min_price}")
        if max_price is not None:
            filters.append(f"price le {max_price}")
        filter_str = " and ".join(filters) if filters else None

        results = client.search(
            search_text=query,
            filter=filter_str,
            query_type="semantic",
            semantic_configuration_name="semantic-config",
            top=top,
            select=["id", "title", "thumbnail_url", "original_url", "price", "price_currency", "shop_id", "created_at"],
            highlight_fields="title",
        )

        output = []
        for result in results:
            item = dict(result)
            item['score'] = result['@search.score']
            item['highlights'] = result.get('@search.highlights', {})
            output.append(item)

        return output

    @staticmethod
    def delete_product(product_id: str) -> None:
        client = get_search_client()
        client.delete_documents(documents=[{'id': product_id}])
