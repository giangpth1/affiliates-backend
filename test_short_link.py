"""
Test affiliate short link resolution.
"""
import asyncio
import sys
sys.path.insert(0, 'C:\\Projects\\affiliates_management\\backend')

from services.scraper import ShopeeScraperService

async def test_short_link():
    """Test resolving short affiliate links."""
    
    # Short affiliate link (s.shopee.vn)
    short_link = "https://s.shopee.vn/7KteAH4OUm"
    
    print(f"Testing short link: {short_link}")
    print("="*80)
    
    try:
        print("\n1. Validating...")
        valid = ShopeeScraperService.validate_url(short_link)
        print(f"Valid: {valid}")
        
        print("\n2. Resolving redirect...")
        resolved = await ShopeeScraperService.resolve_redirect(short_link)
        print(f"Resolved URL: {resolved}")
        
        print("\n3. Extracting IDs...")
        shop_id, item_id = ShopeeScraperService.extract_ids_from_url(resolved)
        print(f"shop_id: {shop_id}")
        print(f"item_id: {item_id}")
        
        if shop_id == 'unknown' or item_id == 'unknown':
            print("\n❌ Cannot extract IDs from resolved URL")
            print("URL pattern might not match")
        else:
            print("\n✅ Successfully extracted IDs")
            
            # Try scraping
            print("\n4. Scraping product...")
            scraped = await ShopeeScraperService.scrape_product(resolved)
            print(f"Title: {scraped.get('title')}")
            print(f"Thumbnail: {scraped.get('thumbnail_original')}")
            print(f"Price: {scraped.get('price')}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_short_link())
