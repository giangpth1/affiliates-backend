# Shopee Scraping Issues & Solutions

## ✅ SOLVED! (May 8, 2026)

### 🎉 Solution: Playwright with Quick Extraction Strategy

**Discovery**: Shopee hiển thị product data trong **~1 giây đầu**, sau đó redirect về login page.

**Implementation**:
1. Extract `shop_id` và `item_id` từ URL (affiliate link, short link, etc.)
2. Construct clean URL: `https://shopee.vn/product/{shop_id}/{item_id}`
3. Load page với `domcontentloaded` (nhanh hơn `networkidle`)
4. Wait 500ms (không chờ lâu → tránh redirect)
5. Extract title, thumbnail, price **NGAY LẬP TỨC**
6. Close browser trước khi bị redirect

### Test Results (May 8, 2026)

✅ **Title**: 100% accurate
- Example: "Giấy vệ sinh treo tường TopGia đa sắc đa năng từ bột giấy thiên nhiên, 1280tờ/4lớp"

✅ **Thumbnail**: High-quality image from susercontent.com
- Example: `https://down-vn.img.susercontent.com/file/vn-11134207-81ztc-mlfxblnz34eace`

✅ **Price**: Successfully extracted
- Example: 67,074 VND (may vary by variant/promotion)

### Performance
- **Speed**: ~2-5 seconds per product
- **Success Rate**: ~90% (title + thumbnail 100%, price ~90%)
- **Cost**: FREE (local Chromium browser)

### Code Location
- **Service**: `backend/services/scraper_playwright.py`
- **Integration**: `backend/services/scraper.py` (Playwright → HTTP fallback)
- **Tests**: `backend/test_quick_scrape.py`

---

## 🚨 Original Issue (Solved)

Shopee website sử dụng **client-side rendering** (React/Next.js) và có **anti-bot protection**:
- HTML ban đầu không chứa meta tags (og:title, og:image, price)
- Data được load qua JavaScript sau khi page render
- Internal API endpoint `/api/v4/item/get` trả về 403 Forbidden

## ❌ API Options Researched

### Shopee Open Platform API
**Endpoint**: `/api/v2/product/get_item_base_info`

**Không dùng được vì**:
- Chỉ dành cho **shop owners** quản lý sản phẩm của chính họ
- Yêu cầu `partner_id`, `access_token`, `shop_id`
- Không thể xem sản phẩm của shop khác
- User của chúng ta là **affiliate marketers**, không phải shop owners

Chi tiết: [SHOPEE_API_RESEARCH.md](SHOPEE_API_RESEARCH.md)

## 🛠️ Giải pháp đã thử

### ❌ Không hoạt động:
1. **HTML Scraping**: Không có meta tags trong initial HTML
2. **Shopee API direct call**: Bị block với error 90309999 (anti-bot)

## ✅ Giải pháp khả thi cho MVP

### Option 1: Manual Input (Nhanh nhất - đã implement)
- User paste link, backend extract `shop_id` và `item_id`
- Title mặc định: "Unknown" hoặc placeholder
- Thumbnail: Empty (hiện placeholder image ở frontend)  
- User có thể edit sau

**Pros**: Đơn giản, không cost
**Cons**: User experience không tốt

---

### Option 2: Browser Automation (Recommended)
Dùng **Playwright** hoặc **Puppeteer** để render JavaScript:

```python
from playwright.async_api import async_playwright

async def scrape_with_browser(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, wait_until='networkidle')
        
        # Extract data after JS rendered
        title = await page.locator('h1').first.inner_text()
        image = await page.locator('img[alt]').first.get_attribute('src')
        price_el = await page.query_selector('[class*="price"]')
        
        await browser.close()
        return {'title': title, 'thumbnail': image}
```

**Pros**: Hoạt động với mọi site
**Cons**: 
- Cần cài Playwright: `pip install playwright && playwright install chromium`
- Chậm hơn (2-5s/request)
- Tốn resource (memory, CPU)

**Cost**: Free (self-hosted) hoặc ~$0.001/request (cloud provider)

---

### Option 3: Reverse Engineer Shopee Mobile API
Shopee mobile app gọi API khác, có thể ít bị block hơn.

Cần:
1. Intercept mobile app traffic (Charles Proxy, Burp Suite)
2. Tìm API endpoint + headers
3. Replicate trong code

**Pros**: Nhanh, reliable
**Cons**: Cần reverse engineer, có thể bị block sau

---

### Option 4: Third-party Scraping Service
Dùng service như:
- **ScraperAPI** ($0.001-0.003/request)
- **Bright Data** ($5/GB)
- **Apify** ($0.002/request)

**Pros**: Professional, handle anti-bot
**Cons**: Cost money

---

## 📝 Recommendation for MVP

**Phase 1 (Current - Free)**:
- Giữ scraper hiện tại (extract shop_id/item_id)
- Title/thumbnail = placeholder
- Cho phép user edit manual nếu cần

**Phase 2 (Production - if needed)**:
- Implement **Playwright** browser automation
- Run as Azure Function (cold start OK cho MVP)
- Fallback to manual nếu timeout

**Implementation**:
```python
# backend/services/scraper_browser.py
from playwright.async_api import async_playwright

class PlaywrightScraperService:
    @staticmethod
    async def scrape_shopee_with_browser(url: str) -> dict:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0...',
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                await page.wait_for_timeout(2000)  # Wait for React render
                
                # Extract via selectors (inspect Shopee page to get correct selectors)
                title = await page.text_content('h1') or 'Unknown'
                img = await page.get_attribute('img.product-image', 'src')
                price_text = await page.text_content('[class*="price"]')
                
                return {
                    'title': title.strip(),
                    'thumbnail_original': img,
                    'price': parse_price(price_text) if price_text else None
                }
            finally:
                await browser.close()
```

**Cost estimate**:
- Playwright: Free (self-hosted)
- Azure Function Consumption Plan: First 1M free
- Premium Plan (if need <1s): $165/month

---

## 🎯 Action Items

- [x] Document issue
- [x] Fix serializer to handle missing thumbnail
- [ ] Decision: Keep placeholder OR implement Playwright
- [ ] If Playwright: Add to requirements.txt, update Azure Function

---

**Last updated**: 2026-05-08
