---
title: Security & Authentication
version: 1.0.0
updated: 2026-05-06
---

# Security & Authentication

## Overview

Document này định nghĩa security measures cho backend API, data protection, authentication strategy, và compliance với best practices.

> **⚠️ CRITICAL REQUIREMENT**: App BẮT BUỘC user phải đăng nhập trước khi sử dụng. Xem chi tiết full authentication system tại **[USER_AUTHENTICATION.md](USER_AUTHENTICATION.md)**.

---

## Authentication Strategy

### ✅ Required: JWT User Authentication

**App BẮT BUỘC user authentication với JWT tokens**. Chi tiết complete flows, implementation code, và best practices xem tại:

👉 **[USER_AUTHENTICATION.md](USER_AUTHENTICATION.md)**

**Tóm tắt**:
- User registration với email/password
- Login returns JWT access token (1h) + refresh token (7d)
- All API endpoints require `Authorization: Bearer <token>` header
- Auto token refresh via Dio interceptor
- Secure token storage (FlutterSecureStorage)
- Password hashing với bcrypt
- Data isolation per user_id (from JWT claims)

**Quick reference**:
```python
# Django settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Required by default
    ],
}
```

```dart
// Flutter: All requests auto-include token
final dio = Dio();
dio.interceptors.add(AuthInterceptor());  // Adds Bearer token
```

---

### Optional: API Key (Additional Layer)

**Không bắt buộc cho MVP**. Có thể thêm API key layer để authenticate mobile app (ngoài user auth):

**config/settings/base.py**:
```python
API_KEY = env('API_KEY', default='')  # Set via env var
```

**apps/core/authentication.py**:
```python
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return None  # Let other auth methods try
        
        if api_key != settings.API_KEY:
            raise AuthenticationFailed('Invalid API key')
        
        # Return (user, auth) tuple — user là None vì chưa có user system
        return (None, api_key)
```

**apps/core/permissions.py**:
```python
from rest_framework.permissions import BasePermission

class HasAPIKey(BasePermission):
    def has_permission(self, request, view):
        return request.auth is not None
```

**Apply globally**:
```python
# config/settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.core.authentication.APIKeyAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'apps.core.permissions.HasAPIKey',
    ],
    # Health check không cần auth
    'DEFAULT_PERMISSION_CLASSES': [],  # Override per-view
}
```

**Views**:
```python
from rest_framework.decorators import api_view, permission_classes
from apps.core.permissions import HasAPIKey

@api_view(['POST'])
@permission_classes([HasAPIKey])
def create_link(request):
    # Protected endpoint
    pass

@api_view(['GET'])
@permission_classes([])  # Public
def health_check(request):
    pass
```

**Flutter client**:
```dart
// lib/core/dio_client.dart
Dio(
  BaseOptions(
    headers: {
      'X-API-Key': 'your-secret-api-key-here',
    },
  ),
)
```

**Rotate API key**:
```bash
# Generate new key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update Azure Web App qua Portal
# Vào Web App → Settings → Environment variables → cập nhật API_KEY
```

---

### User Authentication Implementation

**Complete implementation code, flows, và best practices**:

👉 **[USER_AUTHENTICATION.md](USER_AUTHENTICATION.md)**

Bao gồm:
- ✅ Registration flow (email, password, display_name)
- ✅ Login flow (JWT token generation)
- ✅ Token refresh flow (auto-retry failed requests)
- ✅ Logout flow (token blacklisting)
- ✅ Protected API requests (middleware)
- ✅ Django backend code (services, views, serializers)
- ✅ Flutter mobile code (repositories, providers, screens)
- ✅ Security best practices (bcrypt, token rotation, secure storage)
- ✅ Testing strategies
- ✅ Monitoring recommendations

---

## CORS Configuration

**config/settings/base.py**:
```python
INSTALLED_APPS += ['corsheaders']

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ...
]

# Development: allow localhost
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    'http://localhost:8000',
    'http://127.0.0.1:8000',
])

# Production: specific domains only
# CORS_ALLOWED_ORIGINS = [
#     'https://shopee-aff.example.com',
# ]

CORS_ALLOW_CREDENTIALS = True
```

---

## Rate Limiting

**Install**:
```bash
pip install django-ratelimit
```

