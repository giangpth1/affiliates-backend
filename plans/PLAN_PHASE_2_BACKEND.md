---
title: Phase 2 — Django Backend Core
version: 1.1.0
updated: 2026-05-08
---

# Phase 2: Django Backend Core

## Goals
- Cosmos DB document schemas hoàn chỉnh
- REST API cho links và products hoạt động
- Shopee scraper tự động lấy title + thumbnail
- Azure Function trigger async scraping
- Unit tests cho tất cả services

---

## Step 2.1 — Core App (Shared Foundation)

### 2.1.1 Abstract Base Model

**`apps/core/models.py`**:
```python
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class BaseDocument:
    """Base class for all Cosmos DB documents."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
```

### 2.1.2 Custom Exceptions

**`apps/core/exceptions.py`**:
```python
from rest_framework.exceptions import APIException
from rest_framework import status


class DocumentNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Document not found.'

class ScrapingFailed(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'Failed to scrape product data.'

class InvalidShopeeURL(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid Shopee affiliate URL.'

class CosmosDBError(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Database service unavailable.'
```

### 2.1.3 Standard Pagination

**`apps/core/pagination.py`**:
```python
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })
```

### 2.1.4 Global Exception Handler

**`apps/core/handlers.py`**:
```python
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return Response(
            {'error': 'Internal server error', 'detail': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    return response
```

---

## Step 2.2 — Cosmos DB Service Layer

**`services/cosmos_db.py`**:
```python
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from django.conf import settings
from apps.core.exceptions import DocumentNotFound, CosmosDBError
import logging

logger = logging.getLogger(__name__)


class CosmosDBService:
    _client = None
    _database = None

    @classmethod
    def get_client(cls) -> CosmosClient:
        if cls._client is None:
            cls._client = CosmosClient(
                url=settings.COSMOS_DB_URL,
                credential=settings.COSMOS_DB_KEY
            )
        return cls._client

    @classmethod
    def get_database(cls):
        if cls._database is None:
            cls._database = cls.get_client().get_database_client(
                settings.COSMOS_DB_DATABASE
            )
        return cls._database

    @classmethod
    def get_container(cls, container_name: str):
        return cls.get_database().get_container_client(container_name)

    @classmethod
    def upsert(cls, container_name: str, document: dict) -> dict:
        try:
            container = cls.get_container(container_name)
            return container.upsert_item(document)
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Cosmos DB upsert error: {e}")
            raise CosmosDBError(detail=str(e))

    @classmethod
    def get_by_id(cls, container_name: str, item_id: str, partition_key: str) -> dict:
        try:
            container = cls.get_container(container_name)
            return container.read_item(item=item_id, partition_key=partition_key)
        except exceptions.CosmosResourceNotFoundError:
            raise DocumentNotFound(detail=f"Document {item_id} not found.")
        except exceptions.CosmosHttpResponseError as e:
            raise CosmosDBError(detail=str(e))

    @classmethod
    def query(cls, container_name: str, query: str, parameters: list = None) -> list:
        try:
            container = cls.get_container(container_name)
            return list(container.query_items(
                query=query,
                parameters=parameters or [],
                enable_cross_partition_query=True
            ))
        except exceptions.CosmosHttpResponseError as e:
            raise CosmosDBError(detail=str(e))

    @classmethod
    def delete(cls, container_name: str, item_id: str, partition_key: str) -> None:
        try:
            container = cls.get_container(container_name)
            container.delete_item(item=item_id, partition_key=partition_key)
        except exceptions.CosmosResourceNotFoundError:
            raise DocumentNotFound(detail=f"Document {item_id} not found.")
```

---

## Step 2.2A — Users App (User Authentication)

> **⚠️ CRITICAL**: App BẮT BUỘC user authentication. Xem chi tiết full flows tại **[USER_AUTHENTICATION.md](USER_AUTHENTICATION.md)**.

### 2.2A.1 Install Dependencies

```bash
pip install djangorestframework-simplejwt bcrypt
```

**requirements.txt**:
```txt
djangorestframework-simplejwt==5.3.1
bcrypt==4.1.2
```

### 2.2A.2 Django Settings

**config/settings/base.py**:
```python
INSTALLED_APPS += [
    'rest_framework_simplejwt',
    'apps.users',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Require auth by default
    ],
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

### 2.2A.3 User Model

**`apps/users/models.py`**:
```python
from dataclasses import dataclass
from typing import Optional
from apps.core.models import BaseDocument

@dataclass
class User(BaseDocument):
    """User account for authentication."""
    email: str                    # Unique, lowercase
    password_hash: str            # bcrypt hash
    display_name: str             # User's display name
    
    status: str = "active"        # active | suspended | deleted
    email_verified: bool = False
    
    # Optional
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    
    # Metadata
    last_login_at: Optional[str] = None
    login_count: int = 0
    
    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}
    
    def to_response(self) -> dict:
        """Safe dict for API response (no password_hash)."""
        return {
            'id': self.id,
            'email': self.email,
            'display_name': self.display_name,
            'status': self.status,
            'email_verified': self.email_verified,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at,
        }
```

### 2.2A.4 User Service

**`apps/users/services.py`**:
```python
import bcrypt
import uuid
from datetime import datetime
from typing import Optional
from services.cosmos_db import CosmosDBService
from apps.users.models import User
from apps.core.exceptions import DocumentNotFound
from rest_framework.exceptions import ValidationError, AuthenticationFailed

class UserService:
    CONTAINER = 'users'
    
    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    @staticmethod
    def exists_by_email(email: str) -> bool:
        query = "SELECT c.id FROM c WHERE c.email = @email"
        params = [{"name": "@email", "value": email.lower()}]
        items = CosmosDBService.query(UserService.CONTAINER, query, params)
        return len(items) > 0
    
    @staticmethod
    def create(email: str, password: str, display_name: str) -> User:
        email = email.lower().strip()
        
        if UserService.exists_by_email(email):
            raise ValidationError({"email": "Email đã được đăng ký."})
        
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            password_hash=UserService.hash_password(password),
            display_name=display_name.strip(),
            status='active',
            email_verified=False,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )
        
        CosmosDBService.upsert(UserService.CONTAINER, user.to_dict())
        return user
    
    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        query = "SELECT * FROM c WHERE c.email = @email"
        params = [{"name": "@email", "value": email.lower()}]
        items = CosmosDBService.query(UserService.CONTAINER, query, params)
        return User(**items[0]) if items else None
    
    @staticmethod
    def get_by_id(user_id: str) -> User:
        item = CosmosDBService.get_by_id(UserService.CONTAINER, user_id, partition_key=user_id)
        return User(**item)
    
    @staticmethod
    def authenticate(email: str, password: str) -> User:
        user = UserService.get_by_email(email)
        
        if not user or not UserService.verify_password(password, user.password_hash):
            raise AuthenticationFailed("Email hoặc mật khẩu không đúng.")
        
        if user.status != 'active':
            raise AuthenticationFailed("Tài khoản đã bị tạm khóa.")
        
        # Update last login
        user.last_login_at = datetime.utcnow().isoformat()
        user.login_count += 1
        user.updated_at = datetime.utcnow().isoformat()
        CosmosDBService.upsert(UserService.CONTAINER, user.to_dict())
        
        return user
    
    @staticmethod
    def change_password(user_id: str, old_password: str, new_password: str) -> None:
        user = UserService.get_by_id(user_id)
        
        if not UserService.verify_password(old_password, user.password_hash):
            raise AuthenticationFailed("Mật khẩu hiện tại không đúng.")
        
        user.password_hash = UserService.hash_password(new_password)
        user.updated_at = datetime.utcnow().isoformat()
        CosmosDBService.upsert(UserService.CONTAINER, user.to_dict())
