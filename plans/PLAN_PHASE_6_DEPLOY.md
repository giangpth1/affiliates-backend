---
title: Phase 6 — Deployment & CI/CD
version: 1.1.0
updated: 2026-05-08
---

# Phase 6: Deployment & CI/CD

## Goals
- Django backend chạy trên Azure Web App
- Azure Function App deployed
- GitHub Actions pipeline tự động deploy
- Environment variables đầy đủ trên Azure
- Flutter build APK release với URL production

---

## Step 6.1 — Dockerize Django Backend

### 6.1.1 Dockerfile

**`backend/Dockerfile`**:
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=config.settings.production
ENV PORT=8000

EXPOSE 8000

CMD gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
```

### 6.1.2 .dockerignore

**`backend/.dockerignore`**:
```
venv/
__pycache__/
*.pyc
*.pyo
.env
.env.*
!.env.example
db.sqlite3
*.log
tests/
.pytest_cache/
```

### 6.1.3 Test Docker build locally

```powershell
cd backend
docker build -t shopee-aff-backend .
docker run -p 8000:8000 --env-file .env shopee-aff-backend

# Test: http://localhost:8000/api/health/
```

---

## Step 6.2 — Azure Web App Deployment (Portal)

### 6.2.1 Tạo Azure Web App
1. Vào **App Services** → **+ Create** → **Web App**
2. Resource Group: `rg-shopee-aff-dev`
3. Name: `app-shopee-aff-dev`
4. Publish: **Code**
5. Runtime stack: **Python 3.13**
6. Operating System: **Linux**
7. App Service Plan: tạo mới `asp-shopee-aff-dev`, SKU **B2**
8. **Review + create** → **Create**

### 6.2.2 Configure Environment Variables
1. Vào Web App → **Settings** → **Environment variables**
2. Thêm các app settings:

| Key | Value |
|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `DJANGO_SECRET_KEY` | `<your-secret-key>` |
| `DJANGO_DEBUG` | `False` |
| `ALLOWED_HOSTS` | `app-shopee-aff-dev.azurewebsites.net` |
| `COSMOS_DB_URL` | `https://cosmos-shopee-aff-dev.documents.azure.com:443/` |
| `COSMOS_DB_KEY` | `<key>` |
| `COSMOS_DB_DATABASE` | `shopee-aff-db` |
| `AZURE_STORAGE_CONNECTION_STRING` | `<conn-string>` |
| `AZURE_STORAGE_CONTAINER` | `thumbnails` |
| `AZURE_SEARCH_ENDPOINT` | `https://srch-shopee-aff-dev.search.windows.net` |
| `AZURE_SEARCH_KEY` | `<key>` |
| `AZURE_SEARCH_INDEX` | `products` |
| `FUNCTION_APP_URL` | `https://func-shopee-aff-dev.azurewebsites.net` |
| `FUNCTION_APP_KEY` | `<function-key>` |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` |
| `WEBSITE_RUN_FROM_PACKAGE` | `1` |

### 6.2.3 Configure Startup Command
1. Vào Web App → **Settings** → **Configuration** → **General settings**
2. Startup Command: `gunicorn config.wsgi:application --bind=0.0.0.0:8000 --workers=2 --timeout=120`
3. **Save**

### 6.2.4 Deploy via ZIP (thủ công lần đầu)
1. Xóa thư mục `venv/` trước khi zip
2. Zip toàn bộ thư mục `backend/` thành `backend.zip`
3. Vào Web App → **Deployment** → **Deployment Center**
4. Source: **Zip Deploy** → upload `backend.zip`
5. Sau này sẽ dùng GitHub Actions để tự động deploy

---

## Step 6.2B — Laravel Frontend Deployment (Separate Azure Web App)

> **MỤC TIÊU**: Deploy Laravel frontend trên **Azure Web App PHP riêng**, kết nối với Django backend API.

### 6.2B.1 Kiến trúc Separate Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                  Azure Web App (Python)                     │
│                    app-shopee-aff-backend                   │
├─────────────────────────────────────────────────────────────┤
│  Django REST Framework APIs                                 │
│  - /api/auth/*, /api/products/*, /api/links/*, /api/search/ │
└─────────────────────────────────────────────────────────────┘
                              ↑ HTTP (JSON)
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Azure Web App (PHP 8.3)                   │
│                     app-shopee-aff-web                      │
├─────────────────────────────────────────────────────────────┤
│  Laravel 11 + Blade templates                               │
│  - Auth, Products, Add Link, Search pages                   │
│  - Bootstrap 5 + CSS (Shopee Orange theme)                  │
│  - Session-based auth with API tokens                       │
└─────────────────────────────────────────────────────────────┘
```

