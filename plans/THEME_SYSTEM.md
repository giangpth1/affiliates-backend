---
title: Theme System & Design Guidelines
version: 1.0.0
updated: 2026-05-06
---

# Theme System & Design Guidelines

## Overview

Document này định nghĩa theme system cho Flutter mobile app, bao gồm color schemes, typography, spacing, và component styling. Backend không có UI nên không cần theme system.

---

## Design Principles

### 1. Brand Identity
- **Primary color**: Shopee Orange (`#EE4D2D`) - recognizable, energetic
- **Secondary color**: Deep Orange (`#FF6F3D`) - warm, inviting
- **Accent color**: Teal (`#00BFA5`) - fresh, modern

### 2. Accessibility
- WCAG 2.1 Level AA compliance
- Minimum contrast ratio: 4.5:1 for text
- Color-blind friendly palette
- Support for system accessibility settings

### 3. Consistency
- Unified design language across all screens
- Reusable components với theme support
- Predictable user experience

---

## Color Palette

### Light Theme (Default)

```dart
// lib/shared/theme/colors.dart
class AppColors {
  // Primary colors
  static const Color primary = Color(0xFFEE4D2D);      // Shopee Orange
  static const Color primaryDark = Color(0xFFD84315);  // Darker orange
  static const Color primaryLight = Color(0xFFFF6F3D); // Lighter orange
  
  // Secondary colors
  static const Color secondary = Color(0xFF00BFA5);    // Teal
  static const Color secondaryDark = Color(0xFF00897B);
  static const Color secondaryLight = Color(0xFF80CBC4);
  
  // Background colors
  static const Color background = Color(0xFFF5F5F5);   // Light gray
  static const Color surface = Color(0xFFFFFFFF);      // White
  static const Color cardBackground = Color(0xFFFFFFFF);
  
  // Text colors
  static const Color textPrimary = Color(0xFF212121);  // Almost black
  static const Color textSecondary = Color(0xFF757575); // Gray
  static const Color textHint = Color(0xFFBDBDBD);     // Light gray
  static const Color textOnPrimary = Color(0xFFFFFFFF); // White
  
  // Status colors
  static const Color success = Color(0xFF4CAF50);      // Green
  static const Color error = Color(0xFFF44336);        // Red
  static const Color warning = Color(0xFFFF9800);      // Orange
  static const Color info = Color(0xFF2196F3);         // Blue
  
  // Border & divider
  static const Color border = Color(0xFFE0E0E0);
  static const Color divider = Color(0xFFEEEEEE);
  
  // Overlay & shadow
  static const Color overlay = Color(0x33000000);      // 20% black
  static const Color shadow = Color(0x1F000000);       // 12% black
}
```

### Dark Theme

```dart
class AppColorsDark {
  // Primary colors (same as light)
  static const Color primary = Color(0xFFEE4D2D);
  static const Color primaryDark = Color(0xFFD84315);
  static const Color primaryLight = Color(0xFFFF6F3D);
  
  // Secondary colors (adjusted for dark mode)
  static const Color secondary = Color(0xFF80CBC4);    // Lighter teal
  static const Color secondaryDark = Color(0xFF4DB6AC);
  static const Color secondaryLight = Color(0xFFB2DFDB);
  
  // Background colors
  static const Color background = Color(0xFF121212);   // Near black
  static const Color surface = Color(0xFF1E1E1E);      // Dark gray
  static const Color cardBackground = Color(0xFF2C2C2C);
  
  // Text colors
  static const Color textPrimary = Color(0xFFFFFFFF);  // White
  static const Color textSecondary = Color(0xFFB0B0B0); // Light gray
  static const Color textHint = Color(0xFF6E6E6E);     // Gray
  static const Color textOnPrimary = Color(0xFFFFFFFF);
  
  // Status colors (same as light)
  static const Color success = Color(0xFF4CAF50);
  static const Color error = Color(0xFFF44336);
  static const Color warning = Color(0xFFFF9800);
  static const Color info = Color(0xFF2196F3);
  
  // Border & divider
  static const Color border = Color(0xFF3E3E3E);
  static const Color divider = Color(0xFF2C2C2C);
  
  // Overlay & shadow
  static const Color overlay = Color(0x66000000);      // 40% black
  static const Color shadow = Color(0x33000000);       // 20% black
}
```

