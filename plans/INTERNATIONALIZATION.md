---
title: Internationalization (i18n) Strategy
version: 1.0.0
updated: 2026-05-06
---

# Internationalization (i18n) Strategy

## Overview

Document này định nghĩa chiến lược hỗ trợ đa ngôn ngữ (internationalization - i18n) cho cả backend và mobile app. Ngôn ngữ chính: **Tiếng Việt**, với support cho English và có thể mở rộng sang Thai, Indonesian.

---

## Supported Languages

### Phase 1 (MVP)
- 🇻🇳 **Vietnamese (vi)** - Primary language
- 🇬🇧 **English (en)** - Secondary language

### Phase 2 (Future)
- 🇹🇭 **Thai (th)** - Shopee Thailand expansion
- 🇮🇩 **Indonesian (id)** - Shopee Indonesia expansion
- 🇲🇾 **Malay (ms)** - Shopee Malaysia/Singapore

---

## Backend Internationalization

### Django i18n Setup

**Install**:
```bash
pip install django-modeltranslation
```

**config/settings/base.py**:
```python
from django.utils.translation import gettext_lazy as _

# Internationalization
LANGUAGE_CODE = 'vi'  # Default language
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('vi', _('Vietnamese')),
    ('en', _('English')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.locale.LocaleMiddleware',  # Add after SessionMiddleware
    # ... other middleware
]
```

### Translation Files

**Create translation files**:
```bash
# From backend/ directory
django-admin makemessages -l vi
django-admin makemessages -l en
```

**File structure**:
```
backend/locale/
├── vi/
│   └── LC_MESSAGES/
│       ├── django.po
│       └── django.mo
└── en/
    └── LC_MESSAGES/
        ├── django.po
        └── django.mo
```

### API Response Translation

**Example usage**:
```python
# apps/core/exceptions.py
from django.utils.translation import gettext_lazy as _

class InvalidShopeeURL(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Invalid Shopee affiliate URL.')

class ScrapingFailed(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = _('Failed to scrape product data.')
```

**Error messages in Vietnamese**:
```python
# locale/vi/LC_MESSAGES/django.po
msgid "Invalid Shopee affiliate URL."
msgstr "URL affiliate Shopee không hợp lệ."

msgid "Failed to scrape product data."
msgstr "Không thể lấy thông tin sản phẩm."
```

**Error messages in English**:
```python
# locale/en/LC_MESSAGES/django.po
msgid "Invalid Shopee affiliate URL."
msgstr "Invalid Shopee affiliate URL."

msgid "Failed to scrape product data."
msgstr "Failed to scrape product data."
```

### Language Detection

**Via Accept-Language Header**:
```python
# Client sends:
# Accept-Language: vi

# Or via query param:
GET /api/products/?lang=vi
```

**Middleware automatically detects** từ:
1. Query parameter `?lang=vi`
2. HTTP header `Accept-Language: vi`
3. Cookie `django_language=vi`
4. Default setting `LANGUAGE_CODE = 'vi'`

### API Examples

**Request with language header**:
```bash
curl -X POST /api/links/ \
  -H "Accept-Language: vi" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://shp.ee/invalid"}'
```

**Response in Vietnamese**:
```json
{
  "detail": "URL affiliate Shopee không hợp lệ."
}
```

**Request with English**:
```bash
curl -X POST /api/links/ \
  -H "Accept-Language: en" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://shp.ee/invalid"}'
```

**Response in English**:
```json
{
  "detail": "Invalid Shopee affiliate URL."
}
```

---

## Mobile App Internationalization

### Flutter i18n Setup

**Dependencies** (`pubspec.yaml`):
```yaml
dependencies:
  flutter_localizations:
    sdk: flutter
  intl: ^0.19.0
  easy_localization: ^3.0.7  # Recommended i18n package

dev_dependencies:
  easy_localization_loader: ^2.0.2
```

**Directory structure**:
```
mobile/assets/
└── translations/
    ├── vi.json
    └── en.json
```

**pubspec.yaml** (assets):
```yaml
flutter:
  assets:
    - assets/translations/
```

### Translation Files

