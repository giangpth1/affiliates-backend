---
title: Phase 5 — Flutter Mobile App
version: 1.0.0
updated: 2026-05-08
---

# Phase 5: Flutter Mobile App

## Goals
- Flutter project với feature-first architecture
- Màn hình Add Link: paste URL + polling trạng thái
- Màn hình Product List: danh sách card + thumbnail
- Màn hình Smart Search: RAG search với highlights
- Kết nối đầy đủ với Django backend API

---

## Step 5.1 — Scaffold Flutter Project

```powershell
# Từ C:\Projects\New project\
flutter create mobile --org com.shopeeaff --project-name shopee_aff_manager
cd mobile
```

### 5.1.1 Cấu trúc thư mục

```
mobile/lib/
├── main.dart
├── app/
│   ├── app.dart              # MaterialApp root
│   └── router.dart           # go_router config
├── core/
│   ├── constants.dart        # API base URL, etc.
│   ├── dio_client.dart       # Dio HTTP client singleton
│   └── error_handler.dart    # API error → user message
├── features/
│   ├── links/
│   │   ├── data/
│   │   │   ├── link_repository.dart
│   │   │   └── link_model.dart
│   │   ├── domain/
│   │   │   └── link_provider.dart   # Riverpod provider
│   │   └── presentation/
│   │       ├── add_link_screen.dart
│   │       └── links_list_screen.dart
│   ├── products/
│   │   ├── data/
│   │   │   ├── product_repository.dart
│   │   │   └── product_model.dart
│   │   ├── domain/
│   │   │   └── product_provider.dart
│   │   └── presentation/
│   │       ├── product_list_screen.dart
│   │       └── product_detail_screen.dart
│   └── search/
│       ├── data/
│       │   ├── search_repository.dart
│       │   └── search_result_model.dart
│       ├── domain/
│       │   └── search_provider.dart
│       └── presentation/
│           └── search_screen.dart
└── shared/
    ├── widgets/
    │   ├── product_card.dart
    │   ├── thumbnail_image.dart
    │   ├── loading_overlay.dart
    │   └── error_snackbar.dart
    └── theme/
        └── app_theme.dart
```

### 5.1.2 Dependencies

**`pubspec.yaml`** — thêm vào `dependencies`:
```yaml
dependencies:
  flutter:
    sdk: flutter
  flutter_riverpod: ^2.6.1
  riverpod_annotation: ^2.6.1
  dio: ^5.8.0
  go_router: ^14.8.1
  cached_network_image: ^3.4.1
  flutter_hooks: ^0.20.5
  hooks_riverpod: ^2.6.1
  share_plus: ^10.1.3       # Share link from other apps
  url_launcher: ^6.3.1      # Open Shopee link in browser

dev_dependencies:
  flutter_test:
    sdk: flutter
  riverpod_generator: ^2.6.1
  build_runner: ^2.4.13
  flutter_lints: ^5.0.0
```

```powershell
flutter pub get
```

---

## Step 5.2 — Core Setup

### 5.2.1 Constants

**`lib/core/constants.dart`**:
```dart
class AppConstants {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/api',  // Android emulator → localhost
  );
  static const Duration pollingInterval = Duration(seconds: 3);
  static const int maxPollingAttempts = 20;  // 60 seconds total
}
```

### 5.2.2 Dio Client

**`lib/core/dio_client.dart`**:
```dart
import 'package:dio/dio.dart';
import 'constants.dart';

class DioClient {
  static Dio? _instance;

  static Dio get instance {
    _instance ??= Dio(
      BaseOptions(
        baseUrl: AppConstants.baseUrl,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 30),
        headers: {'Content-Type': 'application/json'},
      ),
    )
      ..interceptors.add(LogInterceptor(
        requestBody: true,
        responseBody: true,
      ));
    return _instance!;
  }
}
```

### 5.2.3 App Theme

**See detailed theme system in**: [THEME_SYSTEM.md](THEME_SYSTEM.md)

