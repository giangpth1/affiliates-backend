"""Test scraper with real Shopee URL"""
import os, sys
import django
import asyncio
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.development'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'apps'))
django.setup()

from services.scraper import ShopeeScraperService


async def main():
    url = "https://s.shopee.vn/7KteAH4OUm"
    
    print(f"Testing with URL: {url}\n")
    
    # Test 1: Resolve redirect
    print("1. Resolving redirect...")
    resolved = await ShopeeScraperService.resolve_redirect(url)
    print(f"   ✓ Resolved: {resolved}\n")
    
    # Test 2: Extract IDs
    print("2. Extracting shop_id and item_id...")
    shop_id, item_id = ShopeeScraperService.extract_ids_from_url(resolved)
    print(f"   ✓ shop_id: {shop_id}")
    print(f"   ✓ item_id: {item_id}\n")
    
    # Test 3: Scrape product
    print("3. Scraping product info...")
    product = await ShopeeScraperService.scrape_product(resolved)
    print(f"   ✓ title: {product['title']}")
    print(f"   ✓ thumbnail: {product.get('thumbnail_original', 'N/A')[:80]}...")
    print(f"   ✓ price: {product.get('price')}\n")
    
    print("✅ All tests passed!")


if __name__ == '__main__':
    asyncio.run(main())
