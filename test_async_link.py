"""
Test async link creation with background processing.
"""
import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_async_link_creation():
    """Test creating link in async mode."""
    
    # Test URL
    url = "https://s.shopee.vn/7KteAH4OUm"
    
    print("="*80)
    print("Testing ASYNC Link Creation")
    print("="*80)
    
    # 1. Create link
    print(f"\n1. Creating link with URL: {url}")
    start_time = time.time()
    
    response = requests.post(
        f"{BASE_URL}/api/links/",
        json={"url": url},
        headers={"Content-Type": "application/json"}
    )
    
    create_time = time.time() - start_time
    print(f"✅ Response received in {create_time:.2f}s")
    
    if response.status_code != 201:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return
    
    link = response.json()
    link_id = link['id']
    
    print(f"\nLink created:")
    print(f"  ID: {link_id}")
    print(f"  Status: {link['status']}")
    print(f"  Original URL: {link['original_url']}")
    
    if link['status'] != 'pending':
        print(f"⚠️ Expected status='pending', got '{link['status']}'")
        print("   (Might be running in sync mode)")
        return
    
    # 2. Poll for completion
    print(f"\n2. Polling for completion (checking every 2s)...")
    max_attempts = 30  # 60 seconds max
    
    for i in range(max_attempts):
        time.sleep(2)
        
        response = requests.get(
            f"{BASE_URL}/api/links/{link_id}/",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get link: {response.status_code}")
            return
        
        link = response.json()
        status_text = link['status']
        
        print(f"  Attempt {i+1}: status={status_text}")
        
        if status_text == 'done':
            print(f"\n✅ Link processing completed!")
            print(f"\nFinal link data:")
            print(f"  Resolved URL: {link.get('resolved_url', 'N/A')}")
            print(f"  Shop ID: {link.get('shop_id', 'N/A')}")
            print(f"  Item ID: {link.get('item_id', 'N/A')}")
            print(f"  Product ID: {link.get('product_id', 'N/A')}")
            
            # Get product info
            if link.get('product_id'):
                print(f"\n3. Fetching product info...")
                prod_response = requests.get(
                    f"{BASE_URL}/api/products/?page=1&page_size=20"
                )
                if prod_response.status_code == 200:
                    products = prod_response.json()['results']
                    product = next((p for p in products if p['id'] == link['product_id']), None)
                    if product:
                        print(f"\nProduct details:")
                        print(f"  Title: {product.get('title', 'N/A')}")
                        print(f"  Price: {product.get('price', 'N/A')}")
                        print(f"  Thumbnail: {product.get('thumbnail_url', 'N/A')[:80]}...")
            
            return
        elif status_text == 'failed':
            print(f"\n❌ Link processing failed!")
            print(f"  Error: {link.get('error_message', 'Unknown error')}")
            return
    
    print(f"\n⏱️ Timeout after {max_attempts * 2}s - link still processing")

if __name__ == '__main__':
    test_async_link_creation()
