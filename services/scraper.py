import httpx
import re
from urllib.parse import urlparse, parse_qs
import logging

logger = logging.getLogger(__name__)

SHOPEE_DOMAIN_PATTERN = re.compile(
    r'(shp\.ee|shopee\.vn|shopee\.com)'
)

SHOPEE_PRODUCT_PATTERN_1 = re.compile(
    r'shopee\.vn/(?:[^/]+/)?i\.(\d+)\.(\d+)'
)

SHOPEE_PRODUCT_PATTERN_2 = re.compile(
    r'shopee\.vn/[^/]+/(\d+)/(\d+)'
)


class ShopeeScraperService:

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
        match = SHOPEE_PRODUCT_PATTERN_1.search(url)
        if match:
            return match.group(1), match.group(2)

        match = SHOPEE_PRODUCT_PATTERN_2.search(url)
        if match:
            return match.group(1), match.group(2)

        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        shop_id = params.get('shopid', [None])[0]
        item_id = params.get('itemid', [None])[0]
        if shop_id and item_id:
            return shop_id, item_id

        logger.warning(f"Cannot extract IDs from URL: {url}")
        return 'unknown', 'unknown'
