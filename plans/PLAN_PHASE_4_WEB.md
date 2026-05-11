---
title: Phase 4 — Web Frontend (Laravel)
version: 2.0.0
updated: 2026-05-08
---

# Phase 4: Web Frontend (Laravel + Blade)

## Goals
- Web app với design system giống hệt mobile app
- Laravel với Blade templates + HTML/CSS/JS thuần
- Shopee Orange theme
- Các màn hình: Auth, Product List, Add Link, Search, Product Detail
- Kết nối với Django backend API qua HTTP client

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Laravel 13 | PHP Framework |
| Blade | Template engine |
| Bootstrap 5.3 | CSS framework (hoặc TailwindCSS) |
| Vanilla JS | Interactivity (không framework) |
| Axios (CDN) | HTTP client |
| Laravel HTTP Client | Backend API calls (Guzzle wrapper) |

---

## Kiến trúc

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure Web App (PHP)                      │
│                         Laravel                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Browser Request                                            │
│       ↓                                                     │
│  Laravel Routes → Controllers → Views (Blade)              │
│       ↓                                                     │
│  API Calls (Guzzle/HTTP Client)                            │
│       ↓                                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Django Backend API (Python)               │   │
│  │           (Separate Azure Web App)                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 4.1 — Scaffold Laravel Project

### 4.1.1 Tạo project

```powershell
# Từ C:\Projects\affiliates_management\
composer create-project laravel/laravel frontend
cd frontend
```

### 4.1.2 Cấu trúc thư mục

```
frontend/
├── app/
│   ├── Http/
│   │   ├── Controllers/
│   │   │   ├── AuthController.php
│   │   │   ├── ProductController.php
│   │   │   ├── LinkController.php
│   │   │   └── SearchController.php
│   │   └── Middleware/
│   │       └── EnsureTokenIsValid.php
│   └── Services/
│       └── ApiService.php          # HTTP client wrapper
├── resources/
│   ├── views/
│   │   ├── layouts/
│   │   │   ├── app.blade.php       # Main layout
│   │   │   └── auth.blade.php      # Auth layout (no sidebar)
│   │   ├── components/
│   │   │   ├── sidebar.blade.php
│   │   │   ├── header.blade.php
│   │   │   ├── product-card.blade.php
│   │   │   └── alert.blade.php
│   │   ├── auth/
│   │   │   ├── login.blade.php
│   │   │   └── register.blade.php
│   │   ├── products/
│   │   │   ├── index.blade.php
│   │   │   └── show.blade.php
│   │   ├── links/
│   │   │   └── create.blade.php
│   │   └── search/
│   │       └── index.blade.php
│   ├── css/
│   │   └── app.css                 # Custom styles
│   └── js/
│       └── app.js                  # Vanilla JS
├── public/
│   ├── css/
│   ├── js/
│   └── images/
├── routes/
│   └── web.php
├── .env
└── composer.json
```

### 4.1.3 Environment Configuration

**`.env`**:
```env
APP_NAME="Shopee Aff Manager"
APP_ENV=local
APP_KEY=base64:...
APP_DEBUG=true
APP_URL=http://localhost:8080

# Django Backend API
API_BASE_URL=http://localhost:8000/api
API_TIMEOUT=30
```

---

## Step 4.2 — Theme & Design System

### 4.2.1 CSS Variables (Shopee Theme)

**`resources/css/app.css`**:
```css
:root {
  /* Primary - Shopee Orange */
  --color-primary: #EE4D2D;
  --color-primary-dark: #D83E1F;
  --color-primary-light: #FF6F3D;
  
  /* Secondary - Teal */
  --color-secondary: #00BFA5;
  --color-secondary-dark: #00897B;
  
  /* Backgrounds */
  --color-bg: #F5F5F5;
  --color-surface: #FFFFFF;
  --color-surface-dark: #1E1E1E;
  
  /* Text */
  --color-text-primary: #212121;
  --color-text-secondary: #757575;
  --color-text-hint: #BDBDBD;
  
  /* Status */
  --color-success: #4CAF50;
  --color-error: #F44336;
  --color-warning: #FF9800;
  --color-info: #2196F3;
  
  /* Spacing (8pt grid) */
  --space-1: 0.25rem;  /* 4px */
  --space-2: 0.5rem;   /* 8px */
  --space-3: 0.75rem;  /* 12px */
  --space-4: 1rem;     /* 16px */
  --space-6: 1.5rem;   /* 24px */
  --space-8: 2rem;     /* 32px */
  
  /* Border radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  
  /* Shadows */
  --shadow-card: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.08);
  --shadow-card-hover: 0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06);
}

/* Font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body {
  font-family: 'Inter', system-ui, sans-serif;
  background-color: var(--color-bg);
  color: var(--color-text-primary);
}

/* Buttons */
.btn-primary {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.btn-primary:hover {
  background-color: var(--color-primary-dark);
  border-color: var(--color-primary-dark);
}

.btn-outline-primary {
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.btn-outline-primary:hover {
  background-color: var(--color-primary);
  color: white;
}

/* Cards */
.card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  border: none;
}

.card:hover {
  box-shadow: var(--shadow-card-hover);
}

/* Form inputs */
.form-control:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 0.2rem rgba(238, 77, 45, 0.25);
}

/* Sidebar */
.sidebar {
  background: var(--color-surface);
  width: 260px;
  min-height: 100vh;
  border-right: 1px solid #E0E0E0;
}

.sidebar .nav-link {
  color: var(--color-text-secondary);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  margin: var(--space-1) var(--space-2);
}

.sidebar .nav-link:hover {
  background-color: var(--color-bg);
}

.sidebar .nav-link.active {
  background-color: var(--color-primary);
  color: white;
}

/* Product card */
.product-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.product-card:hover {
  transform: translateY(-2px);
}

.product-card .product-image {
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: var(--radius-md) var(--radius-md) 0 0;
}

.product-card .product-price {
  color: var(--color-primary);
  font-weight: 700;
  font-size: 1.25rem;
}

/* Badge status */
.badge-pending { background-color: var(--color-warning); }
.badge-processing { background-color: var(--color-info); }
.badge-done { background-color: var(--color-success); }
.badge-failed { background-color: var(--color-error); }

/* Loading spinner */
.spinner-shopee {
  color: var(--color-primary);
}
```

