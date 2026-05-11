---
title: User Authentication System
version: 1.0.0
updated: 2026-05-06
---

# User Authentication System

## Overview

Complete authentication system với user registration, login, JWT tokens, và session management. App **BẮT BUỘC** user phải đăng nhập trước khi sử dụng.

---

## Authentication Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      FLUTTER MOBILE APP                         │
│                                                                 │
│  ┌───────────────┐   ┌──────────────┐   ┌──────────────────┐   │
│  │ Login Screen  │   │ Register     │   │ Protected        │   │
│  │               │   │ Screen       │   │ Screens          │   │
│  └───────┬───────┘   └──────┬───────┘   └────────┬─────────┘   │
│          │                  │                    │             │
│          │  POST /auth/login│ POST /auth/register│ Headers:    │
│          │  {email,password}│ {email,password,...}│ Bearer token│
│          │                  │                    │             │
│          └──────────────────┴────────────────────┘             │
│                             │                                   │
└─────────────────────────────┼───────────────────────────────────┘
                              │ HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DJANGO BACKEND API                           │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               JWT Authentication Middleware               │  │
│  │  - Verify JWT signature                                  │  │
│  │  - Check expiration                                       │  │
│  │  - Extract user_id from token                             │  │
│  │  - Attach user object to request                          │  │
│  └──────────────┬───────────────────────────────────────────┘  │
│                 │                                              │
│  ┌──────────────▼───────────────────────────────────────────┐  │
│  │                    Protected Views                        │  │
│  │  - POST /api/links/     (requires auth)                   │  │
│  │  - GET  /api/products/  (requires auth)                   │  │
│  │  - GET  /api/search/    (requires auth)                   │  │
│  └──────────────┬───────────────────────────────────────────┘  │
└─────────────────┼──────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                  AZURE COSMOS DB                                │
│                                                                 │
│  ┌─────────────────────────┐  ┌─────────────────────────────┐  │
│  │  Container: users       │  │  Container: products        │  │
│  │  Partition key: /id     │  │  Partition key: /user_id    │  │
│  │  - id (PK)              │  │  - user_id (FK to users)    │  │
│  │  - email (unique)       │  │  - product data             │  │
│  │  - password_hash        │  │                             │  │
│  │  - display_name         │  └─────────────────────────────┘  │
│  │  - created_at           │                                   │
│  └─────────────────────────┘  ┌─────────────────────────────┐  │
│                               │  Container: links           │  │
│                               │  Partition key: /user_id    │  │
│                               │  - user_id (FK to users)    │  │
│                               └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Authentication Flows

### 1. Registration Flow

```
User (Mobile App)                 Backend API                 Cosmos DB
      │                                │                           │
      │  POST /auth/register/          │                           │
      │  {                             │                           │
      │    "email": "user@example.com",│                           │
      │    "password": "StrongPass123",│                           │
      │    "display_name": "Nguyễn A"  │                           │
      │  }                             │                           │
      ├───────────────────────────────>│                           │
      │                                │ Validate input            │
      │                                │  - Email format           │
      │                                │  - Password strength      │
      │                                │  - Required fields        │
      │                                │                           │
      │                                │ Check email exists        │
      │                                ├──────────────────────────>│
      │                                │  Query users by email     │
      │                                │<──────────────────────────┤
      │                                │  Result: null (not exists)│
      │                                │                           │
      │                                │ Hash password (bcrypt)    │
      │                                │                           │
      │                                │ Create user record        │
      │                                ├──────────────────────────>│
      │                                │  {                        │
      │                                │    id: uuid(),            │
      │                                │    email: "...",          │
      │                                │    password_hash: "$2b...",│
      │                                │    display_name: "...",   │
      │                                │    status: "active",      │
      │                                │    created_at: now()      │
      │                                │  }                        │
      │                                │<──────────────────────────┤
      │                                │  Success                  │
      │                                │                           │
      │                                │ Generate JWT tokens       │
      │                                │  - Access token (1h)      │
      │                                │  - Refresh token (7d)     │
      │                                │                           │
      │  201 Created                   │                           │
      │  {                             │                           │
      │    "user": {                   │                           │
      │      "id": "...",              │                           │
      │      "email": "...",           │                           │
      │      "display_name": "..."     │                           │
      │    },                          │                           │
      │    "access": "eyJhbGc...",     │                           │
      │    "refresh": "eyJhbGc..."     │                           │
      │  }                             │                           │
      │<───────────────────────────────┤                           │
      │                                │                           │
      │ Save tokens to secure storage  │                           │
      │ Navigate to home screen        │                           │
      │                                │                           │
```

