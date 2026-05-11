---
title: API Specification
version: 1.0.0
updated: 2026-05-06
---

# API Specification — Shopee Aff Link Manager

Base URL: `https://app-shopee-aff-dev.azurewebsites.net/api`
Local URL: `http://localhost:8000/api`

All requests/responses use `application/json`.

---

## Authentication

> **⚠️ BẮT BUỘC**: Hầu hết các endpoints yêu cầu user authentication với JWT. Xem chi tiết tại **[USER_AUTHENTICATION.md](USER_AUTHENTICATION.md)**.

**Authorization Header (required for protected endpoints)**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### POST `/auth/register/`
Register new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "StrongPassword123",
  "display_name": "Nguyễn Văn A"
}
```

**Response 201:**
```json
{
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "display_name": "Nguyễn Văn A",
    "status": "active",
    "email_verified": false,
    "created_at": "2026-05-06T00:00:00Z"
  },
  "access": "eyJhbGci...access_token",
  "refresh": "eyJhbGci...refresh_token"
}
```

**Response 400** — Validation error:
```json
{
  "email": ["Email này đã được đăng ký."],
  "password": ["Mật khẩu phải chứa ít nhất 1 chữ hoa."]
}
```

**Password Requirements**:
- Min 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number

---

### POST `/auth/login/`
Login with email/password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "StrongPassword123"
}
```

**Response 200:**
```json
{
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "display_name": "Nguyễn Văn A",
    "status": "active",
    "email_verified": false,
    "created_at": "2026-05-06T00:00:00Z"
  },
  "access": "eyJhbGci...access_token",
  "refresh": "eyJhbGci...refresh_token"
}
```

**Response 401** — Invalid credentials:
```json
{ "detail": "Email hoặc mật khẩu không đúng." }
```

**Token Lifetimes**:
- Access token: 1 hour
- Refresh token: 7 days

---

### POST `/auth/refresh/`
Refresh expired access token using refresh token.

**Request:**
```json
{
  "refresh": "eyJhbGci...refresh_token"
}
```

**Response 200:**
```json
{
  "access": "eyJhbGci...new_access_token",
  "refresh": "eyJhbGci...new_refresh_token"
}
```

**Response 401** — Invalid/expired refresh token:
```json
{ "detail": "Token is invalid or expired." }
```

---

### POST `/auth/logout/`
Logout user (blacklist refresh token).

**Headers:** `Authorization: Bearer <access_token>`

**Request:**
```json
{
  "refresh": "eyJhbGci...refresh_token"
}
```

**Response 204:** No content.

---

### GET `/auth/me/`
Get current authenticated user profile.

**Headers:** `Authorization: Bearer <access_token>`

**Response 200:**
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "display_name": "Nguyễn Văn A",
  "status": "active",
  "email_verified": false,
  "avatar_url": null,
  "created_at": "2026-05-06T00:00:00Z"
}
```

---

### POST `/auth/change-password/`
Change password for authenticated user.

**Headers:** `Authorization: Bearer <access_token>`

**Request:**
```json
{
  "old_password": "OldPassword123",
  "new_password": "NewPassword456"
}
```

**Response 200:**
```json
{ "detail": "Đổi mật khẩu thành công." }
```

**Response 401** — Old password incorrect:
```json
{ "detail": "Mật khẩu hiện tại không đúng." }
```

---

## Health

### GET `/health/`
Check server status (public, no auth required).

**Response 200:**
```json
{ "status": "ok" }
```

---

## Links

> **🔒 All link endpoints require authentication.**

### POST `/links/`
Submit a new Shopee affiliate link. Triggers async scraping.

**Headers:** `Authorization: Bearer <access_token>`

**Request:**
```json
{
  "url": "https://shp.ee/abc123",
  "notes": "Optional note"
}
```

**Response 201:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "original_url": "https://shp.ee/abc123",
  "resolved_url": "",
  "product_id": null,
  "status": "pending",
  "notes": "Optional note",
  "error_message": null,
  "created_at": "2026-05-06T00:00:00Z",
  "updated_at": "2026-05-06T00:00:00Z"
}
```

**Response 400** — Invalid URL:
```json
{ "detail": "Invalid Shopee affiliate URL." }
```

---

### GET `/links/`
List all links for authenticated user.

**Headers:** `Authorization: Bearer <access_token>`

**Query params:**
| Param | Type | Default | Description |
|---|---|---|---|
| `page` | int | `1` | Page number |
| `page_size` | int | `20` | Items per page |

**Response 200:**
```json
{
  "count": 42,
  "results": [
    {
      "id": "...",
      "original_url": "https://shp.ee/abc123",
      "status": "done",
      "product_id": "...",
      "created_at": "2026-05-06T00:00:00Z"
    }
  ]
}
```

---

### GET `/links/{link_id}/`
Get status of a specific link (use for polling).

**Headers:** `Authorization: Bearer <access_token>`

