---
title: Project Checklist
version: 1.1.0
updated: 2026-05-08
---

# Project Implementation Checklist

Checklist chi tiết cho toàn bộ quá trình implementation.

---

## Phase 1: Setup & Infrastructure

### Developer Environment
- [ ] Install Python 3.13
- [ ] Azure Portal access (https://portal.azure.com)
- [ ] Install Azure Functions Core Tools v4
- [ ] Install Flutter SDK
- [ ] Install VS Code + extensions (Python, Flutter, Azure Tools)
- [ ] Configure Git + GitHub account

### Django Project Setup
- [ ] Create virtual environment
- [ ] Install Django + dependencies
- [ ] Scaffold Django project with settings split
- [ ] Create `.env` file with Azure credentials
- [ ] Create `.env.example` (sanitized)
- [ ] Add `.gitignore` (venv, .env, __pycache__)
- [ ] Create app modules (core, links, products, search)
- [ ] Test `python manage.py runserver`

### Azure Resources Provisioning
- [ ] Login to Azure Portal (https://portal.azure.com)
- [ ] Create resource group
- [ ] Create Azure Cosmos DB account (serverless)
  - [ ] Create database `shopee-aff-db`
  - [ ] Create container `products` (partition: `/shop_id`)
  - [ ] Create container `links` (partition: `/user_id`)
- [ ] Create Azure Storage account
  - [ ] Create blob container `thumbnails` (public read)
  - [ ] Create blob container `backups` (private)
- [ ] Create Azure AI Search service (Free tier for dev)
- [ ] Create Azure Function App
- [ ] Create Application Insights resource
- [ ] Save all connection strings & keys to `.env`

### Verification
- [ ] Run `python scripts/verify_connections.py`
- [ ] All Azure services reachable
- [ ] Django server starts without errors

---

## Phase 2: Django Backend Core

### Core App (Shared)
- [ ] Implement `BaseDocument` dataclass
- [ ] Implement custom exceptions (DocumentNotFound, ScrapingFailed, etc.)
- [ ] Implement `StandardPagination`
- [ ] Implement custom exception handler
- [ ] Implement API key authentication
- [ ] Write unit tests for core utilities

### Cosmos DB Service
- [ ] Implement `CosmosDBService` singleton
- [ ] Methods: `upsert`, `get_by_id`, `query`, `delete`
- [ ] Error handling (404, 429, 503)
- [ ] Connection pooling
- [ ] Test all CRUD operations

### Users App (Authentication) — ⚠️ IMPLEMENT FIRST
- [ ] Install dependencies (`djangorestframework-simplejwt`, `bcrypt`)
- [ ] Configure Django settings for JWT
  - [ ] Add `rest_framework_simplejwt` to INSTALLED_APPS
  - [ ] Set JWT authentication as default
  - [ ] Configure SIMPLE_JWT settings (1h access, 7d refresh)
  - [ ] Add password validators
- [ ] Create Cosmos DB `users` container (partition key: /id)
- [ ] Define `User` dataclass model
  - [ ] Fields: email, password_hash, display_name, status, email_verified
  - [ ] Method: `to_response()` (exclude password_hash)
- [ ] Implement `UserService`
  - [ ] `hash_password(password: str)` - bcrypt hashing
  - [ ] `verify_password(password: str, hash: str)` - bcrypt verify
  - [ ] `exists_by_email(email: str)` - check uniqueness
  - [ ] `create(email, password, display_name)` - registration
  - [ ] `get_by_email(email: str)` - find user
  - [ ] `get_by_id(user_id: str)` - fetch by ID
  - [ ] `authenticate(email, password)` - login validation
  - [ ] `change_password(user_id, old_pass, new_pass)`
- [ ] Implement serializers
  - [ ] `UserRegistrationSerializer` - validate email, password strength, display name
  - [ ] `UserLoginSerializer` - email + password
  - [ ] `UserSerializer` - safe response (no password)
  - [ ] `ChangePasswordSerializer` - old + new password
- [ ] Implement views
  - [ ] `POST /api/auth/register/` - create account + return JWT
  - [ ] `POST /api/auth/login/` - authenticate + return JWT
  - [ ] `POST /api/auth/logout/` - blacklist refresh token
  - [ ] `POST /api/auth/refresh/` - refresh access token (built-in)
  - [ ] `GET /api/auth/me/` - get current user profile
  - [ ] `POST /api/auth/change-password/` - change password
- [ ] Register URLs (`/api/auth/`)
- [ ] Write auth tests
  - [ ] Test registration success
  - [ ] Test duplicate email error
  - [ ] Test login success
  - [ ] Test wrong password error
  - [ ] Test JWT token validation
  - [ ] Test token refresh
  - [ ] Test protected endpoints (401 without token)
- [ ] Update all existing endpoints to require authentication
  - [ ] Products endpoints use `request.user.id` from JWT
  - [ ] Links endpoints use `request.user.id` from JWT
  - [ ] Remove hardcoded `user_id: "default"`

### Products App
- [ ] Define `Product` dataclass model
- [ ] Implement `ProductSerializer`
- [ ] Implement `ProductService` (create, get, list, delete)
- [ ] Implement views (GET /products/, GET /products/{id}/, DELETE)
- [ ] Register URLs (`/api/products/`)
- [ ] Write API tests (pytest or Django test)

### Links App
- [ ] Define `Link` dataclass model
- [ ] Implement `LinkSerializer`
- [ ] Implement `LinkService` (create, get, list, update_status)
- [ ] Implement views (POST /links/, GET /links/, GET /links/{id}/)
- [ ] URL validation (only Shopee domains)
- [ ] Write API tests

### Shopee Scraper Service
- [ ] Implement `ShopeeScraperService`
  - [ ] URL redirect resolution (`shp.ee` → actual URL)
  - [ ] HTML fetching with httpx
  - [ ] Parse title with BeautifulSoup
  - [ ] Parse thumbnail URL
  - [ ] Parse price (optional)
  - [ ] Extract shop_id & item_id from URL
- [ ] Error handling (timeout, invalid HTML, 404)
- [ ] Add User-Agent rotation (avoid blocking)
- [ ] Add retry logic (tenacity)
- [ ] Write unit tests with mock responses

### Azure Storage Integration
- [ ] Implement `AzureStorageService`
- [ ] Method: `upload_thumbnail(image_url: str) -> blob_url`
- [ ] Download image from Shopee
- [ ] Upload to Azure Blob Storage
- [ ] Return public URL
- [ ] Handle errors (download fail, upload fail)

### Azure Function App (Scraper)
- [ ] Scaffold Function App project (`func init`)
- [ ] Create HTTP trigger function `scrape_product`
- [ ] Input: `{link_id, url, user_id}`
- [ ] Logic:
  - [ ] Fetch link record from Cosmos DB
  - [ ] Update status to `processing`
  - [ ] Run scraper
  - [ ] Create product record
  - [ ] Upload thumbnail
  - [ ] Update link status to `done` (or `failed`)
- [ ] Deploy to Azure (`func azure functionapp publish`)
- [ ] Test via Postman

### API Integration
- [ ] Django calls Function App after creating link
- [ ] Use `httpx.AsyncClient` to trigger function
- [ ] Handle function errors gracefully
- [ ] Test end-to-end flow (POST link → scrape → product created)

### Admin Dashboard (Django)
- [ ] Create `apps/admin_dashboard/` app
- [ ] Add to INSTALLED_APPS
- [ ] Configure session backend for admin auth
- [ ] Update User model with `role` field (user/admin)
- [ ] Admin Services:
  - [ ] `get_dashboard_stats()` - statistics
  - [ ] `list_users()`, `get_user()`, `update_user_status()`, `delete_user()`
  - [ ] `list_products()`, `get_product()`, `delete_product()`
  - [ ] `list_links()`, `get_link()`, `retry_failed_link()`, `delete_link()`
- [ ] Admin Forms:
  - [ ] `AdminLoginForm`
  - [ ] `UserStatusForm`
  - [ ] `ProductFilterForm`, `LinkFilterForm`
- [ ] Admin Views:
  - [ ] Login/Logout (session-based)
  - [ ] Dashboard với statistics
  - [ ] User list, detail, update status, delete
  - [ ] Product list (filter by shop_id), detail, delete
  - [ ] Link list (filter by status), detail, retry, delete
- [ ] Admin Templates (Bootstrap 5):
  - [ ] `base.html` với sidebar navigation
  - [ ] `login.html`
  - [ ] `dashboard.html` với stat cards
  - [ ] User templates (list.html, detail.html)
  - [ ] Product templates (list.html, detail.html)
  - [ ] Link templates (list.html, detail.html)
- [ ] Admin URLs:
  - [ ] `/admin/` → Dashboard
  - [ ] `/admin/login/`, `/admin/logout/`
  - [ ] `/admin/users/`, `/admin/users/<id>/`
  - [ ] `/admin/products/`, `/admin/products/<shop_id>/<id>/`
  - [ ] `/admin/links/`, `/admin/links/<user_id>/<id>/`
- [ ] Create `scripts/create_admin.py` script
- [ ] Test admin login flow
- [ ] Test user management (list, update status, delete)
- [ ] Test product management (list, filter, delete)
- [ ] Test link management (list, filter, retry failed, delete)

---

## Phase 3: AI / RAG Integration

### Azure AI Search Index
- [ ] Write `scripts/create_search_index.py`
- [ ] Define index schema with fields:
  - [ ] id, title, category, shop_id, item_id
  - [ ] thumbnail_url, original_url, price
  - [ ] title_vector (1536 dimensions)
- [ ] Configure Vietnamese analyzer
- [ ] Configure semantic search
- [ ] Run script to create index
- [ ] Verify index created in Azure Portal

### OpenAI Embedding Service
- [ ] Implement `embed_text(text: str) -> list[float]`
- [ ] Implement `embed_texts(texts: list[str]) -> list[list[float]]` (batch)
- [ ] Error handling (quota exceeded, timeout)
- [ ] Token usage logging
- [ ] Test with sample product titles

### Azure Search Service
- [ ] Implement `AzureSearchService`
- [ ] Method: `index_product(product: dict)`
  - [ ] Generate embedding for title
  - [ ] Upload document to search index
- [ ] Method: `index_products_batch(products: list[dict])`
- [ ] Method: `hybrid_search(query: str, top: int, filters: dict)`
  - [ ] Generate query embedding
  - [ ] Vectorized query (k=50)
  - [ ] BM25 text search
  - [ ] Combine results with semantic ranking
  - [ ] Return with highlights
- [ ] Method: `delete_product(product_id: str)`
- [ ] Test all methods

### Auto-Indexing Integration
- [ ] Update `ProductService.create()` to auto-index after save
- [ ] Update Function App scraper to trigger indexing
- [ ] Test: Create product → verify in search index

### Search API
- [ ] Create `apps/search/views.py`
- [ ] Implement `GET /api/search/` endpoint
  - [ ] Query params: q, top, min_price, max_price
  - [ ] Input validation (1-200 chars)
  - [ ] Call `AzureSearchService.hybrid_search()`
  - [ ] Return ranked results with highlights
- [ ] Register URLs (`/api/search/`)
- [ ] Write API tests
- [ ] Test với Vietnamese queries

---
## Phase 4: Web Frontend (Laravel)

### Laravel Project Setup
- [ ] Create Laravel project (`composer create-project laravel/laravel frontend`)
- [ ] Configure `.env` with API_BASE_URL
- [ ] Setup folder structure (Controllers, Services, Views)
- [ ] Create ApiService class for HTTP client
- [ ] Configure session-based auth with API tokens

### Design System (CSS)
- [ ] Create custom CSS file with Shopee theme variables
- [ ] Configure Bootstrap 5 via CDN
- [ ] Configure Bootstrap Icons via CDN
- [ ] Create app.css with Shopee Orange (#EE4D2D) theme
- [ ] Configure Inter font via Google Fonts

### Layouts & Components
- [ ] Create main layout (layouts/app.blade.php)
  - [ ] Sidebar with navigation
  - [ ] Mobile header with offcanvas menu
  - [ ] Flash messages (success, error)
- [ ] Create auth layout (layouts/auth.blade.php)
- [ ] Create Blade components:
  - [ ] sidebar.blade.php (navigation, user info, logout)
  - [ ] header.blade.php (mobile menu)
  - [ ] product-card.blade.php (thumbnail, title, price)
  - [ ] alert.blade.php (flash messages)

### Middleware & Routes
- [ ] Create EnsureTokenIsValid middleware
- [ ] Register middleware alias ('auth.api')
- [ ] Configure web routes:
  - [ ] Guest routes (login, register)
  - [ ] Protected routes (products, links, search)

### Controllers
- [ ] AuthController (login, register, logout)
- [ ] ProductController (index, show, destroy)
- [ ] LinkController (create, store, status)
- [ ] SearchController (index)

### Views - Auth
- [ ] Login page (auth/login.blade.php)
  - [ ] Email input
  - [ ] Password input with toggle
  - [ ] Login button
  - [ ] Link to register
- [ ] Register page (auth/register.blade.php)
  - [ ] Display name input
  - [ ] Email input
  - [ ] Password input
  - [ ] Link to login

### Views - Products
- [ ] Products list page (products/index.blade.php)
  - [ ] Product cards grid (responsive)
  - [ ] Empty state
  - [ ] Pagination
- [ ] Product detail page (products/show.blade.php)
  - [ ] Product image
  - [ ] Product info (title, price, IDs)
  - [ ] Copy link button
  - [ ] Open Shopee button
  - [ ] Delete button

### Views - Links
- [ ] Add link page (links/create.blade.php)
  - [ ] URL input with paste button
  - [ ] Submit button
  - [ ] Supported formats info
- [ ] Link status page (links/status.blade.php)
  - [ ] Status icons (loading, success, failed)
  - [ ] AJAX polling for status updates
  - [ ] View product / Retry buttons

### Views - Search
- [ ] Search page (search/index.blade.php)
  - [ ] Search input
  - [ ] Price filter (min, max)
  - [ ] Results grid
  - [ ] Empty state

### JavaScript (Vanilla)
- [ ] Toggle password visibility
- [ ] Paste from clipboard
- [ ] Copy URL to clipboard
- [ ] Link status polling (fetch API)

### Testing
- [ ] Test auth flow (register, login, logout)
- [ ] Test product CRUD
- [ ] Test add link flow with polling
- [ ] Test search
- [ ] Test responsive design (mobile/desktop)
- [ ] Test API connectivity with Django backend

---
## Phase 5: Flutter Mobile App

### Flutter Project Setup
- [ ] Create Flutter project (`flutter create`)
- [ ] Add dependencies (Riverpod, Dio, go_router, etc.)
- [ ] Configure `pubspec.yaml`
- [ ] Setup folder structure (features, core, shared)
- [ ] Create `AppTheme` (Shopee orange branding)
- [ ] Setup `go_router` with routes

### Core Setup
- [ ] Create `DioClient` singleton with base URL
- [ ] Add JWT interceptor (auto-add Bearer token)
- [ ] Add token refresh interceptor (auto-retry on 401)
- [ ] Create error handler (Dio interceptor)
- [ ] Create constants file (API URL, etc.)

### Auth Feature — ⚠️ IMPLEMENT FIRST
- [ ] Install dependencies
  - [ ] `flutter_secure_storage` - secure token storage
  - [ ] `go_router` - routing with auth guard
- [ ] Create `TokenStorage` service
  - [ ] `saveTokens(accessToken, refreshToken)`
  - [ ] `getAccessToken()`
  - [ ] `getRefreshToken()`
  - [ ] `deleteTokens()`
  - [ ] `hasTokens()`
- [ ] Create `User` model
  - [ ] Fields: id, email, displayName, status, emailVerified
  - [ ] `fromJson()` factory
- [ ] Create `AuthResponse` model
  - [ ] Fields: user, accessToken, refreshToken
  - [ ] `fromJson()` factory
- [ ] Create `AuthRepository`
  - [ ] `register(email, password, displayName)` - POST /auth/register/
  - [ ] `login(email, password)` - POST /auth/login/
  - [ ] `logout()` - POST /auth/logout/ + clear tokens
  - [ ] `getCurrentUser()` - GET /auth/me/
- [ ] Create `AuthNotifier` (Riverpod StateNotifier)
  - [ ] State: initial, loading, authenticated, unauthenticated, error
  - [ ] `_checkAuthStatus()` - auto-check on app start
  - [ ] `register()` method
  - [ ] `login()` method
  - [ ] `logout()` method
- [ ] Create `LoginScreen`
  - [ ] Email text field with validation
  - [ ] Password text field with visibility toggle
  - [ ] Login button (disabled while loading)
  - [ ] Navigate to RegisterScreen link
  - [ ] Show error snackbar on failure
  - [ ] Navigate to home on success
- [ ] Create `RegisterScreen`
  - [ ] Display name text field
  - [ ] Email text field with validation
  - [ ] Password text field with validation
  - [ ] Password requirements hint text
  - [ ] Register button (disabled while loading)
  - [ ] Show error snackbar on failure
  - [ ] Navigate to home on success
- [ ] Update `go_router` with auth guard
  - [ ] Redirect unauthenticated users to /login
  - [ ] Redirect authenticated users from /login to /home
  - [ ] Show splash screen while checking auth status
- [ ] Update `DioClient` with auth interceptor
  - [ ] Add `Authorization: Bearer <token>` to all requests
  - [ ] On 401 error: refresh token automatically
  - [ ] Retry failed request with new token
  - [ ] On refresh failure: clear tokens + redirect to login
- [ ] Test auth flow
  - [ ] Register new account
  - [ ] Login with correct credentials
  - [ ] Login with wrong credentials (show error)
  - [ ] Token auto-refresh on expired access token
  - [ ] Logout clears tokens and redirects to login
  - [ ] App restart preserves authentication

### Links Feature
- [ ] Create `LinkModel`
- [ ] Create `LinkRepository` (Dio calls)
  - [ ] `createLink(url: String)`
  - [ ] `getLink(id: String)`
  - [ ] `listLinks()`
- [ ] Create `linkProvider` (Riverpod)
- [ ] Create `AddLinkScreen`
  - [ ] Text field for URL input
  - [ ] Paste from clipboard button
  - [ ] Submit button
  - [ ] Show loading spinner
  - [ ] Poll status every 3s (max 20 attempts)
  - [ ] Show success/error message
  - [ ] Navigate to product detail on success
- [ ] Test on Android emulator

### Theme System (THEME_SYSTEM.md)
- [ ] Define color palette (light + dark modes)
- [ ] Setup typography system (Inter font)
- [ ] Configure spacing & radius constants
- [ ] Create `AppColors` class
- [ ] Create `AppTextStyles` class
- [ ] Create `AppSpacing` and `AppRadius` classes
- [ ] Implement `AppTheme.light` ThemeData
- [ ] Implement `AppTheme.dark` ThemeData
- [ ] Create `ThemeProvider` with Riverpod
- [ ] Add theme persistence (SharedPreferences)
- [ ] Create `ThemeSwitcher` widget
- [ ] Test theme switching
- [ ] Verify accessibility (contrast ratios)
- [ ] Test responsive design

### Internationalization (INTERNATIONALIZATION.md)
- [ ] **Backend i18n**:
  - [ ] Install django-modeltranslation
  - [ ] Configure LANGUAGES in settings
  - [ ] Add LocaleMiddleware
  - [ ] Create locale/ directory
  - [ ] Run makemessages for vi, en
  - [ ] Translate error messages
  - [ ] Test Accept-Language header
- [ ] **Mobile i18n**:
  - [ ] Add easy_localization package
  - [ ] Create assets/translations/ folder
  - [ ] Create vi.json translation file
  - [ ] Create en.json translation file
  - [ ] Initialize EasyLocalization in main.dart
  - [ ] Translate all UI strings
  - [ ] Create `LanguageSwitcher` widget
  - [ ] Add language persistence
  - [ ] Test date/time formatting
  - [ ] Test number/currency formatting
  - [ ] Test language switching

### Products Feature
- [ ] Create `ProductModel`
- [ ] Create `ProductRepository`
  - [ ] `listProducts(page: int)`
  - [ ] `getProduct(id: String, shopId: String)`
- [ ] Create `productProvider` (Riverpod)
- [ ] Create `ProductListScreen`
  - [ ] Pull-to-refresh
  - [ ] Infinite scroll pagination
  - [ ] Product cards with thumbnail + title + price
  - [ ] Tap to view detail
- [ ] Create `ProductDetailScreen`
  - [ ] Show large thumbnail
  - [ ] Title, price, shop info
  - [ ] Open link in browser button
  - [ ] Share button
- [ ] Test navigation

### Search Feature
- [ ] Create `SearchResultModel`
- [ ] Create `SearchRepository`
  - [ ] `search(query: String, filters: Map)`
- [ ] Create `searchProvider` (Riverpod)
- [ ] Create `SearchScreen`
  - [ ] Search bar with auto-focus
  - [ ] Search history (optional)
  - [ ] Show results with highlights
  - [ ] Loading state
  - [ ] Empty state (no results)
  - [ ] Error state
- [ ] Test search with Vietnamese queries

### Shared Widgets
- [ ] `ProductCard` widget (reusable)
- [ ] `ThumbnailImage` with cached loading
- [ ] `LoadingOverlay` (full-screen spinner)
- [ ] `ErrorSnackbar` (error toast)

### Testing
- [ ] Widget tests for screens
- [ ] Unit tests for repositories
- [ ] Integration test (add link → view product)

---

## Phase 6: Deployment & CI/CD

### Backend Deployment Prep
- [ ] Create `Dockerfile`
- [ ] Create `.dockerignore`
- [ ] Add `gunicorn` to requirements.txt
- [ ] Test Docker build locally
- [ ] Create `backend-deploy.zip` script

### Azure Web App Deployment
- [ ] Create Azure Web App (Python 3.13 runtime)
- [ ] Configure app settings (all env vars)
- [ ] Configure startup command (gunicorn)
- [ ] Deploy via ZIP
- [ ] Test health check endpoint
- [ ] Verify all endpoints working

### Unified Deployment (Django + Next.js Static)
> **KHUYẾN NGHỊ**: Deploy cả backend và frontend trên cùng một Azure Web App (chỉ Python)

- [ ] Configure Next.js for static export
  - [ ] Update `next.config.mjs` với `output: 'export'`
  - [ ] Replace `next/image` với native `<img>` (hoặc unoptimized)
  - [ ] Ensure all pages are client components (`'use client'`)
- [ ] Build frontend static files
  - [ ] Run `npm run build` (creates `frontend/out/`)
  - [ ] Copy `out/` to `backend/frontend_dist/`
- [ ] Configure Django to serve frontend
  - [ ] Add `whitenoise` to requirements.txt
  - [ ] Add WhiteNoise middleware
  - [ ] Create `FrontendView` in `apps/core/views.py`
  - [ ] Update `config/urls.py` with frontend catch-all route
- [ ] Create unified build script (`scripts/build_unified.ps1`)
- [ ] Test locally (Django serving both API and frontend)
- [ ] Create unified GitHub Actions workflow
- [ ] Deploy to Azure Web App
- [ ] Verify:
  - [ ] API endpoints working (`/api/health/`)
  - [ ] Frontend pages loading (`/`, `/login/`, `/products/`)
  - [ ] Static assets loading (`/_next/static/*`)

### Azure Function Deployment
- [ ] Configure Function App settings (env vars)
- [ ] Deploy via `func azure functionapp publish`
- [ ] Test scraping trigger
- [ ] Verify logs in Application Insights

### GitHub Actions CI/CD
- [ ] Add secrets to GitHub repo
  - [ ] `AZURE_WEBAPP_PUBLISH_PROFILE`
  - [ ] `AZURE_WEBAPP_NAME`
- [ ] Create `.github/workflows/unified-deploy.yml`
  - [ ] Build frontend (Node.js)
  - [ ] Copy frontend to backend
  - [ ] Run backend tests (Python)
  - [ ] Deploy to Azure on push to main
  - [ ] Health check after deploy
- [ ] Create `.github/workflows/function.yml` (Function App)
- [ ] Create `.github/workflows/mobile.yml` (Flutter APK)
- [ ] Test pipeline with dummy commit

### HTTPS & Custom Domain (Optional)
- [ ] Force HTTPS on Web App
- [ ] Add custom domain (optional)
- [ ] Configure SSL certificate
- [ ] Update mobile app API URL

### Production Checklist
- [ ] All environment variables configured
- [ ] HTTPS enforced
- [ ] API key rotated (not using dev key)
- [ ] Application Insights enabled
- [ ] Alerts configured (5xx errors, high latency)
- [ ] Cost alerts configured
- [ ] Backup procedures documented
- [ ] Disaster recovery plan tested

---

## Post-Deployment

### Monitoring Setup
- [ ] Create Application Insights dashboard
- [ ] Configure alerts (see MONITORING.md)
- [ ] Test alert delivery (email/Slack)
- [ ] Set up log retention policy
- [ ] Create runbook for common issues

### Security Hardening
- [ ] Enable Azure Key Vault for secrets
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Review security headers
- [ ] Run vulnerability scan (OWASP ZAP)
- [ ] Review Application Insights logs for anomalies

### Documentation
- [ ] Update README with production URLs
- [ ] Document runbook procedures in `docs/`
- [ ] Create user guide (if needed) in `docs/`
- [ ] Update `plans/API_SPEC.md` with production examples
- [ ] Create FAQ document in `docs/`
- [ ] Verify all links in documentation working
- [ ] Update `docs/API_ENDPOINTS.md` với live examples

### Testing
- [ ] Load testing (simulate 1000 users)
- [ ] Disaster recovery drill (restore from backup)
- [ ] Penetration testing
- [ ] Mobile app beta testing (TestFlight/Firebase)

---

## Maintenance Tasks

### Weekly
- [ ] Review Application Insights errors
- [ ] Check OpenAI token usage
- [ ] Analyze search query logs
- [ ] Review cost dashboard

### Monthly
- [ ] Update dependencies
- [ ] Security scan (`pip-audit`)
- [ ] Manual search index backup
- [ ] Review documentation accuracy
- [ ] Database cleanup (old test data)

### Quarterly
- [ ] Penetration testing
- [ ] Load testing
- [ ] Disaster recovery drill
- [ ] User feedback review
- [ ] Tech debt assessment

---

## Future Enhancements Checklist

### Telegram Bot Integration
- [ ] Create Telegram bot (BotFather)
- [ ] Implement webhook handler in Django
- [ ] Reuse `LinkService` for adding links
- [ ] Send product details with inline buttons
- [ ] Deploy webhook endpoint

### Price Tracking
- [ ] Add `price_history` subcollection in Cosmos DB
- [ ] Scheduled job to check prices daily
- [ ] Alert users on price drops
- [ ] Price chart visualization

### Analytics Dashboard
- [ ] Track link clicks
- [ ] Commission estimates
- [ ] Top products report
- [ ] Conversion funnel

---

## Success Criteria

### Phase 1 Complete
- [ ] All Azure resources provisioned
- [ ] Django server running locally
- [ ] All service connections verified

### Phase 2 Complete
- [ ] All API endpoints working
- [ ] Scraping pipeline functional
- [ ] Unit tests passing (>80% coverage)

### Phase 3 Complete
- [ ] Search index operational
- [ ] RAG search returning relevant results
- [ ] Vietnamese queries working

### Phase 4 Complete
- [ ] Web app running on localhost
- [ ] All pages functional
- [ ] Responsive design working
- [ ] Same design as mobile app

### Phase 5 Complete
- [ ] Mobile app running on emulator
- [ ] All screens functional
- [ ] Navigation working

### Phase 6 Complete
- [ ] Backend deployed to Azure
- [ ] Web app deployed (Vercel/Azure Static Web Apps)
- [ ] Mobile app built (APK/IPA)
- [ ] CI/CD pipeline working
- [ ] Production monitoring active

### Production Ready
- [ ] All success criteria met
- [ ] Documentation complete
- [ ] Security audit passed
- [ ] Load testing passed
- [ ] Beta users onboarded
