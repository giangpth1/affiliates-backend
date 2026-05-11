# Shopee Affiliate Link Manager

Hệ thống quản lý link affiliate Shopee với smart search dựa trên Azure AI và RAG (Retrieval-Augmented Generation).

## Tổng quan

- **Backend**: Python 3.13 + Django 5.x + Django REST Framework
- **Mobile**: Flutter 3.x với Riverpod state management
- **Database**: Azure Cosmos DB (NoSQL)
- **Search**: Azure AI Search (semantic search)
- **Storage**: Azure Blob Storage (thumbnails)
- **Async Processing**: Azure Function App (scraping pipeline)

## Tính năng chính

🔒 **User Authentication**: JWT-based authentication (required) - register, login, secure token storage  
✅ **Auto-scraping**: Paste link Shopee affiliate → tự động lấy title + thumbnail  
✅ **Smart search**: RAG-powered search với Vietnamese language support  
✅ **Mobile-first**: Flutter app với offline-ready architecture  
🎨 **Theme System**: Light/dark modes với Shopee Orange branding  
🌐 **Internationalization**: Vietnamese (primary) + English support  
✅ **Scalable**: Azure-native, production-ready deployment  
✅ **Extensible**: Dễ dàng mở rộng (Telegram bot, price tracking, v.v.)

## Cấu trúc dự án

```
.
├── backend/              # Django REST API
│   ├── apps/            # Django apps (users, links, products, search)
│   ├── config/          # Settings & routing
│   ├── services/        # Azure SDK integrations
│   └── scripts/         # Maintenance scripts
├── azure_functions/      # Azure Function App (async scraper)
├── mobile/              # Flutter mobile app
├── plans/               # Planning & architecture docs
│   ├── PLAN.md                    # Master plan overview
│   ├── ARCHITECTURE.md            # System architecture
│   ├── API_SPEC.md                # REST API specification (with auth endpoints)
│   ├── USER_AUTHENTICATION.md     # **Complete auth system (REQUIRED)**
│   ├── PLAN_PHASE_*.md            # Detailed implementation plans (5 phases)
│   ├── SECURITY.md                # Security & authentication
│   ├── MONITORING.md              # Monitoring & logging strategy
│   ├── MAINTENANCE.md             # Maintenance & operations
│   ├── COST_ESTIMATION.md         # Azure cost breakdown
│   ├── THEME_SYSTEM.md            # Flutter theme design
│   ├── INTERNATIONALIZATION.md    # i18n strategy
│   └── PROJECT_STRUCTURE.md       # Project organization guide
└── docs/                # Code documentation (auto-generated)
    ├── API_ENDPOINTS.md           # Live API endpoints reference
    ├── DATABASE_SCHEMA.md         # Cosmos DB schemas
    ├── THEME_I18N_CONFIG.md       # Live theme & i18n config
    └── FEATURES.md                # Implemented features
```

## Quick Start

### Prerequisites

- Python 3.13+
- Flutter 3.x
- Azure subscription (with OpenAI access)

### 1. Clone & Setup Backend

```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # Linux/Mac

pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` → `.env` và điền Azure credentials:

```env
DJANGO_SECRET_KEY=your-secret-key
COSMOS_DB_URL=https://your-cosmos.documents.azure.com:443/
COSMOS_DB_KEY=your-cosmos-key
# ... (see .env.example for full list)
```

### 3. Run Development Server

```bash
python manage.py runserver
```

API available at: `http://localhost:8000/api/`

### 4. Setup Mobile App

```bash
cd mobile
flutter pub get
flutter run
```

---

## Documentation

### 📘 Planning & Architecture
- **[Master Plan](plans/PLAN.md)**: Project overview, phases, timeline
- **[Architecture](plans/ARCHITECTURE.md)**: System design, data flow, tech stack
- **[API Spec](plans/API_SPEC.md)**: Complete REST API reference

### 🛠️ Implementation Guides
- **[Phase 1: Setup](plans/PLAN_PHASE_1_SETUP.md)**: Dev environment + Azure provisioning
- **[Phase 2: Backend](plans/PLAN_PHASE_2_BACKEND.md)**: Django core + scraper
- **[Phase 3: AI Search](plans/PLAN_PHASE_3_AI_RAG.md)**: Semantic search indexing
- **[Phase 4: Mobile](plans/PLAN_PHASE_4_MOBILE.md)**: Flutter app development
- **[Phase 5: Deploy](plans/PLAN_PHASE_5_DEPLOY.md)**: Production deployment + CI/CD

### 🔧 Operations
- **[Monitoring](plans/MONITORING.md)**: Application Insights, alerts, dashboards
- **[Security](plans/SECURITY.md)**: Authentication, CORS, rate limiting
- **[Maintenance](plans/MAINTENANCE.md)**: Backup, disaster recovery, troubleshooting
- **[Cost Estimation](plans/COST_ESTIMATION.md)**: Azure pricing, optimization strategies
- **[Project Structure](plans/PROJECT_STRUCTURE.md)**: Directory organization, conventions