---

## Step 4.3 — API Service

### 4.3.1 HTTP Client Wrapper

**`app/Services/ApiService.php`**:
```php
<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Http\Client\Response;
use Illuminate\Http\Client\RequestException;

class ApiService
{
    protected string $baseUrl;
    protected int $timeout;

    public function __construct()
    {
        $this->baseUrl = config('services.api.base_url');
        $this->timeout = config('services.api.timeout', 30);
    }

    /**
     * Make authenticated request to Django API
     */
    protected function request(): \Illuminate\Http\Client\PendingRequest
    {
        $request = Http::baseUrl($this->baseUrl)
            ->timeout($this->timeout)
            ->acceptJson();

        // Add JWT token if exists
        $token = session('access_token');
        if ($token) {
            $request->withToken($token);
        }

        return $request;
    }

    /**
     * Handle token refresh on 401
     */
    protected function handleUnauthorized(): bool
    {
        $refreshToken = session('refresh_token');
        if (!$refreshToken) {
            return false;
        }

        try {
            $response = Http::baseUrl($this->baseUrl)
                ->post('/auth/refresh/', ['refresh' => $refreshToken]);

            if ($response->successful()) {
                session(['access_token' => $response->json('access')]);
                return true;
            }
        } catch (\Exception $e) {
            // Refresh failed
        }

        // Clear tokens and redirect to login
        session()->forget(['access_token', 'refresh_token', 'user']);
        return false;
    }

    // ============ AUTH ============

    public function register(array $data): array
    {
        $response = $this->request()->post('/auth/register/', $data);
        
        if ($response->successful()) {
            $this->storeTokens($response->json());
        }
        
        return $this->handleResponse($response);
    }

    public function login(string $email, string $password): array
    {
        $response = $this->request()->post('/auth/login/', [
            'email' => $email,
            'password' => $password,
        ]);
        
        if ($response->successful()) {
            $this->storeTokens($response->json());
        }
        
        return $this->handleResponse($response);
    }

    public function logout(): void
    {
        try {
            $this->request()->post('/auth/logout/', [
                'refresh' => session('refresh_token'),
            ]);
        } catch (\Exception $e) {
            // Ignore errors
        }
        
        session()->forget(['access_token', 'refresh_token', 'user']);
    }

    public function getCurrentUser(): ?array
    {
        $response = $this->request()->get('/auth/me/');
        
        if ($response->status() === 401 && $this->handleUnauthorized()) {
            $response = $this->request()->get('/auth/me/');
        }
        
        return $response->successful() ? $response->json() : null;
    }

    protected function storeTokens(array $data): void
    {
        session([
            'access_token' => $data['access'],
            'refresh_token' => $data['refresh'],
            'user' => $data['user'],
        ]);
    }

    // ============ PRODUCTS ============

    public function getProducts(int $page = 1, int $pageSize = 20): array
    {
        $response = $this->request()->get('/products/', [
            'page' => $page,
            'page_size' => $pageSize,
        ]);
        
        if ($response->status() === 401 && $this->handleUnauthorized()) {
            $response = $this->request()->get('/products/', [
                'page' => $page,
                'page_size' => $pageSize,
            ]);
        }
        
        return $this->handleResponse($response);
    }

    public function getProduct(string $id): array
    {
        $response = $this->request()->get("/products/{$id}/");
        
        if ($response->status() === 401 && $this->handleUnauthorized()) {
            $response = $this->request()->get("/products/{$id}/");
        }
        
        return $this->handleResponse($response);
    }

    public function deleteProduct(string $id, string $shopId): array
    {
        $response = $this->request()->delete("/products/{$id}/", [
            'shop_id' => $shopId,
        ]);
        
        return $this->handleResponse($response);
    }

    // ============ LINKS ============

    public function createLink(string $url): array
    {
        $response = $this->request()->post('/links/', ['url' => $url]);
        
        if ($response->status() === 401 && $this->handleUnauthorized()) {
            $response = $this->request()->post('/links/', ['url' => $url]);
        }
        
        return $this->handleResponse($response);
    }

    public function getLink(string $id): array
    {
        $response = $this->request()->get("/links/{$id}/");
        
        return $this->handleResponse($response);
    }

    // ============ SEARCH ============

    public function search(string $query, array $filters = []): array
    {
        $params = array_merge(['q' => $query], $filters);
        $response = $this->request()->get('/search/', $params);
        
        if ($response->status() === 401 && $this->handleUnauthorized()) {
            $response = $this->request()->get('/search/', $params);
        }
        
        return $this->handleResponse($response);
    }

    // ============ HELPERS ============

    protected function handleResponse(Response $response): array
    {
        if ($response->successful()) {
            return [
                'success' => true,
                'data' => $response->json(),
            ];
        }

        return [
            'success' => false,
            'error' => $response->json('detail') ?? 'Có lỗi xảy ra',
            'status' => $response->status(),
        ];
    }
}
```

### 4.3.2 Service Configuration

**`config/services.php`** (thêm):
```php
return [
    // ... existing services

    'api' => [
        'base_url' => env('API_BASE_URL', 'http://localhost:8000/api'),
        'timeout' => env('API_TIMEOUT', 30),
    ],
];
```

### 4.3.3 Service Provider

**`app/Providers/AppServiceProvider.php`** (update):
```php
<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;
use App\Services\ApiService;

class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        $this->app->singleton(ApiService::class, function ($app) {
            return new ApiService();
        });
    }

    public function boot(): void
    {
        //
    }
}
```

---