**Validation Rules**:
- Email: Valid format, unique (case-insensitive)
- Password: Min 8 chars, must contain uppercase, lowercase, number
- Display name: 2-50 chars, không chứa ký tự đặc biệt

**Error Responses**:
- `400 Bad Request` — Validation failed
  ```json
  {
    "email": ["This email is already registered."],
    "password": ["Password must be at least 8 characters."]
  }
  ```

---

### 2. Login Flow

```
User (Mobile App)                 Backend API                 Cosmos DB
      │                                │                           │
      │  POST /auth/login/             │                           │
      │  {                             │                           │
      │    "email": "user@example.com",│                           │
      │    "password": "StrongPass123" │                           │
      │  }                             │                           │
      ├───────────────────────────────>│                           │
      │                                │ Find user by email        │
      │                                ├──────────────────────────>│
      │                                │  Query: email = "..."     │
      │                                │<──────────────────────────┤
      │                                │  Result: User object      │
      │                                │                           │
      │                                │ Verify password           │
      │                                │  bcrypt.checkpw(          │
      │                                │    input_password,        │
      │                                │    stored_hash            │
      │                                │  )                        │
      │                                │                           │
      │                                │ Check user status         │
      │                                │  if status != "active":   │
      │                                │    raise Forbidden        │
      │                                │                           │
      │                                │ Generate JWT tokens       │
      │                                │  Payload: {               │
      │                                │    user_id: "...",        │
      │                                │    email: "...",          │
      │                                │    exp: now() + 1h        │
      │                                │  }                        │
      │                                │                           │
      │  200 OK                        │                           │
      │  {                             │                           │
      │    "user": {                   │                           │
      │      "id": "...",              │                           │
      │      "email": "...",           │                           │
      │      "display_name": "..."     │                           │
      │    },                          │                           │
      │    "access": "eyJhbGc...",     │                           │
      │    "refresh": "eyJhbGc..."     │                           │
      │  }                             │                           │
      │<───────────────────────────────┤                           │
      │                                │                           │
      │ Save tokens to secure storage  │                           │
      │ Navigate to home screen        │                           │
      │                                │                           │
```

**Error Responses**:
- `401 Unauthorized` — Invalid credentials
  ```json
  { "detail": "Email hoặc mật khẩu không đúng." }
  ```
- `403 Forbidden` — Account suspended
  ```json
  { "detail": "Tài khoản đã bị tạm khóa." }
  ```

---

### 3. Token Refresh Flow

```
Mobile App                        Backend API
      │                                │
      │ Access token expired (401)     │
      │ Detected by Dio interceptor    │
      │                                │
      │ POST /auth/refresh/            │
      │ {                              │
      │   "refresh": "eyJhbGc..."      │
      │ }                              │
      ├───────────────────────────────>│
      │                                │ Verify refresh token
      │                                │  - Check signature
      │                                │  - Check expiration
      │                                │  - Check not blacklisted
      │                                │
      │                                │ Generate new access token
      │                                │ (Optional) Rotate refresh token
      │                                │
      │ 200 OK                         │
      │ {                              │
      │   "access": "new_access_token",│
      │   "refresh": "new_refresh_tok" │
      │ }                              │
      │<───────────────────────────────┤
      │                                │
      │ Save new tokens                │
      │ Retry original request         │
      │                                │
```

**Token Rotation** (recommended):
- Mỗi lần refresh, issue new refresh token
- Blacklist old refresh token (stored in Cosmos DB)
- Prevents token reuse attacks

---

### 4. Logout Flow