---

## Typography

### Font Family

**Primary**: **Inter** (Google Fonts)
- Modern, highly readable
- Excellent Vietnamese character support
- Wide range of weights (300-900)

**Fallback**: System default (Roboto on Android, SF Pro on iOS)

### Text Styles

```dart
// lib/shared/theme/text_styles.dart
class AppTextStyles {
  static const String fontFamily = 'Inter';
  
  // Headings
  static const TextStyle h1 = TextStyle(
    fontFamily: fontFamily,
    fontSize: 32,
    fontWeight: FontWeight.w700, // Bold
    height: 1.25,
    letterSpacing: -0.5,
  );
  
  static const TextStyle h2 = TextStyle(
    fontFamily: fontFamily,
    fontSize: 24,
    fontWeight: FontWeight.w600, // Semi-bold
    height: 1.33,
    letterSpacing: -0.3,
  );
  
  static const TextStyle h3 = TextStyle(
    fontFamily: fontFamily,
    fontSize: 20,
    fontWeight: FontWeight.w600,
    height: 1.4,
    letterSpacing: -0.2,
  );
  
  static const TextStyle h4 = TextStyle(
    fontFamily: fontFamily,
    fontSize: 18,
    fontWeight: FontWeight.w600,
    height: 1.44,
  );
  
  // Body text
  static const TextStyle bodyLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w400, // Regular
    height: 1.5,
  );
  
  static const TextStyle bodyMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w400,
    height: 1.5,
  );
  
  static const TextStyle bodySmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    fontWeight: FontWeight.w400,
    height: 1.5,
  );
  
  // Special
  static const TextStyle button = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w600,
    height: 1.43,
    letterSpacing: 0.5,
  );
  
  static const TextStyle caption = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    fontWeight: FontWeight.w400,
    height: 1.33,
    letterSpacing: 0.4,
  );
  
  static const TextStyle overline = TextStyle(
    fontFamily: fontFamily,
    fontSize: 10,
    fontWeight: FontWeight.w500,
    height: 1.6,
    letterSpacing: 1.5,
  );
}
```

---

## Spacing System

### 8pt Grid System

```dart
// lib/shared/theme/spacing.dart
class AppSpacing {
  static const double xs = 4.0;    // Extra small
  static const double sm = 8.0;    // Small
  static const double md = 16.0;   // Medium (base)
  static const double lg = 24.0;   // Large
  static const double xl = 32.0;   // Extra large
  static const double xxl = 48.0;  // XX Large
  static const double xxxl = 64.0; // XXX Large
  
  // Semantic spacing
  static const double cardPadding = md;
  static const double screenPadding = md;
  static const double sectionSpacing = lg;
  static const double elementSpacing = sm;
}
```

### Border Radius

```dart
class AppRadius {
  static const double none = 0.0;
  static const double sm = 4.0;
  static const double md = 8.0;
  static const double lg = 12.0;
  static const double xl = 16.0;
  static const double xxl = 24.0;
  static const double circular = 999.0; // Fully rounded
  
  // Semantic radius
  static const double card = lg;
  static const double button = md;
  static const double input = md;
  static const double sheet = xl;
}
```

---

## Theme Implementation

### ThemeData Configuration