```

### 2.2A.5 User Serializers

**`apps/users/serializers.py`**:
```python
from rest_framework import serializers
import re
from apps.users.services import UserService

class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, max_length=128, write_only=True)
    display_name = serializers.CharField(min_length=2, max_length=50)
    
    def validate_email(self, value):
        value = value.lower().strip()
        if UserService.exists_by_email(value):
            raise serializers.ValidationError("Email này đã được đăng ký.")
        return value
    
    def validate_password(self, value):
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Mật khẩu phải chứa ít nhất 1 chữ hoa.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Mật khẩu phải chứa ít nhất 1 chữ thường.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Mật khẩu phải chứa ít nhất 1 số.")
        return value
    
    def validate_display_name(self, value):
        value = value.strip()
        if not re.match(r'^[a-zA-ZÀ-ỹ\s\.]+$', value):
            raise serializers.ValidationError("Tên chỉ được chứa chữ cái và khoảng trắng.")
        return value


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.Serializer):
    id = serializers.CharField()
    email = serializers.EmailField()
    display_name = serializers.CharField()
    status = serializers.CharField()
    email_verified = serializers.BooleanField()
    avatar_url = serializers.CharField(allow_null=True)
    created_at = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8, write_only=True)
```

### 2.2A.6 Auth Views

**`apps/users/views.py`**:
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    ChangePasswordSerializer,
)
from apps.users.services import UserService

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = UserService.create(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            display_name=serializer.validated_data['display_name'],
        )
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': user.to_response(),
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = UserService.authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
        )
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': user.to_response(),
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = UserService.get_by_id(request.user.id)
        return Response(user.to_response())


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        UserService.change_password(
            user_id=request.user.id,
            old_password=serializer.validated_data['old_password'],
            new_password=serializer.validated_data['new_password'],
        )
        
        return Response({'detail': 'Đổi mật khẩu thành công.'})
```

### 2.2A.7 URLs

**`apps/users/urls.py`**:
```python
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.users.views import (
    RegisterView, LoginView, LogoutView, MeView, ChangePasswordView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', MeView.as_view(), name='current_user'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
]
```

**config/urls.py**:
```python
urlpatterns = [
    path('api/auth/', include('apps.users.urls')),
    # ... other URLs

    class LogoutView(APIView):
        permission_classes = [IsAuthenticated]
        
        def post(self, request):
            try:
                refresh_token = request.data.get('refresh')
                if refresh_token:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
            except Exception:
                pass
            return Response(status=status.HTTP_204_NO_CONTENT)


    class MeView(APIView):
        permission_classes = [IsAuthenticated]
        
        def get(self, request):
            user = UserService.get_by_id(request.user.id)
            return Response(user.to_response())

## Step 2.3 — Products App

### 2.3.1 Product Document Schema

**`apps/products/models.py`**:
```python
from dataclasses import dataclass, field
from typing import Optional
from apps.core.models import BaseDocument

# Cosmos DB container: "products"
# Partition key: /shop_id

@dataclass
class Product(BaseDocument):
    title: str = ""
    original_url: str = ""         # Actual Shopee product URL
    shop_id: str = ""              # Partition key
    item_id: str = ""              # Shopee item ID
    thumbnail_url: str = ""        # Azure Blob Storage URL
    thumbnail_original: str = ""   # Original Shopee thumbnail URL
    price: Optional[float] = None
    price_currency: str = "VND"
    category: Optional[str] = None
    status: str = "active"         # active | deleted

# Example document:
# {
#   "id": "uuid",
#   "title": "Tai nghe Sony WH-1000XM5",
#   "original_url": "https://shopee.vn/product/123456/789012",
#   "shop_id": "123456",
#   "item_id": "789012",
#   "thumbnail_url": "https://stshopeeaffdev.blob.core.windows.net/thumbnails/uuid.jpg",
#   "thumbnail_original": "https://down-vn.img.susercontent.com/file/xxx.jpg",
#   "price": 4990000.0,
#   "price_currency": "VND",
#   "status": "active",
#   "created_at": "2026-05-06T00:00:00Z",
#   "updated_at": "2026-05-06T00:00:00Z"
# }
```

### 2.3.2 Product Serializer

**`apps/products/serializers.py`**:
```python
from rest_framework import serializers


class ProductSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField()
    original_url = serializers.URLField()
    shop_id = serializers.CharField(read_only=True)
    item_id = serializers.CharField(read_only=True)
    thumbnail_url = serializers.URLField(read_only=True)
    price = serializers.FloatField(allow_null=True, required=False)
    price_currency = serializers.CharField(default='VND')
    category = serializers.CharField(allow_null=True, required=False)
    status = serializers.CharField(read_only=True)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)


class ProductListSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    thumbnail_url = serializers.URLField()
    price = serializers.FloatField(allow_null=True)
    price_currency = serializers.CharField()
    created_at = serializers.CharField()
```

### 2.3.3 Product Service

**`apps/products/services.py`**:
```python
from services.cosmos_db import CosmosDBService
from apps.products.models import Product
from apps.core.exceptions import DocumentNotFound
from datetime import datetime, timezone

CONTAINER = 'products'


class ProductService:

    @staticmethod
    def create(data: dict) -> dict:
        product = Product(**data)
        return CosmosDBService.upsert(CONTAINER, product.to_dict())

    @staticmethod
    def get(product_id: str, shop_id: str) -> dict:
        return CosmosDBService.get_by_id(CONTAINER, product_id, shop_id)

    @staticmethod
    def list_all(page: int = 1, page_size: int = 20) -> tuple[list, int]:
        offset = (page - 1) * page_size
        query = """
            SELECT * FROM c
            WHERE c.status = 'active'
            ORDER BY c.created_at DESC
            OFFSET @offset LIMIT @limit
        """
        count_query = "SELECT VALUE COUNT(1) FROM c WHERE c.status = 'active'"
        items = CosmosDBService.query(CONTAINER, query, [
            {"name": "@offset", "value": offset},
            {"name": "@limit", "value": page_size},
        ])
        counts = CosmosDBService.query(CONTAINER, count_query)
        total = counts[0] if counts else 0
        return items, total

    @staticmethod
    def update(product_id: str, shop_id: str, data: dict) -> dict:
        existing = CosmosDBService.get_by_id(CONTAINER, product_id, shop_id)
        existing.update(data)
        existing['updated_at'] = datetime.now(timezone.utc).isoformat()
        return CosmosDBService.upsert(CONTAINER, existing)

    @staticmethod
    def delete(product_id: str, shop_id: str) -> None:
        existing = CosmosDBService.get_by_id(CONTAINER, product_id, shop_id)
        existing['status'] = 'deleted'
        existing['updated_at'] = datetime.now(timezone.utc).isoformat()
        CosmosDBService.upsert(CONTAINER, existing)
