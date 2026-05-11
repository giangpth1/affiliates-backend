"""
Test with full affiliate URL (will be converted to clean URL).
"""
import asyncio
import sys
sys.path.insert(0, 'C:\\Projects\\affiliates_management\\backend')

from services.scraper_playwright import PlaywrightScraperService

async def test_affiliate_url():
    """Test with full affiliate URL."""
    
    # User's full affiliate URL
    affiliate_url = "https://shopee.vn/product/1016604648/23552060269?credential_token=8wEwiDL7YDd6xUGHhvUdzLBhR2eyTiurCCo8WLEPrp&exp_group=rollout&gads_t_sig=gqRjZGVrxHCFomtpsTE0MjUxOnRzc19zZGtfa2V5omt20QABpGFsZ2_SAAAAZKNkZWvAomN0xEAAAAAMRoz0ZUjQw0QlRa--FjB0AKnHQPF7xv4DyGj9-GQwqn4zSdB6gztmw7ebmtsZs9FPJxlVqctc57WUE3IRqmNpcGhlcnRleHTElQAAAAyW2yQ0KVKFWAtI44SW-FJC0nLcoXX9LR6n-UkZwxmwqrMGFNrMX4ycsxtCVwNhvwFl9OT1Eqg3pTyaoQac_gmhWLNncbptPsbHzdJt0rrNlm5wYxuisGsPiSlE-hoe7Fxu55MCcqvpSETMx_0e9RpQVvTFYMJgMbpOe8iGiqsB-9qq2oyFe6C5BqzNb6BzAgSS&mmp_pid=an_17365300534&uls_trackid=55jgpq4q000q&utm_campaign=id_Ddt2A3OVJ9&utm_content=----&utm_medium=affiliates&utm_source=an_17365300534&utm_term=ev8a1o84zkwy"
    
    print(f"Testing affiliate URL extraction...")
    print(f"Original URL: {affiliate_url[:100]}...\n")
    
    # Extract IDs
    shop_id, item_id = PlaywrightScraperService._extract_shop_item_ids(affiliate_url)
    print(f"Extracted shop_id: {shop_id}")
    print(f"Extracted item_id: {item_id}")
    
    clean_url = f"https://shopee.vn/product/{shop_id}/{item_id}"
    print(f"Clean URL: {clean_url}\n")
    print("="*80)
    
    try:
        result = await PlaywrightScraperService.scrape_shopee_product(affiliate_url)
        
        print("\n✅ SCRAPING SUCCESS!")
        print("="*80)
        print(f"Title: {result.get('title')}")
        print(f"Thumbnail: {result.get('thumbnail_original')}")
        print(f"Price: {result.get('price')}")
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")

if __name__ == '__main__':
    asyncio.run(test_affiliate_url())