```
Mobile App                        Backend API                 Cosmos DB
      │                                │                           │
      │ POST /auth/logout/             │                           │
      │ Authorization: Bearer <token>  │                           │
      ├───────────────────────────────>│                           │
      │                                │ Extract user_id from token│
      │                                │                           │
      │                                │ Blacklist refresh token   │
      │                                ├──────────────────────────>│
      │                                │  Create blacklist entry   │
      │                                │  {                        │
      │                                │    token: "refresh_token",│
      │                                │    user_id: "...",        │
      │                                │    expires_at: 7d from now│
      │                                │  }                        │
      │                                │<──────────────────────────┤
      │                                │                           │
      │ 204 No Content                 │                           │
      │<───────────────────────────────┤                           │
      │                                │                           │
      │ Delete tokens from local storage│                          │
      │ Navigate to login screen       │                           │
      │                                │                           │
```

**Note**: Access tokens cannot be revoked (stateless). They expire naturally after 1 hour.

---

### 5. Protected API Request Flow

```
Mobile App                        Backend API                 Cosmos DB
      │                                │                           │
      │ GET /api/products/             │                           │
      │ Authorization: Bearer <access> │                           │
      ├───────────────────────────────>│                           │
      │                                │ JWT Middleware            │
      │                                │  - Verify token signature │
      │                                │  - Check expiration       │
      │                                │  - Decode payload:        │
      │                                │    {                      │
      │                                │      user_id: "...",      │
      │                                │      email: "...",        │
      │                                │      exp: 1234567890      │
      │                                │    }                      │
      │                                │                           │
      │                                │ Fetch user (optional)     │
      │                                ├──────────────────────────>│
      │                                │  Get user by ID           │
      │                                │<──────────────────────────┤
      │                                │  User object              │
      │                                │                           │
      │                                │ Attach user to request    │
      │                                │  request.user = user_obj  │
      │                                │                           │
      │                                │ ProductListView           │
      │                                │  user_id = request.user.id│
      │                                │  Query products           │
      │                                ├──────────────────────────>│
      │                                │  Filter: user_id = "..."  │
      │                                │<──────────────────────────┤
      │                                │  Products list            │
      │                                │                           │
      │ 200 OK                         │                           │
      │ { "results": [...] }           │                           │
      │<───────────────────────────────┤                           │
      │                                │                           │
```

**Error Handling**:
- Missing token → `401 Unauthorized`
- Invalid token → `401 Unauthorized`
- Expired token → `401 Unauthorized` (trigger refresh)
- User not found → `401 Unauthorized`
- User suspended → `403 Forbidden`

---

## Data Models

### User Model

**Cosmos DB Container**: `users`  
**Partition Key**: `/id` (user ID)

```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from apps.core.models import BaseDocument

@dataclass
class User(BaseDocument):
    """User account for authentication."""
    
    # Inherited from BaseDocument:
    # - id: str (UUID)
    # - created_at: str (ISO datetime)
    # - updated_at: str (ISO datetime)
    
    email: str                    # Unique, lowercase, validated
    password_hash: str            # bcrypt hash
    display_name: str             # User's display name
    
    status: str = "active"        # active | suspended | deleted
    email_verified: bool = False  # For future email verification
    
    # Optional fields
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    
    # Metadata
    last_login_at: Optional[str] = None
    login_count: int = 0
    
    def to_dict(self) -> dict:
        """Convert to dict for Cosmos DB."""
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

### Token Blacklist Model

**Cosmos DB Container**: `token_blacklist`  
**Partition Key**: `/user_id`  
**TTL**: Set to token expiration (auto-delete expired tokens)

```python
@dataclass
class TokenBlacklist(BaseDocument):
    """Blacklisted refresh tokens (for logout)."""
    
    user_id: str          # Partition key
    token: str            # Refresh token hash
    expires_at: str       # ISO datetime
    reason: str = "logout"  # logout | password_change | security
```

---

## Backend Implementation

### Install Dependencies

```bash
pip install djangorestframework-simplejwt bcrypt
```

**requirements.txt**:
```txt
djangorestframework-simplejwt==5.3.1
bcrypt==4.1.2
```

### Django Settings

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
    'ROTATE_REFRESH_TOKENS': True,  # Issue new refresh token on refresh
    'BLACKLIST_AFTER_ROTATION': True,  # Blacklist old refresh token
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```

### User Serializers

