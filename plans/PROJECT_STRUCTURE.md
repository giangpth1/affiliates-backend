---
title: Project Structure Guide
version: 1.0.0
updated: 2026-05-06
---

# Project Structure Guide

## Overview

Dự án được tổ chức theo monorepo pattern với 3 phần chính: Backend (Django), Azure Functions, và Mobile (Flutter).

```
shopee-aff-manager/
├── backend/                      # Django REST API
├── azure_functions/              # Serverless scraper
├── mobile/                       # Flutter mobile app
├── plans/                       # Planning & architecture docs
├── docs/                         # Code documentation (auto-generated)
├── scripts/                      # Utility scripts (future)
├── .github/workflows/            # CI/CD pipelines (future)
├── .gitignore
├── README.md
├── LICENSE
├── CHANGELOG.md
└── CHECKLIST.md
```

---

## Backend Structure (Django)

```
backend/
├── manage.py                     # Django CLI
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container build
├── .env.example                  # Env vars template
├── .env                          # Local env vars (gitignored)
│
├── config/                       # Django project settings
│   ├── __init__.py
│   ├── wsgi.py                  # WSGI entry point
│   ├── urls.py                  # Root URL routing
│   └── settings/
│       ├── __init__.py
│       ├── base.py              # Shared settings
│       ├── development.py       # Dev overrides
│       └── production.py        # Production config
│
├── apps/                         # Django applications
│   ├── core/                    # Shared utilities
│   │   ├── __init__.py
│   │   ├── models.py           # BaseDocument
│   │   ├── exceptions.py       # Custom exceptions
│   │   ├── pagination.py       # StandardPagination
│   │   ├── authentication.py   # APIKeyAuthentication
│   │   ├── permissions.py      # Custom permissions
│   │   └── middleware.py       # Security headers
│   │
│   ├── users/              # User authentication
│   │   ├── __init__.py
│   │   ├── models.py       # User dataclass
│   │   ├── serializers.py  # Registration, login, etc.
│   │   ├── views.py        # Auth endpoints
│   │   ├── urls.py
│   │   └── services.py     # UserService (bcrypt, JWT)
│   │
│   ├── links/                   # Affiliate link management
│   │   ├── __init__.py
│   │   ├── models.py           # Link dataclass
│   │   ├── serializers.py      # Link serializers
│   │   ├── views.py            # Link API views
│   │   ├── urls.py             # /api/links/ routes
│   │   └── services.py         # LinkService
│   │
│   ├── products/                # Product management
│   │   ├── __init__.py
│   │   ├── models.py           # Product dataclass
│   │   ├── serializers.py      # Product serializers
│   │   ├── views.py            # Product API views
│   │   ├── urls.py             # /api/products/ routes
│   │   └── services.py         # ProductService
│   │
│   └── search/                  # RAG search
│       ├── __init__.py
│       ├── views.py            # Search API views
│       ├── urls.py             # /api/search/ routes
│       ├── services.py         # SearchService
│       └── serializers.py      # Search serializers
│
├── services/                     # External service integrations
│   ├── __init__.py
│   ├── cosmos_db.py            # Cosmos DB client
│   ├── azure_storage.py        # Blob storage client
│   ├── azure_search.py         # AI Search client
│   └── scraper.py              # Shopee scraper
│
├── scripts/                      # Maintenance scripts
│   ├── verify_connections.py   # Test Azure connections
│   ├── create_search_index.py  # Initialize search index
│   ├── backup_cosmos.py        # Manual backup
│   ├── reindex_all.py          # Re-index products
│   └── cleanup_test_data.py    # Database cleanup
│
└── tests/                        # Unit & integration tests
    ├── __init__.py
    ├── test_links.py
    ├── test_products.py
    ├── test_search.py
    ├── test_scraper.py
    └── fixtures/
        └── sample_products.json
```

---

## Azure Functions Structure

```
azure_functions/
├── host.json                     # Function App config
├── requirements.txt              # Python dependencies
├── local.settings.json           # Local env (gitignored)
│
└── scrape_product/               # HTTP trigger function
    ├── __init__.py              # Main handler
    └── function.json            # Function metadata
```

**`scrape_product/__init__.py`** — Main logic:
1. Receive HTTP request với `{link_id, url, user_id}`
2. Update link status → `processing`
3. Run scraper (fetch HTML, parse title/thumbnail)
4. Upload thumbnail → Azure Blob Storage
5. Create product record → Cosmos DB
6. Index product → Azure AI Search
7. Update link status → `done` hoặc `failed`

---

## Mobile App Structure (Flutter)