### 6.2B.2 Tạo Azure Web App cho Laravel

1. Vào **App Services** → **+ Create** → **Web App**
2. Resource Group: `rg-shopee-aff-dev`
3. Name: `app-shopee-aff-web` (frontend)
4. Publish: **Code**
5. Runtime stack: **PHP 8.3**
6. Operating System: **Linux**
7. App Service Plan: dùng chung `asp-shopee-aff-dev` hoặc tạo mới
8. **Review + create** → **Create**

### 6.2B.3 Configure Laravel Environment Variables

Vào Web App → **Settings** → **Environment variables**:

| Key | Value |
|---|---|
| `APP_NAME` | `Shopee Affiliate Manager` |
| `APP_ENV` | `production` |
| `APP_KEY` | `base64:...` (generate với `php artisan key:generate --show`) |
| `APP_DEBUG` | `false` |
| `APP_URL` | `https://app-shopee-aff-web.azurewebsites.net` |
| `API_BASE_URL` | `https://app-shopee-aff-backend.azurewebsites.net/api` |
| `API_TIMEOUT` | `30` |
| `SESSION_DRIVER` | `cookie` |
| `LOG_CHANNEL` | `stderr` |

### 6.2B.4 Deploy Laravel via Git/ZIP

**Option A: GitHub Actions (khuyến nghị)**

Xem workflow ở Step 6.2B.6

**Option B: Local ZIP Deploy**

```powershell
cd frontend
composer install --optimize-autoloader --no-dev
php artisan config:cache
php artisan route:cache
php artisan view:cache

# Zip (loại bỏ .env, storage/logs, etc.)
Compress-Archive -Path * -DestinationPath frontend.zip -Force

# Upload via Azure CLI hoặc Portal
az webapp deployment source config-zip `
  --resource-group rg-shopee-aff-dev `
  --name app-shopee-aff-web `
  --src frontend.zip
```

### 6.2B.5 Configure Startup Command

Vào Web App → **Settings** → **Configuration** → **General settings** → Startup Command:

```bash
cp /home/site/wwwroot/nginx.conf /etc/nginx/sites-available/default && service nginx reload
```

Hoặc dùng default (Azure auto-detect Laravel).

### 6.2B.6 GitHub Actions Laravel Workflow

**`.github/workflows/frontend.yml`**:
```yaml
name: Frontend CI/CD (Laravel)

on:
  push:
    branches: [main]
    paths: ['frontend/**']
  pull_request:
    branches: [main]
    paths: ['frontend/**']

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup PHP
        uses: shivammathur/setup-php@v2
        with:
          php-version: '8.3'
          extensions: mbstring, xml, ctype, json, curl
          tools: composer:v2

      - name: Install dependencies
        working-directory: frontend
        run: composer install --prefer-dist --no-dev --optimize-autoloader

      - name: Prepare Laravel
        working-directory: frontend
        run: |
          cp .env.example .env
          php artisan key:generate
          php artisan config:cache
          php artisan route:cache
          php artisan view:cache

      - name: Deploy to Azure Web App
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        uses: azure/webapps-deploy@v3
        with:
          app-name: ${{ secrets.AZURE_WEBAPP_FRONTEND_NAME }}
          publish-profile: ${{ secrets.AZURE_WEBAPP_FRONTEND_PUBLISH_PROFILE }}
          package: frontend

      - name: Health check
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        run: |
          sleep 60
          curl -f https://${{ secrets.AZURE_WEBAPP_FRONTEND_NAME }}.azurewebsites.net/
```

### 6.2B.7 CORS Configuration (Backend)

Đảm bảo Django backend cho phép requests từ frontend:

**`backend/config/settings/production.py`** (update CORS):
```python
CORS_ALLOWED_ORIGINS = [
    "https://app-shopee-aff-web.azurewebsites.net",
]
```

### 6.2B.8 Verification

```powershell
# Test Frontend
curl https://app-shopee-aff-web.azurewebsites.net/login

# Test Backend API
curl https://app-shopee-aff-backend.azurewebsites.net/api/health/