**apps/users/serializers.py**:
```python
from rest_framework import serializers
import re
import bcrypt

class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, max_length=128, write_only=True)
    display_name = serializers.CharField(min_length=2, max_length=50)
    
    def validate_email(self, value):
        """Normalize email to lowercase."""
        value = value.lower().strip()
        
        # Check if email already exists
        from apps.users.services import UserService
        if UserService.exists_by_email(value):
            raise serializers.ValidationError("Email này đã được đăng ký.")
        
        return value
    
    def validate_password(self, value):
        """Validate password strength."""
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Mật khẩu phải chứa ít nhất 1 chữ hoa.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Mật khẩu phải chứa ít nhất 1 chữ thường.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Mật khẩu phải chứa ít nhất 1 số.")
        return value
    
    def validate_display_name(self, value):
        """Validate display name."""
        value = value.strip()
        
        # Allow Vietnamese characters, spaces, basic punctuation
        if not re.match(r'^[a-zA-ZÀ-ỹ\s\.]+$', value):
            raise serializers.ValidationError("Tên hiển thị chỉ được chứa chữ cái và khoảng trắng.")
        
        return value


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.Serializer):
    """User response serializer (safe, no password)."""
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
    
    def validate_new_password(self, value):
        # Same validation as registration
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Mật khẩu phải chứa ít nhất 1 chữ hoa.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Mật khẩu phải chứa ít nhất 1 chữ thường.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Mật khẩu phải chứa ít nhất 1 số.")
        return value
```

### User Service

**apps/users/services.py**:
```python
import bcrypt
import uuid
from datetime import datetime
from typing import Optional
from apps.core.cosmos_service import CosmosDBService
from apps.users.models import User
from apps.core.exceptions import ValidationError, NotFoundError, AuthenticationError

class UserService:
    """User management service."""
    
    CONTAINER = 'users'
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    @staticmethod
    def exists_by_email(email: str) -> bool:
        """Check if email already registered."""
        query = f"SELECT c.id FROM c WHERE c.email = @email"
        params = [{"name": "@email", "value": email.lower()}]
        
        items = CosmosDBService.query(UserService.CONTAINER, query, params)
        return len(items) > 0
    
    @staticmethod
    def create(email: str, password: str, display_name: str) -> User:
        """Register new user."""
        email = email.lower().strip()
        
        # Double-check email uniqueness
        if UserService.exists_by_email(email):
            raise ValidationError("Email đã được đăng ký.")
        
        # Create user object
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
        
        # Save to Cosmos DB
        CosmosDBService.create(UserService.CONTAINER, user.to_dict(), partition_key=user.id)
        
        return user
    
    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        """Find user by email."""
        query = f"SELECT * FROM c WHERE c.email = @email"
        params = [{"name": "@email", "value": email.lower()}]
        
        items = CosmosDBService.query(UserService.CONTAINER, query, params)
        
        if not items:
            return None
        
        return User(**items[0])
    
    @staticmethod
    def get_by_id(user_id: str) -> User:
        """Get user by ID."""
        item = CosmosDBService.get(UserService.CONTAINER, user_id, partition_key=user_id)
        
        if not item:
            raise NotFoundError("User không tồn tại.")
        
        return User(**item)
    
    @staticmethod
    def authenticate(email: str, password: str) -> User:
        """Authenticate user with email/password."""
        user = UserService.get_by_email(email)
        
        if not user:
            raise AuthenticationError("Email hoặc mật khẩu không đúng.")
        
        if not UserService.verify_password(password, user.password_hash):
            raise AuthenticationError("Email hoặc mật khẩu không đúng.")
        
        if user.status != 'active':
            raise AuthenticationError("Tài khoản đã bị tạm khóa.")
        
        # Update last login
        user.last_login_at = datetime.utcnow().isoformat()
        user.login_count += 1
        user.updated_at = datetime.utcnow().isoformat()
        
        CosmosDBService.update(
            UserService.CONTAINER,
            user.id,
            user.to_dict(),
            partition_key=user.id
        )
        
        return user
    
    @staticmethod
    def change_password(user_id: str, old_password: str, new_password: str) -> None:
        """Change user password."""
        user = UserService.get_by_id(user_id)
        
        # Verify old password
        if not UserService.verify_password(old_password, user.password_hash):
            raise AuthenticationError("Mật khẩu hiện tại không đúng.")
        
        # Update password
        user.password_hash = UserService.hash_password(new_password)
        user.updated_at = datetime.utcnow().isoformat()
        
        CosmosDBService.update(
            UserService.CONTAINER,
            user.id,
            user.to_dict(),
            partition_key=user.id
        )
        
        # TODO: Blacklist all refresh tokens for this user
```