**assets/translations/vi.json**:
```json
{
  "app": {
    "title": "Quản lý Link Shopee",
    "description": "Quản lý link affiliate Shopee của bạn"
  },
  "common": {
    "ok": "OK",
    "cancel": "Hủy",
    "confirm": "Xác nhận",
    "delete": "Xóa",
    "edit": "Sửa",
    "save": "Lưu",
    "search": "Tìm kiếm",
    "loading": "Đang tải...",
    "error": "Lỗi",
    "success": "Thành công",
    "retry": "Thử lại"
  },
  "auth": {
    "login": "Đăng nhập",
    "logout": "Đăng xuất",
    "email": "Email",
    "password": "Mật khẩu"
  },
  "links": {
    "title": "Link của tôi",
    "add_link": "Thêm link mới",
    "paste_link": "Dán link Shopee",
    "link_added": "Đã thêm link thành công",
    "invalid_url": "URL không hợp lệ",
    "status": {
      "pending": "Đang chờ",
      "processing": "Đang xử lý",
      "done": "Hoàn thành",
      "failed": "Thất bại"
    }
  },
  "products": {
    "title": "Sản phẩm",
    "no_products": "Chưa có sản phẩm nào",
    "price": "Giá",
    "view_product": "Xem sản phẩm",
    "delete_product": "Xóa sản phẩm",
    "delete_confirm": "Bạn có chắc muốn xóa sản phẩm này?"
  },
  "search": {
    "title": "Tìm kiếm",
    "hint": "Tìm sản phẩm...",
    "no_results": "Không tìm thấy kết quả",
    "results_count": "{count} kết quả"
  },
  "settings": {
    "title": "Cài đặt",
    "language": "Ngôn ngữ",
    "theme": "Giao diện",
    "theme_light": "Sáng",
    "theme_dark": "Tối",
    "theme_auto": "Tự động"
  },
  "errors": {
    "network_error": "Lỗi kết nối mạng",
    "server_error": "Lỗi máy chủ",
    "unknown_error": "Lỗi không xác định",
    "scraping_failed": "Không thể lấy thông tin sản phẩm"
  }
}
```

**assets/translations/en.json**:
```json
{
  "app": {
    "title": "Shopee Link Manager",
    "description": "Manage your Shopee affiliate links"
  },
  "common": {
    "ok": "OK",
    "cancel": "Cancel",
    "confirm": "Confirm",
    "delete": "Delete",
    "edit": "Edit",
    "save": "Save",
    "search": "Search",
    "loading": "Loading...",
    "error": "Error",
    "success": "Success",
    "retry": "Retry"
  },
  "auth": {
    "login": "Login",
    "logout": "Logout",
    "email": "Email",
    "password": "Password"
  },
  "links": {
    "title": "My Links",
    "add_link": "Add New Link",
    "paste_link": "Paste Shopee Link",
    "link_added": "Link added successfully",
    "invalid_url": "Invalid URL",
    "status": {
      "pending": "Pending",
      "processing": "Processing",
      "done": "Done",
      "failed": "Failed"
    }
  },
  "products": {
    "title": "Products",
    "no_products": "No products yet",
    "price": "Price",
    "view_product": "View Product",
    "delete_product": "Delete Product",
    "delete_confirm": "Are you sure you want to delete this product?"
  },
  "search": {
    "title": "Search",
    "hint": "Search products...",
    "no_results": "No results found",
    "results_count": "{count} results"
  },
  "settings": {
    "title": "Settings",
    "language": "Language",
    "theme": "Theme",
    "theme_light": "Light",
    "theme_dark": "Dark",
    "theme_auto": "Auto"
  },
  "errors": {
    "network_error": "Network connection error",
    "server_error": "Server error",
    "unknown_error": "Unknown error",
    "scraping_failed": "Failed to fetch product information"
  }
}
```

### App Initialization

**lib/main.dart**:
```dart
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:easy_localization/easy_localization.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await EasyLocalization.ensureInitialized();

  runApp(
    EasyLocalization(
      supportedLocales: const [
        Locale('vi', 'VN'),
        Locale('en', 'US'),
      ],
      path: 'assets/translations',
      fallbackLocale: const Locale('vi', 'VN'),
      startLocale: const Locale('vi', 'VN'),
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'app.title'.tr(),
      
      // Localization delegates
      localizationsDelegates: [
        ...context.localizationDelegates,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: context.supportedLocales,
      locale: context.locale,
      
      theme: AppTheme.light,
      home: const HomeScreen(),
    );
  }
}
```

### Using Translations

**Simple translation**:
```dart
Text('common.loading'.tr())
// Output (vi): "Đang tải..."
// Output (en): "Loading..."
```

**Translation with parameters**:
```dart
Text('search.results_count'.tr(namedArgs: {'count': '42'}))
// Output (vi): "42 kết quả"
// Output (en): "42 results"
```

**Plural forms**:
```dart
Text('products.count'.plural(productCount))
```

**Translation in JSON** (for plurals):
```json
{
  "products": {
    "count": {
      "zero": "Không có sản phẩm",
      "one": "1 sản phẩm",
      "other": "{} sản phẩm"
    }
  }
}
```

