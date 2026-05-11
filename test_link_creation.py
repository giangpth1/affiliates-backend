"""
Debug script: Test link creation flow với Playwright scraper.
"""
import asyncio
import sys
sys.path.insert(0, 'C:\\Projects\\affiliates_management\\backend')

from apps.links.services import LinkService

async def test_link_creation():
    """Test full link creation flow including scraping."""
    
    # Test URLs (thay bằng URL user đã dùng)
    test_urls = [
        "https://shopee.vn/product/1016604648/23552060269",
        # Add URL user đã thử ở đây
    ]
    
    for url in test_urls:
        print(f"\n{'='*80}")
        print(f"Testing URL: {url}")
        print('='*80)
        
        try:
            # Simulate link creation (without actually saving)
            from services.scraper import ShopeeScraperService
            
            print("\n1. Validating URL...")
            if not ShopeeScraperService.validate_url(url):
                print("❌ Invalid Shopee URL")
                continue
            print("✅ URL is valid Shopee link")
            
            print("\n2. Resolving redirects...")
            resolved = await ShopeeScraperService.resolve_redirect(url)
            print(f"Resolved URL: {resolved}")
            
            print("\n3. Extracting shop_id and item_id...")
            shop_id, item_id = ShopeeScraperService.extract_ids_from_url(resolved)
            print(f"shop_id: {shop_id}")
            print(f"item_id: {item_id}")
            
            print("\n4. Scraping product data...")
            scraped = await ShopeeScraperService.scrape_product(resolved)
            
            print("\n✅ SCRAPING RESULTS:")
            print(f"Title: {scraped.get('title')}")
            print(f"Thumbnail: {scraped.get('thumbnail_original')}")
            print(f"Price: {scraped.get('price')}")
            
            # Check if data is valid
            if scraped.get('title') == 'Unknown':
                print("\n⚠️ WARNING: Title is 'Unknown' - scraping may have failed")
            if not scraped.get('thumbnail_original'):
                print("⚠️ WARNING: No thumbnail found")
            if not scraped.get('price'):
                print("⚠️ WARNING: No price found")
                
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_link_creation())