```

### 2.3.4 Product Views

**`apps/products/views.py`**:
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.products.services import ProductService
from apps.products.serializers import ProductSerializer, ProductListSerializer
from apps.core.pagination import StandardPagination


class ProductListView(APIView):
    def get(self, request):
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        items, total = ProductService.list_all(page, page_size)
        serializer = ProductListSerializer(items, many=True)
        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'results': serializer.data,
        })


class ProductDetailView(APIView):
    def get(self, request, product_id):
        shop_id = request.query_params.get('shop_id', '')
        product = ProductService.get(product_id, shop_id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def delete(self, request, product_id):
        shop_id = request.query_params.get('shop_id', '')
        ProductService.delete(product_id, shop_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
```

### 2.3.5 Product URLs

**`apps/products/urls.py`**:
```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product-list'),
    path('<str:product_id>/', views.ProductDetailView.as_view(), name='product-detail'),
]
```

---

## Step 2.4 — Shopee Scraper Service

### 2.4.1 URL Resolver

**`services/scraper.py`**:
```python
import httpx
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from apps.core.exceptions import InvalidShopeeURL, ScrapingFailed
import logging

logger = logging.getLogger(__name__)

SHOPEE_DOMAIN_PATTERN = re.compile(
    r'(shp\.ee|shopee\.vn|shopee\.com)'
)

SHOPEE_PRODUCT_PATTERN = re.compile(
    r'shopee\.vn/(?:[^/]+/)?i\.(\d+)\.(\d+)'
)


class ShopeeScraperService:
    """
    Shopee product scraper with multiple fallback strategies.
    
    Strategy 1: Parse HTML directly (fastest)
    Strategy 2: Use Shopee API endpoints (if HTML changes)
    Strategy 3: Retry with different User-Agents
    """
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]

    @staticmethod
    def validate_url(url: str) -> bool:
        return bool(SHOPEE_DOMAIN_PATTERN.search(url))

    @staticmethod
    async def resolve_redirect(url: str) -> str:
        """Resolve shp.ee short links to full Shopee URLs."""
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            response = await client.head(url)
            return str(response.url)

    @staticmethod
    def extract_ids_from_url(url: str) -> tuple[str, str]:
        """Extract shop_id and item_id from Shopee URL."""
        match = SHOPEE_PRODUCT_PATTERN.search(url)
        if not match:
            # Try query params: ?shopid=xxx&itemid=xxx
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            shop_id = params.get('shopid', [None])[0]
            item_id = params.get('itemid', [None])[0]
            if shop_id and item_id:
                return shop_id, item_id
            raise InvalidShopeeURL(detail=f"Cannot extract IDs from URL: {url}")
        return match.group(1), match.group(2)

    @staticmethod
    async def scrape_product(url: str) -> dict:
        """Scrape title and thumbnail from Shopee product page."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'vi-VN,vi;q=0.9',
        }

        try:
            async with httpx.AsyncClient(timeout=20, headers=headers) as client:
                response = await client.get(url)
                response.raise_for_status()
        except httpx.HTTPError as e:
            raise ScrapingFailed(detail=f"HTTP error: {str(e)}")

        soup = BeautifulSoup(response.text, 'lxml')

        # Extract title
        title = None
        og_title = soup.find('meta', property='og:title')
        if og_title:
            title = og_title.get('content', '').strip()
        if not title:
            title_tag = soup.find('title')
            title = title_tag.text.strip() if title_tag else 'Unknown Product'

        # Remove " | Shopee" suffix
        title = re.sub(r'\s*\|\s*Shopee.*$', '', title).strip()

        # Extract thumbnail
        thumbnail_url = None
        og_image = soup.find('meta', property='og:image')
        if og_image:
            thumbnail_url = og_image.get('content', '').strip()

        # Extract price (best-effort)
        price = None
        price_meta = soup.find('meta', property='product:price:amount')
        if price_meta:
            try:
                price = float(price_meta.get('content', '0').replace(',', ''))
            except ValueError:
                pass

        return {
            'title': title,
            'thumbnail_original': thumbnail_url,
            'price': price,
        }
```

### 2.4.2 Azure Storage Upload Service

**`services/azure_storage.py`**:
```python
import httpx
import uuid
from azure.storage.blob import BlobServiceClient, ContentSettings
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class AzureStorageService:
    _client = None

    @classmethod
    def get_client(cls) -> BlobServiceClient:
        if cls._client is None:
            cls._client = BlobServiceClient.from_connection_string(
                settings.AZURE_STORAGE_CONNECTION_STRING
            )
        return cls._client

    @classmethod
    async def upload_image_from_url(cls, image_url: str) -> str:
        """Download image and upload to Azure Blob Storage. Returns blob URL."""
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(image_url)
            response.raise_for_status()
            content_type = response.headers.get('content-type', 'image/jpeg')
            image_data = response.content

        blob_name = f"{uuid.uuid4()}.jpg"
        blob_client = cls.get_client().get_blob_client(
            container=settings.AZURE_STORAGE_CONTAINER,
            blob=blob_name
        )

        blob_client.upload_blob(
            image_data,
            content_settings=ContentSettings(content_type=content_type),
            overwrite=True
        )

        return blob_client.url
```

---

## Step 2.5 — Links App

### 2.5.1 Link Document Schema

**`apps/links/models.py`**:
```python
from dataclasses import dataclass, field
from typing import Optional
from apps.core.models import BaseDocument

# Cosmos DB container: "links"
# Partition key: /user_id

@dataclass
class AffLink(BaseDocument):
    original_url: str = ""          # URL người dùng paste vào
    resolved_url: str = ""          # URL sau khi resolve redirect
    shop_id: str = ""
    item_id: str = ""
    product_id: Optional[str] = None  # FK → products container
    user_id: str = "default"          # For future multi-user support
    status: str = "pending"           # pending | processing | done | failed
    error_message: Optional[str] = None
    notes: Optional[str] = None       # User notes on this link
```

### 2.5.2 Link Service