**`lib/shared/theme/app_theme.dart`** (simplified version):
```dart
import 'package:flutter/material.dart';
import 'colors.dart';
import 'text_styles.dart';

class AppTheme {
  static ThemeData get light => ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    colorScheme: ColorScheme.light(
      primary: AppColors.primary,
      secondary: AppColors.secondary,
      surface: AppColors.surface,
      background: AppColors.background,
    ),
    textTheme: TextTheme(
      displayLarge: AppTextStyles.h1,
      displayMedium: AppTextStyles.h2,
      bodyLarge: AppTextStyles.bodyLarge,
    ),
    appBarTheme: AppBarTheme(
      backgroundColor: AppColors.primary,
      foregroundColor: AppColors.textOnPrimary,
      elevation: 0,
    ),
  );
  
  static ThemeData get dark => ThemeData(
    // See THEME_SYSTEM.md for full dark theme config
    useMaterial3: true,
    brightness: Brightness.dark,
  );
}

// For full implementation, see plans/THEME_SYSTEM.md
```

### 5.2.4 Router

**`lib/app/router.dart`**:
```dart
import 'package:go_router/go_router.dart';
import '../features/links/presentation/add_link_screen.dart';
import '../features/products/presentation/product_list_screen.dart';
import '../features/products/presentation/product_detail_screen.dart';
import '../features/search/presentation/search_screen.dart';

final appRouter = GoRouter(
  initialLocation: '/products',
  routes: [
    GoRoute(path: '/products', builder: (_, __) => const ProductListScreen()),
    GoRoute(path: '/products/:id', builder: (ctx, state) =>
        ProductDetailScreen(productId: state.pathParameters['id']!)),
    GoRoute(path: '/links/add', builder: (_, __) => const AddLinkScreen()),
    GoRoute(path: '/search', builder: (_, __) => const SearchScreen()),
  ],
);
```

### 5.2.5 Main App

**`lib/main.dart`**:
```dart
import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'app/router.dart';
import 'shared/theme/app_theme.dart';

void main() {
  runApp(const ProviderScope(child: ShopeeAffApp()));
}

class ShopeeAffApp extends StatelessWidget {
  const ShopeeAffApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'Shopee Aff Manager',
      theme: AppTheme.light,
      routerConfig: appRouter,
    );
  }
}
```

---

## Step 5.2A — Auth Feature (⚠️ IMPLEMENT FIRST)

> **BẮT BUỘC**: User phải login trước khi sử dụng app. Xem chi tiết tại **[USER_AUTHENTICATION.md](USER_AUTHENTICATION.md)**.

### 5.2A.1 Dependencies

Add to `pubspec.yaml`:
```yaml
dependencies:
  flutter_secure_storage: ^9.0.0  # Secure token storage
  go_router: ^13.0.0               # Routing with auth guard
```

### 5.2A.2 Token Storage Service

**`lib/core/services/token_storage.dart`**:
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
  
  static Future<String?> getAccessToken() => _storage.read(key: _accessTokenKey);
  static Future<String?> getRefreshToken() => _storage.read(key: _refreshTokenKey);
  
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

### 5.2A.3 User Model

**`lib/features/auth/data/user_model.dart`**:
```dart
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
  
  factory User.fromJson(Map<String, dynamic> json) => User(
    id: json['id'],
    email: json['email'],
    displayName: json['display_name'],
    status: json['status'],
    emailVerified: json['email_verified'],
  );
}

class AuthResponse {
  final User user;
  final String accessToken;
  final String refreshToken;
  
  AuthResponse({
    required this.user,
    required this.accessToken,
    required this.refreshToken,
  });
  
  factory AuthResponse.fromJson(Map<String, dynamic> json) => AuthResponse(
    user: User.fromJson(json['user']),
    accessToken: json['access'],
    refreshToken: json['refresh'],
  );
}
```

### 5.2A.4 Auth Repository

**`lib/features/auth/data/auth_repository.dart`**:
```dart
import 'package:dio/dio.dart';
import '../../../core/services/token_storage.dart';
import 'user_model.dart';

class AuthRepository {
  final Dio _dio;
  
  AuthRepository(this._dio);
  
  Future<AuthResponse> register({
    required String email,
    required String password,
    required String displayName,
  }) async {
    final response = await _dio.post('/auth/register/', data: {
      'email': email,
      'password': password,
      'display_name': displayName,
    });
    
    final authResponse = AuthResponse.fromJson(response.data);
    await TokenStorage.saveTokens(
      accessToken: authResponse.accessToken,
      refreshToken: authResponse.refreshToken,
    );
    return authResponse;
  }
  
  Future<AuthResponse> login({
    required String email,
    required String password,
  }) async {
    final response = await _dio.post('/auth/login/', data: {
      'email': email,
      'password': password,
    });
    
    final authResponse = AuthResponse.fromJson(response.data);
    await TokenStorage.saveTokens(
      accessToken: authResponse.accessToken,
      refreshToken: authResponse.refreshToken,
    );
    return authResponse;
  }
  
  Future<void> logout() async {
    final refreshToken = await TokenStorage.getRefreshToken();
    try {
      await _dio.post('/auth/logout/', data: {'refresh': refreshToken});
    } catch (e) {
      // Ignore errors
    }
    await TokenStorage.deleteTokens();
  }
  
  Future<User> getCurrentUser() async {
    final response = await _dio.get('/auth/me/');
    return User.fromJson(response.data);
  }
}
```