## Step 4.4 — Middleware (Auth Guard)

### 4.4.1 Auth Middleware

**`app/Http/Middleware/EnsureTokenIsValid.php`**:
```php
<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use App\Services\ApiService;
use Symfony\Component\HttpFoundation\Response;

class EnsureTokenIsValid
{
    public function __construct(protected ApiService $api)
    {
    }

    public function handle(Request $request, Closure $next): Response
    {
        if (!session('access_token')) {
            return redirect()->route('login');
        }

        // Verify token is still valid
        $user = $this->api->getCurrentUser();
        if (!$user) {
            session()->forget(['access_token', 'refresh_token', 'user']);
            return redirect()->route('login')->with('error', 'Phiên đăng nhập hết hạn');
        }

        // Share user with all views
        view()->share('currentUser', session('user'));

        return $next($request);
    }
}
```

### 4.4.2 Register Middleware

**`bootstrap/app.php`** (Laravel 11):
```php
<?php

use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
    )
    ->withMiddleware(function (Middleware $middleware) {
        $middleware->alias([
            'auth.api' => \App\Http\Middleware\EnsureTokenIsValid::class,
        ]);
    })
    ->withExceptions(function (Exceptions $exceptions) {
        //
    })->create();
```

---

## Step 4.5 — Routes

**`routes/web.php`**:
```php
<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\ProductController;
use App\Http\Controllers\LinkController;
use App\Http\Controllers\SearchController;

// Public routes
Route::get('/', function () {
    return redirect()->route('products.index');
});

// Auth routes (guest only)
Route::middleware('guest')->group(function () {
    Route::get('/login', [AuthController::class, 'showLogin'])->name('login');
    Route::post('/login', [AuthController::class, 'login']);
    Route::get('/register', [AuthController::class, 'showRegister'])->name('register');
    Route::post('/register', [AuthController::class, 'register']);
});

// Protected routes
Route::middleware('auth.api')->group(function () {
    // Logout
    Route::post('/logout', [AuthController::class, 'logout'])->name('logout');
    
    // Products
    Route::get('/products', [ProductController::class, 'index'])->name('products.index');
    Route::get('/products/{id}', [ProductController::class, 'show'])->name('products.show');
    Route::delete('/products/{id}', [ProductController::class, 'destroy'])->name('products.destroy');
    
    // Links
    Route::get('/links/add', [LinkController::class, 'create'])->name('links.create');
    Route::post('/links', [LinkController::class, 'store'])->name('links.store');
    Route::get('/links/{id}/status', [LinkController::class, 'status'])->name('links.status');
    
    // Search
    Route::get('/search', [SearchController::class, 'index'])->name('search.index');
});
```

---

## Step 4.6 — Controllers

### 4.6.1 Auth Controller

**`app/Http/Controllers/AuthController.php`**:
```php
<?php

namespace App\Http\Controllers;

use App\Services\ApiService;
use Illuminate\Http\Request;

class AuthController extends Controller
{
    public function __construct(protected ApiService $api)
    {
    }

    public function showLogin()
    {
        return view('auth.login');
    }

    public function login(Request $request)
    {
        $request->validate([
            'email' => 'required|email',
            'password' => 'required',
        ]);

        $result = $this->api->login(
            $request->input('email'),
            $request->input('password')
        );

        if ($result['success']) {
            return redirect()->route('products.index');
        }

        return back()->withErrors(['email' => $result['error']])->withInput();
    }

    public function showRegister()
    {
        return view('auth.register');
    }

    public function register(Request $request)
    {
        $request->validate([
            'display_name' => 'required|min:2|max:50',
            'email' => 'required|email',
            'password' => 'required|min:8',
        ]);

        $result = $this->api->register([
            'display_name' => $request->input('display_name'),
            'email' => $request->input('email'),
            'password' => $request->input('password'),
        ]);

        if ($result['success']) {
            return redirect()->route('products.index');
        }

        return back()->withErrors(['email' => $result['error']])->withInput();
    }

    public function logout()
    {
        $this->api->logout();
        return redirect()->route('login');
    }
}
```

### 4.6.2 Product Controller

**`app/Http/Controllers/ProductController.php`**:
```php
<?php

namespace App\Http\Controllers;

use App\Services\ApiService;
use Illuminate\Http\Request;

class ProductController extends Controller
{
    public function __construct(protected ApiService $api)
    {
    }

    public function index(Request $request)
    {
        $page = $request->input('page', 1);
        $result = $this->api->getProducts($page);

        if (!$result['success']) {
            return back()->with('error', $result['error']);
        }

        return view('products.index', [
            'products' => $result['data']['results'],
            'total' => $result['data']['count'],
            'page' => $page,
            'totalPages' => ceil($result['data']['count'] / 20),
        ]);
    }

    public function show(string $id)
    {
        $result = $this->api->getProduct($id);

        if (!$result['success']) {
            return redirect()->route('products.index')->with('error', 'Không tìm thấy sản phẩm');
        }

        return view('products.show', [
            'product' => $result['data'],
        ]);
    }

    public function destroy(string $id, Request $request)
    {
        $shopId = $request->input('shop_id');
        $result = $this->api->deleteProduct($id, $shopId);

        if ($result['success']) {
            return redirect()->route('products.index')->with('success', 'Đã xóa sản phẩm');
        }

        return back()->with('error', $result['error']);
    }
}
```

### 4.6.3 Link Controller

**`app/Http/Controllers/LinkController.php`**:
```php
<?php

namespace App\Http\Controllers;

use App\Services\ApiService;
use Illuminate\Http\Request;

class LinkController extends Controller
{
    public function __construct(protected ApiService $api)
    {
    }

    public function create()
    {
        return view('links.create');
    }

    public function store(Request $request)
    {
        $request->validate([
            'url' => 'required|url',
        ]);

        $result = $this->api->createLink($request->input('url'));

        if ($result['success']) {
            return redirect()->route('links.status', $result['data']['id']);
        }

        return back()->withErrors(['url' => $result['error']])->withInput();
    }

    public function status(string $id)
    {
        $result = $this->api->getLink($id);

        if (!$result['success']) {
            return redirect()->route('links.create')->with('error', 'Link không tồn tại');
        }

        $link = $result['data'];

        // Return JSON for AJAX polling
        if (request()->wantsJson()) {
            return response()->json($link);
        }

        return view('links.status', compact('link'));
    }
}
```

