"""
Script to test shop name extraction from Shopee product page.
Run: python backend/scripts/test_shop_name.py
"""
import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')


from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_shop_name_extraction(url: str):
    """Test shop name extraction with detailed logging."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Show browser
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='vi-VN',
        )
        
        page = await context.new_page()
        
        try:
            print(f"\n🔍 Testing URL: {url}\n")
            
            # Navigate to page
            await page.goto(url, wait_until='domcontentloaded')
            print("✅ Page loaded")
            
            # Wait for content to render
            await page.wait_for_timeout(2000)  # 2 seconds
            print("✅ Waited 2 seconds for content")
            
            # Try all selectors
            selectors = [
                'div.shopee-seller-info-panel__shop-name a',
                'a.shopee-seller-info-panel__shop-name',
                'div[class*="shop-name"] a',
                'a[class*="shop-name"]',
                'div[class*="seller-name"]',
                'span[class*="seller-name"]',
                'div[class*="pdp-seller-info"] a',
                'div[class*="seller-info"] span',
                'div[class*="shop-info"] a',
                '.shopee-avatar__name',
                'div.shopee-avatar__info a',
                'span[class*="_3oo6cp"]',
                'div._1o67o_ a',
                '[data-sqe="shop-name"]',
                '[data-testid="shop-name"]',
            ]
            
            print(f"\n📋 Testing {len(selectors)} selectors:\n")
            
            found_any = False
            for i, selector in enumerate(selectors, 1):
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.inner_text()
                        if text and len(text.strip()) > 0:
                            print(f"✅ {i}. '{selector}' → '{text.strip()}'")
                            found_any = True
                        else:
                            print(f"⚠️  {i}. '{selector}' → Element found but empty")
                    else:
                        print(f"❌ {i}. '{selector}' → Not found")
                except Exception as e:
                    print(f"❌ {i}. '{selector}' → Error: {e}")
            
            if not found_any:
                print("\n⚠️  No selectors matched! Let's inspect the page...")
                
                # Try to find any element with "shop" text
                print("\n🔍 Searching for elements containing 'shop'...")
                shop_elements = await page.query_selector_all('*')
                for elem in shop_elements[:100]:  # Check first 100 elements
                    try:
                        text = await elem.inner_text()
                        if text and 'shop' in text.lower() and len(text) < 100:
                            tag = await elem.evaluate('el => el.tagName')
                            classes = await elem.get_attribute('class') or ''
                            print(f"  - <{tag} class='{classes[:50]}'>: {text[:50]}")
                    except:
                        pass
            
            # Keep browser open for manual inspection
            print("\n\n⏸️  Browser will stay open for 30 seconds for manual inspection...")
            print("👉 Inspect the page to find the shop name element!")
            await page.wait_for_timeout(30000)
            
        finally:
            await browser.close()


if __name__ == '__main__':
    # Test URL - replace with actual Shopee product URL
    test_url = input("Nhập URL sản phẩm Shopee để test: ").strip()
    
    if not test_url:
        test_url = "https://shopee.vn/product/123/456"  # Placeholder
        print(f"Using default: {test_url}")
    
    asyncio.run(test_shop_name_extraction(test_url))
