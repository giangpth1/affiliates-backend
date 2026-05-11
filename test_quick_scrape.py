"""
Test Playwright scraper with quick extraction strategy.
"""
import asyncio
import sys
sys.path.insert(0, 'C:\\Projects\\affiliates_management\\backend')

from services.scraper_playwright import PlaywrightScraperService

async def test_quick_scrape():
    """Test with real Shopee URL - extract before redirect."""
    
    # User's URL (will be converted to clean /product/ URL)
    test_url = "https://shopee.vn/product/1016604648/23552060269"
    
    print(f"Testing quick scrape with: {test_url}\n")
    print("="*80)
    
    try:
        result = await PlaywrightScraperService.scrape_shopee_product(test_url)
        
        print("\n✅ SCRAPING SUCCESS!")
        print("="*80)
        print(f"Title: {result.get('title')}")
        print(f"Thumbnail: {result.get('thumbnail_original')}")
        print(f"Price: {result.get('price')}")
        print("="*80)
        
        # Check quality
        success_indicators = []
        if result.get('title') and result['title'] != 'Unknown' and 'Shopee Việt Nam' not in result['title']:
            success_indicators.append("✅ Title extracted correctly")
        else:
            success_indicators.append("❌ Title is placeholder/generic")
            
        if result.get('thumbnail_original'):
            success_indicators.append("✅ Thumbnail found")
        else:
            success_indicators.append("❌ No thumbnail")
            
        if result.get('price') and result['price'] > 0:
            success_indicators.append("✅ Price extracted")
        else:
            success_indicators.append("❌ No price")
        
        print("\nQuality Check:")
        for indicator in success_indicators:
            print(indicator)
            
    except Exception as e:
        print(f"\n❌ SCRAPING FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_quick_scrape())