### 4.6.4 Search Controller

**`app/Http/Controllers/SearchController.php`**:
```php
<?php

namespace App\Http\Controllers;

use App\Services\ApiService;
use Illuminate\Http\Request;

class SearchController extends Controller
{
    public function __construct(protected ApiService $api)
    {
    }

    public function index(Request $request)
    {
        $query = $request->input('q');
        $results = [];
        $total = 0;

        if ($query) {
            $filters = array_filter([
                'min_price' => $request->input('min_price'),
                'max_price' => $request->input('max_price'),
            ]);

            $result = $this->api->search($query, $filters);
            
            if ($result['success']) {
                $results = $result['data']['results'];
                $total = $result['data']['total'];
            }
        }

        return view('search.index', compact('query', 'results', 'total'));
    }
}
```

---

## Step 4.7 — Layouts

### 4.7.1 Main Layout

**`resources/views/layouts/app.blade.php`**:
```html
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>@yield('title', 'Shopee Aff Manager')</title>
    
    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
    <!-- Custom CSS -->
    <link href="{{ asset('css/app.css') }}" rel="stylesheet">
</head>
<body>
    <div class="d-flex">
        <!-- Sidebar -->
        @include('components.sidebar')
        
        <!-- Main Content -->
        <div class="flex-grow-1">
            <!-- Header (Mobile) -->
            @include('components.header')
            
            <!-- Page Content -->
            <main class="p-4">
                @if(session('success'))
                    <div class="alert alert-success alert-dismissible fade show" role="alert">
                        {{ session('success') }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                @endif
                
                @if(session('error'))
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        {{ session('error') }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                @endif
                
                @yield('content')
            </main>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Custom JS -->
    <script src="{{ asset('js/app.js') }}"></script>
    @stack('scripts')
</body>
</html>
```

### 4.7.2 Auth Layout

**`resources/views/layouts/auth.blade.php`**:
```html
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>@yield('title', 'Đăng nhập') - Shopee Aff Manager</title>
    
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
    <link href="{{ asset('css/app.css') }}" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="min-vh-100 d-flex align-items-center justify-content-center p-4">
        @yield('content')
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

### 4.7.3 Sidebar Component

**`resources/views/components/sidebar.blade.php`**:
```html
<aside class="sidebar d-none d-lg-flex flex-column">
    <!-- Logo -->
    <div class="p-4 border-bottom">
        <a href="{{ route('products.index') }}" class="d-flex align-items-center text-decoration-none">
            <div class="rounded-3 d-flex align-items-center justify-content-center me-3"
                 style="width: 40px; height: 40px; background: var(--color-primary);">
                <i class="bi bi-bag-fill text-white"></i>
            </div>
            <span class="fw-bold fs-5 text-dark">Shopee Aff</span>
        </a>
    </div>
    
    <!-- Navigation -->
    <nav class="flex-grow-1 py-3">
        <ul class="nav flex-column">
            <li class="nav-item">
                <a href="{{ route('products.index') }}" 
                   class="nav-link {{ request()->routeIs('products.*') ? 'active' : '' }}">
                    <i class="bi bi-box-seam me-2"></i>
                    Sản phẩm
                </a>
            </li>
            <li class="nav-item">
                <a href="{{ route('links.create') }}" 
                   class="nav-link {{ request()->routeIs('links.*') ? 'active' : '' }}">
                    <i class="bi bi-link-45deg me-2"></i>
                    Thêm link
                </a>
            </li>
            <li class="nav-item">
                <a href="{{ route('search.index') }}" 
                   class="nav-link {{ request()->routeIs('search.*') ? 'active' : '' }}">
                    <i class="bi bi-search me-2"></i>
                    Tìm kiếm
                </a>
            </li>
        </ul>
    </nav>
    
    <!-- User Section -->
    <div class="p-3 border-top">
        <div class="d-flex align-items-center mb-3 px-2">
            <div class="rounded-circle d-flex align-items-center justify-content-center me-3"
                 style="width: 40px; height: 40px; background: #FEF2F0;">
                <span style="color: var(--color-primary); font-weight: 600;">
                    {{ strtoupper(substr($currentUser['display_name'] ?? 'U', 0, 1)) }}
                </span>
            </div>
            <div class="flex-grow-1 overflow-hidden">
                <div class="fw-medium text-truncate">{{ $currentUser['display_name'] ?? 'User' }}</div>
                <small class="text-muted text-truncate d-block">{{ $currentUser['email'] ?? '' }}</small>
            </div>
        </div>
        
        <form action="{{ route('logout') }}" method="POST">
            @csrf
            <button type="submit" class="nav-link w-100 text-start">
                <i class="bi bi-box-arrow-right me-2"></i>
                Đăng xuất
            </button>
        </form>
    </div>
</aside>
```

### 4.7.4 Header Component (Mobile)

**`resources/views/components/header.blade.php`**:
```html
<header class="d-lg-none bg-white border-bottom sticky-top">
    <div class="d-flex align-items-center justify-content-between p-3">
        <!-- Logo -->
        <a href="{{ route('products.index') }}" class="d-flex align-items-center text-decoration-none">
            <div class="rounded-2 d-flex align-items-center justify-content-center me-2"
                 style="width: 32px; height: 32px; background: var(--color-primary);">
                <i class="bi bi-bag-fill text-white"></i>
            </div>
            <span class="fw-bold text-dark">Shopee Aff</span>
        </a>
        
        <!-- Menu Button -->
        <button class="btn btn-outline-secondary" type="button" data-bs-toggle="offcanvas" data-bs-target="#mobileMenu">
            <i class="bi bi-list fs-5"></i>
        </button>
    </div>