### Auth Views

**apps/users/views.py**:
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    ChangePasswordSerializer,
)
from apps.users.services import UserService
from apps.core.exceptions import ValidationError, AuthenticationError

class RegisterView(APIView):
    """User registration endpoint."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create user
        user = UserService.create(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            display_name=serializer.validated_data['display_name'],
        )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': user.to_response(),
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """User login endpoint."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Authenticate
        user = UserService.authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
        )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': user.to_response(),
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


class LogoutView(APIView):
    """User logout endpoint (blacklist refresh token)."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass  # Silent fail, already logged out
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    """Get current user profile."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = UserService.get_by_id(request.user.id)
        return Response(user.to_response())


class ChangePasswordView(APIView):
    """Change password for authenticated user."""
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

### URLs

**apps/users/urls.py**:
```python
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.users.views import (
    RegisterView,
    LoginView,
    LogoutView,
    MeView,
    ChangePasswordView,
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
]
```

### Custom JWT Claims

**apps/users/serializers.py** (add this):
```python
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT serializer to add user data to token."""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['display_name'] = user.display_name
        
        return token
```

---

## Mobile Implementation (Flutter)

### Dependencies

**pubspec.yaml**:
```yaml
dependencies:
  flutter_secure_storage: ^9.0.0  # Secure token storage
  dio: ^5.4.0
  riverpod: ^2.4.0
```

### Token Storage

**lib/core/services/token_storage.dart**:
```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class TokenStorage {
  static const _storage = FlutterSecureStorage();
  
  static const _accessTokenKey = 'access_token';
  static const _refreshTokenKey = 'refresh_token';
  
  static Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    await Future.wait([
      _storage.write(key: _accessTokenKey, value: accessToken),
      _storage.write(key: _refreshTokenKey, value: refreshToken),
    ]);
  }
  
  static Future<String?> getAccessToken() async {
    return await _storage.read(key: _accessTokenKey);
  }
  
  static Future<String?> getRefreshToken() async {
    return await _storage.read(key: _refreshTokenKey);
  }
  
  static Future<void> deleteTokens() async {
    await Future.wait([
      _storage.delete(key: _accessTokenKey),
      _storage.delete(key: _refreshTokenKey),
    ]);
  }
  
  static Future<bool> hasTokens() async {
    final accessToken = await getAccessToken();
    return accessToken != null;
  }
}
```

### Auth Repository

**lib/features/auth/data/auth_repository.dart**:
```dart
import 'package:dio/dio.dart';
import '../../../core/services/token_storage.dart';

class AuthRepository {
  final Dio _dio;
  
  AuthRepository(this._dio);
  
  Future<AuthResponse> register({
    required String email,
    required String password,
    required String displayName,
  }) async {
    final response = await _dio.post(
      '/auth/register/',
      data: {
        'email': email,
        'password': password,
        'display_name': displayName,
      },
    );
    
    final authResponse = AuthResponse.fromJson(response.data);
    
    // Save tokens
    await TokenStorage.saveTokens(
      accessToken: authResponse.access,
      refreshToken: authResponse.refresh,
    );
    
    return authResponse;
  }
  
  Future<AuthResponse> login({
    required String email,
    required String password,
  }) async {
    final response = await _dio.post(
      '/auth/login/',
      data: {
        'email': email,
        'password': password,
      },
    );
    
    final authResponse = AuthResponse.fromJson(response.data);
    
    await TokenStorage.saveTokens(
      accessToken: authResponse.access,
      refreshToken: authResponse.refresh,
    );
    
    return authResponse;
  }
  
  Future<void> logout() async {
    final refreshToken = await TokenStorage.getRefreshToken();
    
    try {
      await _dio.post(
        '/auth/logout/',
        data: {'refresh': refreshToken},
      );
    } catch (e) {
      // Ignore errors, delete local tokens anyway
    }
    
    await TokenStorage.deleteTokens();
  }
  
  Future<User> getCurrentUser() async {
    final response = await _dio.get('/auth/me/');
    return User.fromJson(response.data);
  }
}

class AuthResponse {
  final User user;
  final String access;
  final String refresh;
  
  AuthResponse({
    required this.user,
    required this.access,
    required this.refresh,
  });
  
  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      user: User.fromJson(json['user']),
      access: json['access'],
      refresh: json['refresh'],
    );
  }
}

class User {
  final String id;
  final String email;
  final String displayName;
  final String status;
  final bool emailVerified;
  
  User({
    required this.id,
    required this.email,
    required this.displayName,
    required this.status,
    required this.emailVerified,
  });
  
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      email: json['email'],
      displayName: json['display_name'],
      status: json['status'],
      emailVerified: json['email_verified'],
    );
  }
}
```