**Response 200:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "original_url": "https://shp.ee/abc123",
  "resolved_url": "https://shopee.vn/product/i.123456.789012",
  "product_id": "prod-uuid",
  "status": "done",
  "error_message": null,
  "created_at": "2026-05-06T00:00:00Z",
  "updated_at": "2026-05-06T00:01:30Z"
}
```

**Link Status Values:**
| Status | Meaning |
|---|---|
| `pending` | Vừa tạo, đang chờ xử lý |
| `processing` | Azure Function đang scrape |
| `done` | Đã scrape xong, product đã lưu |
| `failed` | Scrape thất bại (xem `error_message`) |

---

## Products

> **🔒 All product endpoints require authentication.**

### GET `/products/`
List all saved products for authenticated user (paginated).

**Headers:** `Authorization: Bearer <access_token>`

**Query params:**
| Param | Type | Default | Description |
|---|---|---|---|
| `page` | int | `1` | Page number |
| `page_size` | int | `20` | Items per page (max 100) |
| `search` | string | — | Filter by title (substring match) |

**Response 200:**
```json
{
  "count": 100,
  "page": 1,
  "page_size": 20,
  "results": [
    {
      "id": "prod-uuid",
      "title": "Tai nghe Sony WH-1000XM5",
      "thumbnail_url": "https://stshopeeaffdev.blob.core.windows.net/thumbnails/uuid.jpg",
      "price": 4990000.0,
      "price_currency": "VND",
      "created_at": "2026-05-06T00:00:00Z"
    }
  ]
}
```

---

### GET `/products/{product_id}/`
Get full product details. Only returns product if it belongs to authenticated user.

**Headers:** `Authorization: Bearer <access_token>`

**Query params:**
| Param | Type | Required | Description |
|---|---|---|---|
| `shop_id` | string | Yes | Cosmos DB partition key |

**Response 200:**
```json
{
  "id": "prod-uuid",
  "title": "Tai nghe Sony WH-1000XM5",
  "original_url": "https://shopee.vn/product/i.123456.789012",
  "shop_id": "123456",
  "item_id": "789012",
  "thumbnail_url": "https://stshopeeaffdev.blob.core.windows.net/thumbnails/uuid.jpg",
  "price": 4990000.0,
  "price_currency": "VND",
  "category": null,
  "status": "active",
  "created_at": "2026-05-06T00:00:00Z",
  "updated_at": "2026-05-06T00:00:00Z"
}
```

**Response 404** — Product not found or doesn't belong to user:
```json
{ "detail": "Product không tồn tại." }
```

---

### DELETE `/products/{product_id}/`
Soft-delete a product (sets `status = deleted`). Only owner can delete.

**Headers:** `Authorization: Bearer <access_token>`

**Query params:**
| Param | Type | Required |
|---|---|---|
| `shop_id` | string | Yes |

**Response 204:** No content.

**Response 404** — Product not found or doesn't belong to user:
```json
{ "detail": "Product không tồn tại." }
```

---

## Search

> **🔒 Search endpoint requires authentication.**

### GET `/search/`
Smart hybrid search (BM25 + vector RAG). Searches only products owned by authenticated user.

**Headers:** `Authorization: Bearer <access_token>`

**Query params:**
| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `q` | string | Yes | — | Search query (1–200 chars) |
| `top` | int | No | `10` | Max results (1–50) |
| `min_price` | float | No | — | Filter: minimum price |
| `max_price` | float | No | — | Filter: maximum price |

**Response 200:**
```json
{
  "query": "tai nghe sony",
  "count": 3,
  "results": [
    {
      "id": "prod-uuid",
      "title": "Tai nghe Sony WH-1000XM5",
      "thumbnail_url": "https://...",
      "original_url": "https://shopee.vn/...",
      "price": 4990000.0,
      "price_currency": "VND",
      "score": 0.934,
      "highlights": {
        "title": ["<em>Tai nghe Sony</em> WH-1000XM5"]
      }
    }
  ]
}
```

**Response 400** — Invalid query:
```json
{ "detail": "Query không được để trống." }
```

---

## Error Response Format

All errors follow this format:
```json
{
  "detail": "Human-readable error message"
}
```

**Common HTTP Status Codes:**
| Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Created |
| 204 | No content (delete) |
| 400 | Bad request (validation error) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (account suspended) |
| 404 | Not found |
| 422 | Unprocessable (scraping failed) |
| 503 | Service unavailable (Azure DB down) |

---

## Authentication Error Examples

### Missing Authorization Header
**Request:**
```bash
GET /api/products/
```

**Response 401:**
```json
{ "detail": "Authentication credentials were not provided." }
```

### Invalid/Expired Token
**Request:**
```bash
GET /api/products/
Authorization: Bearer invalid_token_here
```

**Response 401:**
```json
{ "detail": "Given token not valid for any token type" }
```

### Account Suspended
**Request:**
```bash
GET /api/products/
Authorization: Bearer valid_token_but_user_suspended
```

**Response 403:**
```json
{ "detail": "Tài khoản đã bị tạm khóa." }
```

---

**For complete authentication flows and implementation**, see **[USER_AUTHENTICATION.md](USER_AUTHENTICATION.md)**.
