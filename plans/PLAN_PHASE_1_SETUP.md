---
title: Phase 1 — Setup & Infrastructure
version: 1.0.0
updated: 2026-05-06
---

# Phase 1: Setup & Infrastructure

## Goals
- Cài đặt đầy đủ môi trường phát triển
- Provision tất cả Azure resources
- Verify connectivity từ local đến mọi Azure service
- Có project Django chạy được với `runserver`

---

## Step 1.1 — Install Developer Tools

### 1.1.1 Python 3.13
```powershell
# Download Python 3.13 từ python.org/downloads
# Sau khi cài:
python --version          # Python 3.13.x
pip --version

# Cài virtualenv
pip install virtualenv
```

### 1.1.2 Azure Portal
```
# Truy cập https://portal.azure.com
# Đăng nhập bằng tài khoản Azure
# Xác nhận subscription đang active
```

> **Lưu ý**: Tất cả Azure resources sẽ được tạo thủ công qua Portal, không dùng CLI.

### 1.1.3 Azure Functions Core Tools v4
```powershell
npm install -g azure-functions-core-tools@4
func --version           # 4.x.x
```

### 1.1.4 Flutter SDK
```powershell
# Download Flutter SDK từ flutter.dev/docs/get-started/install/windows
flutter --version
flutter doctor           # Fix tất cả issues (Android SDK, etc.)
```

### 1.1.5 VS Code Extensions
- Python (Microsoft)
- Flutter (Dart Code)
- Azure Tools (Microsoft)
- REST Client (Huachao Mao) — để test API

---

## Step 1.2 — Scaffold Django Project

### 1.2.1 Tạo project structure
```powershell
# Từ C:\Projects\New project\
mkdir backend
cd backend

python -m virtualenv venv
.\venv\Scripts\Activate.ps1

pip install django==5.2 djangorestframework==3.15 django-environ
django-admin startproject config .
```

### 1.2.2 Tạo settings split
```
backend/config/settings/
├── __init__.py       # Empty
├── base.py           # Shared settings
├── development.py    # Local dev overrides
└── production.py     # Azure production config
```

**`config/settings/base.py`** — settings dùng chung:
```python
import environ

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = env('DJANGO_SECRET_KEY')
DEBUG = env.bool('DJANGO_DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'apps.core',
    'apps.users',
    'apps.links',
    'apps.products',
    'apps.search',
]

# DRF config
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_PAGINATION_CLASS': 'apps.core.pagination.StandardPagination',
    'PAGE_SIZE': 20,
}

# Azure config (read from env)
COSMOS_DB_URL = env('COSMOS_DB_URL')
COSMOS_DB_KEY = env('COSMOS_DB_KEY')
COSMOS_DB_DATABASE = env('COSMOS_DB_DATABASE', default='shopee-aff-db')

AZURE_STORAGE_CONNECTION_STRING = env('AZURE_STORAGE_CONNECTION_STRING')
AZURE_STORAGE_CONTAINER = env('AZURE_STORAGE_CONTAINER', default='thumbnails')

AZURE_SEARCH_ENDPOINT = env('AZURE_SEARCH_ENDPOINT')
AZURE_SEARCH_KEY = env('AZURE_SEARCH_KEY')
AZURE_SEARCH_INDEX = env('AZURE_SEARCH_INDEX', default='products')

FUNCTION_APP_URL = env('FUNCTION_APP_URL')
FUNCTION_APP_KEY = env('FUNCTION_APP_KEY')
```

**`config/settings/development.py`**:
```python
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Disable HTTPS redirects in dev
SECURE_SSL_REDIRECT = False
```

**`config/settings/production.py`**:
```python
from .base import *

DEBUG = False
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 1.2.3 Cập nhật `manage.py`
```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
```

### 1.2.4 Tạo app modules
```powershell
mkdir apps
python manage.py startapp core apps/core
python manage.py startapp users apps/users
python manage.py startapp links apps/links
python manage.py startapp products apps/products
python manage.py startapp search apps/search
```

### 1.2.5 Tạo `.env` file
```
# backend/.env  (KHÔNG commit file này)
DJANGO_SECRET_KEY=your-super-secret-key-here
DJANGO_DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

COSMOS_DB_URL=https://cosmos-shopee-aff-dev.documents.azure.com:443/
COSMOS_DB_KEY=<primary-key>
COSMOS_DB_DATABASE=shopee-aff-db

AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
AZURE_STORAGE_CONTAINER=thumbnails

AZURE_SEARCH_ENDPOINT=https://srch-shopee-aff-dev.search.windows.net
AZURE_SEARCH_KEY=<admin-key>
AZURE_SEARCH_INDEX=products