### 🎨 UI/UX Guidelines
- **[Theme System](plans/THEME_SYSTEM.md)**: Design system, colors, typography, light/dark themes
- **[Internationalization](plans/INTERNATIONALIZATION.md)**: Multi-language support (Vietnamese, English)

### 📝 Code Documentation
- **[API Endpoints](docs/API_ENDPOINTS.md)**: Live API endpoint reference (auto-generated)
- **[Database Schema](docs/DATABASE_SCHEMA.md)**: Cosmos DB schemas (auto-generated)
- **[Features](docs/FEATURES.md)**: Implemented features documentation

---

## Development Workflow

### Backend Development

```bash
# Run tests
python manage.py test

# Create new app
python manage.py startapp myapp apps/myapp

# Verify Azure connections
python scripts/verify_connections.py
```

### Mobile Development

```bash
# Run on emulator
flutter run

# Build APK
flutter build apk --release

# Run tests
flutter test
```

---

## Deployment

### Azure Resources Provisioning

### 2. Provision Azure Resources

Tạo tất cả resources thủ công qua [Azure Portal](https://portal.azure.com). Xem hướng dẫn chi tiết trong [PLAN_PHASE_1_SETUP.md](plans/PLAN_PHASE_1_SETUP.md).

### Backend Deployment

### 3. Deploy Backend

Deploy thủ công qua Azure Portal:
1. Zip thư mục `backend/` (bỏ `venv/`)
2. Vào Web App → Deployment Center → Zip Deploy → upload

Hoặc push lên `main` branch để GitHub Actions tự deploy.

**CI/CD**: GitHub Actions workflow in `.github/workflows/backend.yml`

---

## API Examples

### Create Link
```bash
curl -X POST http://localhost:8000/api/links/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"url": "https://shp.ee/abc123"}'
```

### Search Products
```bash
curl "http://localhost:8000/api/search/?q=tai+nghe+sony" \
  -H "X-API-Key: your-api-key"
```

Full API documentation: [API_SPEC.md](plans/API_SPEC.md)

---

## Project Status

**Current Phase**: Phase 1 (Setup & Planning) ✅  
**Next Milestone**: Phase 2 (Backend Core Implementation)

### Phase Checklist
- [x] Planning & documentation complete
- [x] Architecture designed
- [ ] Azure resources provisioned
- [ ] Backend APIs implemented
- [ ] AI/RAG search working
- [ ] Mobile app MVP
- [ ] Production deployment

---

## Cost Overview

**Development**: ~$80/month  
**Production** (10K users): ~$970/month

Breakdown: [COST_ESTIMATION.md](plans/COST_ESTIMATION.md)

---

## Contributing

### Documentation Updates

**CRITICAL**: Luôn update documentation khi thay đổi code!

**Planning docs** (trong `plans/`):
- API changes → update `plans/API_SPEC.md`
- Architecture changes → update `plans/ARCHITECTURE.md`
- Major feature planning → update `plans/PLAN_PHASE_*.md`
- Security strategy → update `plans/SECURITY.md`
- Operations → update `plans/MONITORING.md`, `plans/MAINTENANCE.md`

**Code docs** (trong `docs/` - auto-generated khi implement):
- API endpoint changes → create/update `docs/API_ENDPOINTS.md`
- Database schema changes → create/update `docs/DATABASE_SCHEMA.md`
- New features → create/update `docs/FEATURES.md`
- Configuration changes → create/update `docs/CONFIGURATION.md`

See: [Documentation Update Workflow](plans/MAINTENANCE.md#documentation-update-workflow)

### Documentation Updates

**CRITICAL**: Luôn update documentation khi thay đổi code!

**Planning docs** (trong `plans/`):
- Architecture changes → update `plans/ARCHITECTURE.md`
- Major feature planning → update `plans/PLAN_PHASE_*.md`
- Security strategy → update `plans/SECURITY.md`

**Code docs** (trong `docs/` - auto-generated):
- API changes → update `docs/API_ENDPOINTS.md` + `plans/API_SPEC.md`
- Schema changes → update `docs/DATABASE_SCHEMA.md`
- New features → update `docs/FEATURES.md`

See: [Documentation Update Workflow](plans/MAINTENANCE.md#documentation-update-workflow)

---

## Architecture Diagram

```
Mobile App (Flutter)
    │
    ▼
Django REST API (Azure Web App)
    │
    ├─→ Azure Cosmos DB (Products, Links)
    ├─→ Azure AI Search (Semantic Search)
    ├─→ Azure Storage (Thumbnails)
    └─→ Azure Function (Async Scraper)
```

Full diagram: [ARCHITECTURE.md](plans/ARCHITECTURE.md)

---

## License

MIT License - see [LICENSE](LICENSE) for details

---

## Support

- **Issues**: [GitHub Issues](https://github.com/your-org/shopee-aff-manager/issues)
- **Documentation**: `/docs` folder
- **Email**: support@example.com

---

## Roadmap

### Post-MVP Features
- [ ] Telegram bot integration
- [ ] Price tracking & alerts
- [ ] Category auto-tagging (AI)
- [ ] Analytics dashboard
- [ ] Product recommendations
- [ ] Batch import (CSV/Excel)

See: [PLAN.md](plans/PLAN.md#extension-points-post-mvp)
