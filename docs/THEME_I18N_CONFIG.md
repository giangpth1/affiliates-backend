# Theme & Internationalization Configuration

> **Auto-generated documentation**: File này sẽ được tạo và update khi implement theme system và i18n.

## Theme Configuration

### Current Theme Settings

**Active Themes**: Light, Dark
**Default Theme**: System (follows device settings)

### Color Palette

#### Light Theme
- Primary: `#EE4D2D` (Shopee Orange)
- Secondary: `#00BFA5` (Teal)
- Background: `#F5F5F5`
- Surface: `#FFFFFF`
- Text Primary: `#212121`

#### Dark Theme
- Primary: `#EE4D2D` (Same)
- Secondary: `#80CBC4` (Lighter Teal)
- Background: `#121212`
- Surface: `#1E1E1E`
- Text Primary: `#FFFFFF`

### Typography

**Font Family**: Inter (Google Fonts)
**Weights Used**: 400 (Regular), 600 (Semi-bold), 700 (Bold)

### Implementation Status

- [ ] Color definitions
- [ ] Typography system
- [ ] Theme provider (Riverpod)
- [ ] Light theme
- [ ] Dark theme
- [ ] Theme switcher UI
- [ ] Theme persistence
- [ ] Custom component themes (buttons, cards, etc.)
- [ ] Accessibility testing
- [ ] Screenshot generation for both themes

---

## Internationalization (i18n)

### Supported Languages

| Language | Code | Status | Coverage |
|---|---|---|---|
| Vietnamese | `vi` | ✅ Complete | 100% |
| English | `en` | ✅ Complete | 100% |
| Thai | `th` | ❌ Planned | 0% |
| Indonesian | `id` | ❌ Planned | 0% |

### Translation Statistics

**Total Keys**: 150
**Vietnamese**: 150/150 (100%)
**English**: 150/150 (100%)

### Backend i18n

**Django Settings**:
- Default Language: `vi` (Vietnamese)
- Supported: `vi`, `en`
- Locale Path: `backend/locale/`

**Translation Files**:
- `locale/vi/LC_MESSAGES/django.po` - Vietnamese
- `locale/en/LC_MESSAGES/django.po` - English

**API Language Detection**:
1. Query parameter: `?lang=vi`
2. HTTP Header: `Accept-Language: vi`
3. Cookie: `django_language=vi`
4. Default: `vi`

### Mobile i18n

**Flutter Package**: `easy_localization`

**Translation Files**:
- `assets/translations/vi.json` - Vietnamese (150 keys)
- `assets/translations/en.json` - English (150 keys)

**Language Persistence**: SharedPreferences (`user_locale` key)

### Date & Time Formats

#### Vietnamese (vi)
- Date: `dd/MM/yyyy` (e.g., `06/05/2026`)
- Time: `HH:mm` (e.g., `14:30`)
- DateTime: `dd/MM/yyyy HH:mm`

#### English (en)
- Date: `MMM d, yyyy` (e.g., `May 6, 2026`)
- Time: `h:mm a` (e.g., `2:30 PM`)
- DateTime: `MMM d, yyyy, h:mm a`

### Currency Formats

#### Vietnamese Dong (VND)
- Format: `#.###.### ₫` (e.g., `4.990.000 ₫`)
- Decimal places: 0
- Thousand separator: `.` (dot)

#### Other Currencies (Future)
- Thai Baht (THB): `฿ #,###.##`
- Indonesian Rupiah (IDR): `Rp #.###`

### Number Formats

#### Vietnamese
- Thousand separator: `.` (dot)
- Decimal separator: `,` (comma)
- Example: `1.234.567,89`

#### English
- Thousand separator: `,` (comma)
- Decimal separator: `.` (dot)
- Example: `1,234,567.89`

---

## Usage Examples

### Backend API

**Vietnamese Request**:
```bash
curl -X POST /api/links/ \
  -H "Accept-Language: vi" \
  -d '{"url": "invalid"}'
```

**Response**:
```json
{
  "detail": "URL affiliate Shopee không hợp lệ."
}
```

**English Request**:
```bash
curl -X POST /api/links/ \
  -H "Accept-Language: en" \
  -d '{"url": "invalid"}'
```

**Response**:
```json
{
  "detail": "Invalid Shopee affiliate URL."
}
```

### Mobile App

**Display translated text**:
```dart
Text('common.loading'.tr())
// Output (vi): "Đang tải..."
// Output (en): "Loading..."
```