</header>

<!-- Mobile Menu Offcanvas -->
<div class="offcanvas offcanvas-end" tabindex="-1" id="mobileMenu">
    <div class="offcanvas-header border-bottom">
        <h5 class="offcanvas-title">Menu</h5>
        <button type="button" class="btn-close" data-bs-dismiss="offcanvas"></button>
    </div>
    <div class="offcanvas-body">
        <ul class="nav flex-column">
            <li class="nav-item">
                <a href="{{ route('products.index') }}" class="nav-link {{ request()->routeIs('products.*') ? 'active' : '' }}">
                    <i class="bi bi-box-seam me-2"></i>Sản phẩm
                </a>
            </li>
            <li class="nav-item">
                <a href="{{ route('links.create') }}" class="nav-link {{ request()->routeIs('links.*') ? 'active' : '' }}">
                    <i class="bi bi-link-45deg me-2"></i>Thêm link
                </a>
            </li>
            <li class="nav-item">
                <a href="{{ route('search.index') }}" class="nav-link {{ request()->routeIs('search.*') ? 'active' : '' }}">
                    <i class="bi bi-search me-2"></i>Tìm kiếm
                </a>
            </li>
        </ul>
        
        <hr>
        
        <form action="{{ route('logout') }}" method="POST">
            @csrf
            <button type="submit" class="nav-link w-100 text-start text-danger">
                <i class="bi bi-box-arrow-right me-2"></i>Đăng xuất
            </button>
        </form>
    </div>
</div>
```

---

## Step 4.8 — Auth Views

### 4.8.1 Login Page

**`resources/views/auth/login.blade.php`**:
```html
@extends('layouts.auth')

@section('title', 'Đăng nhập')

@section('content')
<div class="card shadow-sm" style="max-width: 400px; width: 100%;">
    <div class="card-body p-5">
        <!-- Logo -->
        <div class="text-center mb-4">
            <div class="rounded-circle d-inline-flex align-items-center justify-content-center mb-3"
                 style="width: 64px; height: 64px; background: var(--color-primary);">
                <i class="bi bi-bag-fill text-white fs-3"></i>
            </div>
            <h4 class="mb-1">Đăng nhập</h4>
            <p class="text-muted small">Quản lý link affiliate Shopee</p>
        </div>
        
        <!-- Form -->
        <form method="POST" action="{{ route('login') }}">
            @csrf
            
            <div class="mb-3">
                <label class="form-label">Email</label>
                <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-envelope"></i></span>
                    <input type="email" name="email" class="form-control @error('email') is-invalid @enderror"
                           placeholder="email@example.com" value="{{ old('email') }}" required>
                </div>
                @error('email')
                    <div class="text-danger small mt-1">{{ $message }}</div>
                @enderror
            </div>
            
            <div class="mb-4">
                <label class="form-label">Mật khẩu</label>
                <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-lock"></i></span>
                    <input type="password" name="password" class="form-control @error('password') is-invalid @enderror"
                           placeholder="Nhập mật khẩu" required>
                    <button type="button" class="btn btn-outline-secondary" onclick="togglePassword(this)">
                        <i class="bi bi-eye"></i>
                    </button>
                </div>
                @error('password')
                    <div class="text-danger small mt-1">{{ $message }}</div>
                @enderror
            </div>
            
            <button type="submit" class="btn btn-primary w-100 mb-3">
                Đăng nhập
            </button>
        </form>
        
        <p class="text-center text-muted mb-0">
            Chưa có tài khoản?
            <a href="{{ route('register') }}" style="color: var(--color-primary);">Đăng ký ngay</a>
        </p>
    </div>
</div>

<script>
function togglePassword(btn) {
    const input = btn.previousElementSibling;
    const icon = btn.querySelector('i');
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('bi-eye', 'bi-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.replace('bi-eye-slash', 'bi-eye');
    }
}
</script>
@endsection
```

### 4.8.2 Register Page

**`resources/views/auth/register.blade.php`**:
```html
@extends('layouts.auth')

@section('title', 'Đăng ký')

@section('content')
<div class="card shadow-sm" style="max-width: 400px; width: 100%;">
    <div class="card-body p-5">
        <!-- Logo -->
        <div class="text-center mb-4">
            <div class="rounded-circle d-inline-flex align-items-center justify-content-center mb-3"
                 style="width: 64px; height: 64px; background: var(--color-primary);">
                <i class="bi bi-bag-fill text-white fs-3"></i>
            </div>
            <h4 class="mb-1">Đăng ký</h4>
            <p class="text-muted small">Tạo tài khoản mới</p>
        </div>
        
        <!-- Form -->
        <form method="POST" action="{{ route('register') }}">
            @csrf
            
            <div class="mb-3">
                <label class="form-label">Tên hiển thị</label>
                <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-person"></i></span>
                    <input type="text" name="display_name" class="form-control @error('display_name') is-invalid @enderror"
                           placeholder="Nhập tên của bạn" value="{{ old('display_name') }}" required>
                </div>
                @error('display_name')
                    <div class="text-danger small mt-1">{{ $message }}</div>
                @enderror
            </div>
            
            <div class="mb-3">
                <label class="form-label">Email</label>
                <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-envelope"></i></span>
                    <input type="email" name="email" class="form-control @error('email') is-invalid @enderror"
                           placeholder="email@example.com" value="{{ old('email') }}" required>
                </div>
                @error('email')
                    <div class="text-danger small mt-1">{{ $message }}</div>
                @enderror
            </div>
            
            <div class="mb-3">
                <label class="form-label">Mật khẩu</label>
                <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-lock"></i></span>
                    <input type="password" name="password" class="form-control @error('password') is-invalid @enderror"
                           placeholder="Tạo mật khẩu" required minlength="8">
                    <button type="button" class="btn btn-outline-secondary" onclick="togglePassword(this)">
                        <i class="bi bi-eye"></i>
                    </button>
                </div>
                <small class="text-muted">Tối thiểu 8 ký tự, gồm chữ hoa, chữ thường và số</small>
                @error('password')
                    <div class="text-danger small mt-1">{{ $message }}</div>
                @enderror
            </div>
            
            <button type="submit" class="btn btn-primary w-100 mb-3">
                Đăng ký
            </button>
        </form>
        
        <p class="text-center text-muted mb-0">
            Đã có tài khoản?
            <a href="{{ route('login') }}" style="color: var(--color-primary);">Đăng nhập</a>
        </p>
    </div>
