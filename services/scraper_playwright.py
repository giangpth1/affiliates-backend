"""Playwright-based scraper for Shopee products.

Uses headless browser to render JavaScript and extract product data.
"""
import logging
import re
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from apps.core.exceptions import ScrapingFailed

logger = logging.getLogger(__name__)


class PlaywrightScraperService:
    """Scraper using Playwright headless browser to handle JS-rendered content."""

    # URL patterns for shop_id/item_id extraction
    SHOPEE_PRODUCT_PATTERN_1 = re.compile(r'shopee\.vn/.*?[.-](\d+)\.(\d+)')
    SHOPEE_PRODUCT_PATTERN_2 = re.compile(r'shopee\.vn/[^/]+/(\d+)/(\d+)')

    @staticmethod
    def _extract_shop_item_ids(url: str) -> tuple:
        """Extract shop_id and item_id from Shopee URL."""
        # Try pattern 1: i.{shop_id}.{item_id}
        match = PlaywrightScraperService.SHOPEE_PRODUCT_PATTERN_1.search(url)
        if match:
            return match.group(1), match.group(2)
        
        # Try pattern 2: shopee.vn/{shop_name}/{shop_id}/{item_id}
        match = PlaywrightScraperService.SHOPEE_PRODUCT_PATTERN_2.search(url)
        if match:
            return match.group(1), match.group(2)
        
        return None, None

    @staticmethod
    async def scrape_shopee_product(url: str) -> dict:
        """
        Scrape Shopee product page using Playwright.
        
        IMPORTANT: This function expects a RANDOMIZED URL (with randomized params)
        to avoid Shopee bot detection. Do NOT pass original_url or affiliate_url.
        
        Args:
            url: RANDOMIZED Shopee URL (with params already randomized)
            
        Returns:
            dict with keys: title, thumbnail_original, shop_name
            
        Raises:
            ScrapingFailed: If scraping fails
        """
        logger.info(f"Scraping Shopee product with Playwright (randomized URL): {url[:100]}...")
        
        # Extract shop_id and item_id from URL
        shop_id, item_id = PlaywrightScraperService._extract_shop_item_ids(url)
        if not shop_id or not item_id:
            logger.error(f"Could not extract shop_id/item_id from URL: {url}")
            raise ScrapingFailed(detail="Invalid Shopee URL format")
        
        # Use the randomized URL as-is (already randomized by caller)
        logger.info(f"Using randomized URL with params to avoid detection")
        
        async with async_playwright() as p:
            browser = None
            try:
                # Launch browser
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                    ]
                )
                
                # Create context with realistic settings
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080},
                    locale='vi-VN',
                    timezone_id='Asia/Ho_Chi_Minh',
                )
                
                page = await context.new_page()
                
                try:
                    # Navigate to product page
                    # Use 'domcontentloaded' instead of 'networkidle' to load faster
                    # Using original URL gives more stable page load
                    logger.info(f"Navigating to: {url}")
                    await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                    
                    # Wait longer for dynamic content to load (shop name, etc.)
                    await page.wait_for_timeout(2500)  # Increased to 2.5s
                    
                    # Extract data QUICKLY before redirect
                    # Try all extractions but don't fail if one fails
                    title = 'Unknown'
                    thumbnail = ''
                    shop_name = ''
                    
                    try:
                        title = await PlaywrightScraperService._extract_title(page)
                        logger.info(f"Extracted title: {title}")
                    except Exception as e:
                        logger.warning(f"Failed to extract title: {e}")
                    
                    try:
                        thumbnail = await PlaywrightScraperService._extract_image(page)
                        logger.info(f"Extracted thumbnail: {thumbnail[:80] if thumbnail else 'None'}")
                    except Exception as e:
                        logger.warning(f"Failed to extract thumbnail: {e}")
                    
                    try:
                        shop_name = await PlaywrightScraperService._extract_shop_name(page)
                        logger.info(f"Extracted shop name: {shop_name}")
                    except Exception as e:
                        logger.warning(f"Failed to extract shop name: {e}")
                    
                    return {
                        'title': title,
                        'thumbnail_original': thumbnail,
                        'shop_name': shop_name,
                    }
                    
                except PlaywrightTimeout as e:
                    logger.error(f"Timeout while scraping {url}: {e}")
                    raise ScrapingFailed(detail=f"Timeout: {str(e)}")
                    
                except Exception as e:
                    logger.error(f"Error while scraping {url}: {e}", exc_info=True)
                    raise ScrapingFailed(detail=f"Scraping error: {str(e)}")
                    
            finally:
                if browser:
                    await browser.close()

    @staticmethod
    async def _extract_title(page) -> str:
        """Extract product title from page."""
        # Try multiple selectors (Shopee changes them frequently)
        selectors = [
            'span[class*="WUAIU"]',  # Current Shopee title class (as of 2026)
            'h1[class*="_35xNE"]',
            'div[class*="product-name"] span',
            'h1',
            '[data-testid="product-detail-name"]',
            '.product-title',
            '._3BTQv9',
            '.pdp-mod-product-badge-title',
        ]
        
        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    text = await element.inner_text()
                    if text and len(text.strip()) > 5 and 'shopee' not in text.lower():
                        # Clean title
                        title = text.strip()
                        title = re.sub(r'\s*[|–-]\s*(Shopee|shopee).*$', '', title, flags=re.IGNORECASE)
                        if len(title) > 5:  # Valid title should be longer than 5 chars
                            logger.info(f"Found title with selector {selector}: {title}")
                            return title.strip()
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")
                continue
        
        # Fallback: try page title but exclude generic Shopee titles
        try:
            page_title = await page.title()
            if page_title and 'mua và bán' not in page_title.lower():
                title = re.sub(r'\s*[|–-]\s*(Shopee|shopee).*$', '', page_title, flags=re.IGNORECASE)
                if len(title.strip()) > 5:
                    return title.strip()
        except Exception:
            pass
        
        logger.warning("Could not extract title from page")
        return 'Unknown'

    @staticmethod
    async def _extract_image(page) -> str:
        """Extract product thumbnail image URL."""
        # Try multiple strategies
        selectors = [
            'div[class*="product-image"] img',
            'div[class*="image-view"] img',
            'button[class*="image"] img',
            '[class*="pdp"] img[src*="susercontent"]',
            'img[src*="susercontent"]',
        ]
        
        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    src = await element.get_attribute('src')
                    if src and 'susercontent.com' in src and 'avatar' not in src.lower():
                        # Get higher resolution if available
                        if '_tn' in src:  # thumbnail
                            src = src.replace('_tn', '')  # Full size
                        logger.info(f"Found image with selector {selector}")
                        return src
            except Exception as e:
                logger.debug(f"Image selector {selector} failed: {e}")
                continue
        
        logger.warning("Could not extract image from page")
        return ''

    @staticmethod
    async def _extract_shop_name(page) -> str:
        """Extract shop name from page."""
        logger.info("Attempting to extract shop name...")
        
        # Wait a bit longer for shop info to load
        try:
            await page.wait_for_timeout(800)  # Extra wait for shop section
        except Exception:
            pass
        
        # Try multiple selectors for shop name (updated for 2026 layout)
        selectors = [
        # Current working selector (May 2026)
        'div.fV3TIn',  # Shop name div
        
            'a.shopee-seller-info-panel__shop-name',
            'div[class*="shop-name"] a',
            'a[class*="shop-name"]',
            'div[class*="seller-name"]',
            'span[class*="seller-name"]',
            
            # Shop card/panel selectors
            'div[class*="pdp-seller-info"] a',
            'div[class*="seller-info"] span',
            'div[class*="shop-info"] a',
            
            # Avatar/profile selectors
            '.shopee-avatar__name',
            'div.shopee-avatar__info a',
            
            # Legacy selectors
            'span[class*="_3oo6cp"]',
            'div._1o67o_ a',
            
            # Data attributes
            '[data-sqe="shop-name"]',
            '[data-testid="shop-name"]',
        ]
        
        for i, selector in enumerate(selectors):
            try:
                logger.debug(f"Trying selector {i+1}/{len(selectors)}: {selector}")
                element = await page.query_selector(selector)
                if element:
                    text = await element.inner_text()
                    if text and len(text.strip()) > 0:
                        shop_name = text.strip()
                        # Validate shop name (not too long, not URL)
                        if 2 < len(shop_name) < 100 and 'http' not in shop_name.lower():
                            logger.info(f"✅ Found shop name with selector '{selector}': {shop_name}")
                            return shop_name
                        else:
                            logger.debug(f"Invalid shop name: {shop_name} (len={len(shop_name)})")
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")
                continue
        
        # Fallback 1: Look for any links containing shop info
        logger.info("Trying fallback: shop links...")
        try:
            links = await page.query_selector_all('a[href*="/shop/"]')
            logger.debug(f"Found {len(links)} shop links")
            for link in links[:10]:  # Check first 10 shop links
                text = await link.inner_text()
                if text and 3 < len(text.strip()) < 50 and 'http' not in text.lower():
                    shop_name = text.strip()
                    logger.info(f"✅ Found shop name from shop link: {shop_name}")
                    return shop_name
        except Exception as e:
            logger.debug(f"Shop link fallback failed: {e}")
        
        # Fallback 2: Check meta tags
        logger.info("Trying fallback: meta tags...")
        try:
            content = await page.content()
            import re
            # Look for shop name in meta or structured data
            patterns = [
                r'"shopName":"([^"]+)"',
                r'"seller":\s*"([^"]+)"',
                r'data-shop-name="([^"]+)"',
            ]
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    shop_name = match.group(1)
                    if 3 < len(shop_name) < 100:
                        logger.info(f"✅ Found shop name from page content: {shop_name}")
                        return shop_name
        except Exception as e:
            logger.debug(f"Meta fallback failed: {e}")
        
        logger.warning("❌ Could not extract shop name from page")
        return ''