**apps/core/decorators.py**:
```python
from django_ratelimit.decorators import ratelimit

# Apply to views
@ratelimit(key='ip', rate='10/m', method='POST')
@api_view(['POST'])
def create_link(request):
    pass

@ratelimit(key='ip', rate='60/m', method='GET')
@api_view(['GET'])
def search(request):
    pass
```

**Or use DRF throttling**:
```python
# config/settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',  # Anonymous users
        'user': '1000/hour',  # Authenticated users
    }
}
```

---

## Input Validation & Sanitization

### 1. URL Validation

**apps/links/serializers.py**:
```python
from rest_framework import serializers
import re

class LinkCreateSerializer(serializers.Serializer):
    url = serializers.URLField(max_length=2048)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate_url(self, value):
        # Only allow Shopee domains
        allowed_domains = [
            'shp.ee',
            'shopee.vn',
            'shopee.com.vn',
        ]
        
        from urllib.parse import urlparse
        domain = urlparse(value).netloc.lower()
        
        # Remove www.
        domain = domain.replace('www.', '')
        
        if not any(domain == d or domain.endswith('.' + d) for d in allowed_domains):
            raise serializers.ValidationError(
                'Only Shopee URLs are allowed (shp.ee, shopee.vn, shopee.com.vn)'
            )
        
        return value
    
    def validate_notes(self, value):
        # Strip HTML tags
        import re
        value = re.sub(r'<[^>]+>', '', value)
        
        # Prevent XSS
        dangerous_patterns = ['<script', 'javascript:', 'onerror=', 'onclick=']
        if any(p in value.lower() for p in dangerous_patterns):
            raise serializers.ValidationError('Invalid characters in notes')
        
        return value.strip()
```

### 2. Search Query Sanitization

**apps/search/serializers.py**:
```python
class SearchQuerySerializer(serializers.Serializer):
    q = serializers.CharField(min_length=1, max_length=200)
    top = serializers.IntegerField(min_value=1, max_value=50, default=10)
    min_price = serializers.FloatField(min_value=0, required=False)
    max_price = serializers.FloatField(min_value=0, required=False)
    
    def validate_q(self, value):
        # Remove excessive whitespace
        value = ' '.join(value.split())
        
        # Block SQL injection attempts (paranoid check)
        sql_keywords = ['SELECT', 'DROP', 'INSERT', 'DELETE', 'UPDATE', 'UNION']
        if any(kw in value.upper() for kw in sql_keywords):
            raise serializers.ValidationError('Invalid search query')
        
        return value
```

---

## Secrets Management

### Azure Key Vault (Production Best Practice)

**Install**:
```bash
pip install azure-keyvault-secrets azure-identity
```

**config/settings/production.py**:
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Key Vault setup
KEY_VAULT_NAME = env('KEY_VAULT_NAME', default='kv-shopee-aff-dev')
KEY_VAULT_URI = f'https://{KEY_VAULT_NAME}.vault.azure.net'

credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=KEY_VAULT_URI, credential=credential)

def get_secret(secret_name: str) -> str:
    try:
        return secret_client.get_secret(secret_name).value
    except Exception as e:
        logger.error(f"Failed to fetch secret {secret_name}: {e}")
        raise