```dart
// lib/shared/theme/app_theme.dart
import 'package:flutter/material.dart';
import 'colors.dart';
import 'text_styles.dart';
import 'spacing.dart';

class AppTheme {
  static ThemeData get light => ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    
    // Color scheme
    colorScheme: ColorScheme.light(
      primary: AppColors.primary,
      primaryContainer: AppColors.primaryLight,
      secondary: AppColors.secondary,
      secondaryContainer: AppColors.secondaryLight,
      surface: AppColors.surface,
      background: AppColors.background,
      error: AppColors.error,
      onPrimary: AppColors.textOnPrimary,
      onSecondary: AppColors.textOnPrimary,
      onSurface: AppColors.textPrimary,
      onBackground: AppColors.textPrimary,
      onError: AppColors.textOnPrimary,
    ),
    
    // Typography
    textTheme: TextTheme(
      displayLarge: AppTextStyles.h1,
      displayMedium: AppTextStyles.h2,
      displaySmall: AppTextStyles.h3,
      headlineMedium: AppTextStyles.h4,
      bodyLarge: AppTextStyles.bodyLarge,
      bodyMedium: AppTextStyles.bodyMedium,
      bodySmall: AppTextStyles.bodySmall,
      labelLarge: AppTextStyles.button,
      labelSmall: AppTextStyles.caption,
    ),
    
    // AppBar theme
    appBarTheme: AppBarTheme(
      backgroundColor: AppColors.primary,
      foregroundColor: AppColors.textOnPrimary,
      elevation: 0,
      centerTitle: true,
      titleTextStyle: AppTextStyles.h4.copyWith(
        color: AppColors.textOnPrimary,
      ),
    ),
    
    // Card theme
    cardTheme: CardTheme(
      color: AppColors.cardBackground,
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppRadius.card),
      ),
      margin: EdgeInsets.all(AppSpacing.sm),
    ),
    
    // Button themes
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: AppColors.primary,
        foregroundColor: AppColors.textOnPrimary,
        textStyle: AppTextStyles.button,
        padding: EdgeInsets.symmetric(
          horizontal: AppSpacing.lg,
          vertical: AppSpacing.md,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.button),
        ),
      ),
    ),
    
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: AppColors.primary,
        textStyle: AppTextStyles.button,
        padding: EdgeInsets.symmetric(
          horizontal: AppSpacing.lg,
          vertical: AppSpacing.md,
        ),
        side: BorderSide(color: AppColors.primary, width: 1.5),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.button),
        ),
      ),
    ),
    
    // Input decoration theme
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: AppColors.surface,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppRadius.input),
        borderSide: BorderSide(color: AppColors.border),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppRadius.input),
        borderSide: BorderSide(color: AppColors.border),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppRadius.input),
        borderSide: BorderSide(color: AppColors.primary, width: 2),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppRadius.input),
        borderSide: BorderSide(color: AppColors.error),
      ),
      contentPadding: EdgeInsets.all(AppSpacing.md),
    ),
    
    // Bottom navigation bar theme
    bottomNavigationBarTheme: BottomNavigationBarThemeData(
      backgroundColor: AppColors.surface,
      selectedItemColor: AppColors.primary,
      unselectedItemColor: AppColors.textSecondary,
      type: BottomNavigationBarType.fixed,
      elevation: 8,
    ),
  );
  
  static ThemeData get dark => ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    
    colorScheme: ColorScheme.dark(
      primary: AppColorsDark.primary,
      primaryContainer: AppColorsDark.primaryDark,
      secondary: AppColorsDark.secondary,
      secondaryContainer: AppColorsDark.secondaryDark,
      surface: AppColorsDark.surface,
      background: AppColorsDark.background,
      error: AppColorsDark.error,
      onPrimary: AppColorsDark.textOnPrimary,
      onSecondary: AppColorsDark.textPrimary,
      onSurface: AppColorsDark.textPrimary,
      onBackground: AppColorsDark.textPrimary,
      onError: AppColorsDark.textOnPrimary,
    ),
    
    // Similar configuration for dark theme...
  );
}
```

---

## Theme Management with Riverpod

### Theme State Provider

```dart
// lib/shared/theme/theme_provider.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

enum ThemeMode { light, dark, system }

class ThemeNotifier extends StateNotifier<ThemeMode> {
  ThemeNotifier() : super(ThemeMode.system) {
    _loadTheme();
  }
  
  Future<void> _loadTheme() async {
    final prefs = await SharedPreferences.getInstance();
    final themeName = prefs.getString('theme_mode') ?? 'system';
    state = ThemeMode.values.firstWhere(
      (e) => e.name == themeName,
      orElse: () => ThemeMode.system,
    );
  }
  
  Future<void> setTheme(ThemeMode mode) async {
    state = mode;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('theme_mode', mode.name);
  }
}

final themeProvider = StateNotifierProvider<ThemeNotifier, ThemeMode>(
  (ref) => ThemeNotifier(),
);
```

### App Integration