**`apps/links/services.py`**:
```python
import asyncio
import httpx
from services.cosmos_db import CosmosDBService
from services.scraper import ShopeeScraperService
from services.azure_storage import AzureStorageService
from apps.links.models import AffLink
from apps.products.models import Product
from apps.products.services import ProductService
from django.conf import settings
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

CONTAINER = 'links'


class LinkService:

    @staticmethod
    def create_pending(url: str, user_id: str = 'default') -> dict:
        """Create link in PENDING state, then trigger async scraping."""
        if not ShopeeScraperService.validate_url(url):
            from apps.core.exceptions import InvalidShopeeURL
            raise InvalidShopeeURL()

        link = AffLink(
            original_url=url,
            user_id=user_id,
            status='pending'
        )
        saved = CosmosDBService.upsert(CONTAINER, link.to_dict())

        # Trigger Azure Function asynchronously (fire-and-forget)
        LinkService._trigger_scraping(saved['id'], url)

        return saved

    @staticmethod
    def _trigger_scraping(link_id: str, url: str) -> None:
        """Call Azure Function to process scraping in background."""
        try:
            payload = {'link_id': link_id, 'url': url}
            headers = {'x-functions-key': settings.FUNCTION_APP_KEY}
            with httpx.Client(timeout=5) as client:
                client.post(
                    f"{settings.FUNCTION_APP_URL}/api/scrape_product",
                    json=payload,
                    headers=headers
                )
        except Exception as e:
            logger.warning(f"Failed to trigger Function App: {e}. Will fallback to sync.")
            # Sync fallback for development
            asyncio.run(LinkService._process_sync(link_id, url))

    @staticmethod
    async def _process_sync(link_id: str, url: str) -> None:
        """Synchronous fallback: scrape in-process (dev only)."""
        try:
            LinkService._update_status(link_id, 'processing')

            resolved_url = await ShopeeScraperService.resolve_redirect(url)
            shop_id, item_id = ShopeeScraperService.extract_ids_from_url(resolved_url)
            scraped = await ShopeeScraperService.scrape_product(resolved_url)

            thumbnail_url = ''
            if scraped.get('thumbnail_original'):
                thumbnail_url = await AzureStorageService.upload_image_from_url(
                    scraped['thumbnail_original']
                )

            product = ProductService.create({
                'title': scraped['title'],
                'original_url': resolved_url,
                'shop_id': shop_id,
                'item_id': item_id,
                'thumbnail_url': thumbnail_url,
                'thumbnail_original': scraped.get('thumbnail_original', ''),
                'price': scraped.get('price'),
            })

            link = CosmosDBService.get_by_id(CONTAINER, link_id, 'default')
            link.update({
                'resolved_url': resolved_url,
                'shop_id': shop_id,
                'item_id': item_id,
                'product_id': product['id'],
                'status': 'done',
                'updated_at': datetime.now(timezone.utc).isoformat()
            })
            CosmosDBService.upsert(CONTAINER, link)

        except Exception as e:
            logger.error(f"Scraping failed for link {link_id}: {e}")
            LinkService._update_status(link_id, 'failed', str(e))

    @staticmethod
    def _update_status(link_id: str, status: str, error: str = None) -> None:
        link = CosmosDBService.get_by_id(CONTAINER, link_id, 'default')
        link['status'] = status
        link['updated_at'] = datetime.now(timezone.utc).isoformat()
        if error:
            link['error_message'] = error
        CosmosDBService.upsert(CONTAINER, link)

    @staticmethod
    def get(link_id: str, user_id: str = 'default') -> dict:
        return CosmosDBService.get_by_id(CONTAINER, link_id, user_id)

    @staticmethod
    def list_for_user(user_id: str = 'default', page: int = 1, page_size: int = 20) -> tuple:
        offset = (page - 1) * page_size
        query = """
            SELECT * FROM c
            WHERE c.user_id = @user_id
            ORDER BY c.created_at DESC
            OFFSET @offset LIMIT @limit
        """
        items = CosmosDBService.query(CONTAINER, query, [
            {"name": "@user_id", "value": user_id},
            {"name": "@offset", "value": offset},
            {"name": "@limit", "value": page_size},
        ])
        return items, len(items)
```

### 2.5.3 Link Views

**`apps/links/views.py`**:
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.links.services import LinkService
from apps.links.serializers import AffLinkSerializer, CreateLinkSerializer


class LinkListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id', 'default')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        items, total = LinkService.list_for_user(user_id, page, page_size)
        serializer = AffLinkSerializer(items, many=True)
        return Response({'count': total, 'results': serializer.data})

    def post(self, request):
        serializer = CreateLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        link = LinkService.create_pending(
            url=serializer.validated_data['url'],
            user_id=serializer.validated_data.get('user_id', 'default')
        )
        return Response(AffLinkSerializer(link).data, status=status.HTTP_201_CREATED)


class LinkDetailView(APIView):
    def get(self, request, link_id):
        user_id = request.query_params.get('user_id', 'default')
        link = LinkService.get(link_id, user_id)
        return Response(AffLinkSerializer(link).data)
```

### 2.5.4 Link Serializers

**`apps/links/serializers.py`**:
```python
from rest_framework import serializers


class CreateLinkSerializer(serializers.Serializer):
    url = serializers.URLField()
    user_id = serializers.CharField(default='default', required=False)
    notes = serializers.CharField(allow_blank=True, required=False)


class AffLinkSerializer(serializers.Serializer):
    id = serializers.CharField()
    original_url = serializers.URLField()
    resolved_url = serializers.URLField(allow_blank=True, required=False)
    product_id = serializers.CharField(allow_null=True, required=False)
    status = serializers.CharField()
    notes = serializers.CharField(allow_null=True, required=False)
    error_message = serializers.CharField(allow_null=True, required=False)
    created_at = serializers.CharField()
    updated_at = serializers.CharField()
```

---

## Step 2.6 — Azure Function App (Async Scraper)

**`azure_functions/scrape_product/__init__.py`**:
```python
import azure.functions as func
import asyncio
import json
import logging
import httpx
from bs4 import BeautifulSoup
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient
import os
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

COSMOS_URL = os.environ['COSMOS_DB_URL']
COSMOS_KEY = os.environ['COSMOS_DB_KEY']
COSMOS_DB = os.environ['COSMOS_DB_DATABASE']
STORAGE_CONN = os.environ['AZURE_STORAGE_CONNECTION_STRING']
STORAGE_CONTAINER = os.environ['AZURE_STORAGE_CONTAINER']


async def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        link_id = body['link_id']
        url = body['url']
    except (ValueError, KeyError) as e:
        return func.HttpResponse(f"Bad request: {e}", status_code=400)

    cosmos = CosmosClient(COSMOS_URL, COSMOS_KEY)
    db = cosmos.get_database_client(COSMOS_DB)
    links_container = db.get_container_client('links')
    products_container = db.get_container_client('products')

    # Mark as processing
    _update_link_status(links_container, link_id, 'processing')

    try:
        # 1. Resolve redirect
        resolved_url = await _resolve_redirect(url)

        # 2. Extract IDs
        shop_id, item_id = _extract_shopee_ids(resolved_url)

        # 3. Scrape product page
        scraped = await _scrape(resolved_url)

        # 4. Upload thumbnail
        thumbnail_url = ''
        if scraped.get('thumbnail_original'):
            thumbnail_url = await _upload_thumbnail(
                scraped['thumbnail_original'], STORAGE_CONN, STORAGE_CONTAINER
            )

        # 5. Save product
        product = {
            'id': str(uuid.uuid4()),
            'title': scraped['title'],
            'original_url': resolved_url,
            'shop_id': shop_id,
            'item_id': item_id,
            'thumbnail_url': thumbnail_url,
            'thumbnail_original': scraped.get('thumbnail_original', ''),
            'price': scraped.get('price'),
            'status': 'active',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
        }
        products_container.upsert_item(product)

        # 6. Update link to done
        link = links_container.read_item(item=link_id, partition_key='default')
        link.update({
            'resolved_url': resolved_url,
            'shop_id': shop_id,
            'item_id': item_id,
            'product_id': product['id'],
            'status': 'done',
            'updated_at': datetime.now(timezone.utc).isoformat()
        })
        links_container.upsert_item(link)

        return func.HttpResponse(
            json.dumps({'status': 'done', 'product_id': product['id']}),
            status_code=200,
            mimetype='application/json'
        )

    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        _update_link_status(links_container, link_id, 'failed', str(e))
        return func.HttpResponse(f"Scraping failed: {e}", status_code=500)


def _update_link_status(container, link_id, status, error=None):
    try:
        link = container.read_item(item=link_id, partition_key='default')
        link['status'] = status
        link['updated_at'] = datetime.now(timezone.utc).isoformat()
        if error:
            link['error_message'] = error
        container.upsert_item(link)
    except Exception as e:
        logger.warning(f"Could not update link status: {e}")


async def _resolve_redirect(url: str) -> str:
    async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
        r = await client.head(url)
        return str(r.url)