# Override sensitive settings
DJANGO_SECRET_KEY = get_secret('django-secret-key')
COSMOS_DB_KEY = get_secret('cosmos-db-key')
AZURE_SEARCH_KEY = get_secret('azure-search-key')
API_KEY = get_secret('api-key')
```

**Azure setup (Portal)**:
1. Vào **Key Vaults** → **+ Create**
2. Name: `kv-shopee-aff-dev`, Resource Group: `rg-shopee-aff-dev`
3. **Review + create** → **Create**

**Grant Web App access**:
1. Vào Web App → **Settings** → **Identity** → bật **System assigned**
2. Vào Key Vault → **Access policies** → **+ Create**
3. Chọn Web App's managed identity, grant **Get** + **List** secret permissions

**Add secrets**:
1. Vào Key Vault → **Secrets** → **+ Generate/Import**
2. Thêm từng secret: `django-secret-key`, `cosmos-db-key`, etc.

---

## HTTPS & SSL

### Production Azure Web App

**Force HTTPS**:
1. Vào Web App → **Settings** → **TLS/SSL settings** → **HTTPS Only**: **On**

**Custom domain với SSL certificate** (optional):
1. Vào Web App → **Settings** → **Custom domains** → **+ Add custom domain**
2. Nhập hostname (vd: `api.shopeeaff.example.com`), verify domain
3. Vào **TLS/SSL settings** → **Private Key Certificates** → **Create App Service Managed Certificate**
4. Bind certificate vào custom domain

---

## Data Encryption

### At Rest

**Cosmos DB**: Mặc định encrypted at rest với Microsoft-managed keys.

**Azure Storage**: Mặc định encrypted.

**Upgrade to Customer-Managed Keys** (optional):
```bash
# Tạo Azure Key Vault
# Enable encryption với CMK cho Cosmos DB
# Vào Cosmos DB → Settings → Encryption → chọn Customer-managed key → chọn key từ Key Vault
```

### In Transit

- Tất cả connections dùng TLS 1.2+
- Azure services communication qua HTTPS
- Cosmos DB SDK mặc định dùng HTTPS
- Azure Search, Storage, OpenAI đều enforce HTTPS

---

## Sensitive Data Handling

### 1. Không log sensitive data

**Bad**:
```python
logger.info(f"User logged in: {email}, password: {password}")  # ❌ NEVER
```

**Good**:
```python
logger.info(f"User logged in: {email}")  # ✓
logger.debug(f"Request body: {sanitize_log(request.data)}")  # ✓
```

**apps/core/utils.py**:
```python
def sanitize_log(data: dict) -> dict:
    """Remove sensitive fields from logs."""
    sensitive_keys = {'password', 'api_key', 'token', 'secret', 'authorization'}
    return {
        k: '***REDACTED***' if k.lower() in sensitive_keys else v
        for k, v in data.items()
    }
```

### 2. Không expose internal errors

**Bad**:
```python
return Response({'error': str(exception)}, status=500)  # ❌ Exposes stack trace
```

**Good**:
```python
logger.error(f"Internal error: {exception}", exc_info=True)  # Log full trace
return Response({'error': 'Internal server error'}, status=500)  # Generic message
```

---

## Security Headers

**config/settings/production.py**:
```python
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = 'DENY'

# CSP header
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", 'data:', 'https:')
```

**Custom middleware cho headers** (nếu cần):
```python
# apps/core/middleware.py
class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        return response
```

---

## Dependency Vulnerability Scanning

**Scan with pip-audit**:
```bash
pip install pip-audit
pip-audit --require-hashes --desc
```

**GitHub Dependabot** — tự động tạo PR khi có vulnerability:

**.github/dependabot.yml**:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/backend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

---

## Penetration Testing Checklist

Trước khi launch production:

- [ ] SQL injection testing (không dùng SQL nhưng test Cosmos queries)
- [ ] XSS testing (input fields, search queries)
- [ ] CSRF protection enabled
- [ ] Rate limiting working
- [ ] API key không exposed trong frontend code
- [ ] HTTPS enforced trên tất cả endpoints
- [ ] Security headers present
- [ ] Sensitive data không leak trong logs
- [ ] Error messages không expose stack traces
- [ ] File upload validation (nếu có)

**Tools**:
- OWASP ZAP (automated scan)
- Burp Suite (manual testing)
- Postman (API abuse testing)

---

## Incident Response Plan

### 1. API Key Leaked

**Action**:
```bash
# Immediately rotate
python -c "import secrets; print(secrets.token_urlsafe(32))" > new_key.txt

# Update Azure qua Portal
# Vào Web App → Settings → Environment variables → cập nhật API_KEY

# Notify team
# Force update mobile app
```

### 2. Data Breach Detection

**Steps**:
1. Isolate affected systems (scale down Web App)
2. Review Application Insights logs for unauthorized access
3. Check Cosmos DB audit logs
4. Rotate all credentials
5. Notify affected users (if user data exposed)
6. Document incident

### 3. DDoS Attack

**Mitigation**:
- Azure Web App có built-in DDoS protection
- Enable Azure Front Door với WAF (Web Application Firewall)
- Tăng rate limiting
- Temporary IP blocking

```bash
# Block IP range qua Portal
# Vào Web App → Settings → Networking → Access Restrictions → + Add rule
```

---

## Compliance Considerations

**GDPR** (nếu có EU users):
- Có khả năng export user data
- Có khả năng delete user data (right to be forgotten)
- Log consent cho data collection

**Vietnam Data Protection Law**:
- Store data trong Vietnam hoặc approved countries
- User consent cho data processing
- Data breach notification trong 72h

**PCI DSS** (nếu xử lý payment):
- Không store credit card data
- Dùng Shopee affiliate commissions thay vì direct payment