### Auth State Provider (Riverpod)

**lib/features/auth/domain/auth_provider.dart**:
```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/auth_repository.dart';
import '../../../core/services/token_storage.dart';

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  final dio = ref.watch(dioProvider);
  return AuthRepository(dio);
});

final authStateProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.watch(authRepositoryProvider));
});

class AuthNotifier extends StateNotifier<AuthState> {
  final AuthRepository _repository;
  
  AuthNotifier(this._repository) : super(const AuthState.initial()) {
    _checkAuthStatus();
  }
  
  Future<void> _checkAuthStatus() async {
    state = const AuthState.loading();
    
    final hasTokens = await TokenStorage.hasTokens();
    
    if (hasTokens) {
      try {
        final user = await _repository.getCurrentUser();
        state = AuthState.authenticated(user);
      } catch (e) {
        // Token invalid, logout
        await TokenStorage.deleteTokens();
        state = const AuthState.unauthenticated();
      }
    } else {
      state = const AuthState.unauthenticated();
    }
  }
  
  Future<void> register({
    required String email,
    required String password,
    required String displayName,
  }) async {
    state = const AuthState.loading();
    
    try {
      final response = await _repository.register(
        email: email,
        password: password,
        displayName: displayName,
      );
      
      state = AuthState.authenticated(response.user);
    } catch (e) {
      state = AuthState.error(e.toString());
    }
  }
  
  Future<void> login({
    required String email,
    required String password,
  }) async {
    state = const AuthState.loading();
    
    try {
      final response = await _repository.login(
        email: email,
        password: password,
      );
      
      state = AuthState.authenticated(response.user);
    } catch (e) {
      state = AuthState.error(e.toString());
    }
  }
  
  Future<void> logout() async {
    await _repository.logout();
    state = const AuthState.unauthenticated();
  }
}

class AuthState {
  final AuthStatus status;
  final User? user;
  final String? errorMessage;
  
  const AuthState({
    required this.status,
    this.user,
    this.errorMessage,
  });
  
  const AuthState.initial() : this(status: AuthStatus.initial);
  const AuthState.loading() : this(status: AuthStatus.loading);
  const AuthState.authenticated(User user) : this(status: AuthStatus.authenticated, user: user);
  const AuthState.unauthenticated() : this(status: AuthStatus.unauthenticated);
  const AuthState.error(String message) : this(status: AuthStatus.error, errorMessage: message);
}

enum AuthStatus { initial, loading, authenticated, unauthenticated, error }
```

### Dio Interceptor (Auto Token Refresh)

