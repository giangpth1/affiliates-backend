"""Test Playwright scraper with real Shopee URL"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.async_api import async_playwright
import re


async def scrape_shopee(url: str):
    """Quick test of Playwright scraping."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # Show browser for debugging
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='vi-VN',
        )
        
        page = await context.new_page()
        
        try:
            print(f"Navigating to: {url}")
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for React to render
            print("Waiting for page to render...")
            await page.wait_for_timeout(5000)
            
            # Save screenshot
            await page.screenshot(path='shopee_page.png')
            print("Screenshot saved to shopee_page.png")
            
            # Save HTML
            html = await page.content()
            with open('shopee_page.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("HTML saved to shopee_page.html")
            
            # Extract title - try specific selectors
            print("\nExtracting title...")
            title = None
            
            # Method 1: Look for span with long text
            spans = await page.query_selector_all('span')
            for span in spans:
                text = await span.inner_text()
                if text and len(text) > 20 and 'shopee' not in text.lower():
                    title = text
                    print(f"  Found via span: {title}")
                    break
            
            if not title:
                h1 = await page.query_selector('h1')
                if h1:
                    title = await h1.inner_text()
                    print(f"  Found via h1: {title}")
            
            if not title:
                title = await page.title()
                print(f"  Found via page title: {title}")
            
            if title:
                title = re.sub(r'\s*[|–-]\s*Shopee.*$', '', title, flags=re.IGNORECASE).strip()
            
            print(f"Final title: {title}")
            
            # Extract image - find images from Shopee CDN
            print("\nExtracting image...")
            imgs = await page.query_selector_all('img')
            img_src = None
            print(f"Found {len(imgs)} images")
            for i, img in enumerate(imgs[:10]):  # Check first 10 images
                src = await img.get_attribute('src')
                if src and 'susercontent.com' in src:
                    print(f"  Image {i}: {src[:100]}")
                    if not img_src and 'avatar' not in src:
                        img_src = src
            
            print(f"Selected image: {img_src[:80] if img_src else 'None'}...")
            
            # Extract price - look for price-like numbers
            print("\nExtracting price...")
            # Find divs with price-like classes
            price_divs = await page.query_selector_all('div[class*="price"], div[class*="Price"]')
            print(f"Found {len(price_divs)} price divs")
            for i, div in enumerate(price_divs[:5]):
                text = await div.inner_text()
                print(f"  Price div {i}: {text[:100]}")
            
            body = await page.inner_text('body')
            prices = re.findall(r'(\d{4,8})', body)
            price = None
            if prices:
                price_nums = [int(p) for p in prices if 1000 <= int(p) <= 1000000000]
                if price_nums:
                    price = max(price_nums)
            
            print(f"Extracted price: {price}")
            
            # Keep browser open for manual inspection
            print("\nBrowser will stay open for 10 seconds for inspection...")
            await page.wait_for_timeout(10000)
            
            return {'title': title, 'image': img_src, 'price': price}
            
        finally:
            await browser.close()


async def main():
    url = "https://shopee.vn/opaanlp/1016604648/23552060269"
    
    print(f"=== Testing Playwright Scraper ===\n")
    
    try:
        result = await scrape_shopee(url)
        print("\n=== RESULT ===")
        print(f"✅ Title: {result['title']}")
        print(f"✅ Image: {result['image'][:80] if result['image'] else 'None'}...")
        print(f"✅ Price: {result['price']}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