```dart
// lib/main.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'shared/theme/app_theme.dart';
import 'shared/theme/theme_provider.dart';

void main() {
  runApp(const ProviderScope(child: MyApp()));
}

class MyApp extends ConsumerWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeProvider);
    
    return MaterialApp(
      title: 'Shopee Affiliate Manager',
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      themeMode: themeMode == ThemeMode.system
          ? ThemeMode.system
          : themeMode == ThemeMode.dark
              ? ThemeMode.dark
              : ThemeMode.light,
      // ... rest of app config
    );
  }
}
```

### Theme Switcher Widget

```dart
// lib/shared/widgets/theme_switcher.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../theme/theme_provider.dart' as theme_provider;

class ThemeSwitcher extends ConsumerWidget {
  const ThemeSwitcher({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentTheme = ref.watch(theme_provider.themeProvider);
    
    return SegmentedButton<theme_provider.ThemeMode>(
      segments: const [
        ButtonSegment(
          value: theme_provider.ThemeMode.light,
          icon: Icon(Icons.light_mode),
          label: Text('Light'),
        ),
        ButtonSegment(
          value: theme_provider.ThemeMode.dark,
          icon: Icon(Icons.dark_mode),
          label: Text('Dark'),
        ),
        ButtonSegment(
          value: theme_provider.ThemeMode.system,
          icon: Icon(Icons.brightness_auto),
          label: Text('Auto'),
        ),
      ],
      selected: {currentTheme},
      onSelectionChanged: (Set<theme_provider.ThemeMode> newSelection) {
        ref.read(theme_provider.themeProvider.notifier)
            .setTheme(newSelection.first);
      },
    );
  }
}
```

---

## Component Styling Guidelines

### Buttons

```dart
// Primary action button
ElevatedButton(
  onPressed: () {},
  child: Text('Submit'),
)

// Secondary action button
OutlinedButton(
  onPressed: () {},
  child: Text('Cancel'),
)

// Text button (low emphasis)
TextButton(
  onPressed: () {},
  child: Text('Learn More'),
)
```

### Cards

```dart
Card(
  child: Padding(
    padding: EdgeInsets.all(AppSpacing.md),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Product Title', style: AppTextStyles.h4),
        SizedBox(height: AppSpacing.sm),
        Text('Description', style: AppTextStyles.bodyMedium),
      ],
    ),
  ),
)
```

### Bottom Sheets

```dart
void showCustomSheet(BuildContext context) {
  showModalBottomSheet(
    context: context,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(
        top: Radius.circular(AppRadius.sheet),
      ),
    ),
    builder: (context) => Container(
      padding: EdgeInsets.all(AppSpacing.lg),
      child: YourContent(),
    ),
  );
}
```

---

## Responsive Design

### Breakpoints

```dart
// lib/shared/theme/breakpoints.dart
class AppBreakpoints {
  static const double mobile = 600;    // < 600px
  static const double tablet = 900;    // 600-900px
  static const double desktop = 1200;  // > 900px
}

class ResponsiveLayout extends StatelessWidget {
  final Widget mobile;
  final Widget? tablet;
  final Widget? desktop;

  const ResponsiveLayout({
    super.key,
    required this.mobile,
    this.tablet,
    this.desktop,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth >= AppBreakpoints.desktop) {
          return desktop ?? tablet ?? mobile;
        } else if (constraints.maxWidth >= AppBreakpoints.tablet) {
          return tablet ?? mobile;
        }
        return mobile;
      },
    );
  }
}
```

---

## Icons & Images

### Icon Set

**Primary**: Material Icons (built-in)
**Custom**: SVG icons via `flutter_svg`

```dart
// Common icons mapping
class AppIcons {
  static const IconData home = Icons.home_outlined;
  static const IconData search = Icons.search;
  static const IconData add = Icons.add;
  static const IconData favorite = Icons.favorite_outline;
  static const IconData share = Icons.share;
  static const IconData delete = Icons.delete_outline;
  static const IconData edit = Icons.edit_outlined;
  static const IconData settings = Icons.settings_outlined;
}
```

### Image Loading