### 5.2A.5 Auth State Provider

**`lib/features/auth/domain/auth_provider.dart`**:
```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/auth_repository.dart';
import '../data/user_model.dart';
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
    
    if (await TokenStorage.hasTokens()) {
      try {
        final user = await _repository.getCurrentUser();
        state = AuthState.authenticated(user);
      } catch (e) {
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
  
  Future<void> login({required String email, required String password}) async {
    state = const AuthState.loading();
    try {
      final response = await _repository.login(email: email, password: password);
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
  
  const AuthState({required this.status, this.user, this.errorMessage});
  
  const AuthState.initial() : this(status: AuthStatus.initial);
  const AuthState.loading() : this(status: AuthStatus.loading);
  const AuthState.authenticated(User user) : this(status: AuthStatus.authenticated, user: user);
  const AuthState.unauthenticated() : this(status: AuthStatus.unauthenticated);
  const AuthState.error(String message) : this(status: AuthStatus.error, errorMessage: message);
}

enum AuthStatus { initial, loading, authenticated, unauthenticated, error }
```

### 5.2A.6 Login Screen

**`lib/features/auth/presentation/login_screen.dart`**:
```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../domain/auth_provider.dart';

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
                const Icon(Icons.shopping_bag, size: 80, color: Color(0xFFEE4D2D)),
                const SizedBox(height: 32),
                Text('Đăng nhập', style: Theme.of(context).textTheme.headlineMedium, textAlign: TextAlign.center),
                const SizedBox(height: 32),
                
                TextFormField(
                  controller: _emailController,
                  decoration: const InputDecoration(labelText: 'Email', prefixIcon: Icon(Icons.email)),
                  keyboardType: TextInputType.emailAddress,
                  validator: (value) {
                    if (value == null || value.isEmpty) return 'Vui lòng nhập email';
                    if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) return 'Email không hợp lệ';
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                
                TextFormField(
                  controller: _passwordController,
                  decoration: InputDecoration(
                    labelText: 'Mật khẩu',
                    prefixIcon: const Icon(Icons.lock),
                    suffixIcon: IconButton(
                      icon: Icon(_isPasswordVisible ? Icons.visibility_off : Icons.visibility),
                      onPressed: () => setState(() => _isPasswordVisible = !_isPasswordVisible),
                    ),
                  ),
                  obscureText: !_isPasswordVisible,
                  validator: (value) => value == null || value.isEmpty ? 'Vui lòng nhập mật khẩu' : null,
                ),
                const SizedBox(height: 24),
                
                ElevatedButton(
                  onPressed: isLoading ? null : _login,
                  child: isLoading
                      ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Text('Đăng nhập'),
                ),
                const SizedBox(height: 16),
                
                TextButton(
                  onPressed: () => context.push('/register'),
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

### 5.2A.7 Register Screen

**`lib/features/auth/presentation/register_screen.dart`**:
```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../domain/auth_provider.dart';