# Test Frontend → Backend connection (login)
# Open browser: https://app-shopee-aff-web.azurewebsites.net/login
# Try login - should call backend API
```

---

## Step 6.3 — Deploy Azure Function App (Portal)

### 6.3.1 Configure Function App Settings
1. Vào Function App → **Settings** → **Environment variables**
2. Thêm các app settings:

| Key | Value |
|---|---|
| `COSMOS_DB_URL` | `https://cosmos-shopee-aff-dev.documents.azure.com:443/` |
| `COSMOS_DB_KEY` | `<key>` |
| `COSMOS_DB_DATABASE` | `shopee-aff-db` |
| `AZURE_STORAGE_CONNECTION_STRING` | `<conn-string>` |
| `AZURE_STORAGE_CONTAINER` | `thumbnails` |
| `AZURE_SEARCH_ENDPOINT` | `https://srch-shopee-aff-dev.search.windows.net` |
| `AZURE_SEARCH_KEY` | `<key>` |
| `AZURE_SEARCH_INDEX` | `products` |

### 6.3.2 Deploy Function Code
```powershell
cd azure_functions
func azure functionapp publish func-shopee-aff-dev --python
```

> **Lưu ý**: Cần Azure Functions Core Tools (`func`) để deploy function code. Đây là CLI duy nhất cần thiết.

---

## Step 6.4 — GitHub Actions CI/CD

### 6.4.1 Repository Secrets

Thêm vào GitHub Repository Settings → Secrets and variables → Actions:

| Secret Name | Value |
|---|---|
| `AZURE_WEBAPP_PUBLISH_PROFILE` | Download từ Web App → Overview → **Get publish profile** |
| `AZURE_WEBAPP_NAME` | `app-shopee-aff-dev` |

> **Không cần Service Principal**: Dùng **Publish Profile** để authenticate GitHub Actions với Azure Web App. Đơn giản hơn, không cần Azure CLI.

### 6.4.2 Backend CI/CD Workflow

**`.github/workflows/backend.yml`**:
```yaml
name: Backend CI/CD

on:
  push:
    branches: [main]
    paths: ['backend/**']
  pull_request:
    branches: [main]
    paths: ['backend/**']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
          cache: 'pip'
          cache-dependency-path: backend/requirements.txt

      - name: Install dependencies
        working-directory: backend
        run: pip install -r requirements.txt

      - name: Run tests
        working-directory: backend
        env:
          DJANGO_SETTINGS_MODULE: config.settings.development
          DJANGO_SECRET_KEY: test-secret-key
          DJANGO_DEBUG: "True"
          ALLOWED_HOSTS: localhost
          # Use mock values for Azure services in tests
          COSMOS_DB_URL: https://mock.documents.azure.com/
          COSMOS_DB_KEY: mock-key
          COSMOS_DB_DATABASE: test-db
          AZURE_STORAGE_CONNECTION_STRING: "DefaultEndpointsProtocol=https;AccountName=mock;"
          AZURE_STORAGE_CONTAINER: thumbnails
          AZURE_SEARCH_ENDPOINT: https://mock.search.windows.net
          AZURE_SEARCH_KEY: mock-key
          AZURE_SEARCH_INDEX: products
          FUNCTION_APP_URL: https://mock.azurewebsites.net
          FUNCTION_APP_KEY: mock-key
        run: python manage.py test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'

    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Azure Web App
        uses: azure/webapps-deploy@v3
        with:
          app-name: ${{ secrets.AZURE_WEBAPP_NAME }}
          publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
          package: backend

      - name: Health check
        run: |
          sleep 30
          curl -f https://${{ secrets.AZURE_WEBAPP_NAME }}.azurewebsites.net/api/health/
```

### 6.4.3 Flutter Mobile CI Workflow

**`.github/workflows/mobile.yml`**:
```yaml
name: Mobile CI

on:
  push:
    branches: [main]
    paths: ['mobile/**']
  pull_request:
    branches: [main]
    paths: ['mobile/**']

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.x'
          channel: 'stable'

      - name: Get dependencies
        working-directory: mobile
        run: flutter pub get

      - name: Analyze
        working-directory: mobile
        run: flutter analyze

      - name: Test
        working-directory: mobile
        run: flutter test

      - name: Build APK (release)
        working-directory: mobile
        run: |
          flutter build apk --release \
            --dart-define=API_BASE_URL=https://${{ secrets.AZURE_WEBAPP_NAME }}.azurewebsites.net/api

      - name: Upload APK artifact
        uses: actions/upload-artifact@v4
        with:
          name: shopee-aff-release.apk
          path: mobile/build/app/outputs/flutter-apk/app-release.apk
```