**lib/core/dio_client.dart**:
```dart
import 'package:dio/dio.dart';
import 'services/token_storage.dart';

Dio createDio() {
  final dio = Dio(
    BaseOptions(
      baseUrl: 'https://app-shopee-aff-dev.azurewebsites.net/api',
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
    ),
  );
  
  // Request interceptor: Add auth header
  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) async {
        final accessToken = await TokenStorage.getAccessToken();
        
        if (accessToken != null) {
          options.headers['Authorization'] = 'Bearer $accessToken';
        }
        
        return handler.next(options);
      },
      onError: (error, handler) async {
        // Handle 401 Unauthorized (token expired)
        if (error.response?.statusCode == 401) {
          final refreshToken = await TokenStorage.getRefreshToken();
          
          if (refreshToken != null) {
            try {
              // Refresh token
              final response = await dio.post(
                '/auth/refresh/',
                data: {'refresh': refreshToken},
              );
              
              final newAccessToken = response.data['access'];
              final newRefreshToken = response.data['refresh'];
              
              // Save new tokens
              await TokenStorage.saveTokens(
                accessToken: newAccessToken,
                refreshToken: newRefreshToken,
              );
              
              // Retry original request with new token
              final options = error.requestOptions;
              options.headers['Authorization'] = 'Bearer $newAccessToken';
              
              final retryResponse = await dio.fetch(options);
              return handler.resolve(retryResponse);
              
            } catch (e) {
              // Refresh failed, logout
              await TokenStorage.deleteTokens();
              // Navigate to login screen
              return handler.next(error);
            }
          }
        }
        
        return handler.next(error);
      },
    ),
  );
  
  return dio;
}
```

### Login Screen

**lib/features/auth/presentation/login_screen.dart**:
```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/auth_provider.dart';
import 'package:go_router/go_router.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});
  
  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  
  bool _isPasswordVisible = false;
  
  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }
  
  void _login() async {
    if (_formKey.currentState!.validate()) {
      await ref.read(authStateProvider.notifier).login(
        email: _emailController.text.trim(),
        password: _passwordController.text,
      );
      
      final authState = ref.read(authStateProvider);
      
      if (authState.status == AuthStatus.authenticated) {
        context.go('/home');
      } else if (authState.status == AuthStatus.error) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(authState.errorMessage ?? 'Đăng nhập thất bại')),
        );
      }
    }
  }
  
  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authStateProvider);
    final isLoading = authState.status == AuthStatus.loading;
    
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Logo
                const Icon(
                  Icons.shopping_bag,
                  size: 80,
                  color: Color(0xFFEE4D2D),
                ),
                const SizedBox(height: 32),
                
                // Title
                Text(
                  'Đăng nhập',
                  style: Theme.of(context).textTheme.headlineMedium,
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 32),
                
                // Email field
                TextFormField(
                  controller: _emailController,
                  decoration: const InputDecoration(
                    labelText: 'Email',
                    prefixIcon: Icon(Icons.email),
                  ),
                  keyboardType: TextInputType.emailAddress,
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Vui lòng nhập email';
                    }
                    if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) {
                      return 'Email không hợp lệ';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                
                // Password field
                TextFormField(
                  controller: _passwordController,
                  decoration: InputDecoration(
                    labelText: 'Mật khẩu',
                    prefixIcon: const Icon(Icons.lock),
                    suffixIcon: IconButton(
                      icon: Icon(
                        _isPasswordVisible ? Icons.visibility_off : Icons.visibility,
                      ),
                      onPressed: () {
                        setState(() {
                          _isPasswordVisible = !_isPasswordVisible;
                        });
                      },
                    ),
                  ),
                  obscureText: !_isPasswordVisible,
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Vui lòng nhập mật khẩu';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 24),
                
                // Login button
                ElevatedButton(
                  onPressed: isLoading ? null : _login,
                  child: isLoading
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Đăng nhập'),
                ),
                const SizedBox(height: 16),
                
                // Register link
                TextButton(
                  onPressed: () {
                    context.push('/register');
                  },
                  child: const Text('Chưa có tài khoản? Đăng ký ngay'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
```

### Auth Guard (Router)

**lib/core/router.dart**:
```dart
import 'package:go_router/go_router.dart';
import '../features/auth/presentation/login_screen.dart';
import '../features/auth/presentation/register_screen.dart';
import '../features/auth/domain/auth_provider.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authStateProvider);
  
  return GoRouter(
    initialLocation: '/login',
    redirect: (context, state) {
      final isAuthenticated = authState.status == AuthStatus.authenticated;
      final isLoading = authState.status == AuthStatus.loading;
      
      final isLoginRoute = state.matchedLocation == '/login' || 
                          state.matchedLocation == '/register';
      
      if (isLoading) {
        return '/splash';  // Show splash screen while checking auth
      }
      
      if (!isAuthenticated && !isLoginRoute) {
        return '/login';  // Redirect to login if not authenticated
      }
      
      if (isAuthenticated && isLoginRoute) {
        return '/home';  // Redirect to home if already logged in
      }
      
      return null;  // No redirect
    },
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/register',
        builder: (context, state) => const RegisterScreen(),
      ),
      GoRoute(
        path: '/home',
        builder: (context, state) => const HomeScreen(),
      ),
      // ... other routes
    ],
  );
});
```