def _extract_shopee_ids(url: str) -> tuple[str, str]:
    import re
    from urllib.parse import urlparse, parse_qs
    pattern = re.compile(r'i\.(\d+)\.(\d+)')
    match = pattern.search(url)
    if match:
        return match.group(1), match.group(2)
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return params.get('shopid', ['unknown'])[0], params.get('itemid', ['unknown'])[0]


async def _scrape(url: str) -> dict:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    async with httpx.AsyncClient(timeout=20, headers=headers) as client:
        r = await client.get(url)
        r.raise_for_status()
    soup = BeautifulSoup(r.text, 'lxml')
    title = (soup.find('meta', property='og:title') or {}).get('content', 'Unknown')
    import re
    title = re.sub(r'\s*\|\s*Shopee.*$', '', title).strip()
    thumbnail = (soup.find('meta', property='og:image') or {}).get('content', '')
    price = None
    price_meta = soup.find('meta', property='product:price:amount')
    if price_meta:
        try:
            price = float(price_meta['content'].replace(',', ''))
        except (ValueError, KeyError):
            pass
    return {'title': title, 'thumbnail_original': thumbnail, 'price': price}


async def _upload_thumbnail(image_url: str, conn_str: str, container: str) -> str:
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(image_url)
        r.raise_for_status()
        data = r.content
    blob_name = f"{uuid.uuid4()}.jpg"
    blob_client = BlobServiceClient.from_connection_string(conn_str)\
        .get_blob_client(container=container, blob=blob_name)
    blob_client.upload_blob(data, overwrite=True)
    return blob_client.url
```

**`azure_functions/scrape_product/function.json`**:
```json
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "authLevel": "function",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": ["post"]
    },
    {
      "type": "http",
      "direction": "out",
      "name": "$return"
    }
  ]
}
```

---

## Step 2.7 — Root URL Config

**`config/urls.py`**:
```python
from django.urls import path, include

