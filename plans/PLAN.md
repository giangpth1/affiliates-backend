---
title: Master Project Plan
version: 1.1.0
updated: 2026-05-08
---

# Master Plan — Shopee Affiliate Link Manager

## Project Summary

Build a full-stack system to manage Shopee affiliate links. Users paste a Shopee affiliate URL; the system automatically resolves it, scrapes product title and thumbnail, stores data in Azure Cosmos DB, indexes it in Azure AI Search, and exposes a smart search API powered by Azure AI Search hybrid search (BM25 + vector) for both Web and Mobile clients.

## Phases Overview

| # | Phase | Duration (est.) | Key Deliverable |
|---|---|---|---|
| 1 | Setup & Infrastructure | 1–2 days | Dev environment + Azure resources provisioned |
| 2 | Django Backend Core | 3–4 days | REST APIs for links & products working locally |
| 3 | AI / RAG Integration | 2–3 days | Smart search working end-to-end |
| 4 | Web Frontend | 4–5 days | Laravel web app with same design as mobile |
| 5 | Flutter Mobile App | 5–7 days | Working mobile app connected to backend |
| 6 | Deployment & CI/CD | 2–3 days | Live on Azure, deployable via pipeline |

**Total estimated: ~18–26 working days**

---

## Phase Summaries

### Phase 1 — Setup & Infrastructure
See: [PLAN_PHASE_1_SETUP.md](PLAN_PHASE_1_SETUP.md)

- Install dev tools (Python 3.13, Flutter, VS Code)
- Scaffold Django project with proper settings split
- Provision all Azure resources via Azure Portal
- Configure environment variables and secrets
- Verify all Azure SDK connections locally

### Phase 2 — Django Backend Core
See: [PLAN_PHASE_2_BACKEND.md](PLAN_PHASE_2_BACKEND.md)

- Implement `users` app: registration, login, JWT authentication
- Design Cosmos DB document schemas
- Implement `links` app: POST/GET affiliate links
- Implement `products` app: product CRUD
- Implement Shopee scraper service
- Implement Azure Function for async scraping
- Write unit tests for all services

### Phase 3 — AI / RAG Integration
See: [PLAN_PHASE_3_AI_RAG.md](PLAN_PHASE_3_AI_RAG.md)

- Set up Azure AI Search index with semantic configuration
- Implement semantic search (built-in ML)
- Write search API endpoint (returns ranked product list)

### Phase 4 — Web Frontend
See: [PLAN_PHASE_4_WEB.md](PLAN_PHASE_4_WEB.md)

- Laravel 11 với Blade templates + HTML/CSS/JS thuần
- Bootstrap 5 + CSS variables (Shopee Orange, Inter font)
- Các màn hình: Auth, Product List, Add Link, Search
- Session-based auth với API token từ Django backend
- Responsive design (desktop + mobile browsers)

### Phase 5 — Flutter Mobile App
See: [PLAN_PHASE_5_MOBILE.md](PLAN_PHASE_5_MOBILE.md)

- Scaffold Flutter project with feature-first architecture
- Implement Add Link screen with paste + status polling
- Implement Product List screen with thumbnails
- Implement Smart Search screen with RAG results
- Handle auth (JWT: login, register, token management)

### Phase 6 — Deployment & CI/CD
See: [PLAN_PHASE_6_DEPLOY.md](PLAN_PHASE_6_DEPLOY.md)

- Dockerize Django backend
- Configure Azure Web App deployment
- Set up GitHub Actions CI/CD pipeline
- Configure production environment variables
- Deploy Next.js to Vercel or Azure Static Web Apps
- Write deployment runbook

---

## Estimated Timeline (1 Developer)

| Phase | Nội dung chính | Thời gian | Độ khó |
|---|---|---|---|
| **Phase 1** | Setup & Infrastructure | **2–3 ngày** | ⭐ Dễ |
| **Phase 2** | Django Backend Core | **5–7 ngày** | ⭐⭐⭐ Trung bình |
| **Phase 3** | AI / RAG Integration | **2–3 ngày** | ⭐⭐ Dễ-Trung bình |
| **Phase 4** | Web Frontend (Laravel) | **4–5 ngày** | ⭐⭐⭐ Trung bình |
| **Phase 5** | Flutter Mobile App | **5–7 ngày** | ⭐⭐⭐⭐ Khá |
| **Phase 6** | Deployment & CI/CD | **2–3 ngày** | ⭐⭐ Dễ-Trung bình |
| **Tổng** | **MVP hoàn chỉnh** | **18–26 ngày** | — |

### Chi tiết từng phase

#### Phase 1 — Setup & Infrastructure (2–3 ngày)
| Task | Ngày |
|---|---|
| Cài đặt dev tools (Python, Flutter, VS Code) | 0.5 |
| Scaffold Django project + settings split | 0.5 |
| Provision Azure resources (Cosmos, Storage, Search, OpenAI, Function) | 0.5 |
| Viết script verify connections + tạo `.env` | 0.5 |
| Git init + `.gitignore` | 0.5 |