---

## Step 6.5 — Production Verification

### 6.5.1 Smoke Test Checklist

```powershell
$BASE = "https://app-shopee-aff-dev.azurewebsites.net/api"

# 1. Health check
curl "$BASE/health/"
# Expected: {"status": "ok"}

# 2. Add a link
curl -X POST "$BASE/links/" `
  -H "Content-Type: application/json" `
  -d '{"url": "https://shp.ee/test123"}'
# Expected: 201 + link object with status=pending

# 3. List products
curl "$BASE/products/"
# Expected: 200 + paginated list

# 4. Search
curl "$BASE/search/?q=tai+nghe"
# Expected: 200 + search results
```

### 6.5.2 Azure Monitor Setup (Portal)

1. Vào **Application Insights** → **+ Create**
2. Resource Group: `rg-shopee-aff-dev`
3. Name: `ai-shopee-aff-dev`
4. Application type: **Web**
5. **Review + create** → **Create**

**Kết nối với Web App**:
1. Vào Web App → **Settings** → **Application Insights**
2. Chọn `ai-shopee-aff-dev` → **Apply**
3. Hoặc thêm app setting thủ công: `APPLICATIONINSIGHTS_CONNECTION_STRING` = `<connection-string>`

---

## Step 6.6 — Documentation Update Protocol

Mỗi khi có thay đổi lớn:

1. **API thay đổi** → update `docs/API_SPEC.md`
2. **Schema thay đổi** → update `docs/ARCHITECTURE.md` và data model docs
3. **Phase hoàn thành** → check off checklist trong file phase tương ứng, update version số
4. **Feature mới** → tạo `docs/FEATURE_<name>.md` mô tả implementation

---

## Phase 5 Checklist

- [ ] `Dockerfile` build thành công
- [ ] Docker test local — all endpoints respond
- [ ] Azure Web App deployed và `/api/health/` trả `200`
- [ ] Azure Function App deployed — test scrape thật sự trigger
- [ ] GitHub Actions: backend pipeline green (test + deploy)
- [ ] GitHub Actions: mobile pipeline green (build APK)
- [ ] Production smoke test — POST link → sau ~30s có product
- [ ] Production search test — search trả kết quả đúng
- [ ] Application Insights setup — logs visible
- [ ] Flutter release APK kết nối production BE thành công

---

## Summary: Complete Launch Checklist

### Infrastructure
- [ ] Azure Resource Group với tất cả services provisioned
- [ ] Environment variables đầy đủ (dev + production)
- [ ] Service connections verified

### Backend
- [ ] Django project chuẩn structure (config/apps/services)
- [ ] Products API: list, detail, delete
- [ ] Links API: create (trigger scrape), list, get status
- [ ] Shopee scraper: resolve redirect + extract title + thumbnail
- [ ] Azure Function: async scraping pipeline
- [ ] Azure Blob: thumbnail upload + public URL
- [ ] Azure AI Search: index creation + hybrid search
- [ ] Search API: smart search với RAG
- [ ] Unit tests pass

### Mobile
- [ ] Flutter project với feature-first architecture
- [ ] Add Link screen với clipboard auto-paste + polling
- [ ] Product Grid với thumbnail + price
- [ ] Smart Search với debounce + result highlights
- [ ] Error handling toàn bộ screens

### Deployment
- [ ] Backend live trên Azure Web App
- [ ] Function App live và functional
- [ ] CI/CD pipeline (test + deploy on push to main)
- [ ] Monitoring với Application Insights

---

## Extension Roadmap (Post-MVP)

| Feature | Estimated Effort | Notes |
|---|---|---|
| Telegram Bot | 2–3 days | Add `apps/telegram/` + webhook handler; reuse LinkService |
| Price tracking | 2 days | Subcollection `price_history` + daily Function trigger |
| Push notifications | 1–2 days | Firebase FCM khi scraping done |
| iOS build | 1 day | Cần Mac + Apple Developer account |
| Admin dashboard | 3–5 days | Django Admin hoặc simple React dashboard |