urlpatterns = [
    path('api/links/', include('apps.links.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/search/', include('apps.search.urls')),
    path('api/health/', lambda req: __import__('django.http', fromlist=['JsonResponse']).JsonResponse({'status': 'ok'})),
]
```

---

## Step 2.9 — Django Admin Dashboard

> **Lưu ý**: Vì sử dụng Cosmos DB thay vì Django ORM, không thể dùng `ModelAdmin` truyền thống. Thay vào đó, tạo custom admin views với Django Admin site.

### 2.9.1 Admin Configuration

**`config/settings/base.py`** (update INSTALLED_APPS):
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # ...
    'apps.core',
    'apps.users',
    'apps.products',
    'apps.links',
    'apps.search',
    'apps.admin_dashboard',  # Custom admin app
]

# Session for admin login
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_HTTPONLY = True
```

### 2.9.2 Admin App Structure

```
apps/admin_dashboard/
├── __init__.py
├── apps.py
├── urls.py
├── views.py
├── services.py
├── forms.py
└── templates/
    └── admin_dashboard/
        ├── base.html
        ├── dashboard.html
        ├── users/
        │   ├── list.html
        │   ├── detail.html
        │   └── form.html
        ├── products/
        │   ├── list.html
        │   ├── detail.html
        │   └── form.html
        └── links/
            ├── list.html
            └── detail.html
```

### 2.9.3 Admin App Config

**`apps/admin_dashboard/apps.py`**:
```python
from django.apps import AppConfig


class AdminDashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.admin_dashboard'
    verbose_name = 'Admin Dashboard'
```

### 2.9.4 Admin Services

**`apps/admin_dashboard/services.py`**:
```python
from services.cosmos_db import CosmosDBService


class AdminService:
    """Service layer for admin operations."""

    # ============ STATISTICS ============

    @staticmethod
    def get_dashboard_stats() -> dict:
        """Get statistics for admin dashboard."""
        cosmos = CosmosDBService()

        # Count users
        users_query = "SELECT VALUE COUNT(1) FROM c"
        users_result = list(cosmos.query('users', users_query))
        total_users = users_result[0] if users_result else 0

        # Count products
        products_result = list(cosmos.query('products', users_query))
        total_products = products_result[0] if products_result else 0

        # Count links by status
        links_pending = list(cosmos.query(
            'links',
            "SELECT VALUE COUNT(1) FROM c WHERE c.status = 'pending'"
        ))
        links_processing = list(cosmos.query(
            'links',
            "SELECT VALUE COUNT(1) FROM c WHERE c.status = 'processing'"
        ))
        links_done = list(cosmos.query(
            'links',
            "SELECT VALUE COUNT(1) FROM c WHERE c.status = 'done'"
        ))
        links_failed = list(cosmos.query(
            'links',
            "SELECT VALUE COUNT(1) FROM c WHERE c.status = 'failed'"
        ))

        return {
            'total_users': total_users,
            'total_products': total_products,
            'links': {
                'pending': links_pending[0] if links_pending else 0,
                'processing': links_processing[0] if links_processing else 0,
                'done': links_done[0] if links_done else 0,
                'failed': links_failed[0] if links_failed else 0,
            }
        }

    # ============ USERS ============

    @staticmethod
    def list_users(page: int = 1, page_size: int = 20) -> tuple[list, int]:
        """List all users with pagination."""
        cosmos = CosmosDBService()
        offset = (page - 1) * page_size

        # Get total count
        count_result = list(cosmos.query('users', "SELECT VALUE COUNT(1) FROM c"))
        total = count_result[0] if count_result else 0

        # Get paginated users
        query = f"SELECT * FROM c ORDER BY c.created_at DESC OFFSET {offset} LIMIT {page_size}"
        users = list(cosmos.query('users', query))

        # Remove password_hash from response
        for user in users:
            user.pop('password_hash', None)

        return users, total

    @staticmethod
    def get_user(user_id: str) -> dict | None:
        """Get user by ID."""
        cosmos = CosmosDBService()
        user = cosmos.get_by_id('users', user_id, user_id)
        if user:
            user.pop('password_hash', None)
        return user

    @staticmethod
    def update_user_status(user_id: str, status: str) -> dict | None:
        """Update user status (active/suspended/banned)."""
        cosmos = CosmosDBService()
        user = cosmos.get_by_id('users', user_id, user_id)
        if not user:
            return None

        user['status'] = status
        from datetime import datetime, timezone
        user['updated_at'] = datetime.now(timezone.utc).isoformat()
        cosmos.upsert('users', user, user_id)
        user.pop('password_hash', None)
        return user

    @staticmethod
    def delete_user(user_id: str) -> bool:
        """Delete user and all their data."""
        cosmos = CosmosDBService()
        try:
            # Delete user's links
            links = list(cosmos.query(
                'links',
                f"SELECT c.id FROM c WHERE c.user_id = '{user_id}'"
            ))
            for link in links:
                cosmos.delete('links', link['id'], user_id)

            # Delete user
            cosmos.delete('users', user_id, user_id)
            return True
        except Exception:
            return False

    # ============ PRODUCTS ============

    @staticmethod
    def list_products(page: int = 1, page_size: int = 20, shop_id: str = None) -> tuple[list, int]:
        """List all products with pagination."""
        cosmos = CosmosDBService()
        offset = (page - 1) * page_size

        where_clause = f"WHERE c.shop_id = '{shop_id}'" if shop_id else ""

        # Get total count
        count_query = f"SELECT VALUE COUNT(1) FROM c {where_clause}"
        count_result = list(cosmos.query('products', count_query))
        total = count_result[0] if count_result else 0

        # Get paginated products
        query = f"SELECT * FROM c {where_clause} ORDER BY c.created_at DESC OFFSET {offset} LIMIT {page_size}"
        products = list(cosmos.query('products', query))

        return products, total

    @staticmethod
    def get_product(product_id: str, shop_id: str) -> dict | None:
        """Get product by ID."""
        cosmos = CosmosDBService()
        return cosmos.get_by_id('products', product_id, shop_id)

    @staticmethod
    def delete_product(product_id: str, shop_id: str) -> bool:
        """Delete product."""
        cosmos = CosmosDBService()
        try:
            cosmos.delete('products', product_id, shop_id)
            # Also delete from search index
            from services.azure_search import AzureSearchService
            AzureSearchService().delete_product(product_id)
            return True
        except Exception:
            return False

    # ============ LINKS ============

    @staticmethod
    def list_links(page: int = 1, page_size: int = 20, status: str = None) -> tuple[list, int]:
        """List all links with pagination."""
        cosmos = CosmosDBService()
        offset = (page - 1) * page_size

        where_clause = f"WHERE c.status = '{status}'" if status else ""

        # Get total count (cross-partition)
        count_query = f"SELECT VALUE COUNT(1) FROM c {where_clause}"
        count_result = list(cosmos.query('links', count_query, enable_cross_partition=True))
        total = count_result[0] if count_result else 0

        # Get paginated links
        query = f"SELECT * FROM c {where_clause} ORDER BY c.created_at DESC OFFSET {offset} LIMIT {page_size}"
        links = list(cosmos.query('links', query, enable_cross_partition=True))

        return links, total

    @staticmethod
    def get_link(link_id: str, user_id: str) -> dict | None:
        """Get link by ID."""
        cosmos = CosmosDBService()
        return cosmos.get_by_id('links', link_id, user_id)

    @staticmethod
    def retry_failed_link(link_id: str, user_id: str) -> dict | None:
        """Retry a failed link."""
        cosmos = CosmosDBService()
        link = cosmos.get_by_id('links', link_id, user_id)
        if not link or link['status'] != 'failed':
            return None

        # Reset status to pending
        link['status'] = 'pending'
        link['error_message'] = None
        from datetime import datetime, timezone
        link['updated_at'] = datetime.now(timezone.utc).isoformat()
        cosmos.upsert('links', link, user_id)

        # Trigger scraping again
        from apps.links.services import LinkService
        LinkService._trigger_scraping(link_id, link['original_url'], user_id)

        return link

    @staticmethod
    def delete_link(link_id: str, user_id: str) -> bool:
        """Delete link."""
        cosmos = CosmosDBService()
        try:
            cosmos.delete('links', link_id, user_id)
            return True
        except Exception:
            return False
```

### 2.9.5 Admin Forms

**`apps/admin_dashboard/forms.py`**:
```python
from django import forms


class AdminLoginForm(forms.Form):
    """Admin login form."""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        })
    )


class UserStatusForm(forms.Form):
    """Form to update user status."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('banned', 'Banned'),
    ]
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class ProductFilterForm(forms.Form):
    """Form to filter products."""
    shop_id = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by Shop ID',
        })
    )


class LinkFilterForm(forms.Form):
    """Form to filter links."""
    STATUS_CHOICES = [
        ('', 'All'),
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ]
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
```

### 2.9.6 Admin Views

**`apps/admin_dashboard/views.py`**:
```python
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from functools import wraps

from .services import AdminService
from .forms import AdminLoginForm, UserStatusForm, ProductFilterForm, LinkFilterForm
from apps.users.services import UserService


def admin_required(view_func):
    """Decorator to require admin authentication."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        admin_user = request.session.get('admin_user')
        if not admin_user:
            return redirect('admin_dashboard:login')
        # Verify user is still valid and is admin
        user = UserService.get_by_id(admin_user['id'])
        if not user or user.get('role') != 'admin':
            request.session.pop('admin_user', None)
            return redirect('admin_dashboard:login')
        request.admin_user = user
        return view_func(request, *args, **kwargs)
    return wrapper


class AdminLoginView(View):
    """Admin login page."""
    template_name = 'admin_dashboard/login.html'

    def get(self, request):
        if request.session.get('admin_user'):
            return redirect('admin_dashboard:dashboard')
        form = AdminLoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = UserService.authenticate(email, password)
            if user and user.get('role') == 'admin':
                request.session['admin_user'] = {
                    'id': user['id'],
                    'email': user['email'],
                    'display_name': user['display_name'],
                }
                return redirect('admin_dashboard:dashboard')
            else:
                messages.error(request, 'Invalid credentials or not an admin.')

        return render(request, self.template_name, {'form': form})


class AdminLogoutView(View):
    """Admin logout."""

    def post(self, request):
        request.session.pop('admin_user', None)
        return redirect('admin_dashboard:login')


class DashboardView(View):
    """Admin dashboard with statistics."""
    template_name = 'admin_dashboard/dashboard.html'

    @admin_required
    def get(self, request):
        stats = AdminService.get_dashboard_stats()
        return render(request, self.template_name, {
            'stats': stats,
            'admin_user': request.admin_user,
        })


# ============ USERS ============

class UserListView(View):
    """List all users."""
    template_name = 'admin_dashboard/users/list.html'

    @admin_required
    def get(self, request):
        page = int(request.GET.get('page', 1))
        users, total = AdminService.list_users(page)
        return render(request, self.template_name, {
            'users': users,
            'total': total,
            'page': page,
            'total_pages': (total + 19) // 20,
            'admin_user': request.admin_user,
        })


class UserDetailView(View):
    """User detail page."""
    template_name = 'admin_dashboard/users/detail.html'

    @admin_required
    def get(self, request, user_id):
        user = AdminService.get_user(user_id)
        if not user:
            messages.error(request, 'User not found.')
            return redirect('admin_dashboard:users')

        form = UserStatusForm(initial={'status': user.get('status', 'active')})
        return render(request, self.template_name, {
            'user': user,
            'form': form,
            'admin_user': request.admin_user,
        })

    @admin_required
    def post(self, request, user_id):
        form = UserStatusForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            user = AdminService.update_user_status(user_id, status)
            if user:
                messages.success(request, f'User status updated to {status}.')
            else:
                messages.error(request, 'Failed to update user.')

        return redirect('admin_dashboard:user_detail', user_id=user_id)


class UserDeleteView(View):
    """Delete user."""

    @admin_required
    def post(self, request, user_id):
        if AdminService.delete_user(user_id):
            messages.success(request, 'User deleted.')
        else:
            messages.error(request, 'Failed to delete user.')
        return redirect('admin_dashboard:users')


# ============ PRODUCTS ============

class ProductListView(View):
    """List all products."""
    template_name = 'admin_dashboard/products/list.html'

    @admin_required
    def get(self, request):
        page = int(request.GET.get('page', 1))
        form = ProductFilterForm(request.GET)
        shop_id = None
        if form.is_valid():
            shop_id = form.cleaned_data.get('shop_id')

        products, total = AdminService.list_products(page, shop_id=shop_id)
        return render(request, self.template_name, {
            'products': products,
            'total': total,
            'page': page,
            'total_pages': (total + 19) // 20,
            'form': form,
            'admin_user': request.admin_user,
        })


class ProductDetailView(View):
    """Product detail page."""
    template_name = 'admin_dashboard/products/detail.html'

    @admin_required
    def get(self, request, product_id, shop_id):
        product = AdminService.get_product(product_id, shop_id)
        if not product:
            messages.error(request, 'Product not found.')
            return redirect('admin_dashboard:products')

        return render(request, self.template_name, {
            'product': product,
            'admin_user': request.admin_user,
        })


class ProductDeleteView(View):
    """Delete product."""

    @admin_required
    def post(self, request, product_id, shop_id):
        if AdminService.delete_product(product_id, shop_id):
            messages.success(request, 'Product deleted.')
        else:
            messages.error(request, 'Failed to delete product.')
        return redirect('admin_dashboard:products')


# ============ LINKS ============

class LinkListView(View):
    """List all links."""
    template_name = 'admin_dashboard/links/list.html'

    @admin_required
    def get(self, request):
        page = int(request.GET.get('page', 1))
        form = LinkFilterForm(request.GET)
        status = None
        if form.is_valid():
            status = form.cleaned_data.get('status')

        links, total = AdminService.list_links(page, status=status)
        return render(request, self.template_name, {
            'links': links,
            'total': total,
            'page': page,
            'total_pages': (total + 19) // 20,
            'form': form,
            'admin_user': request.admin_user,
        })


class LinkDetailView(View):
    """Link detail page."""
    template_name = 'admin_dashboard/links/detail.html'

    @admin_required
    def get(self, request, link_id, user_id):
        link = AdminService.get_link(link_id, user_id)
        if not link:
            messages.error(request, 'Link not found.')
            return redirect('admin_dashboard:links')

        return render(request, self.template_name, {
            'link': link,
            'admin_user': request.admin_user,
        })


class LinkRetryView(View):
    """Retry failed link."""

    @admin_required
    def post(self, request, link_id, user_id):
        link = AdminService.retry_failed_link(link_id, user_id)
        if link:
            messages.success(request, 'Link queued for retry.')
        else:
            messages.error(request, 'Cannot retry this link.')
        return redirect('admin_dashboard:link_detail', link_id=link_id, user_id=user_id)


class LinkDeleteView(View):
    """Delete link."""

    @admin_required
    def post(self, request, link_id, user_id):
        if AdminService.delete_link(link_id, user_id):
            messages.success(request, 'Link deleted.')
        else:
            messages.error(request, 'Failed to delete link.')
        return redirect('admin_dashboard:links')
```

### 2.9.7 Admin URLs

**`apps/admin_dashboard/urls.py`**:
```python
from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    # Auth
    path('login/', views.AdminLoginView.as_view(), name='login'),
    path('logout/', views.AdminLogoutView.as_view(), name='logout'),

    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),

    # Users
    path('users/', views.UserListView.as_view(), name='users'),
    path('users/<str:user_id>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<str:user_id>/delete/', views.UserDeleteView.as_view(), name='user_delete'),

    # Products
    path('products/', views.ProductListView.as_view(), name='products'),
    path('products/<str:shop_id>/<str:product_id>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/<str:shop_id>/<str:product_id>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),

    # Links
    path('links/', views.LinkListView.as_view(), name='links'),
    path('links/<str:user_id>/<str:link_id>/', views.LinkDetailView.as_view(), name='link_detail'),
    path('links/<str:user_id>/<str:link_id>/retry/', views.LinkRetryView.as_view(), name='link_retry'),
    path('links/<str:user_id>/<str:link_id>/delete/', views.LinkDeleteView.as_view(), name='link_delete'),
]
```

### 2.9.8 Update User Model for Admin Role

**`apps/users/models.py`** (thêm field `role`):
```python
from dataclasses import dataclass, field
from apps.core.models import BaseDocument


@dataclass
class User(BaseDocument):
    email: str = ""
    password_hash: str = ""
    display_name: str = ""
    status: str = "active"  # active, suspended, banned
    role: str = "user"      # user, admin  ← THÊM MỚI
    email_verified: bool = False

    def to_response(self) -> dict:
        """Return user data without sensitive fields."""
        data = self.to_dict()
        data.pop('password_hash', None)
        return data
```

### 2.9.9 Admin Base Template

**`apps/admin_dashboard/templates/admin_dashboard/base.html`**:
```html
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Admin{% endblock %} - Shopee Affiliate Manager</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
    <style>
        :root {
            --color-primary: #EE4D2D;
        }
        .sidebar {
            width: 250px;
            min-height: 100vh;
            background: #1e1e1e;
        }
        .sidebar .nav-link {
            color: #adb5bd;
            padding: 0.75rem 1rem;
        }
        .sidebar .nav-link:hover,
        .sidebar .nav-link.active {
            color: #fff;
            background: rgba(238, 77, 45, 0.2);
        }
        .sidebar .nav-link.active {
            border-left: 3px solid var(--color-primary);
        }
        .main-content {
            flex: 1;
            background: #f8f9fa;
        }
        .stat-card {
            border-left: 4px solid var(--color-primary);
        }
        .btn-primary {
            background-color: var(--color-primary);
            border-color: var(--color-primary);
        }
        .btn-primary:hover {
            background-color: #d83e1f;
            border-color: #d83e1f;
        }
    </style>
</head>
<body>
    <div class="d-flex">
        <!-- Sidebar -->
        <aside class="sidebar d-flex flex-column">
            <div class="p-3 border-bottom border-secondary">
                <span class="text-white fw-bold">
                    <i class="bi bi-bag-fill me-2" style="color: var(--color-primary);"></i>
                    Admin Panel
                </span>
            </div>
            <nav class="flex-grow-1 py-3">
                <ul class="nav flex-column">
                    <li class="nav-item">
                        <a href="{% url 'admin_dashboard:dashboard' %}"
                           class="nav-link {% if request.resolver_match.url_name == 'dashboard' %}active{% endif %}">
                            <i class="bi bi-speedometer2 me-2"></i>Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a href="{% url 'admin_dashboard:users' %}"
                           class="nav-link {% if 'user' in request.resolver_match.url_name %}active{% endif %}">
                            <i class="bi bi-people me-2"></i>Users
                        </a>
                    </li>
                    <li class="nav-item">
                        <a href="{% url 'admin_dashboard:products' %}"
                           class="nav-link {% if 'product' in request.resolver_match.url_name %}active{% endif %}">
                            <i class="bi bi-box-seam me-2"></i>Products
                        </a>
                    </li>
                    <li class="nav-item">
                        <a href="{% url 'admin_dashboard:links' %}"
                           class="nav-link {% if 'link' in request.resolver_match.url_name %}active{% endif %}">
                            <i class="bi bi-link-45deg me-2"></i>Links
                        </a>
                    </li>
                </ul>
            </nav>
            <div class="p-3 border-top border-secondary">
                <div class="text-white-50 small mb-2">
                    {{ admin_user.display_name }}
                </div>
                <form method="POST" action="{% url 'admin_dashboard:logout' %}">
                    {% csrf_token %}
                    <button type="submit" class="btn btn-outline-secondary btn-sm w-100">
                        <i class="bi bi-box-arrow-right me-1"></i>Logout
                    </button>
                </form>
            </div>
        </aside>

        <!-- Main Content -->
        <main class="main-content">
            <div class="p-4">
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    {% endfor %}
                {% endif %}

                {% block content %}{% endblock %}
            </div>
        </main>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

### 2.9.10 Dashboard Template

**`apps/admin_dashboard/templates/admin_dashboard/dashboard.html`**:
```html
{% extends 'admin_dashboard/base.html' %}

{% block title %}Dashboard{% endblock %}

{% block content %}
<h4 class="mb-4">Dashboard</h4>

<div class="row g-4">
    <!-- Users -->
    <div class="col-md-6 col-lg-3">
        <div class="card stat-card">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <h6 class="text-muted">Total Users</h6>
                        <h3>{{ stats.total_users }}</h3>
                    </div>
                    <div class="align-self-center">
                        <i class="bi bi-people fs-1 text-muted"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Products -->
    <div class="col-md-6 col-lg-3">
        <div class="card stat-card">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <h6 class="text-muted">Total Products</h6>
                        <h3>{{ stats.total_products }}</h3>
                    </div>
                    <div class="align-self-center">
                        <i class="bi bi-box-seam fs-1 text-muted"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Links Done -->
    <div class="col-md-6 col-lg-3">
        <div class="card stat-card" style="border-left-color: #28a745;">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <h6 class="text-muted">Links Done</h6>
                        <h3>{{ stats.links.done }}</h3>
                    </div>
                    <div class="align-self-center">
                        <i class="bi bi-check-circle fs-1 text-success"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Links Failed -->
    <div class="col-md-6 col-lg-3">
        <div class="card stat-card" style="border-left-color: #dc3545;">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <h6 class="text-muted">Links Failed</h6>
                        <h3>{{ stats.links.failed }}</h3>
                    </div>
                    <div class="align-self-center">
                        <i class="bi bi-x-circle fs-1 text-danger"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row g-4 mt-2">
    <!-- Links Status -->
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h6 class="mb-0">Links Status</h6>
            </div>
            <div class="card-body">
                <table class="table table-sm mb-0">
                    <tr>
                        <td><span class="badge bg-warning">Pending</span></td>
                        <td class="text-end">{{ stats.links.pending }}</td>
                    </tr>
                    <tr>
                        <td><span class="badge bg-info">Processing</span></td>
                        <td class="text-end">{{ stats.links.processing }}</td>
                    </tr>
                    <tr>
                        <td><span class="badge bg-success">Done</span></td>
                        <td class="text-end">{{ stats.links.done }}</td>
                    </tr>
                    <tr>
                        <td><span class="badge bg-danger">Failed</span></td>
                        <td class="text-end">{{ stats.links.failed }}</td>
                    </tr>
                </table>
            </div>
        </div>
    </div>

    <!-- Quick Actions -->
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h6 class="mb-0">Quick Actions</h6>
            </div>
            <div class="card-body">
                <a href="{% url 'admin_dashboard:users' %}" class="btn btn-outline-primary mb-2 w-100">
                    <i class="bi bi-people me-1"></i>Manage Users
                </a>
                <a href="{% url 'admin_dashboard:products' %}" class="btn btn-outline-primary mb-2 w-100">
                    <i class="bi bi-box-seam me-1"></i>Manage Products
                </a>
                <a href="{% url 'admin_dashboard:links' %}?status=failed" class="btn btn-outline-danger w-100">
                    <i class="bi bi-exclamation-triangle me-1"></i>View Failed Links
                </a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### 2.9.11 Login Template

**`apps/admin_dashboard/templates/admin_dashboard/login.html`**:
```html
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - Shopee Affiliate Manager</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .login-card { max-width: 400px; margin: 100px auto; }
        .btn-primary {
            background-color: #EE4D2D;
            border-color: #EE4D2D;
        }
        .btn-primary:hover {
            background-color: #d83e1f;
            border-color: #d83e1f;
        }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="card shadow-sm">
            <div class="card-body p-4">
                <div class="text-center mb-4">
                    <h4>Admin Login</h4>
                    <p class="text-muted">Shopee Affiliate Manager</p>
                </div>

                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-danger">{{ message }}</div>
                    {% endfor %}
                {% endif %}

                <form method="POST">
                    {% csrf_token %}
                    <div class="mb-3">
                        {{ form.email }}
                    </div>
                    <div class="mb-4">
                        {{ form.password }}
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Login</button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
```

### 2.9.12 Update Root URLs

**`config/urls.py`** (thêm admin_dashboard):
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django built-in admin (optional, keep for superuser)
    path('django-admin/', admin.site.urls),

    # Custom admin dashboard
    path('admin/', include('apps.admin_dashboard.urls')),

    # API endpoints
    path('api/', include([
        path('auth/', include('apps.users.urls')),
        path('products/', include('apps.products.urls')),
        path('links/', include('apps.links.urls')),
        path('search/', include('apps.search.urls')),
        path('health/', include('apps.core.urls')),
    ])),
]
```

### 2.9.13 Create Admin User Script

**`scripts/create_admin.py`**:
```python
#!/usr/bin/env python
"""Script to create an admin user."""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.users.services import UserService