---

## Security Best Practices

### 1. Password Security
- ✅ Use bcrypt (slow, prevents brute force)
- ✅ Min 8 chars, complexity requirements
- ✅ Never log passwords
- ✅ Hash on backend, never send plaintext

### 2. Token Security
- ✅ Short-lived access tokens (1 hour)
- ✅ Longer refresh tokens (7 days)
- ✅ Rotate refresh tokens on use
- ✅ Blacklist on logout
- ✅ Store in FlutterSecureStorage (encrypted)
- ✅ Use HTTPS only

### 3. API Security
- ✅ Require authentication by default
- ✅ Rate limiting (future)
- ✅ Input validation
- ✅ CORS whitelist
- ✅ Don't expose user_id in URLs (use JWT user_id)

### 4. Data Isolation
- ✅ Filter all queries by user_id from JWT
- ✅ Never trust client-provided user_id
- ✅ Partition Cosmos DB by user_id for performance

---

## Testing

### Backend Tests

**tests/test_auth.py**:
```python
from django.test import TestCase
from apps.users.services import UserService
from apps.core.exceptions import ValidationError, AuthenticationError

class UserServiceTest(TestCase):
    def test_create_user_success(self):
        user = UserService.create(
            email='test@example.com',
            password='Password123',
            display_name='Test User',
        )
        
        self.assertIsNotNone(user.id)
        self.assertEqual(user.email, 'test@example.com')
        self.assertNotEqual(user.password_hash, 'Password123')  # Hashed
    
    def test_create_user_duplicate_email(self):
        UserService.create('test@example.com', 'Password123', 'User 1')
        
        with self.assertRaises(ValidationError):
            UserService.create('test@example.com', 'Password123', 'User 2')
    
    def test_authenticate_success(self):
        UserService.create('test@example.com', 'Password123', 'Test User')
        
        user = UserService.authenticate('test@example.com', 'Password123')
        
        self.assertEqual(user.email, 'test@example.com')
    
    def test_authenticate_wrong_password(self):
        UserService.create('test@example.com', 'Password123', 'Test User')
        
        with self.assertRaises(AuthenticationError):
            UserService.authenticate('test@example.com', 'WrongPassword')
```

### Mobile Tests

**test/features/auth/auth_provider_test.dart**:
```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';

void main() {
  group('AuthNotifier', () {
    test('login success updates state to authenticated', () async {
      // Mock repository
      final mockRepo = MockAuthRepository();
      when(mockRepo.login(email: 'test@example.com', password: 'Password123'))
          .thenAnswer((_) async => AuthResponse(...));
      
      final notifier = AuthNotifier(mockRepo);
      
      await notifier.login(email: 'test@example.com', password: 'Password123');
      
      expect(notifier.state.status, AuthStatus.authenticated);
    });
  });
}
```

---

## Future Enhancements

### Email Verification
- Send verification email on registration
- Require email confirmation before full access

### Social Login
- Google Sign-In
- Facebook Login
- Apple Sign-In

### Two-Factor Authentication (2FA)
- SMS OTP
- Authenticator app (TOTP)

### Password Reset
- Forgot password flow
- Email reset link
- Security questions

### Account Management
- Update profile (avatar, display name)
- Delete account
- View login history

---

## Monitoring

### Metrics to Track
- Registration rate
- Login success/failure rate
- Token refresh rate
- Password change frequency
- Account suspension events

### Alerts
- High login failure rate (possible attack)
- Unusual registration spike (possible bots)
- Token blacklist growing too fast

---

**Last updated**: 2026-05-06
**Status**: Planning complete, ready for implementation
**Dependencies**: Cosmos DB, django-rest-framework-simplejwt, bcrypt, flutter_secure_storage
