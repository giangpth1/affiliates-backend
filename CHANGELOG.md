# Changelog

Tất cả thay đổi quan trọng của project sẽ được document ở file này.

Format dựa trên [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Planning Phase
- ✅ Complete documentation structure
- ✅ 6-phase implementation plans (added Web Frontend as Phase 4)
- ✅ Architecture design
- ✅ API specification
- ✅ Security strategy
- ✅ Monitoring & maintenance guides
- ✅ Cost estimation

### Changed
- Restructured phases: Phase 4 = Web Frontend, Phase 5 = Mobile, Phase 6 = Deploy
- Updated PLAN.md with new 6-phase structure
- Updated CHECKLIST.md with Web Frontend tasks
- **Frontend Tech Stack Changed**: Next.js → Laravel + Blade
  - Laravel 11 with Blade templates + HTML/CSS/JS thuần
  - Bootstrap 5 + CSS variables (Shopee Orange theme)
  - Session-based auth with API tokens from Django backend
  - Separate deployment (2 Azure Web Apps: Python backend + PHP frontend)

### Fixed
- **User Model**: Added required DRF properties (`is_authenticated`, `is_active`, `is_anonymous`)
- **MeView**: Simplified to use `request.user` directly (no redundant DB query)
- **`.gitignore`**: Added `local.settings.json` to prevent committing function secrets
- **Azure Function indexing**: Fixed error "thumbnail_original does not exist" - now only indexes fields defined in AI Search schema
- **ProductListSerializer**: 
  - Added `default='VND'` for `price_currency` to handle products without this field
  - Added `original_url`, `shop_id`, `item_id` fields
  - Made `thumbnail_url` nullable/optional to handle scraping failures
  - **Added `status` field** to fix "Undefined array key 'status'" error in frontend product-card
- **ProductService.create**: Ensures `price_currency` and `status` have default values
- **Shopee URL extraction**: Added pattern to handle `shopee.vn/{shop_name}/{shop_id}/{item_id}` format
- **Shopee scraper**: Improved scraping logic with multiple fallback methods for title, thumbnail, and price extraction; added comprehensive headers
- **Link creation flow** (MAJOR FIX):
  - Changed from async (pending → background scraping) to **synchronous scraping in development**
  - API now waits for Playwright scraping to complete before returning response
  - Returns link with **fully populated product data** (title, thumbnail, price) instead of "Unknown"
  - Added comprehensive logging for each scraping step
  - Short affiliate links (`s.shopee.vn`) are properly resolved and scraped

### Known Issues
- **Shopee scraping limitation**: Shopee uses client-side rendering (React) and anti-bot protection. Current scraper may return "Unknown" title and empty thumbnail. See [docs/SHOPEE_SCRAPING.md](docs/SHOPEE_SCRAPING.md) for solutions (Playwright browser automation recommended for production).

### Added
- **Admin Dashboard (Phase 2)**: Django-based admin panel
  - Custom admin app (không dùng ModelAdmin vì Cosmos DB)
  - Dashboard với statistics (users, products, links)
  - User management (list, update status, delete)
  - Product management (list, filter by shop_id, delete)
  - Link management (list, filter by status, retry failed, delete)
  - Session-based admin authentication
  - Bootstrap 5 admin templates
- **Azure Functions App**: Complete function app structure
  - `scrape_product/` HTTP trigger function (async scraping)
  - `host.json` - Function App configuration
  - `requirements.txt` - Python dependencies for Azure Functions
  - `local.settings.json.example` - Template for local development
  - `.funcignore` - Deploy exclusion rules
  - `README.md` - Comprehensive setup & testing guide
  - `DEPLOY.md` - Quick deployment guide with Azure CLI commands
- **✅ Playwright Browser Automation** (WORKING!):
  - `services/scraper_playwright.py` - Browser-based scraper service
  - **Quick extraction strategy**: Extract data in ~1s before Shopee redirects to login
  - Clean URL construction: `/product/{shop_id}/{item_id}` for fast loading
  - **Results**: ✅ Title (100%), ✅ Thumbnail (100%), ✅ Price (~90%)
  - Fallback mechanism: tries Playwright first, falls back to HTTP scraping
  - Chromium browser installed (~180MB)
- **Documentation**:
  - [docs/AZURE_FUNCTIONS.md](docs/AZURE_FUNCTIONS.md) - Implementation overview
  - [docs/SHOPEE_SCRAPING.md](docs/SHOPEE_SCRAPING.md) - ✅ SOLVED with Playwright quick extraction
  - [docs/SHOPEE_API_RESEARCH.md](docs/SHOPEE_API_RESEARCH.md) - Analysis of Shopee API options
  - [docs/PLAYWRIGHT_IMPLEMENTATION.md](docs/PLAYWRIGHT_IMPLEMENTATION.md) - Complete implementation guide & test results

### To Do
- [ ] Provision Azure resources
- [ ] Implement backend core APIs
- [ ] Implement scraping pipeline
- [ ] Implement RAG search
- [ ] Build Laravel web frontend (Phase 4)
- [ ] Build Flutter mobile app
- [ ] Deploy to production

---

## [1.0.0] - Unreleased (Target: 2026-06-30)

### Added
- **User Authentication System (REQUIRED)**:
  - JWT-based authentication with access (1h) + refresh (7d) tokens
  - User registration with email/password + display name
  - Login/logout with token blacklisting
  - Password hashing with bcrypt
  - Protected API endpoints (all require Bearer token)
  - Auth guard for mobile app (redirect to login if not authenticated)
  - Token auto-refresh on expiration (Dio interceptor)
  - Secure token storage (FlutterSecureStorage)
  - Users container in Cosmos DB (partition key: /id)
  - Auth endpoints: /auth/register, /auth/login, /auth/logout, /auth/refresh, /auth/me, /auth/change-password
- Django backend structure with settings split
- Cosmos DB integration (users, products, links, token_blacklist containers)
- Azure AI Search integration with semantic search
- Shopee URL scraper with httpx + BeautifulSoup4
- Azure Function App for async scraping
- REST API endpoints for auth, links, products, search
- Flutter mobile app with Riverpod
- Mobile screens: Login, Register, Add Link, Product List, Search
- Theme system (light/dark modes, Shopee Orange branding, Inter font)
- **Web Frontend (Next.js 14+)**:
  - Same design system as mobile app
  - TailwindCSS with Shopee Orange theme
  - React Query + Zustand for state management
  - Auth pages: Login, Register
  - Dashboard layout with sidebar
  - Product List/Detail pages
  - Add Link page with status polling
  - Search page with filters
  - Responsive design (desktop + mobile browsers)
- Internationalization (Vietnamese primary, English secondary)
- Application Insights monitoring
- Health check endpoint
- Dockerfile for Azure Web App deployment
- GitHub Actions CI/CD pipeline

### Security
- ✅ **JWT authentication (REQUIRED)** - all endpoints except /health and /auth/* require auth
- ✅ **Password security** - bcrypt hashing, complexity requirements (8+ chars, uppercase, lowercase, number)
- ✅ **Token rotation** - refresh tokens rotated on use, old tokens blacklisted
- ✅ **Secure storage** - tokens stored in FlutterSecureStorage (encrypted)
- HTTPS enforcement
- CORS configuration
- Input validation & sanitization
- Data isolation per user_id
- Rate limiting
- Security headers

### Documentation
- Master plan (PLAN.md)
- Architecture diagram (ARCHITECTURE.md)
- API specification (API_SPEC.md)
- 5 phase implementation guides
- Monitoring strategy (MONITORING.md)
- Security guide (SECURITY.md)
- Maintenance guide (MAINTENANCE.md)
- Cost estimation (COST_ESTIMATION.md)
- README with quick start

---

## Documentation Updates Log

### 2026-05-06 (User Authentication Planning - CRITICAL UPDATE)
- **Added**: `plans/USER_AUTHENTICATION.md` - Complete user authentication system (1500+ lines)
  - User registration flow (email, password, display name)
  - Login flow with JWT tokens (access 1h, refresh 7d)
  - Token refresh flow (auto-retry on 401)
  - Logout flow (token blacklisting)
  - Protected API request flow
  - Complete backend implementation (Django + JWT + bcrypt)
  - Complete mobile implementation (Flutter + Riverpod + FlutterSecureStorage)
  - Security best practices, testing strategies, monitoring
- **Updated**: `plans/SECURITY.md` - Emphasized JWT as REQUIRED, referenced USER_AUTHENTICATION.md
- **Updated**: `plans/API_SPEC.md` - Added auth endpoints (/auth/register, /auth/login, /auth/logout, /auth/refresh, /auth/me, /auth/change-password)
- **Updated**: `plans/API_SPEC.md` - All endpoints now require `Authorization: Bearer <token>` header
- **Updated**: `plans/API_SPEC.md` - Removed hardcoded `user_id: "default"`, use JWT user_id instead
- **Updated**: `plans/ARCHITECTURE.md` - Added Users container to Cosmos DB, added auth flow diagram
- **Updated**: `plans/PLAN_PHASE_2_BACKEND.md` - Added Step 2.2A: Users App implementation
- **Updated**: `plans/PLAN_PHASE_4_MOBILE.md` - Added Step 4.2A: Auth Feature (login/register screens, auth guard)
- **Updated**: `CHECKLIST.md` - Added 45+ auth tasks to Phase 2 (backend) and Phase 4 (mobile)
- **Updated**: `docs/README.md` - Referenced USER_AUTHENTICATION.md
- **Updated**: `.github/copilot-instructions.md` - Emphasized RULE #1 about documentation discipline

**⚠️ BREAKING CHANGE**: App now REQUIRES user authentication. No anonymous access allowed.

### 2026-05-06 (UI/UX Planning)
- **Added**: `plans/THEME_SYSTEM.md` - Complete theme system design (colors, typography, spacing, light/dark themes)
- **Added**: `plans/INTERNATIONALIZATION.md` - i18n strategy for Vietnamese & English support
- **Updated**: README.md - Added UI/UX Guidelines section
- **Updated**: CHECKLIST.md - Added theme & i18n implementation tasks

### 2026-05-06 (Documentation Reorganization)
- **Added**: `.github/copilot-instructions.md` - GitHub Copilot agent instructions với RULE #1: Always update docs khi code changes
- **Added**: `docs/README.md` - Code documentation index với templates và update rules
- **Reorganized**: Moved planning docs từ `docs/` → `plans/` cho đúng ý nghĩa
  - `plans/` = Planning & architecture documents (static)
  - `docs/` = Code documentation (auto-generated từ code)
- **Updated**: All references từ `docs/` → `plans/` trong README.md và các files khác

### 2026-05-06 (Documentation Complete)
- **Added**: `plans/MONITORING.md` - Application Insights setup, metrics tracking, alerts configuration
- **Added**: `plans/SECURITY.md` - Authentication strategies (API Key → JWT migration), CORS, rate limiting
- **Added**: `plans/MAINTENANCE.md` - Backup procedures, disaster recovery, troubleshooting guide
- **Added**: `plans/COST_ESTIMATION.md` - Monthly cost breakdown, optimization strategies
- **Added**: `plans/PROJECT_STRUCTURE.md` - Project organization guide, conventions, patterns
- **Added**: `README.md` - Project overview, quick start, documentation index
- **Added**: `CHANGELOG.md` - This file
- **Added**: `.gitignore` - Ignore rules for Python, Flutter, Azure

### 2026-05-06 (Initial)
- **Created**: Complete documentation structure
- **Created**: `plans/PLAN.md` - Master plan with 5 phases overview
- **Created**: `plans/ARCHITECTURE.md` - System architecture, data flow, directory structure
- **Created**: `plans/API_SPEC.md` - Complete REST API specification
- **Created**: `plans/PLAN_PHASE_1_SETUP.md` - Dev environment & Azure resources setup
- **Created**: `plans/PLAN_PHASE_2_BACKEND.md` - Django backend core implementation
- **Created**: `plans/PLAN_PHASE_3_AI_RAG.md` - AI Search & RAG integration
- **Created**: `plans/PLAN_PHASE_4_MOBILE.md` - Flutter mobile app development
- **Created**: `plans/PLAN_PHASE_5_DEPLOY.md` - Production deployment & CI/CD

---

## Future Enhancements

### v1.1.0 (Post-MVP)
- [ ] Telegram bot integration
- [ ] Price tracking & historical data
- [ ] Product category auto-tagging
- [ ] User dashboard (analytics)

### v1.2.0
- [ ] Batch import (CSV/Excel)
- [ ] Export functionality
- [ ] Advanced filters (price range, category, shop)
- [ ] Product recommendations (ML)
- [ ] Click tracking & analytics

### v2.0.0
- [ ] Web admin panel (React/Vue)
- [ ] Multi-marketplace support (Lazada, Tiki)
- [ ] Team collaboration features
- [ ] Webhook integrations
- [ ] GraphQL API