</div>

<script>
function togglePassword(btn) {
    const input = btn.previousElementSibling;
    const icon = btn.querySelector('i');
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('bi-eye', 'bi-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.replace('bi-eye-slash', 'bi-eye');
    }
}
</script>
@endsection
```

---

## Step 4.9 — Product Views

### 4.9.1 Product List

**`resources/views/products/index.blade.php`**:
```html
@extends('layouts.app')

@section('title', 'Sản phẩm')

@section('content')
<div class="d-flex justify-content-between align-items-center mb-4">
    <div>
        <h4 class="mb-1">Sản phẩm</h4>
        <p class="text-muted mb-0">{{ $total }} sản phẩm</p>
    </div>
    <a href="{{ route('links.create') }}" class="btn btn-primary">
        <i class="bi bi-plus-lg me-1"></i>Thêm link
    </a>
</div>

@if(count($products) > 0)
    <!-- Product Grid -->
    <div class="row row-cols-1 row-cols-sm-2 row-cols-lg-3 row-cols-xl-4 g-4">
        @foreach($products as $product)
            <div class="col">
                @include('components.product-card', ['product' => $product])
            </div>
        @endforeach
    </div>
    
    <!-- Pagination -->
    @if($totalPages > 1)
        <nav class="mt-4">
            <ul class="pagination justify-content-center">
                <li class="page-item {{ $page <= 1 ? 'disabled' : '' }}">
                    <a class="page-link" href="?page={{ $page - 1 }}">Trước</a>
                </li>
                <li class="page-item disabled">
                    <span class="page-link">Trang {{ $page }} / {{ $totalPages }}</span>
                </li>
                <li class="page-item {{ $page >= $totalPages ? 'disabled' : '' }}">
                    <a class="page-link" href="?page={{ $page + 1 }}">Sau</a>
                </li>
            </ul>
        </nav>
    @endif
@else
    <!-- Empty State -->
    <div class="card text-center py-5">
        <div class="card-body">
            <i class="bi bi-box-seam display-1 text-muted mb-3"></i>
            <h5>Chưa có sản phẩm</h5>
            <p class="text-muted mb-4">Thêm link Shopee để bắt đầu quản lý sản phẩm</p>
            <a href="{{ route('links.create') }}" class="btn btn-primary">
                <i class="bi bi-plus-lg me-1"></i>Thêm link đầu tiên
            </a>
        </div>
    </div>
@endif
@endsection
```

### 4.9.2 Product Card Component

**`resources/views/components/product-card.blade.php`**:
```html
<div class="card product-card h-100">
    <a href="{{ route('products.show', $product['id']) }}" class="text-decoration-none">
        <!-- Thumbnail -->
        <div class="position-relative">
            @if($product['thumbnail_url'])
                <img src="{{ $product['thumbnail_url'] }}" alt="{{ $product['title'] }}"
                     class="card-img-top product-image">
            @else
                <div class="card-img-top product-image bg-light d-flex align-items-center justify-content-center">
                    <span class="text-muted">No Image</span>
                </div>
            @endif
            
            <!-- External Link -->
            <a href="{{ $product['original_url'] }}" target="_blank" rel="noopener"
               class="position-absolute top-0 end-0 m-2 btn btn-sm btn-light rounded-circle"
               onclick="event.stopPropagation();">
                <i class="bi bi-box-arrow-up-right"></i>
            </a>
        </div>
        
        <!-- Content -->
        <div class="card-body">
            <h6 class="card-title text-dark mb-2" style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                {{ $product['title'] }}
            </h6>
            
            @if($product['price'])
                <p class="product-price mb-2">
                    {{ number_format($product['price'], 0, ',', '.') }}đ
                </p>
            @endif
            
            <div class="d-flex justify-content-between align-items-center">
                <span class="badge bg-success">{{ $product['status'] }}</span>
                <small class="text-muted">
                    {{ \Carbon\Carbon::parse($product['created_at'])->diffForHumans() }}
                </small>
            </div>
        </div>
    </a>
</div>
```

### 4.9.3 Product Detail

**`resources/views/products/show.blade.php`**:
```html
@extends('layouts.app')

@section('title', $product['title'])

@section('content')
<a href="{{ route('products.index') }}" class="btn btn-link text-muted mb-4 ps-0">
    <i class="bi bi-arrow-left me-1"></i>Quay lại
</a>