```
mobile/
├── pubspec.yaml                  # Flutter dependencies
├── lib/
│   ├── main.dart                # App entry point
│   │
│   ├── app/
│   │   ├── app.dart            # MaterialApp root
│   │   └── router.dart         # go_router config
│   │
│   ├── core/                    # Core utilities
│   │   ├── constants.dart      # API URL, constants
│   │   ├── dio_client.dart     # HTTP client singleton
│   │   └── error_handler.dart  # API error mapping
│   │
│   ├── features/                # Feature modules (clean arch)
│   │   ├── links/
│   │   │   ├── data/
│   │   │   │   ├── link_repository.dart
│   │   │   │   └── link_model.dart
│   │   │   ├── domain/
│   │   │   │   └── link_provider.dart      # Riverpod state
│   │   │   └── presentation/
│   │   │       ├── add_link_screen.dart
│   │   │       └── links_list_screen.dart
│   │   │
│   │   ├── products/
│   │   │   ├── data/
│   │   │   │   ├── product_repository.dart
│   │   │   │   └── product_model.dart
│   │   │   ├── domain/
│   │   │   │   └── product_provider.dart
│   │   │   └── presentation/
│   │   │       ├── product_list_screen.dart
│   │   │       └── product_detail_screen.dart
│   │   │
│   │   └── search/
│   │       ├── data/
│   │       │   ├── search_repository.dart
│   │       │   └── search_result_model.dart
│   │       ├── domain/
│   │       │   └── search_provider.dart
│   │       └── presentation/
│   │           └── search_screen.dart
│   │
│   └── shared/                   # Reusable widgets
│       ├── widgets/
│       │   ├── product_card.dart
│       │   ├── thumbnail_image.dart
│       │   ├── loading_overlay.dart
│       │   └── error_snackbar.dart
│       └── theme/
│           └── app_theme.dart
│
├── android/                      # Android native config
├── ios/                          # iOS native config
└── test/                         # Unit & widget tests
    ├── widget_test.dart
    └── unit/
```

---

## Documentation Structure

```
plans/
├── PLAN.md                       # Master plan (phases overview)
├── ARCHITECTURE.md               # System architecture
├── API_SPEC.md                   # REST API reference
├── USER_AUTHENTICATION.md        # Complete auth system
├── PLAN_PHASE_1_SETUP.md         # Dev env + Azure setup
├── PLAN_PHASE_2_BACKEND.md       # Django backend core
├── PLAN_PHASE_3_AI_RAG.md        # AI Search & RAG
├── PLAN_PHASE_4_MOBILE.md        # Flutter mobile app
├── PLAN_PHASE_5_DEPLOY.md        # Deployment & CI/CD
├── MONITORING.md                 # Monitoring strategy
├── SECURITY.md                   # Security best practices
├── MAINTENANCE.md                # Ops & troubleshooting
├── COST_ESTIMATION.md            # Azure cost breakdown
├── THEME_SYSTEM.md               # Theme design guidelines
├── INTERNATIONALIZATION.md       # i18n strategy
└── PROJECT_STRUCTURE.md          # This file

docs/
├── README.md                     # Code documentation index
├── THEME_I18N_CONFIG.md          # Theme & i18n live config
└── ... (auto-generated from code)
```

---

## Scripts Structure (Future)

```
scripts/
├── provision_azure.sh            # Automate Azure resource creation
├── deploy_backend.sh             # Deploy Django to Azure Web App
├── deploy_function.sh            # Deploy Azure Function
├── run_tests.sh                  # Run all test suites
├── generate_api_docs.sh          # Auto-generate OpenAPI spec
└── cost_report.py                # Azure cost analysis
```

---

## CI/CD Structure (Future)

```
.github/workflows/
├── backend.yml                   # Django CI/CD
│   ├── Trigger: push to main, PR
│   ├── Steps: test → build → deploy
│   └── Deploy to: Azure Web App
│
├── function.yml                  # Azure Function CI/CD
│   ├── Trigger: push to main (azure_functions/** changed)
│   └── Deploy to: Azure Function App
│
├── mobile.yml                    # Flutter CI/CD
│   ├── Trigger: push to main (mobile/** changed)
│   ├── Steps: test → build APK/IPA
│   └── Upload to: Firebase App Distribution
│
└── docs.yml                      # Documentation validation
    ├── Trigger: PR
    └── Steps: markdown lint, link check
```

---

## File Naming Conventions

