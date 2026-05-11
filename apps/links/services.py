import asyncio
import httpx
import threading
from services.cosmos_db import CosmosDBService
from services.scraper import ShopeeScraperService
from services.azure_storage import AzureStorageService
from apps.links.models import AffLink
from apps.products.services import ProductService
from django.conf import settings
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

CONTAINER = 'links'


class LinkService:

    @staticmethod
    def create_and_process(url: str, user_id: str = 'default', async_mode: bool = True) -> dict:
        """
        Create link and process scraping.
        
        Args:
            url: Shopee affiliate link (short or full)
            user_id: User ID
            async_mode: If True, processes in background and returns immediately (recommended)
                       If False, waits for scraping to complete (blocks for 5-10s)
        
        Returns:
            Link dict with status='pending' (async) or status='done'/'failed' (sync)
        """
        if not ShopeeScraperService.validate_url(url):
            from apps.core.exceptions import InvalidShopeeURL
            raise InvalidShopeeURL()

        link = AffLink(
            original_url=url,
            user_id=user_id,
            status='pending'
        )
        saved = CosmosDBService.upsert(CONTAINER, link.to_dict())
        
        function_url = settings.FUNCTION_APP_URL
        
        if async_mode:
            # ASYNC MODE: Return immediately, process in background
            logger.info(f"Creating link {saved['id']} in async mode (will process in background)")
            
            if function_url and function_url.startswith('http'):
                # Production: Use Azure Function App
                LinkService._trigger_async_scraping(saved['id'], url)
            else:
                # Development: Use background thread (simulates Function App)
                def process_in_thread():
                    try:
                        asyncio.run(LinkService._process_sync(saved['id'], url))
                    except Exception as e:
                        logger.error(f"Background processing failed for {saved['id']}: {e}", exc_info=True)
                
                thread = threading.Thread(target=process_in_thread, daemon=True)
                thread.start()
                logger.info(f"Started background thread for link {saved['id']}")
            
            # Return pending link immediately
            return saved
        else:
            # SYNC MODE: Wait for completion (blocks request)
            logger.warning(f"Creating link {saved['id']} in SYNC mode (will block for 5-10s)")
            try:
                asyncio.run(LinkService._process_sync(saved['id'], url))
                saved = CosmosDBService.get_by_id(CONTAINER, saved['id'], user_id)
                logger.info(f"Link {saved['id']} processed successfully: {saved.get('status')}")
            except Exception as e:
                logger.error(f"Sync processing failed for {saved['id']}: {e}", exc_info=True)
            
            return saved

    @staticmethod
    def create_pending(url: str, user_id: str = 'default') -> dict:
        """Legacy method - use create_and_process instead."""
        return LinkService.create_and_process(url, user_id)

    @staticmethod
    def _trigger_async_scraping(link_id: str, url: str) -> None:
        """
        Trigger async scraping via Azure Function App.
        
        Falls back to local scraping if Function App is unreachable.
        """
        function_url = settings.FUNCTION_APP_URL
        
        try:
            payload = {'link_id': link_id, 'url': url}
            headers = {'x-functions-key': settings.FUNCTION_APP_KEY}
            with httpx.Client(timeout=90) as client:  # Increased to 90s for HTTP scraping fallback
                response = client.post(
                    f"{function_url}/api/scrape_product",
                    json=payload,
                    headers=headers
                )
                if response.status_code in [200, 202]:
                    logger.info(f"Function App triggered successfully for link {link_id}")
                    return
        except Exception as e:
            logger.warning(f"Failed to trigger Function App: {e}. Falling back to local scraping.")
        
        # Fallback: Process locally in background THREAD (don't block!)
        logger.info(f"Processing scraping locally in background thread for link {link_id}")
        
        def process_in_thread():
            try:
                asyncio.run(LinkService._process_sync(link_id, url))
            except Exception as e:
                logger.error(f"Background processing failed for {link_id}: {e}", exc_info=True)
        
        thread = threading.Thread(target=process_in_thread, daemon=True)
        thread.start()
    
    @staticmethod
    def _trigger_scraping(link_id: str, url: str) -> None:
        """Legacy method - use _trigger_async_scraping instead."""
        LinkService._trigger_async_scraping(link_id, url)

    @staticmethod
    async def _process_sync(link_id: str, url: str) -> None:
        """Process scraping synchronously."""
        try:
            logger.info(f"Starting scraping for link {link_id}, URL: {url}")
            LinkService._update_status(link_id, 'processing')

            # Step 1: Resolve short link to full URL
            logger.info(f"Resolving redirect for: {url}")
            resolved_url = await ShopeeScraperService.resolve_redirect(url)
            logger.info(f"Resolved to: {resolved_url}")
            
            # Step 1.5: Randomize URL params to avoid detection
            from services.url_randomizer import randomize_shopee_url
            randomized_url = randomize_shopee_url(resolved_url)
            logger.info(f"Randomized URL for scraping: {randomized_url}")
            
            # Step 2: Extract shop_id and item_id
            shop_id, item_id = ShopeeScraperService.extract_ids_from_url(resolved_url)
            logger.info(f"Extracted shop_id={shop_id}, item_id={item_id}")
            
            # Step 3: Scrape product data with Playwright (use randomized URL)
            logger.info(f"Scraping product data with randomized URL...")
            scraped = await ShopeeScraperService.scrape_product(randomized_url)
            logger.info(f"Scraped: title='{scraped.get('title')}', thumbnail={bool(scraped.get('thumbnail_original'))}, price={scraped.get('price')}")

            # Step 4: Upload thumbnail to Azure Storage
            thumbnail_url = ''
            if scraped.get('thumbnail_original'):
                logger.info(f"Uploading thumbnail to Azure Storage...")
                try:
                    thumbnail_url = await AzureStorageService.upload_image_from_url(
                        scraped['thumbnail_original']
                    )
                    logger.info(f"Thumbnail uploaded: {thumbnail_url}")
                except Exception as e:
                    logger.warning(f"Failed to upload thumbnail: {e}. Using original URL.")
                    thumbnail_url = scraped['thumbnail_original']

            # Step 5: Create product in Cosmos DB
            logger.info(f"Creating product in database...")
            product = ProductService.create({
                'title': scraped['title'],
                'original_url': resolved_url,
                'affiliate_url': url,  # User's original affiliate link
                'randomized_url': randomized_url,  # Randomized URL used for scraping
                'shop_id': shop_id,
                'shop_name': scraped.get('shop_name', ''),
                'item_id': item_id,
                'thumbnail_url': thumbnail_url,
                'thumbnail_original': scraped.get('thumbnail_original', ''),
                'price': scraped.get('price'),
            })
            logger.info(f"Product created with ID: {product['id']}")

            # Step 6: Update link with product reference
            logger.info(f"Updating link {link_id} with product data...")
            # Step 6: Update link with product reference
            logger.info(f"Updating link {link_id} with product data...")
            link = CosmosDBService.get_by_id(CONTAINER, link_id, 'default')
            link.update({
                'resolved_url': resolved_url,
                'shop_id': shop_id,
                'item_id': item_id,
                'product_id': product['id'],
                'status': 'done',
                'updated_at': datetime.now(timezone.utc).isoformat()
            })
            CosmosDBService.upsert(CONTAINER, link)
            logger.info(f"✅ Link {link_id} processing completed successfully!")

        except Exception as e:
            logger.error(f"❌ Scraping failed for link {link_id}: {e}", exc_info=True)
            LinkService._update_status(link_id, 'failed', str(e))

    @staticmethod
    def _update_status(link_id: str, status: str, error: str = None) -> None:
        link = CosmosDBService.get_by_id(CONTAINER, link_id, 'default')
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