<div class="row g-4">
    <!-- Image -->
    <div class="col-md-6">
        <div class="card">
            @if($product['thumbnail_url'])
                <img src="{{ $product['thumbnail_url'] }}" alt="{{ $product['title'] }}"
                     class="card-img-top" style="aspect-ratio: 1; object-fit: cover;">
            @else
                <div class="bg-light d-flex align-items-center justify-content-center" style="aspect-ratio: 1;">
                    <span class="text-muted fs-4">No Image</span>
                </div>
            @endif
        </div>
    </div>
    
    <!-- Details -->
    <div class="col-md-6">
        <div class="card mb-4">
            <div class="card-body">
                <h4 class="mb-3">{{ $product['title'] }}</h4>
                
                @if($product['price'])
                    <p class="product-price fs-3 mb-4">
                        {{ number_format($product['price'], 0, ',', '.') }}đ
                    </p>
                @endif
                
                <table class="table table-borderless">
                    <tr>
                        <td class="text-muted">Trạng thái</td>
                        <td><span class="badge bg-success">{{ $product['status'] }}</span></td>
                    </tr>
                    <tr>
                        <td class="text-muted">Shop ID</td>
                        <td>{{ $product['shop_id'] }}</td>
                    </tr>
                    <tr>
                        <td class="text-muted">Item ID</td>
                        <td>{{ $product['item_id'] }}</td>
                    </tr>
                    <tr>
                        <td class="text-muted">Ngày tạo</td>
                        <td>{{ \Carbon\Carbon::parse($product['created_at'])->format('d/m/Y H:i') }}</td>
                    </tr>
                </table>
            </div>
        </div>
        
        <!-- Actions -->
        <div class="d-flex flex-column flex-sm-row gap-2 mb-4">
            <button class="btn btn-outline-secondary flex-fill" onclick="copyUrl()">
                <i class="bi bi-clipboard me-1"></i>Copy link
            </button>
            <a href="{{ $product['original_url'] }}" target="_blank" rel="noopener"
               class="btn btn-primary flex-fill">
                <i class="bi bi-box-arrow-up-right me-1"></i>Mở Shopee
            </a>
        </div>
        
        <form action="{{ route('products.destroy', $product['id']) }}" method="POST"
              onsubmit="return confirm('Bạn có chắc muốn xóa sản phẩm này?');">
            @csrf
            @method('DELETE')
            <input type="hidden" name="shop_id" value="{{ $product['shop_id'] }}">
            <button type="submit" class="btn btn-outline-danger w-100">
                <i class="bi bi-trash me-1"></i>Xóa sản phẩm
            </button>
        </form>
    </div>
</div>

@push('scripts')
<script>
function copyUrl() {
    navigator.clipboard.writeText('{{ $product['original_url'] }}').then(() => {
        alert('Đã copy link!');
    });
}
</script>
@endpush
@endsection
```

---

## Step 4.10 — Link Views

### 4.10.1 Add Link Page

**`resources/views/links/create.blade.php`**:
```html
@extends('layouts.app')

@section('title', 'Thêm link')

@section('content')
<div class="row justify-content-center">
    <div class="col-lg-6">
        <h4 class="mb-2">Thêm link</h4>
        <p class="text-muted mb-4">Paste link Shopee để tự động lấy thông tin sản phẩm</p>
        
        <div class="card">
            <div class="card-body">
                <form method="POST" action="{{ route('links.store') }}">
                    @csrf
                    
                    <div class="mb-3">
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-link-45deg"></i></span>
                            <input type="url" name="url" class="form-control @error('url') is-invalid @enderror"
                                   placeholder="https://shopee.vn/... hoặc https://shp.ee/..."
                                   value="{{ old('url') }}" required>
                            <button type="button" class="btn btn-outline-secondary" onclick="pasteFromClipboard()">
                                <i class="bi bi-clipboard"></i>
                            </button>
                        </div>
                        @error('url')
                            <div class="text-danger small mt-1">{{ $message }}</div>
                        @enderror
                    </div>
                    
                    <button type="submit" class="btn btn-primary w-100">
                        Thêm sản phẩm
                    </button>
                </form>
                
                <hr>
                
                <p class="text-muted small mb-2">Định dạng được hỗ trợ:</p>
                <ul class="text-muted small mb-0">
                    <li>https://shopee.vn/product/...</li>
                    <li>https://shp.ee/...</li>
                    <li>https://vn.shp.ee/...</li>
                </ul>
            </div>
        </div>
    </div>
</div>

@push('scripts')
<script>
async function pasteFromClipboard() {
    try {
        const text = await navigator.clipboard.readText();
        if (text.includes('shopee') || text.includes('shp.ee')) {
            document.querySelector('input[name="url"]').value = text;
        }
    } catch (err) {
        console.error('Failed to read clipboard');
    }
}
</script>
@endpush
@endsection
```

### 4.10.2 Link Status Page

**`resources/views/links/status.blade.php`**:
```html
@extends('layouts.app')

@section('title', 'Đang xử lý')

@section('content')
<div class="row justify-content-center">
    <div class="col-lg-6">
        <div class="card text-center py-5" id="statusCard">
            <div class="card-body">
                <!-- Status Icon -->
                <div class="mb-4" id="statusIcon">
                    @if($link['status'] === 'done')
                        <div class="rounded-circle d-inline-flex align-items-center justify-content-center"
                             style="width: 80px; height: 80px; background: #E8F5E9;">
                            <i class="bi bi-check-circle-fill text-success display-4"></i>
                        </div>
                    @elseif($link['status'] === 'failed')
                        <div class="rounded-circle d-inline-flex align-items-center justify-content-center"
                             style="width: 80px; height: 80px; background: #FFEBEE;">
                            <i class="bi bi-x-circle-fill text-danger display-4"></i>
                        </div>
                    @else
                        <div class="rounded-circle d-inline-flex align-items-center justify-content-center"
                             style="width: 80px; height: 80px; background: #E3F2FD;">
                            <div class="spinner-border spinner-shopee" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>
                    @endif
                </div>
                
                <!-- Status Text -->
                <div id="statusText">
                    @if($link['status'] === 'done')
                        <span class="badge bg-success mb-3">Hoàn thành</span>
                        <p class="text-muted mb-4">Sản phẩm đã được thêm thành công!</p>
                        <div class="d-flex justify-content-center gap-2">
                            <a href="{{ route('products.show', $link['product_id']) }}" class="btn btn-primary">
                                Xem sản phẩm
                            </a>
                            <a href="{{ route('links.create') }}" class="btn btn-outline-secondary">
                                Thêm link khác
                            </a>
                        </div>
                    @elseif($link['status'] === 'failed')
                        <span class="badge bg-danger mb-3">Thất bại</span>
                        <p class="text-danger mb-4">{{ $link['error_message'] ?? 'Không thể xử lý link này' }}</p>
                        <a href="{{ route('links.create') }}" class="btn btn-outline-secondary">
                            Thử lại
                        </a>
                    @else
                        <span class="badge bg-info mb-3" id="statusBadge">
                            {{ $link['status'] === 'pending' ? 'Đang chờ xử lý' : 'Đang scrape...' }}
                        </span>
                        <p class="text-muted mb-0" id="pollCount">Đang xử lý...</p>
                    @endif
                </div>
            </div>
        </div>
    </div>
