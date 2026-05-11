import asyncio
import httpx
import threading
from services.cosmos_db import CosmosDBService
from services.scraper import ShopeeScraperService
from apps.links.models import AffLink
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

CONTAINER = 'links'


class LinkService:

    @staticmethod
    def create_and_process(url: str, user_id: str = 'default') -> dict:
        if not ShopeeScraperService.validate_url(url):
            from apps.core.exceptions import InvalidShopeeURL
            raise InvalidShopeeURL()

        link = AffLink(
            original_url=url,
            user_id=user_id,
            status='pending'
        )
        saved = CosmosDBService.upsert(CONTAINER, link.to_dict())
        logger.info(f"Link {saved['id']} created, processing in background...")

        def process_in_thread():
            try:
                asyncio.run(LinkService._process_with_third_party(saved['id'], url, user_id))
            except Exception as e:
                logger.error(f"Background processing failed for {saved['id']}: {e}", exc_info=True)

        threading.Thread(target=process_in_thread, daemon=True).start()

        return saved

    @staticmethod
    async def _process_with_third_party(link_id: str, url: str, user_id: str) -> None:
        try:
            LinkService._update_status(link_id, 'processing', user_id)

            resolved_url = await ShopeeScraperService.resolve_redirect(url)
            shop_id, item_id = ShopeeScraperService.extract_ids_from_url(resolved_url)
            logger.info(f"Link {link_id}: resolved shop_id={shop_id} item_id={item_id}")

            api_url = f"https://data.addlivetag.com/product-data/product-data.php?item_id={item_id}"
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(api_url)
            response.raise_for_status()

            body = response.json()
            if body.get('status') != 'success' or not body.get('productInfo'):
                raise ValueError(f"Third-party API error: {body}")

            info = body['productInfo']
            logger.info(f"Link {link_id}: got product '{info.get('productName')}'")

            link = CosmosDBService.get_by_id(CONTAINER, link_id, user_id)
            link.update({
                'title': info.get('productName', ''),
                'shop_id': str(shop_id),
                'shop_name': info.get('shopName', ''),
                'item_id': str(item_id),
                'thumbnail_url': info.get('imageUrl', ''),
                'price': info.get('price'),
                'resolved_url': resolved_url,
                'status': 'done',
                'updated_at': datetime.now(timezone.utc).isoformat(),
            })
            CosmosDBService.upsert(CONTAINER, link)
            logger.info(f"Link {link_id}: done ✅")

            try:
                from services.rag_search import RagSearchService
                RagSearchService.index_link(link)
            except Exception as e:
                logger.warning(f"RAG index failed for link {link_id}: {e}")

        except Exception as e:
            logger.error(f"Link {link_id}: failed ❌ {e}", exc_info=True)
            LinkService._update_status(link_id, 'failed', user_id, str(e))

    @staticmethod
    def _update_status(link_id: str, status: str, user_id: str, error: str = None) -> None:
        link = CosmosDBService.get_by_id(CONTAINER, link_id, user_id)
        link['status'] = status
        link['updated_at'] = datetime.now(timezone.utc).isoformat()
        if error:
            link['error_message'] = error
        CosmosDBService.upsert(CONTAINER, link)

    @staticmethod
    def get(link_id: str, user_id: str = 'default') -> dict:
        return CosmosDBService.get_by_id(CONTAINER, link_id, user_id)

    @staticmethod
    def list_for_user(user_id: str = 'default', page: int = 1, page_size: int = 20) -> tuple:
        offset = (page - 1) * page_size
        query = """
            SELECT * FROM c
            WHERE c.user_id = @user_id
            ORDER BY c.created_at DESC
            OFFSET @offset LIMIT @limit
        """
        items = CosmosDBService.query(CONTAINER, query, [
            {"name": "@user_id", "value": user_id},
            {"name": "@offset", "value": offset},
            {"name": "@limit", "value": page_size},
        ])
        return items, len(items)

    @staticmethod
    def list_done_for_user(user_id: str, page: int = 1, page_size: int = 20) -> tuple[list, int]:
        offset = (page - 1) * page_size
        query = """
            SELECT * FROM c
            WHERE c.user_id = @user_id AND c.status = 'done'
            ORDER BY c.created_at DESC
            OFFSET @offset LIMIT @limit
        """
        count_query = """
            SELECT VALUE COUNT(1) FROM c
            WHERE c.user_id = @user_id AND c.status = 'done'
        """
        params = [{"name": "@user_id", "value": user_id}]
        items = CosmosDBService.query(CONTAINER, query, params + [
            {"name": "@offset", "value": offset},
            {"name": "@limit", "value": page_size},
        ])
        counts = CosmosDBService.query(CONTAINER, count_query, params)
        total = counts[0] if counts else 0
        return items, total