### Language Switcher Widget

**lib/shared/widgets/language_switcher.dart**:
```dart
import 'package:flutter/material.dart';
import 'package:easy_localization/easy_localization.dart';

class LanguageSwitcher extends StatelessWidget {
  const LanguageSwitcher({super.key});

  @override
  Widget build(BuildContext context) {
    return PopupMenuButton<Locale>(
      icon: const Icon(Icons.language),
      tooltip: 'settings.language'.tr(),
      onSelected: (Locale locale) {
        context.setLocale(locale);
      },
      itemBuilder: (BuildContext context) => [
        PopupMenuItem(
          value: const Locale('vi', 'VN'),
          child: Row(
            children: [
              Text('🇻🇳'),
              SizedBox(width: 8),
              Text('Tiếng Việt'),
              if (context.locale.languageCode == 'vi')
                Icon(Icons.check, color: AppColors.primary),
            ],
          ),
        ),
        PopupMenuItem(
          value: const Locale('en', 'US'),
          child: Row(
            children: [
              Text('🇬🇧'),
              SizedBox(width: 8),
              Text('English'),
              if (context.locale.languageCode == 'en')
                Icon(Icons.check, color: AppColors.primary),
            ],
          ),
        ),
      ],
    );
  }
}
```

### Language Persistence

**Save language preference**:
```dart
// lib/core/preferences.dart
import 'package:shared_preferences/shared_preferences.dart';
import 'package:easy_localization/easy_localization.dart';

class LocalePreferences {
  static const String _localeKey = 'user_locale';
  
  static Future<void> saveLocale(Locale locale) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_localeKey, locale.languageCode);
  }
  
  static Future<Locale?> getSavedLocale() async {
    final prefs = await SharedPreferences.getInstance();
    final languageCode = prefs.getString(_localeKey);
    
    if (languageCode == null) return null;
    
    return Locale(languageCode);
  }
}
```

**Load on app start**:
```dart
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await EasyLocalization.ensureInitialized();
  
  // Load saved locale
  final savedLocale = await LocalePreferences.getSavedLocale();
  
  runApp(
    EasyLocalization(
      supportedLocales: const [Locale('vi'), Locale('en')],
      path: 'assets/translations',
      fallbackLocale: const Locale('vi'),
      startLocale: savedLocale ?? const Locale('vi'),
      child: const MyApp(),
    ),
  );
}
```

---

## Date & Time Formatting

### Backend (Django)

**Vietnamese format**:
```python
from django.utils import formats
from django.utils.translation import activate

activate('vi')
date_str = formats.date_format(datetime.now(), "SHORT_DATETIME_FORMAT")
# Output: "06/05/2026 14:30"
```

**English format**:
```python
activate('en')
date_str = formats.date_format(datetime.now(), "SHORT_DATETIME_FORMAT")
# Output: "May 6, 2026, 2:30 p.m."
```

### Mobile (Flutter)

**Using intl package**:
```dart
import 'package:intl/intl.dart';

// Vietnamese
final viFormat = DateFormat.yMd('vi').add_jm();
print(viFormat.format(DateTime.now()));
// Output: "06/05/2026 14:30"

// English
final enFormat = DateFormat.yMMMd('en').add_jm();
print(enFormat.format(DateTime.now()));
// Output: "May 6, 2026 2:30 PM"
```

**Relative time**:
```dart
import 'package:timeago/timeago.dart' as timeago;

// Configure Vietnamese
timeago.setLocaleMessages('vi', timeago.ViMessages());

// Usage
final timeAgo = timeago.format(
  DateTime.now().subtract(Duration(hours: 2)),
  locale: 'vi',
);
// Output: "2 giờ trước"
```

---

## Number & Currency Formatting

### Backend

**Vietnamese number format**:
```python
from django.utils.formats import number_format
from django.utils.translation import activate

activate('vi')
formatted = number_format(1234567.89, decimal_pos=0)
# Output: "1.234.568" (uses dot as thousand separator)
```

**Currency (VND)**:
```python
def format_vnd(amount):
    return f"{number_format(amount, decimal_pos=0)} ₫"

# Usage
price = format_vnd(4990000)
# Output: "4.990.000 ₫"
```

### Mobile

**Vietnamese currency**:
```dart
import 'package:intl/intl.dart';

final vndFormat = NumberFormat.currency(
  locale: 'vi',
  symbol: '₫',
  decimalDigits: 0,
);

print(vndFormat.format(4990000));
// Output: "4.990.000 ₫"
```

**Compact number format**:
```dart
final compactFormat = NumberFormat.compact(locale: 'vi');
print(compactFormat.format(1500000));
// Output: "1,5 Tr" (1.5 triệu)
```