```dart
// lib/shared/widgets/thumbnail_image.dart
import 'package:cached_network_image/cached_network_image.dart';

class ThumbnailImage extends StatelessWidget {
  final String imageUrl;
  final double? width;
  final double? height;

  const ThumbnailImage({
    super.key,
    required this.imageUrl,
    this.width,
    this.height,
  });

  @override
  Widget build(BuildContext context) {
    return CachedNetworkImage(
      imageUrl: imageUrl,
      width: width,
      height: height,
      fit: BoxFit.cover,
      placeholder: (context, url) => Container(
        color: AppColors.background,
        child: Center(
          child: CircularProgressIndicator(),
        ),
      ),
      errorWidget: (context, url, error) => Container(
        color: AppColors.background,
        child: Icon(Icons.broken_image, color: AppColors.textHint),
      ),
    );
  }
}
```

---

## Animations & Transitions

### Standard Durations

```dart
class AppAnimations {
  static const Duration fast = Duration(milliseconds: 150);
  static const Duration normal = Duration(milliseconds: 300);
  static const Duration slow = Duration(milliseconds: 500);
  
  static const Curve defaultCurve = Curves.easeInOut;
  static const Curve emphasizedCurve = Curves.easeOutCubic;
}
```

### Page Transitions

```dart
// lib/app/router.dart
PageRouteBuilder customPageRoute(Widget page) {
  return PageRouteBuilder(
    pageBuilder: (context, animation, secondaryAnimation) => page,
    transitionDuration: AppAnimations.normal,
    transitionsBuilder: (context, animation, secondaryAnimation, child) {
      const begin = Offset(1.0, 0.0);
      const end = Offset.zero;
      final tween = Tween(begin: begin, end: end);
      final offsetAnimation = animation.drive(tween.chain(
        CurveTween(curve: AppAnimations.emphasizedCurve),
      ));
      
      return SlideTransition(
        position: offsetAnimation,
        child: child,
      );
    },
  );
}
```

---

## Accessibility

### Semantic Labels

```dart
// Always provide semantic labels for icons
IconButton(
  icon: Icon(Icons.add),
  onPressed: () {},
  tooltip: 'Add new link',
  semanticLabel: 'Add new affiliate link',
)
```

### Text Scaling

```dart
// Support user's text scale preferences
Text(
  'Product Title',
  style: AppTextStyles.h4,
  maxLines: 2,
  overflow: TextOverflow.ellipsis,
  // Flutter automatically respects MediaQuery.textScaleFactor
)
```

### Focus Management

```dart
// Proper focus order for forms
FocusScope.of(context).requestFocus(nextFocusNode);
```

---

## Testing Theme

### Theme Test

```dart
// test/theme_test.dart
void main() {
  testWidgets('Light theme has correct colors', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.light,
        home: Builder(
          builder: (context) {
            final theme = Theme.of(context);
            expect(theme.colorScheme.primary, AppColors.primary);
            expect(theme.brightness, Brightness.light);
            return Container();
          },
        ),
      ),
    );
  });
  
  testWidgets('Dark theme has correct colors', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.dark,
        home: Builder(
          builder: (context) {
            final theme = Theme.of(context);
            expect(theme.colorScheme.primary, AppColorsDark.primary);
            expect(theme.brightness, Brightness.dark);
            return Container();
          },
        ),
      ),
    );
  });
}
```

---

## Dependencies

Add to `pubspec.yaml`:

```yaml
dependencies:
  google_fonts: ^6.2.1           # Inter font
  cached_network_image: ^3.4.1   # Image caching
  flutter_svg: ^2.0.10           # SVG support
  shared_preferences: ^2.3.4     # Theme persistence

dev_dependencies:
  flutter_test:
    sdk: flutter
```

---

## Checklist

Theme implementation checklist:

- [ ] Define color palette (light + dark)
- [ ] Setup typography system
- [ ] Configure spacing & radius constants
- [ ] Create ThemeData for light mode
- [ ] Create ThemeData for dark mode
- [ ] Implement theme provider (Riverpod)
- [ ] Add theme persistence (SharedPreferences)
- [ ] Create theme switcher UI
- [ ] Test theme switching
- [ ] Verify accessibility (contrast ratios)
- [ ] Test on different screen sizes
- [ ] Document custom components

---

**Last updated**: 2026-05-06
**Status**: Planning phase
**Next steps**: Implement during Phase 4 (Mobile App Development)