FUNCTION_APP_URL=https://func-shopee-aff-dev.azurewebsites.net
FUNCTION_APP_KEY=<function-key>
```

### 1.2.6 Tạo `.env.example`
Copy `.env` nhưng thay tất cả values bằng placeholder, commit file này.

---

## Step 1.3 — Provision Azure Resources (Azure Portal)

> **Tất cả resources được tạo thủ công qua [Azure Portal](https://portal.azure.com).**
> Sau khi tạo mỗi resource, copy connection string/key vào `.env`.

### 1.3.1 Tạo Resource Group
1. Vào **Resource groups** → **+ Create**
2. Subscription: chọn subscription của bạn
3. Resource group name: `rg-shopee-aff-dev`
4. Region: `Southeast Asia`
5. **Review + create** → **Create**

### 1.3.2 Tạo Azure Cosmos DB
1. Vào **Azure Cosmos DB** → **+ Create**
2. API: **Azure Cosmos DB for NoSQL**
3. Account name: `cosmos-shopee-aff-dev`
4. Capacity mode: **Serverless** (tiết kiệm cost cho dev)
5. **Review + create** → **Create**

**Tạo Database & Containers** (sau khi account ready):
1. Vào Cosmos DB account → **Data Explorer**
2. **New Database**: `shopee-aff-db`
3. **New Container** — tạo lần lượt 4 containers:

| Container | Partition Key |
|---|---|
| `products` | `/shop_id` |
| `links` | `/user_id` |
| `users` | `/id` |
| `token_blacklist` | `/token_type` |

**Lấy connection string**:
1. Vào Cosmos DB account → **Keys**
2. Copy **URI** → `COSMOS_DB_URL`
3. Copy **PRIMARY KEY** → `COSMOS_DB_KEY`

### 1.3.3 Tạo Azure Storage Account
1. Vào **Storage accounts** → **+ Create**
2. Storage account name: `stshopeeaffdev`
3. Redundancy: **LRS**
4. **Review + create** → **Create**

**Tạo Blob Container**:
1. Vào Storage account → **Containers** → **+ Container**
2. Name: `thumbnails`
3. Public access level: **Blob (anonymous read access)**

**Lấy connection string**:
1. Vào Storage account → **Access keys**
2. Copy **Connection string** → `AZURE_STORAGE_CONNECTION_STRING`

### 1.3.4 Tạo Azure AI Search
1. Vào **AI Search** → **+ Create**
2. Service name: `srch-shopee-aff-dev`
3. Pricing tier: **Free** (đủ cho dev, 50MB, 3 indexes, 10K docs)
4. **Review + create** → **Create**

**Lấy admin key**:
1. Vào Search service → **Keys**
2. Copy **Primary admin key** → `AZURE_SEARCH_KEY`
3. URL mặc định: `https://srch-shopee-aff-dev.search.windows.net` → `AZURE_SEARCH_ENDPOINT`

### 1.3.5 Tạo Azure Function App
1. Vào **Function App** → **+ Create**
2. Publish: **Code**
3. Runtime stack: **Python**
4. Version: **3.13**
5. Plan type: **Consumption (Serverless)**
6. Storage account: tạo mới `stfuncshopeedev`
7. **Review + create** → **Create**

**Lấy function key** (sau khi deploy function code):
1. Vào Function App → **Functions** → chọn function → **Function Keys**
2. Copy **default** key → `FUNCTION_APP_KEY`
3. URL: `https://func-shopee-aff-dev.azurewebsites.net` → `FUNCTION_APP_URL`

---

## Step 1.4 — Install Python Dependencies

```powershell
# backend/requirements.txt
pip install \
  django==5.2 \
  djangorestframework==3.15 \
  djangorestframework-simplejwt==5.4 \
  django-environ==0.11 \
  bcrypt==4.2 \
  azure-cosmos==4.9 \
  azure-storage-blob==12.24 \
  azure-search-documents==11.6 \
  openai==1.78 \
  httpx==0.28 \
  beautifulsoup4==4.13 \
  lxml==5.4 \
  Pillow==11.2 \
  gunicorn==23.0

pip freeze > requirements.txt
```

---

## Step 1.5 — Verify All Connections

Tạo `backend/scripts/verify_connections.py`:

```python
"""Run this script to verify all Azure connections work."""
import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.development'
django.setup()

from django.conf import settings
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

def check_cosmos():
    client = CosmosClient(settings.COSMOS_DB_URL, settings.COSMOS_DB_KEY)
    db = client.get_database_client(settings.COSMOS_DB_DATABASE)
    containers = list(db.list_containers())
    print(f"✓ Cosmos DB: {len(containers)} containers found")

def check_storage():
    client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
    containers = list(client.list_containers())
    print(f"✓ Azure Storage: connected, {len(containers)} containers")

def check_search():
    client = SearchClient(
        endpoint=settings.AZURE_SEARCH_ENDPOINT,
        index_name=settings.AZURE_SEARCH_INDEX,
        credential=AzureKeyCredential(settings.AZURE_SEARCH_KEY)
    )
    print(f"✓ Azure AI Search: connected")

if __name__ == '__main__':
    check_cosmos()
    check_storage()
    check_search()
    print("\nAll connections verified!")
```

```powershell
cd backend
python scripts/verify_connections.py
# Expected: ✓ for all services
```

---

## Step 1.6 — Initialize Git Repository

```powershell
# Từ C:\Projects\New project\
git init
git add .gitignore
git commit -m "chore: init project structure"
```

**`.gitignore`** phải bao gồm:
```
# Python
backend/venv/
backend/__pycache__/
backend/*.pyc
backend/.env
backend/db.sqlite3

# Flutter
mobile/.dart_tool/
mobile/build/
mobile/.flutter-plugins*

# Azure
*.publishsettings
local.settings.json

# Secrets
*.key
*.pem
```

---

## Phase 1 Checklist

- [ ] Python 3.13 installed và virtualenv active
- [ ] Azure Portal access với đúng subscription
- [ ] Flutter doctor — no critical errors
- [ ] Django project starts: `python manage.py runserver` → OK
- [ ] All 5 apps created (core, users, links, products, search)
- [ ] `.env` file populated với Azure credentials
- [ ] All Azure resources provisioned qua Portal (Cosmos, Storage, Search, Function)
- [ ] `verify_connections.py` — all green
- [ ] Git repo initialized với `.gitignore`

**Next:** [Phase 2 — Django Backend Core](PLAN_PHASE_2_BACKEND.md)