**Switch language**:
```dart
// Change to English
context.setLocale(Locale('en'));

// Change to Vietnamese
context.setLocale(Locale('vi'));
```

**Get current language**:
```dart
final currentLang = context.locale.languageCode;
// Returns: 'vi' or 'en'
```

---

## Translation Keys Index

### Common Keys (common.*)
- `common.ok` - OK button
- `common.cancel` - Cancel button
- `common.save` - Save button
- `common.delete` - Delete button
- `common.loading` - Loading text
- `common.error` - Error text
- `common.success` - Success text

### Links Module (links.*)
- `links.title` - Links screen title
- `links.add_link` - Add link button
- `links.paste_link` - Paste link hint
- `links.status.pending` - Pending status
- `links.status.processing` - Processing status
- `links.status.done` - Done status
- `links.status.failed` - Failed status

### Products Module (products.*)
- `products.title` - Products screen title
- `products.no_products` - Empty state
- `products.price` - Price label
- `products.view_product` - View product action
- `products.delete_product` - Delete product action

### Search Module (search.*)
- `search.title` - Search screen title
- `search.hint` - Search input hint
- `search.no_results` - No results text
- `search.results_count` - Results count (with parameter)

### Settings Module (settings.*)
- `settings.title` - Settings screen title
- `settings.language` - Language option
- `settings.theme` - Theme option
- `settings.theme_light` - Light theme
- `settings.theme_dark` - Dark theme
- `settings.theme_auto` - Auto theme

### Errors (errors.*)
- `errors.network_error` - Network error
- `errors.server_error` - Server error
- `errors.unknown_error` - Unknown error
- `errors.scraping_failed` - Scraping failed

---

## Adding New Translations

### 1. Add Key to Translation Files

**vi.json**:
```json
{
  "new_feature": {
    "title": "Tính năng mới",
    "description": "Mô tả tính năng"
  }
}
```

**en.json**:
```json
{
  "new_feature": {
    "title": "New Feature",
    "description": "Feature description"
  }
}
```

### 2. Use in Code

```dart
Text('new_feature.title'.tr())
```

### 3. Update This Documentation

- [ ] Add key to "Translation Keys Index" section
- [ ] Update translation statistics
- [ ] Add usage example if complex

---

## Testing Translations

### Checklist

- [ ] All UI text uses translation keys (no hardcoded strings)
- [ ] Vietnamese translations accurate and natural
- [ ] English translations grammatically correct
- [ ] Date/time formats correct for each locale
- [ ] Currency formats display correctly
- [ ] Numbers formatted with correct separators
- [ ] Plurals handled correctly
- [ ] Long strings don't break UI layout
- [ ] Language switcher works
- [ ] Language preference persists after app restart

---

## Screenshot Gallery

### Light Theme

**Vietnamese**:
![Home Screen - Light - Vietnamese](screenshots/home_light_vi.png)
![Product List - Light - Vietnamese](screenshots/products_light_vi.png)

**English**:
![Home Screen - Light - English](screenshots/home_light_en.png)
![Product List - Light - English](screenshots/products_light_en.png)

### Dark Theme

**Vietnamese**:
![Home Screen - Dark - Vietnamese](screenshots/home_dark_vi.png)
![Product List - Dark - Vietnamese](screenshots/products_dark_vi.png)

**English**:
![Home Screen - Dark - English](screenshots/home_dark_en.png)
![Product List - Dark - English](screenshots/products_dark_en.png)

---

## Maintenance

### Update Translations

**Backend**:
```bash
cd backend
python manage.py makemessages -l vi -l en
# Edit .po files
python manage.py compilemessages
```

**Mobile**:
```bash
# Edit vi.json and en.json files
# No compilation needed - hot reload in development
```

### Translation Coverage Report

Run this script to check coverage:

```bash
# TODO: Create script to compare keys between vi.json and en.json
```

---

**Last updated**: [Auto-generated when implemented]
**Maintained by**: Development team
**Next review**: After each major feature addition

---

## Related Documentation

**Planning**:
- [Theme System Plan](../plans/THEME_SYSTEM.md) - Complete theme design guidelines
- [Internationalization Plan](../plans/INTERNATIONALIZATION.md) - i18n strategy

**Implementation**:
- Backend: `backend/locale/` - Django translation files
- Mobile: `mobile/assets/translations/` - Flutter translation files
- Mobile: `mobile/lib/shared/theme/` - Theme implementation
