"""Quick test to verify shop name extraction works"""
import asyncio
from playwright.async_api import async_playwright

async def test():
    url = input("Nhập URL Shopee: ").strip()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.goto(url, wait_until='domcontentloaded')
        print("✅ Page loaded, waiting 2 seconds...")
        await page.wait_for_timeout(2000)
        
        # Test selector
        element = await page.query_selector('div.fV3TIn')
        if element:
            shop_name = await element.inner_text()
            print(f"\n✅ FOUND: '{shop_name}'")
        else:
            print("\n❌ NOT FOUND with selector 'div.fV3TIn'")
            
            # Try to find it manually
            print("\nSearching for shop name manually...")
            content = await page.content()
            if 'fV3TIn' in content:
                print("✅ Class 'fV3TIn' exists in page HTML")
            else:
                print("❌ Class 'fV3TIn' NOT in page HTML - Shopee changed layout!")
        
        await page.wait_for_timeout(5000)
        await browser.close()

asyncio.run(test())
