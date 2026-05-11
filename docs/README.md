# Code Documentation Index

> **Lưu ý quan trọng**: Thư mục này chứa documentation tự động generate từ code và các hướng dẫn implementation chi tiết. Các file planning chính nằm trong thư mục `plans/`.

## 📋 Documentation Structure

### Auto-Generated Documentation
Các files này được tự động tạo/cập nhật khi code thay đổi:

- **API_ENDPOINTS.md** - Danh sách tất cả API endpoints với examples
- **DATABASE_SCHEMA.md** - Chi tiết schemas của Cosmos DB containers (users, products, links, token_blacklist)
- **FEATURES.md** - Tài liệu các features đã implement
- **CONFIGURATION.md** - Hướng dẫn cấu hình hệ thống
- **DEPLOYMENT.md** - Step-by-step deployment guide
- **TROUBLESHOOTING.md** - Common issues và solutions
- **THEME_I18N_CONFIG.md** - Theme và i18n configuration (live status)

### Planning Documentation
Các files planning nằm trong thư mục `plans/`:

- `plans/PLAN.md` - Master plan
- `plans/ARCHITECTURE.md` - System architecture
- `plans/API_SPEC.md` - API specification (includes auth endpoints)
- **`plans/USER_AUTHENTICATION.md`** - **Complete user auth system (REQUIRED)**
- `plans/SECURITY.md` - Security guidelines
- `plans/MONITORING.md` - Monitoring strategy
- `plans/THEME_SYSTEM.md` - Flutter theme design
- `plans/INTERNATIONALIZATION.md` - i18n strategy
- Và các file PLAN_PHASE_*.md

## 🔄 Documentation Update Rules

### Rule #1: API Changes
**Khi thay đổi API endpoints:**
```
Code changed: apps/products/views.py, apps/products/urls.py
→ Update: docs/API_ENDPOINTS.md
→ Update: docs/API_SPEC.md (in plans/ if spec changes)
→ Update: CHANGELOG.md
```

### Rule #2: Database Schema Changes
**Khi thay đổi Cosmos DB schemas:**
```
Code changed: apps/*/models.py
→ Update: docs/DATABASE_SCHEMA.md
→ Update: plans/ARCHITECTURE.md (if major change)
→ Update: CHANGELOG.md
```

### Rule #3: New Features
**Khi thêm feature mới:**
```
Code changed: apps/new_feature/*
→ Create: docs/features/new_feature.md
→ Update: docs/FEATURES.md (add to index)
→ Update: README.md (if user-facing)
→ Update: CHANGELOG.md
```

### Rule #4: Configuration Changes
**Khi thay đổi config:**
```
Code changed: config/settings/*.py, .env.example
→ Update: docs/CONFIGURATION.md
→ Update: plans/PLAN_PHASE_1_SETUP.md (if env vars)
→ Update: CHANGELOG.md
```

### Rule #5: Deployment Changes
**Khi thay đổi deployment:**
```
Code changed: Dockerfile, .github/workflows/*.yml
→ Update: docs/DEPLOYMENT.md
→ Update: plans/PLAN_PHASE_5_DEPLOY.md
→ Update: CHANGELOG.md
```

## 📝 Documentation Templates

### API Endpoint Documentation Template
```markdown
## POST /api/resource/

**Description**: Brief description of what this endpoint does.

**Authentication**: Required (API Key)

**Request Body**:
\`\`\`json
{
  "field1": "value",
  "field2": 123
}
\`\`\`

**Response 201 (Success)**:
\`\`\`json
{
  "id": "uuid",
  "field1": "value",
  "created_at": "2026-05-06T00:00:00Z"
}
\`\`\`

**Response 400 (Validation Error)**:
\`\`\`json
{
  "detail": "Error message"
}
\`\`\`

**Example**:
\`\`\`bash
curl -X POST https://api.example.com/api/resource/ \\
  -H "X-API-Key: your-key" \\
  -H "Content-Type: application/json" \\
  -d '{"field1": "value"}'
\`\`\`
```

### Database Schema Documentation Template
```markdown
## Container: {container_name}

**Partition Key**: `/field_name`

**Schema**:
\`\`\`python
@dataclass
class ModelName(BaseDocument):
    field1: str = ""
    field2: int = 0
    partition_key: str = ""  # Partition key field
\`\`\`

**Example Document**:
\`\`\`json
{
  "id": "uuid",
  "field1": "value",
  "field2": 123,
  "partition_key": "value",
  "created_at": "2026-05-06T00:00:00Z",
  "updated_at": "2026-05-06T00:00:00Z"
}
\`\`\`

**Indexes**: Default (automatic indexing on all fields)

**Queries**:
- List all: `SELECT * FROM c WHERE c.partition_key = @pk`
- Filter by status: `SELECT * FROM c WHERE c.status = 'active'`
```

### Feature Documentation Template
```markdown
# Feature: {Feature Name}

## Overview
Brief description of the feature.

## User Story
As a [user type], I want to [action] so that [benefit].

## Implementation

### Backend
- **Endpoint**: `POST /api/feature/`
- **Service**: `apps/feature/services.py → FeatureService`
- **Model**: `apps/feature/models.py → FeatureModel`

### Frontend (Mobile)
- **Screen**: `mobile/lib/features/feature/presentation/feature_screen.dart`
- **Provider**: `mobile/lib/features/feature/domain/feature_provider.dart`

### Database
- **Container**: `feature_container`
- **Partition Key**: `/user_id`

## Usage

### API Example
\`\`\`bash
curl -X POST /api/feature/ -d '{"param": "value"}'
\`\`\`

### Mobile Example
\`\`\`dart
final result = await ref.read(featureProvider).performAction(param);
\`\`\`

## Testing
- Unit tests: `tests/test_feature.py`
- Widget tests: `mobile/test/feature_test.dart`

## Dependencies
- Azure Service X
- Python package Y
- Flutter package Z
```

## 🎯 Documentation Quality Checklist

Trước khi commit documentation:

- [ ] File được đặt đúng thư mục (`docs/` cho code docs, `plans/` cho planning)
- [ ] Frontmatter có version và updated date
- [ ] Code examples đã test và working
- [ ] Links đến files khác đều hoạt động
- [ ] Markdown syntax đúng (no broken formatting)
- [ ] Spelling và grammar đã check
- [ ] Technical terms consistent với project

## 🔗 Quick Links

**Planning Docs**: [`../plans/`](../plans/)  
**Project Root**: [`../README.md`](../README.md)  
**Changelog**: [`../CHANGELOG.md`](../CHANGELOG.md)  
**Checklist**: [`../CHECKLIST.md`](../CHECKLIST.md)

---

**Note**: Thư mục này sẽ được populate dần khi project được implement. Ưu tiên tạo docs theo thứ tự: API_ENDPOINTS → DATABASE_SCHEMA → FEATURES → CONFIGURATION → DEPLOYMENT → TROUBLESHOOTING.
