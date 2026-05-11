---
title: System Architecture
version: 1.0.0
updated: 2026-05-06
---

# System Architecture — Shopee Affiliate Link Manager

## Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                │
│                                                                     │
│   ┌─────────────────┐              ┌──────────────────────────┐    │
│   │  Flutter Mobile  │              │  Telegram Bot (future)   │    │
│   │      App         │              │                          │    │
│   └────────┬────────┘              └────────────┬─────────────┘    │
└────────────┼────────────────────────────────────┼──────────────────┘
             │ HTTPS / REST API                   │
             ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     AZURE WEB APP (BE Layer)                        │
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │                   Django Application                         │  │
│   │                                                             │  │
│   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │  │
│   │  │  Auth API    │  │  Links API   │  │  Search API  │  │ Products   │  │  │
│   │  │  /api/auth/  │  │  /api/links/ │  │  /api/search/│  │ API        │  │  │
│   │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └─────┬──────┘  │  │
│   │         │                 │                 │                 │         │  │
│   │  ┌──────▼──────────────────────────────────────────────────────────┐  │  │
│   │  │         JWT Authentication Middleware (all except /auth/)        │  │  │
│   │  └──────┬──────────────────────────────────────────────────────────┘  │  │
│   │         │                                                              │  │
│   │  ┌──────▼──────────────────────────────────────────────────────────┐  │  │
│   │  │              Service Layer                                       │  │  │
│   │  │  UserService │ LinkService │ SearchService │ ProductService      │  │  │
│   │  └──────┬──────────────┬────────────────┬─────────────────┬────────┘  │  │
│   └─────────┼──────────────┼────────────────────────────────────┘  │
└─────────────┼──────────────┼─────────────────────────────────────┘
              │              │
              ▼              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      AZURE SERVICES LAYER                           │
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  Azure Cosmos DB │  │  Azure AI Search │  │  Azure Storage   │  │
│  │  Containers:     │  │  (RAG Indexing)  │  │  (Thumbnails)    │  │
│  │  - users         │  │                  │  │                  │  │
│  │  - products      │  │                  │  │                  │  │
│  │  - links         │  │                  │  │                  │  │
│  │  - token_blackl. │  │                  │  │                  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                     │
│  ┌──────────────────┐                                             │
│  │ Azure Function   │                                             │
│  │ (Async Scraping) │                                             │
│  └──────────────────┘                                             │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 0. User Authentication Flow
```
Mobile App (Login Screen)
  │── POST /api/auth/login/ { email, password }
  │
  ▼
Django API (UserService)
  │── Validate credentials
  │── Query users container → Cosmos DB
  │── Verify password (bcrypt)
  │── Generate JWT tokens:
  │    - Access token (1h)
  │    - Refresh token (7d)
  │
  ▼
Mobile App
  │── Save tokens → FlutterSecureStorage
  │── Navigate to home screen
  │
  │── All subsequent API requests include:
  │    Authorization: Bearer <access_token>
  │
  ▼
Django JWT Middleware
  │── Verify token signature
  │── Extract user_id from token
  │── Attach user object to request
  │── Forward to protected endpoints
```

### 1. Add Affiliate Link Flow (Authenticated)
```
Mobile App
  │── POST /api/links/ 
  │    Authorization: Bearer <token>
  │    { url: "https://shp.ee/xxxxx" }
  │
  ▼
Django JWT Middleware
  │── Extract user_id from token
  │
  ▼
Django API (LinkService)
  │── Validate URL format
  │── Resolve redirect → actual Shopee product URL
  │── Save link record (status: PENDING, user_id) → Cosmos DB
  │── Trigger Azure Function (async)
  │
  ▼
Azure Function App (Scraper)
  │── Fetch product page HTML
  │── Extract: title, thumbnail URL, price, shop_id
  │── Upload thumbnail → Azure Blob Storage
  │── Update product record → Cosmos DB (status: DONE)
  │── Index document → Azure AI Search
  │
  ▼
Mobile App
  │── Poll GET /api/links/{id}/ or WebSocket for status
```