class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({super.key});
  
  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _displayNameController = TextEditingController();
  bool _isPasswordVisible = false;
  
  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _displayNameController.dispose();
    super.dispose();
  }
  
  void _register() async {
    if (_formKey.currentState!.validate()) {
      await ref.read(authStateProvider.notifier).register(
        email: _emailController.text.trim(),
        password: _passwordController.text,
        displayName: _displayNameController.text.trim(),
      );
      
      final authState = ref.read(authStateProvider);
      if (authState.status == AuthStatus.authenticated) {
        context.go('/home');
      } else if (authState.status == AuthStatus.error) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(authState.errorMessage ?? 'Đăng ký thất bại')),
        );
      }
    }
  }
  
  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authStateProvider);
    final isLoading = authState.status == AuthStatus.loading;
    
    return Scaffold(
      appBar: AppBar(title: const Text('Đăng ký')),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Form(
            key: _formKey,
            child: ListView(
              children: [
                const SizedBox(height: 32),
                TextFormField(
                  controller: _displayNameController,
                  decoration: const InputDecoration(labelText: 'Tên hiển thị', prefixIcon: Icon(Icons.person)),
                  validator: (value) {
                    if (value == null || value.isEmpty) return 'Vui lòng nhập tên';
                    if (value.length < 2) return 'Tên phải có ít nhất 2 ký tự';
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                
                TextFormField(
                  controller: _emailController,
                  decoration: const InputDecoration(labelText: 'Email', prefixIcon: Icon(Icons.email)),
                  keyboardType: TextInputType.emailAddress,
                  validator: (value) {
                    if (value == null || value.isEmpty) return 'Vui lòng nhập email';
                    if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) return 'Email không hợp lệ';
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                
                TextFormField(
                  controller: _passwordController,
                  decoration: InputDecoration(
                    labelText: 'Mật khẩu',
                    prefixIcon: const Icon(Icons.lock),
                    suffixIcon: IconButton(
                      icon: Icon(_isPasswordVisible ? Icons.visibility_off : Icons.visibility),
                      onPressed: () => setState(() => _isPasswordVisible = !_isPasswordVisible),
                    ),
                  ),
                  obscureText: !_isPasswordVisible,
                  validator: (value) {
                    if (value == null || value.isEmpty) return 'Vui lòng nhập mật khẩu';
                    if (value.length < 8) return 'Mật khẩu phải có ít nhất 8 ký tự';
                    return null;
                  },
                ),
                const SizedBox(height: 8),
                Text('Mật khẩu phải có ít nhất 8 ký tự, gồm chữ hoa, chữ thường và số',
                  style: Theme.of(context).textTheme.bodySmall),
                const SizedBox(height: 24),
                
                ElevatedButton(
                  onPressed: isLoading ? null : _register,
                  child: isLoading
                      ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Text('Đăng ký'),
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

### 5.2A.8 Update Router with Auth Guard

**`lib/app/router.dart`** (update):
```dart
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
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
      final isLoginRoute = state.matchedLocation == '/login' || state.matchedLocation == '/register';
      
      if (isLoading) return '/splash';
      if (!isAuthenticated && !isLoginRoute) return '/login';
      if (isAuthenticated && isLoginRoute) return '/home';
      return null;
    },
    routes: [
      GoRoute(path: '/login', builder: (context, state) => const LoginScreen()),
      GoRoute(path: '/register', builder: (context, state) => const RegisterScreen()),
      GoRoute(path: '/home', builder: (context, state) => const HomeScreen()),
      // ... other routes
    ],
  );
});
```

### 5.2A.9 Update Dio with Auth Interceptor

**`lib/core/dio_client.dart`** (update):
```dart
import 'package:dio/dio.dart';
import 'services/token_storage.dart';

Dio createDio() {
  final dio = Dio(BaseOptions(
    baseUrl: 'https://app-shopee-aff-dev.azurewebsites.net/api',
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
  ));
  
  dio.interceptors.add(InterceptorsWrapper(
    onRequest: (options, handler) async {
      final accessToken = await TokenStorage.getAccessToken();
      if (accessToken != null) {
        options.headers['Authorization'] = 'Bearer $accessToken';
      }
      return handler.next(options);
    },
    onError: (error, handler) async {
      if (error.response?.statusCode == 401) {
        final refreshToken = await TokenStorage.getRefreshToken();
        if (refreshToken != null) {
          try {
            final response = await dio.post('/auth/refresh/', data: {'refresh': refreshToken});
            await TokenStorage.saveTokens(
              accessToken: response.data['access'],
              refreshToken: response.data['refresh'],
            );
            
            // Retry original request
            final options = error.requestOptions;
            options.headers['Authorization'] = 'Bearer ${response.data['access']}';
            final retryResponse = await dio.fetch(options);
            return handler.resolve(retryResponse);
          } catch (e) {
            await TokenStorage.deleteTokens();
          }
        }
      }
      return handler.next(error);
    },
  ));
  
  return dio;
}
```

---

## Step 5.3 — Links Feature

### 5.3.1 Link Model

**`lib/features/links/data/link_model.dart`**:
```dart
class LinkModel {
  final String id;
  final String originalUrl;
  final String? resolvedUrl;
  final String? productId;
  final String status;  // pending | processing | done | failed
  final String? errorMessage;
  final String? notes;
  final String createdAt;

  const LinkModel({
    required this.id,
    required this.originalUrl,
    this.resolvedUrl,
    this.productId,
    required this.status,
    this.errorMessage,
    this.notes,
    required this.createdAt,
  });

  factory LinkModel.fromJson(Map<String, dynamic> json) => LinkModel(
    id: json['id'],
    originalUrl: json['original_url'],
    resolvedUrl: json['resolved_url'],
    productId: json['product_id'],
    status: json['status'],
    errorMessage: json['error_message'],
    notes: json['notes'],
    createdAt: json['created_at'],
  );

  bool get isPending => status == 'pending' || status == 'processing';
  bool get isDone => status == 'done';
  bool get isFailed => status == 'failed';
}
```

### 5.3.2 Link Repository

**`lib/features/links/data/link_repository.dart`**:
```dart
import 'package:dio/dio.dart';
import '../../../core/dio_client.dart';
import '../../../core/constants.dart';
import 'link_model.dart';

class LinkRepository {
  final Dio _dio = DioClient.instance;

  Future<LinkModel> createLink(String url, {String? notes}) async {
    final response = await _dio.post('/links/', data: {
      'url': url,
      'user_id': AppConstants.defaultUserId,
      if (notes != null) 'notes': notes,
    });
    return LinkModel.fromJson(response.data);
  }

  Future<LinkModel> getLink(String linkId) async {
    final response = await _dio.get(
      '/links/$linkId/',
      queryParameters: {'user_id': AppConstants.defaultUserId},
    );
    return LinkModel.fromJson(response.data);
  }

  Future<List<LinkModel>> listLinks({int page = 1}) async {
    final response = await _dio.get('/links/', queryParameters: {
      'user_id': AppConstants.defaultUserId,
      'page': page,
    });
    final items = response.data['results'] as List;
    return items.map((e) => LinkModel.fromJson(e)).toList();
  }
}
```

### 5.3.3 Link Provider (Riverpod)

**`lib/features/links/domain/link_provider.dart`**:
```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/link_repository.dart';
import '../data/link_model.dart';
import '../../../core/constants.dart';

final linkRepositoryProvider = Provider((_) => LinkRepository());

// State: link creation + polling
class LinkNotifier extends AsyncNotifier<LinkModel?> {
  @override
  Future<LinkModel?> build() async => null;

  Future<void> submitLink(String url, {String? notes}) async {
    state = const AsyncLoading();
    final repo = ref.read(linkRepositoryProvider);

    try {
      final link = await repo.createLink(url, notes: notes);
      state = AsyncData(link);
      if (link.isPending) {
        _startPolling(link.id, repo);
      }
    } catch (e, st) {
      state = AsyncError(e, st);
    }
  }

  void _startPolling(String linkId, LinkRepository repo) async {
    for (int i = 0; i < AppConstants.maxPollingAttempts; i++) {
      await Future.delayed(AppConstants.pollingInterval);
      try {
        final updated = await repo.getLink(linkId);
        state = AsyncData(updated);
        if (!updated.isPending) return;
      } catch (_) {}
    }
    // Timeout
    state = AsyncError('Timeout: scraping took too long', StackTrace.current);
  }
}

final linkNotifierProvider = AsyncNotifierProvider<LinkNotifier, LinkModel?>(
  LinkNotifier.new,
);
```

### 5.3.4 Add Link Screen

**`lib/features/links/presentation/add_link_screen.dart`**:
```dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../domain/link_provider.dart';
import '../data/link_model.dart';

class AddLinkScreen extends ConsumerStatefulWidget {
  const AddLinkScreen({super.key});

  @override
  ConsumerState<AddLinkScreen> createState() => _AddLinkScreenState();
}

class _AddLinkScreenState extends ConsumerState<AddLinkScreen> {
  final _controller = TextEditingController();

  @override
  void initState() {
    super.initState();
    _pasteFromClipboard();
  }

  Future<void> _pasteFromClipboard() async {
    final data = await Clipboard.getData(Clipboard.kTextPlain);
    if (data?.text != null && data!.text!.contains('shp.ee')) {
      _controller.text = data.text!;
    }
  }

  @override
  Widget build(BuildContext context) {
    final linkState = ref.watch(linkNotifierProvider);

    ref.listen(linkNotifierProvider, (_, next) {
      next.whenData((link) {
        if (link?.isDone == true) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Đã lưu sản phẩm thành công!'), backgroundColor: Colors.green),
          );
          context.go('/products');
        } else if (link?.isFailed == true) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Lỗi: ${link?.errorMessage ?? 'Không thể lấy dữ liệu'}'), backgroundColor: Colors.red),
          );
        }
      });
    });

    return Scaffold(
      appBar: AppBar(title: const Text('Thêm Affiliate Link')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _controller,
              decoration: InputDecoration(
                labelText: 'Dán link Shopee vào đây',
                hintText: 'https://shp.ee/...',
                border: const OutlineInputBorder(),
                suffixIcon: IconButton(
                  icon: const Icon(Icons.paste),
                  onPressed: _pasteFromClipboard,
                ),
              ),
              keyboardType: TextInputType.url,
            ),
            const SizedBox(height: 16),
            // Status indicator
            if (linkState.isLoading)
              _buildStatusCard(
                icon: Icons.sync,
                color: Colors.orange,
                title: 'Đang xử lý...',
                subtitle: 'Đang lấy thông tin sản phẩm',
              ),
            if (linkState.hasError)
              _buildStatusCard(
                icon: Icons.error,
                color: Colors.red,
                title: 'Lỗi',
                subtitle: linkState.error.toString(),
              ),
            linkState.whenData((link) {
              if (link == null) return const SizedBox();
              return _buildStatusCard(
                icon: link.isDone ? Icons.check_circle : Icons.hourglass_top,
                color: link.isDone ? Colors.green : Colors.orange,
                title: link.isDone ? 'Hoàn tất!' : 'Đang xử lý (${link.status})',
                subtitle: link.isDone ? link.resolvedUrl ?? '' : 'Vui lòng chờ...',
              );
            }) ?? const SizedBox(),
            const Spacer(),
            ElevatedButton.icon(
              onPressed: linkState.isLoading
                  ? null
                  : () {
                      final url = _controller.text.trim();
                      if (url.isEmpty) return;
                      ref.read(linkNotifierProvider.notifier).submitLink(url);
                    },
              icon: const Icon(Icons.add_link),
              label: const Text('Lưu Link'),
              style: ElevatedButton.styleFrom(
                minimumSize: const Size.fromHeight(50),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusCard({
    required IconData icon,
    required Color color,
    required String title,
    required String subtitle,
  }) {
    return Card(
      child: ListTile(
        leading: Icon(icon, color: color, size: 36),
        title: Text(title, style: TextStyle(color: color, fontWeight: FontWeight.bold)),
        subtitle: Text(subtitle, maxLines: 2, overflow: TextOverflow.ellipsis),
      ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}
```

---

## Step 5.4 — Products Feature

### 5.4.1 Product Model

**`lib/features/products/data/product_model.dart`**:
```dart
class ProductModel {
  final String id;
  final String title;
  final String thumbnailUrl;
  final String originalUrl;
  final double? price;
  final String priceCurrency;
  final String createdAt;

  const ProductModel({
    required this.id,
    required this.title,
    required this.thumbnailUrl,
    required this.originalUrl,
    this.price,
    required this.priceCurrency,
    required this.createdAt,
  });

  factory ProductModel.fromJson(Map<String, dynamic> json) => ProductModel(
    id: json['id'],
    title: json['title'],
    thumbnailUrl: json['thumbnail_url'] ?? '',
    originalUrl: json['original_url'],
    price: json['price']?.toDouble(),
    priceCurrency: json['price_currency'] ?? 'VND',
    createdAt: json['created_at'],
  );

  String get formattedPrice {
    if (price == null) return 'Chưa có giá';
    return '${price!.toStringAsFixed(0).replaceAllMapped(
      RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
      (m) => '${m[1]}.',
    )}đ';
  }
}
```

### 5.4.2 Product Repository

**`lib/features/products/data/product_repository.dart`**:
```dart
import 'package:dio/dio.dart';
import '../../../core/dio_client.dart';
import 'product_model.dart';

class ProductRepository {
  final Dio _dio = DioClient.instance;

  Future<List<ProductModel>> listProducts({int page = 1, int pageSize = 20}) async {
    final response = await _dio.get('/products/', queryParameters: {
      'page': page,
      'page_size': pageSize,
    });
    final items = response.data['results'] as List;
    return items.map((e) => ProductModel.fromJson(e)).toList();
  }
}

final productRepositoryProvider = Provider((_) => ProductRepository());

final productsProvider = FutureProvider.autoDispose<List<ProductModel>>((ref) {
  return ref.read(productRepositoryProvider).listProducts();
});
```

### 5.4.3 Product List Screen

**`lib/features/products/presentation/product_list_screen.dart`**:
```dart
import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../data/product_repository.dart';
import '../../../shared/widgets/product_card.dart';

class ProductListScreen extends ConsumerWidget {
  const ProductListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final productsAsync = ref.watch(productsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Sản phẩm của tôi'),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () => context.push('/search'),
          ),
        ],
      ),
      body: productsAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Lỗi: $e')),
        data: (products) => products.isEmpty
            ? _buildEmptyState(context)
            : RefreshIndicator(
                onRefresh: () => ref.refresh(productsProvider.future),
                child: GridView.builder(
                  padding: const EdgeInsets.all(12),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    childAspectRatio: 0.72,
                    crossAxisSpacing: 10,
                    mainAxisSpacing: 10,
                  ),
                  itemCount: products.length,
                  itemBuilder: (ctx, i) => ProductCard(
                    product: products[i],
                    onTap: () => context.push('/products/${products[i].id}'),
                  ),
                ),
              ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.push('/links/add'),
        icon: const Icon(Icons.add_link),
        label: const Text('Thêm Link'),
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.inventory_2_outlined, size: 80, color: Colors.grey),
          const SizedBox(height: 16),
          const Text('Chưa có sản phẩm nào', style: TextStyle(fontSize: 18)),
          const SizedBox(height: 8),
          ElevatedButton.icon(
            onPressed: () => context.push('/links/add'),
            icon: const Icon(Icons.add_link),
            label: const Text('Thêm link đầu tiên'),
          ),
        ],
      ),
    );
  }
}
```

---

## Step 5.5 — Shared Widgets

### 5.5.1 Product Card

**`lib/shared/widgets/product_card.dart`**:
```dart
import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../features/products/data/product_model.dart';

class ProductCard extends StatelessWidget {
  final ProductModel product;
  final VoidCallback? onTap;

  const ProductCard({super.key, required this.product, this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            AspectRatio(
              aspectRatio: 1,
              child: product.thumbnailUrl.isNotEmpty
                  ? CachedNetworkImage(
                      imageUrl: product.thumbnailUrl,
                      fit: BoxFit.cover,
                      placeholder: (_, __) => const Center(
                        child: CircularProgressIndicator(strokeWidth: 2),
                      ),
                      errorWidget: (_, __, ___) => const Icon(Icons.broken_image, size: 48),
                    )
                  : const Center(child: Icon(Icons.image_not_supported, size: 48)),
            ),
            Padding(
              padding: const EdgeInsets.all(8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    product.title,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    product.formattedPrice,
                    style: const TextStyle(
                      fontSize: 14,
                      color: Color(0xFFEE4D2D),
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## Step 5.6 — Search Feature

### 5.6.1 Search Result Model

**`lib/features/search/data/search_result_model.dart`**:
```dart
class SearchResultModel {
  final String id;
  final String title;
  final String thumbnailUrl;
  final String originalUrl;
  final double? price;
  final double score;
  final List<String> highlights;

  const SearchResultModel({
    required this.id,
    required this.title,
    required this.thumbnailUrl,
    required this.originalUrl,
    this.price,
    required this.score,
    required this.highlights,
  });

  factory SearchResultModel.fromJson(Map<String, dynamic> json) {
    final rawHighlights = json['highlights'] as Map<String, dynamic>? ?? {};
    final titleHighlights = rawHighlights['title'] as List? ?? [];
    return SearchResultModel(
      id: json['id'],
      title: json['title'],
      thumbnailUrl: json['thumbnail_url'] ?? '',
      originalUrl: json['original_url'],
      price: json['price']?.toDouble(),
      score: (json['score'] as num).toDouble(),
      highlights: titleHighlights.cast<String>(),
    );
  }
}
```

### 5.6.2 Search Provider

**`lib/features/search/domain/search_provider.dart`**:
```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import '../data/search_result_model.dart';
import '../../../core/dio_client.dart';

class SearchNotifier extends AutoDisposeAsyncNotifier<List<SearchResultModel>> {
  @override
  Future<List<SearchResultModel>> build() async => [];

  Future<void> search(String query) async {
    if (query.trim().isEmpty) {
      state = const AsyncData([]);
      return;
    }

    state = const AsyncLoading();
    try {
      final response = await DioClient.instance.get(
        '/search/',
        queryParameters: {'q': query, 'top': 20},
      );
      final items = (response.data['results'] as List)
          .map((e) => SearchResultModel.fromJson(e))
          .toList();
      state = AsyncData(items);
    } catch (e, st) {
      state = AsyncError(e, st);
    }
  }
}

final searchProvider = AsyncNotifierProvider.autoDispose<
    SearchNotifier, List<SearchResultModel>>(SearchNotifier.new);
```

### 5.6.3 Search Screen

**`lib/features/search/presentation/search_screen.dart`**:
```dart
import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../domain/search_provider.dart';
import '../data/search_result_model.dart';

class SearchScreen extends HookConsumerWidget {
  const SearchScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final controller = useTextEditingController();
    final searchState = ref.watch(searchProvider);

    // Debounced search
    useEffect(() {
      void listener() {
        Future.delayed(const Duration(milliseconds: 400), () {
          if (controller.text.isNotEmpty) {
            ref.read(searchProvider.notifier).search(controller.text);
          }
        });
      }
      controller.addListener(listener);
      return () => controller.removeListener(listener);
    }, [controller]);

    return Scaffold(
      appBar: AppBar(
        title: TextField(
          controller: controller,
          autofocus: true,
          style: const TextStyle(color: Colors.white),
          decoration: const InputDecoration(
            hintText: 'Tìm sản phẩm...',
            hintStyle: TextStyle(color: Colors.white70),
            border: InputBorder.none,
          ),
          onSubmitted: (q) => ref.read(searchProvider.notifier).search(q),
        ),
        actions: [
          if (controller.text.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.clear),
              onPressed: () {
                controller.clear();
                ref.read(searchProvider.notifier).search('');
              },
            ),
        ],
      ),
      body: searchState.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Lỗi tìm kiếm: $e')),
        data: (results) => results.isEmpty
            ? const Center(child: Text('Không tìm thấy kết quả'))
            : ListView.separated(
                itemCount: results.length,
                separatorBuilder: (_, __) => const Divider(height: 1),
                itemBuilder: (ctx, i) => _SearchResultTile(result: results[i]),
              ),
      ),
    );
  }
}

class _SearchResultTile extends StatelessWidget {
  final SearchResultModel result;
  const _SearchResultTile({required this.result});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: ClipRRect(
        borderRadius: BorderRadius.circular(6),
        child: result.thumbnailUrl.isNotEmpty
            ? CachedNetworkImage(
                imageUrl: result.thumbnailUrl,
                width: 60, height: 60, fit: BoxFit.cover,
                errorWidget: (_, __, ___) => const Icon(Icons.broken_image),
              )
            : const Icon(Icons.image_not_supported, size: 60),
      ),
      title: Text(result.title, maxLines: 2, overflow: TextOverflow.ellipsis),
      subtitle: result.price != null
          ? Text(
              '${result.price!.toStringAsFixed(0)}đ',
              style: const TextStyle(color: Color(0xFFEE4D2D), fontWeight: FontWeight.bold),
            )
          : null,
      trailing: Text(
        '${(result.score * 100).toStringAsFixed(0)}%',
        style: const TextStyle(color: Colors.grey, fontSize: 12),
      ),
    );
  }
}
```

---

## Step 5.7 — Run & Test Mobile App

```powershell
cd mobile

# Test trên Android emulator (localhost → 10.0.2.2)
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000/api

# Test trên iOS simulator (localhost)
flutter run --dart-define=API_BASE_URL=http://localhost:8000/api

# Build release APK để test
flutter build apk --dart-define=API_BASE_URL=https://app-shopee-aff-dev.azurewebsites.net/api
```

---

## Phase 4 Checklist

- [ ] `flutter pub get` — no dependency errors
- [ ] App builds và runs trên emulator
- [ ] Add Link screen: paste URL → xem status polling
- [ ] Product List screen: hiển thị grid với thumbnails
- [ ] Pull-to-refresh Product List hoạt động
- [ ] Search screen: gõ từ khóa → kết quả xuất hiện (<1s debounce)
- [ ] Product Card hiển thị đúng title, thumbnail, giá
- [ ] Error states hiển thị (khi backend offline, URL sai)
- [ ] Empty state khi không có sản phẩm

**Next:** [Phase 5 — Deployment & CI/CD](PLAN_PHASE_5_DEPLOY.md)
