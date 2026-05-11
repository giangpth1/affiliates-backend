import httpx
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from apps.core.exceptions import InvalidShopeeURL, ScrapingFailed
import logging

logger = logging.getLogger(__name__)

SHOPEE_DOMAIN_PATTERN = re.compile(
    r'(shp\.ee|shopee\.vn|shopee\.com)'
)

# Pattern 1: shopee.vn/i.{shop_id}.{item_id}
SHOPEE_PRODUCT_PATTERN_1 = re.compile(
    r'shopee\.vn/(?:[^/]+/)?i\.(\d+)\.(\d+)'
)

# Pattern 2: shopee.vn/{shop_name}/{shop_id}/{item_id}
SHOPEE_PRODUCT_PATTERN_2 = re.compile(
    r'shopee\.vn/[^/]+/(\d+)/(\d+)'
)


class ShopeeScraperService:

    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]

    @staticmethod
    def validate_url(url: str) -> bool:
        return bool(SHOPEE_DOMAIN_PATTERN.search(url))

    @staticmethod
    async def resolve_redirect(url: str) -> str:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            response = await client.head(url)
            return str(response.url)

    @staticmethod
    def extract_ids_from_url(url: str) -> tuple[str, str]:
        # Try pattern 1: i.{shop_id}.{item_id}
        match = SHOPEE_PRODUCT_PATTERN_1.search(url)
        if match:
            return match.group(1), match.group(2)
        
        # Try pattern 2: {shop_name}/{shop_id}/{item_id}
        match = SHOPEE_PRODUCT_PATTERN_2.search(url)
        if match:
            return match.group(1), match.group(2)
        
        # Fallback: try query params
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        shop_id = params.get('shopid', [None])[0]
        item_id = params.get('itemid', [None])[0]
        if shop_id and item_id:
            return shop_id, item_id
        
        # Last resort: return 'unknown' instead of raising error
        logger.warning(f"Cannot extract IDs from URL: {url}")
        return 'unknown', 'unknown'

    @staticmethod
    async def scrape_product(url: str) -> dict:
        """
        Scrape Shopee product page.
        
        Uses Playwright browser automation to handle JavaScript-rendered content.
        Falls back to basic HTTP scraping if Playwright fails.
        
        Args:
            url: Full Shopee product URL
            
        Returns:
            dict with keys: title, thumbnail_original, price
        """
        # Try Playwright first (handles JS-rendered content)
        try:
            from services.scraper_playwright import PlaywrightScraperService
            logger.info(f"Attempting Playwright scraping for: {url}")
            result = await PlaywrightScraperService.scrape_shopee_product(url)
            
            # Validate result
            if result.get('title') and result['title'] != 'Unknown':
                logger.info(f"Playwright scraping successful: {result['title']}")
                return result
            else:
                logger.warning("Playwright returned Unknown title, will use fallback")
                
        except Exception as e:
            logger.warning(f"Playwright scraping failed: {e}. Falling back to HTTP scraping.")
        
        # Fallback to basic HTTP scraping (likely won't work for Shopee, but try anyway)
        return await ShopeeScraperService._scrape_with_http(url)
    
    @staticmethod
    async def _scrape_with_http(url: str) -> dict:
        """Fallback HTTP scraping (unlikely to work for Shopee)."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://shopee.vn/',
        }

        try:
            async with httpx.AsyncClient(timeout=20, headers=headers, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error when scraping {url}: {e}")
            raise ScrapingFailed(detail=f"HTTP error: {str(e)}")

        soup = BeautifulSoup(response.text, 'lxml')

        # Extract title
        title = 'Unknown'
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            title = og_title.get('content', '').strip()
            title = re.sub(r'\s*[|–-]\s*(Shopee|shopee).*$', '', title, flags=re.IGNORECASE).strip()
        
        # Extract thumbnail
        thumbnail_url = ''
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            thumbnail_url = og_image.get('content', '').strip()
        
        # Extract price
        price = None
        price_meta = soup.find('meta', property='product:price:amount')
        if price_meta and price_meta.get('content'):
            try:
                price = float(price_meta.get('content', '0').replace(',', ''))
            except ValueError:
                pass

        logger.info(f"HTTP scraping result - title: {title}, thumbnail: {bool(thumbnail_url)}, price: {price}")
        
        return {
            'title': title,
            'thumbnail_original': thumbnail_url,
            'price': price,
            'shop_name': '',  # HTTP scraping doesn't extract shop name reliably
        }
