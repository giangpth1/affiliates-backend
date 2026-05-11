# Shopee API Options Research

## 🔍 API Types

### 1. Shopee Open Platform API (Seller/Partner API)
**Endpoint**: `https://partner.shopeemobile.com/api/v2/`

**Use case**: Cho shop owners quản lý sản phẩm, đơn hàng của chính họ

**Authentication**:
- Cần đăng ký làm Shopee Partner
- `partner_id` + `partner_key`
- OAuth/Shop authorization flow
- HMAC signature cho mỗi request

**Ví dụ**:
```
POST /api/v2/product/get_item_base_info
{
  "partner_id": "<your_partner_id>",
  "timestamp": "<current_timestamp>",
  "access_token": "<your_access_token>",
  "shop_id": "<your_shop_id>",
  "sign": "<generated_signature>",
  "item_id_list": [123456]
}
```

**Limitations**:
- ❌ Chỉ xem được sản phẩm của shop mình sở hữu
- ❌ Không thể xem sản phẩm của shop khác
- ❌ Yêu cầu user phải là shop owner (không phải affiliate marketer)

**Kết luận**: **KHÔNG phù hợp** cho project này vì:
- User là affiliate marketer, không phải shop owner
- Muốn xem sản phẩm từ BẤT KỲ shop nào trên Shopee
- Không có quyền truy cập vào shop data của người khác

---

### 2. Shopee Affiliate API
**Trang chủ**: https://affiliate.shopee.vn/

**Use case**: Cho affiliates tạo link, track commission

**Features** (nếu có):
- Tạo affiliate link
- Track clicks, conversions
- Xem earnings, commission
- **KHÔNG** có API để lấy thông tin sản phẩm (title, image, price)

**Kết luận**: **Có thể hữu ích** để:
- Tạo affiliate link chính thức (thay vì user tự paste)
- Track commission tự động

Nhưng **KHÔNG giải quyết** vấn đề scraping product info.

---

### 3. Shopee Internal API (Không công khai)
**Endpoint**: `https://shopee.vn/api/v4/item/get`

**Use case**: Dùng bởi Shopee website/mobile app

**Đã test**: ❌ Trả về 403 Forbidden (anti-bot)

```python
# Tested
url = "https://shopee.vn/api/v4/item/get"
params = {'shopid': '123', 'itemid': '456'}
# Response: {"error": 90309999, "tracking_id": "..."}
```

**Kết luận**: Bị block, không dùng được.

---

## ✅ Recommendations

### For MVP (Current):
**Keep current approach**:
- Extract `shop_id`, `item_id` từ URL ✅
- Title/thumbnail = placeholder/default
- User có thể edit manual nếu cần

**Pros**: 
- Simple, no external dependency
- Free
- Đủ cho MVP

**Cons**:
- User experience không tốt (phải nhập thủ công)

---

### For Production (Recommended):
**Option A: Playwright Browser Automation** (Recommended)

Dùng headless browser để render JavaScript như browser thật:

```python
from playwright.async_api import async_playwright

async def scrape_shopee_product(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-bots-flag']
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        try:
            # Navigate and wait for React to render
            await page.goto(url, wait_until='networkidle', timeout=20000)
            
            # Wait for product container to load
            await page.wait_for_selector('.product-detail', timeout=10000)
            
            # Extract data using CSS selectors
            title = await page.text_content('h1._2rQP1z') or 'Unknown'
            
            # Get image src
            image = await page.get_attribute('img.product-image', 'src')
            
            # Get price
            price_el = await page.query_selector('._3n5NQx')
            price_text = await price_el.text_content() if price_el else None
            
            return {
                'title': title.strip(),
                'thumbnail_original': image,
                'price': parse_price(price_text)
            }
            
        finally:
            await browser.close()
```

**Implementation steps**:
1. Install: `pip install playwright && playwright install chromium`
2. Update `requirements.txt`
3. Replace scraper in `services/scraper.py`
4. Update Azure Function (add Playwright layer)

**Pros**:
- ✅ Hoạt động với mọi website (bypass anti-bot)
- ✅ Lấy được data đầy đủ
- ✅ Free (self-hosted)

**Cons**:
- Chậm hơn (2-5s/request)
- Tốn resource (memory ~200MB/browser)

**Cost**:
- Development: Free
- Azure Function Premium Plan (EP1): $165/month (nếu cần always-on)
- Consumption Plan: Free tier 1M requests

---

**Option B: Paid Scraping Service**

Dùng service chuyên nghiệp:
- **ScraperAPI**: $49/month (100K requests)
- **Bright Data**: $5/GB
- **Apify**: $49/month

**Pros**: Reliable, maintained
**Cons**: Cost money

---

## 🎯 Decision Matrix

| Solution | Cost | Speed | Reliability | Effort |
|----------|------|-------|-------------|--------|
| Current (placeholder) | $0 | Fast | 100% | ✅ Done |
| Playwright | $0-165/mo | Medium (2-5s) | 95% | Medium |
| Paid service | $49+/mo | Fast | 99% | Low |
| Shopee Partner API | N/A | N/A | N/A | ❌ Not applicable |

---

## 📝 Recommendation

**Phase 1 (MVP - Now)**:
- Keep current approach (placeholder data)
- Add note trong UI: "Thông tin sản phẩm sẽ tự động cập nhật sau"

**Phase 2 (Beta)**:
- Implement Playwright scraper
- Run on Azure Function (Consumption Plan = Free)
- Test với real users

**Phase 3 (Production)**:
- If scraping stable → Keep Playwright
- If too slow/unreliable → Switch to paid service
- Monitor cost và performance

---

## 🔗 Resources

- Shopee Open Platform: https://open.shopee.com/documents
- Shopee Affiliate: https://affiliate.shopee.vn/
- Playwright Python: https://playwright.dev/python/
- ScraperAPI: https://www.scraperapi.com/

---

**Last Updated**: 2026-05-08
**Decision**: Keep placeholder for MVP, implement Playwright for beta