### Python (Backend)
- **Models**: `snake_case` (e.g., `link_model.py`, `product.py`)
- **Classes**: `PascalCase` (e.g., `LinkService`, `ProductSerializer`)
- **Functions**: `snake_case` (e.g., `create_link`, `get_product`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_PAGE_SIZE`, `API_VERSION`)

### Dart (Mobile)
- **Files**: `snake_case` (e.g., `product_card.dart`, `search_screen.dart`)
- **Classes**: `PascalCase` (e.g., `ProductCard`, `SearchScreen`)
- **Variables**: `camelCase` (e.g., `productId`, `searchQuery`)
- **Constants**: `lowerCamelCase` (e.g., `defaultPageSize`, `maxRetries`)

### Documentation
- **Markdown**: `UPPER_SNAKE_CASE` (e.g., `README.md`, `ARCHITECTURE.md`)
- **Phase docs**: `PLAN_PHASE_N_NAME.md` (e.g., `PLAN_PHASE_1_SETUP.md`)

---

## Import Organization

### Python
```python
# 1. Standard library
import os
import json
from datetime import datetime

# 2. Third-party packages
from django.conf import settings
from rest_framework.views import APIView
from azure.cosmos import CosmosClient

# 3. Local imports
from apps.core.models import BaseDocument
from services.cosmos_db import CosmosDBService
```

### Dart
```dart
// 1. Dart SDK
import 'dart:async';
import 'dart:convert';

// 2. Flutter framework
import 'package:flutter/material.dart';

// 3. Third-party packages
import 'package:dio/dio.dart';
import 'package:riverpod/riverpod.dart';

// 4. Local imports (relative)
import '../data/product_model.dart';
import '../../../core/dio_client.dart';
```

---

## Environment Files

### Development
```
backend/.env                      # Local secrets (gitignored)
backend/.env.example              # Template (committed)
azure_functions/local.settings.json  # Function secrets (gitignored)
mobile/lib/core/constants.dart    # API URL (localhost)
```

### Production
- **Azure Web App**: App Settings (environment variables)
- **Azure Function**: App Settings
- **Mobile**: Build-time constants (via `--dart-define`)

---

## Key Design Patterns

### Backend
- **Service Layer Pattern**: Business logic in `services.py`
- **Repository Pattern**: Data access via `CosmosDBService`
- **Serializer Pattern**: DRF serializers for validation
- **Singleton Pattern**: Azure SDK clients (lazy init)

### Mobile
- **Feature-First Architecture**: Group by feature (links, products, search)
- **Clean Architecture**: Separation (data, domain, presentation)
- **Provider Pattern**: Riverpod for state management
- **Repository Pattern**: Abstract API calls in repositories

---

## Testing Structure

### Backend Tests
```
tests/
├── test_links.py                 # Link API tests
├── test_products.py              # Product API tests
├── test_search.py                # Search API tests
├── test_scraper.py               # Scraper unit tests
└── test_cosmos_db.py             # Cosmos DB service tests
```

**Run tests**:
```bash
python manage.py test
# Or with pytest
pytest tests/ -v --cov=apps --cov=services
```

### Mobile Tests
```
test/
├── widget_test.dart              # Widget tests
├── unit/
│   ├── repository_test.dart     # Repository tests
│   └── model_test.dart          # Model tests
└── integration/
    └── app_test.dart            # E2E tests
```

**Run tests**:
```bash
flutter test
# With coverage
flutter test --coverage
```

---

## Deployment Artifacts

### Backend
- **Local**: Django dev server (port 8000)
- **Azure**: Docker container (via ZIP deploy or ACR)
- **Artifact**: `backend-deploy.zip` hoặc Docker image

### Azure Functions
- **Local**: Functions Core Tools (port 7071)
- **Azure**: Consumption plan deployment
- **Artifact**: Function App package (ZIP)

### Mobile
- **Android**: `build/app/outputs/flutter-apk/app-release.apk`
- **iOS**: `build/ios/iphoneos/Runner.app` (requires Mac + Xcode)
- **Artifact**: APK/IPA files

---

## Version Control Workflow

### Branch Strategy
- `main` — Production-ready code
- `develop` — Development branch (optional)
- `feature/xxx` — Feature branches
- `hotfix/xxx` — Critical bug fixes

### Commit Message Convention
```
type(scope): description

Examples:
feat(api): add batch product upload endpoint
fix(scraper): handle timeout on Shopee requests
docs(readme): update installation instructions
refactor(auth): migrate to JWT authentication
test(links): add unit tests for LinkService
```

**Types**: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`

---

## Monitoring & Logs

### Application Logs Location
- **Azure Web App**: Stream via Portal → Web App → Monitoring → Log stream
- **Azure Function**: Application Insights Logs
- **Local Django**: Console output
- **Mobile**: Debug console (Flutter DevTools)

### Metrics Dashboard
- **Azure Portal**: Application Insights → Dashboards
- **Custom**: Kusto queries for specific metrics
- **Alerts**: Email/Slack notifications

---

## Quick Navigation

| Need | File/Folder |
|---|---|
| Add new API endpoint | `apps/*/views.py` → `apps/*/urls.py` |
| Change database schema | `apps/*/models.py` |
| Modify scraping logic | `services/scraper.py` |
| Update search algorithm | `services/azure_search.py` |
| Add new mobile screen | `mobile/lib/features/*/presentation/` |
| Configure Azure resources | `.env` → Azure Portal App Settings |
| View API spec | `docs/API_SPEC.md` |
| Troubleshoot errors | `docs/MAINTENANCE.md` |
| Check costs | `docs/COST_ESTIMATION.md` |
| Run tests | `backend/tests/` or `mobile/test/` |

---

**Last updated**: 2026-05-06