#### Phase 2 — Django Backend Core (5–7 ngày)
| Task | Ngày |
|---|---|
| Core app: BaseDocument, exceptions, pagination, error handler | 0.5 |
| Users app: registration, login, JWT (access + refresh), token blacklist | 2 |
| Cosmos DB service layer (CRUD operations) | 0.5 |
| Links app: models, serializers, views, LinkService | 1 |
| Products app: models, serializers, views, ProductService | 1 |
| Shopee scraper service (httpx + BeautifulSoup4) | 1 |
| Azure Function: async scraping pipeline | 1 |
| Unit tests cho tất cả services | 1 |

#### Phase 3 — AI / RAG Integration (2–3 ngày)
| Task | Ngày |
|---|---|
| Tạo Azure AI Search index với semantic config | 0.5 |
| Azure Search service: index/delete/search products | 1 |
| Search API endpoint với semantic search | 0.5 |

#### Phase 4 — Web Frontend (4–5 ngày)
| Task | Ngày |
|---|---|
| Scaffold Next.js + TailwindCSS + core setup | 0.5 |
| UI Components: Button, Input, Card, Badge, Loading | 0.5 |
| Auth screens: Login, Register, Zustand store | 1 |
| Dashboard layout: Sidebar, Header, responsive | 0.5 |
| Product List + Product Detail pages | 1 |
| Add Link page: form, polling status | 0.5 |
| Search page: search bar, filters, results | 0.5 |
| Error handling + loading states + polish | 0.5 |

#### Phase 5 — Flutter Mobile App (5–7 ngày)
| Task | Ngày |
|---|---|
| Scaffold Flutter + core setup (Dio, Router, Theme) | 1 |
| Auth screens: login, register, token storage | 1 |
| Add Link screen: paste URL, submit, polling status | 1 |
| Product List screen: grid + thumbnail cards | 1 |
| Product Detail screen | 0.5 |
| Smart Search screen: debounce input, RAG results, highlights | 1 |
| Error handling + loading states + polish | 1 |

#### Phase 6 — Deployment & CI/CD (2–3 ngày)
| Task | Ngày |
|---|---|
| Dockerize Django backend + test local | 0.5 |
| Deploy Azure Web App + configure app settings | 0.5 |
| Deploy Azure Function App | 0.5 |
| Deploy Next.js to Vercel/Azure Static Web Apps | 0.5 |
| GitHub Actions: backend CI/CD (test → deploy) | 0.5 |
| GitHub Actions: mobile CI (build APK) | 0.5 |
| Production smoke test + Application Insights setup | 0.5 |

### Ghi chú
- **Thời gian trên là conservative estimate** cho 1 developer làm full-time (8h/ngày)
- Phase 2 là phase nặng nhất vì bao gồm toàn bộ auth system + business logic
- Phase 3 đã được đơn giản hóa: chỉ dùng Azure AI Search hybrid, không cần GPT-4o
- Phase 3 và 4 có thể làm song song nếu có 2 developers (backend + mobile)
- Các task trong mỗi phase có thể được làm tuần tự, không nên parallel trong cùng phase vì có dependency
- Post-MVP features (Telegram Bot, Price Tracking, etc.): thêm **5–10 ngày** tùy scope

---

## Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| DB | Cosmos DB NoSQL (Core API) | Schema-less, easy to evolve; Azure-native |
| ORM | No traditional ORM | Cosmos DB SDK used directly via service layer |
| Search | Hybrid (BM25 + vector) | Better recall than pure vector for product names |
| Scraping | httpx + BeautifulSoup4 | Async-capable; no browser required |
| Auth | JWT (required) | User authentication bắt buộc; access (1h) + refresh (7d) tokens |
| Mobile State | Riverpod | Testable, compile-safe, no global singletons |

---

## Extension Points (Post-MVP)

- **Telegram Bot**: Add `apps/telegram/` with webhook handler; reuse `LinkService`
- **Price Tracking**: Add `price_history` subcollection in Cosmos DB
- **Categories**: Extend product schema + AI auto-categorization
- **Multi-user**: Add User model + per-user link collections
- **Analytics**: Track click counts via Azure Function

---

## Additional Documentation

| Document | Description |
|---|---|
| [MONITORING.md](MONITORING.md) | Application Insights setup, metrics, alerts |
| [SECURITY.md](SECURITY.md) | Authentication, CORS, rate limiting, secrets |
| [MAINTENANCE.md](MAINTENANCE.md) | Backup, disaster recovery, troubleshooting |
| [COST_ESTIMATION.md](COST_ESTIMATION.md) | Azure pricing breakdown, optimization |
| [CHECKLIST.md](../CHECKLIST.md) | Detailed implementation checklist |
| [CHANGELOG.md](../CHANGELOG.md) | Version history and updates |
| [README.md](../README.md) | Project overview and quick start |