### 2. Smart Search Flow (Authenticated)
```
Mobile App
  │── GET /api/search/?q="tai nghe sony"
  │    Authorization: Bearer <token>
  │
  ▼
Django JWT Middleware
  │── Extract user_id from token
  │
  ▼
Django API (SearchService)
  │── Semantic search → Azure AI Search (built-in ML)
  │── Filter results: only user's products (user_id)
  │── Return ranked results with highlights
  │
  ▼
Mobile App
  │── Display search results with thumbnails
```

## Directory Structure

```
shopee-aff-manager/
├── backend/                    # Django project root
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   ├── config/                 # Django settings module
│   │   ├── __init__.py
│   │   ├── settings/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── core/               # Shared utilities
│   │   │   ├── models.py       # Abstract base models
│   │   │   ├── exceptions.py
│   │   │   ├── pagination.py
│   │   │   └── authentication.py  # JWT custom auth (if needed)
│   │   ├── users/              # User authentication
│   │   │   ├── models.py       # User dataclass
│   │   │   ├── serializers.py  # Registration, login, etc.
│   │   │   ├── views.py        # Auth endpoints
│   │   │   ├── urls.py
│   │   │   └── services.py     # UserService (bcrypt, JWT)
│   │   ├── products/           # Product management
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── services.py
│   │   ├── links/              # Affiliate link management
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── services.py
│   │   └── search/             # RAG search
│   │       ├── views.py
│   │       ├── urls.py
│   │       └── services.py
│   ├── services/               # External integrations
│   │   ├── cosmos_db.py
│   │   ├── azure_storage.py
│   │   ├── azure_search.py
│   │   ├── openai_client.py
│   │   └── scraper.py
│   └── tests/
│       ├── test_links.py
│       ├── test_products.py
│       └── test_search.py
│
├── azure_functions/            # Azure Function App
│   ├── host.json
│   ├── requirements.txt
│   └── scrape_product/
│       ├── __init__.py
│       └── function.json
│
├── mobile/                     # Flutter app
│   ├── pubspec.yaml
│   ├── lib/
│   │   ├── main.dart
│   │   ├── app/
│   │   │   ├── app.dart
│   │   │   └── router.dart
│   │   ├── features/
│   │   │   ├── links/
│   │   │   │   ├── data/
│   │   │   │   ├── domain/
│   │   │   │   └── presentation/
│   │   │   ├── products/
│   │   │   │   ├── data/
│   │   │   │   ├── domain/
│   │   │   │   └── presentation/
│   │   │   └── search/
│   │   │       ├── data/
│   │   │       ├── domain/
│   │   │       └── presentation/
│   │   └── shared/
│   │       ├── widgets/
│   │       ├── services/
│   │       └── theme/
│   └── test/
│
├── docs/
    ├── README.md
    ├── THEME_I18N_CONFIG.md
    └── ... (auto-generated code docs)
```

## Azure Resources

| Resource | Name (template) | Purpose |
|---|---|---|
| Resource Group | `rg-shopee-aff-{env}` | Container for all resources |
| Azure Web App | `app-shopee-aff-{env}` | Django backend host |
| App Service Plan | `asp-shopee-aff-{env}` | B2 or higher |
| Cosmos DB Account | `cosmos-shopee-aff-{env}` | NoSQL document store |
| Cosmos DB Database | `shopee-aff-db` | Main database |
| Cosmos DB Container | `users`, `products`, `links`, `token_blacklist` | Collections |
| Azure AI Search | `srch-shopee-aff-{env}` | RAG vector search |
| Azure Storage | `stshopeeaff{env}` | Blob for thumbnails |
| Azure Function App | `func-shopee-aff-{env}` | Async scraper |

## Technology Stack

| Layer | Technology | Version |
|---|---|---|
| Backend Language | Python | 3.13 |
| Backend Framework | Django | 5.x |
| REST Framework | Django REST Framework | 3.15+ |
| Database Driver | azure-cosmos | 4.x |
| Search Client | azure-search-documents | 11.x |
| Storage Client | azure-storage-blob | 12.x |
| OpenAI Client | openai | 1.x |
| HTTP Scraping | httpx + BeautifulSoup4 | latest |
| Mobile | Flutter | 3.x |
| Mobile State | Riverpod | 2.x |
| Mobile HTTP | Dio | 5.x |