</div>

@if($link['status'] !== 'done' && $link['status'] !== 'failed')
@push('scripts')
<script>
let pollCount = 0;
const maxPolls = 20;
const linkId = '{{ $link['id'] }}';

function poll() {
    pollCount++;
    document.getElementById('pollCount').textContent = `Đang xử lý... (${pollCount}/${maxPolls})`;
    
    if (pollCount >= maxPolls) {
        document.getElementById('statusBadge').className = 'badge bg-warning mb-3';
        document.getElementById('statusBadge').textContent = 'Timeout';
        document.getElementById('pollCount').innerHTML = 
            'Quá thời gian chờ. <a href="{{ route('links.create') }}">Thử lại</a>';
        return;
    }
    
    fetch(`/links/${linkId}/status`, {
        headers: { 'Accept': 'application/json' }
    })
    .then(res => res.json())
    .then(link => {
        if (link.status === 'done' || link.status === 'failed') {
            location.reload();
        } else {
            setTimeout(poll, 3000);
        }
    })
    .catch(err => {
        console.error('Poll error:', err);
        setTimeout(poll, 3000);
    });
}

// Start polling
setTimeout(poll, 3000);
</script>
@endpush
@endif
@endsection
```

---

## Step 4.11 — Search View

**`resources/views/search/index.blade.php`**:
```html
@extends('layouts.app')

@section('title', 'Tìm kiếm')

@section('content')
<h4 class="mb-2">Tìm kiếm</h4>
<p class="text-muted mb-4">Tìm kiếm sản phẩm với AI</p>

<!-- Search Form -->
<div class="card mb-4">
    <div class="card-body">
        <form method="GET" action="{{ route('search.index') }}">
            <div class="row g-3">
                <div class="col-12 col-md-8">
                    <div class="input-group">
                        <span class="input-group-text"><i class="bi bi-search"></i></span>
                        <input type="text" name="q" class="form-control" placeholder="Tìm kiếm sản phẩm..."
                               value="{{ $query }}">
                    </div>
                </div>
                <div class="col-6 col-md-2">
                    <input type="number" name="min_price" class="form-control" placeholder="Giá từ"
                           value="{{ request('min_price') }}">
                </div>
                <div class="col-6 col-md-2">
                    <input type="number" name="max_price" class="form-control" placeholder="Giá đến"
                           value="{{ request('max_price') }}">
                </div>
            </div>
            <button type="submit" class="btn btn-primary mt-3">
                <i class="bi bi-search me-1"></i>Tìm
            </button>
        </form>
    </div>
</div>

<!-- Results -->
@if($query)
    <p class="text-muted mb-4">Tìm thấy {{ $total }} kết quả cho "{{ $query }}"</p>
    
    @if(count($results) > 0)
        <div class="row row-cols-1 row-cols-sm-2 row-cols-lg-3 row-cols-xl-4 g-4">
            @foreach($results as $product)
                <div class="col">
                    @include('components.product-card', ['product' => $product])
                </div>
            @endforeach
        </div>
    @else
        <div class="card text-center py-5">
            <div class="card-body">
                <i class="bi bi-search display-1 text-muted mb-3"></i>
                <p class="text-muted mb-0">Không tìm thấy sản phẩm phù hợp</p>
            </div>
        </div>
    @endif
@else
    <div class="card text-center py-5">
        <div class="card-body">
            <i class="bi bi-search display-1 text-muted mb-3"></i>
            <p class="text-muted mb-0">Nhập từ khóa để tìm kiếm sản phẩm</p>
        </div>
    </div>
@endif
@endsection
```

---

## Step 4.12 — Run Development Server

```powershell
cd frontend
php artisan serve --port=8080

# Open http://localhost:8080
```

---

## Step 4.13 — Testing Checklist

- [ ] Login page hiển thị đúng
- [ ] Đăng nhập thành công redirect về /products
- [ ] Đăng nhập thất bại hiển thị lỗi
- [ ] Register page hoạt động
- [ ] Product list hiển thị cards
- [ ] Product detail hiển thị thông tin
- [ ] Add link form hoạt động
- [ ] Link status polling hoạt động
- [ ] Search page tìm kiếm được
- [ ] Responsive trên mobile
- [ ] Logout hoạt động

---

## Comparison: Web (Laravel) vs Mobile (Flutter)

| Feature | Web (Laravel) | Mobile (Flutter) |
|---------|--------------|------------------|
| Auth | Session + API tokens | Riverpod + SecureStorage |
| HTTP Client | Guzzle (Laravel HTTP) | Dio |
| Styling | Bootstrap 5 + CSS | Material Theme |
| Routing | Laravel Routes | go_router |
| State | Session + Blade | Riverpod |
| Forms | HTML forms | Built-in validators |
| Icons | Bootstrap Icons | Lucide Icons |
| Design System | Same colors (CSS vars) | Same colors (ThemeData) |

---

## Summary

Phase 4 (Web Frontend - Laravel) tạo một web app với:
- **Laravel 11** với Blade templates
- **Bootstrap 5** + CSS variables (Shopee Orange theme)
- **Vanilla JS** cho interactivity (no framework)
- **Session-based auth** với API token từ Django backend
- **Responsive design** (desktop + mobile)
- **Server-side rendering** (SEO friendly)
- **Deploy**: Azure Web App (PHP runtime)