def main():
    email = input('Admin email: ')
    password = input('Admin password: ')
    display_name = input('Display name: ')

    # Check if user exists
    if UserService.exists_by_email(email):
        print(f'User with email {email} already exists.')
        update = input('Update to admin? (y/n): ')
        if update.lower() == 'y':
            from services.cosmos_db import CosmosDBService
            cosmos = CosmosDBService()
            user = UserService.get_by_email(email)
            user['role'] = 'admin'
            cosmos.upsert('users', user, user['id'])
            print(f'User {email} updated to admin.')
        return

    # Create new admin user
    user = UserService.create(
        email=email,
        password=password,
        display_name=display_name,
    )

    # Update role to admin
    from services.cosmos_db import CosmosDBService
    cosmos = CosmosDBService()
    user['role'] = 'admin'
    cosmos.upsert('users', user, user['id'])

    print(f'Admin user created: {email}')


if __name__ == '__main__':
    main()
```

---

## Phase 2 Checklist

- [ ] `apps/core/` — BaseDocument, exceptions, pagination, handler
- [ ] `services/cosmos_db.py` — CosmosDBService với upsert/get/query/delete
- [ ] `apps/users/` — User model với role field, authentication
- [ ] `apps/products/` — models, serializers, services, views, urls
- [ ] `apps/links/` — models, serializers, services, views, urls
- [ ] `services/scraper.py` — validate, resolve_redirect, extract_ids, scrape
- [ ] `services/azure_storage.py` — upload_image_from_url
- [ ] `azure_functions/scrape_product/` — async function hoàn chỉnh
- [ ] `apps/admin_dashboard/` — Admin dashboard với:
  - [ ] Admin login/logout (session-based)
  - [ ] Dashboard với statistics
  - [ ] User management (list, detail, update status, delete)
  - [ ] Product management (list, filter by shop_id, detail, delete)
  - [ ] Link management (list, filter by status, retry failed, delete)
  - [ ] Admin templates (Bootstrap 5)
- [ ] `scripts/create_admin.py` — Script tạo admin user
- [ ] `config/urls.py` — tất cả routes đã đăng ký (API + Admin)
- [ ] Manual test: POST `/api/links/` với Shopee URL thật → status `done`
- [ ] Manual test: Admin login → Dashboard → Manage data
- [ ] Unit tests pass: `python manage.py test`

**Next:** [Phase 3 — AI / RAG Integration](PLAN_PHASE_3_AI_RAG.md)