---

## Right-to-Left (RTL) Support

**Note**: Vietnamese và English đều là LTR (Left-to-Right), nhưng chuẩn bị sẵn cho Arabic/Hebrew (future):

```dart
// lib/main.dart
MaterialApp(
  // ...
  builder: (context, child) {
    return Directionality(
      textDirection: TextDirection.ltr, // Or rtl for Arabic/Hebrew
      child: child!,
    );
  },
)
```

---

## Testing i18n

### Backend Tests

```python
# tests/test_i18n.py
from django.test import TestCase
from django.utils.translation import activate

class InternationalizationTest(TestCase):
    def test_vietnamese_error_message(self):
        activate('vi')
        response = self.client.post('/api/links/', {
            'url': 'invalid-url'
        })
        self.assertIn('không hợp lệ', response.json()['detail'].lower())
    
    def test_english_error_message(self):
        activate('en')
        response = self.client.post('/api/links/', {
            'url': 'invalid-url'
        })
        self.assertIn('invalid', response.json()['detail'].lower())
```

### Mobile Tests

```dart
// test/i18n_test.dart
void main() {
  testWidgets('Vietnamese translations work', (tester) async {
    await tester.pumpWidget(
      EasyLocalization(
        supportedLocales: [Locale('vi')],
        path: 'assets/translations',
        fallbackLocale: Locale('vi'),
        child: MyApp(),
      ),
    );
    
    await tester.pumpAndSettle();
    
    expect(find.text('Tìm kiếm'), findsOneWidget);
  });
}
```

---

## Translation Workflow

### 1. Extract Translatable Strings

**Backend**:
```bash
cd backend
python manage.py makemessages -l vi -l en
```

**Mobile**: Use `easy_localization` generator (optional):
```bash
flutter pub run easy_localization:generate -S assets/translations
```

### 2. Translate Strings

Edit `.po` files (backend) or `.json` files (mobile).

**Tools**:
- **Poedit** - For .po files (Django)
- **VS Code i18n Ally** - For JSON files (Flutter)

### 3. Compile Translations

**Backend**:
```bash
python manage.py compilemessages
```

**Mobile**: Auto-compiled by `easy_localization` at runtime.

### 4. Test Translations

- Switch language in app
- Verify all UI text translated
- Check formatting (dates, numbers, currency)
- Test edge cases (long strings, plurals)

---

## Best Practices

### 1. Use Translation Keys, Not Hardcoded Text

**❌ Bad**:
```dart
Text('Đang tải...')
```

**✅ Good**:
```dart
Text('common.loading'.tr())
```

### 2. Provide Context in Keys

**❌ Bad**:
```json
{"save": "Lưu"}
```

**✅ Good**:
```json
{
  "buttons": {
    "save": "Lưu"
  }
}
```

### 3. Handle Plurals Properly

**Vietnamese** doesn't have strict plural forms like English, but use descriptive text:

```json
{
  "products": {
    "count_zero": "Không có sản phẩm",
    "count_one": "1 sản phẩm",
    "count_other": "{count} sản phẩm"
  }
}
```

### 4. Keep Translations Organized

Group by feature/screen:

```json
{
  "home": {...},
  "products": {...},
  "search": {...},
  "settings": {...}
}
```

### 5. Use Placeholders for Dynamic Content

```json
{
  "greeting": "Xin chào, {name}!",
  "product_price": "{price} ₫"
}
```

---

## Localization Checklist

- [ ] Setup Django i18n middleware
- [ ] Create locale files (vi, en)
- [ ] Add `easy_localization` to Flutter
- [ ] Create translation JSON files
- [ ] Translate all UI strings
- [ ] Implement language switcher
- [ ] Add language persistence
- [ ] Format dates/numbers correctly
- [ ] Test all languages
- [ ] Update documentation
- [ ] Add screenshots for each language (App Store)

---

## Future Enhancements

### Dynamic Content Translation

**Products**: Store titles in original language (Vietnamese), optionally translate via Azure Translator API:

```python
# services/translator.py (optional)
from azure.ai.translation.text import TextTranslationClient

def translate_product_title(title: str, target_lang: str) -> str:
    client = TextTranslationClient(...)
    result = client.translate([title], to=[target_lang])
    return result[0].translations[0].text
```

### Crowdsourced Translations

Use services like:
- **Crowdin** - Community translation platform
- **Lokalise** - Translation management
- **POEditor** - Collaborative translation

---

**Last updated**: 2026-05-06
**Status**: Planning phase
**Next steps**: Implement during Phase 4 (Mobile App Development)
