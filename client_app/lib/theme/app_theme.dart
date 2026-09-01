import 'package:flutter/material.dart';

/// نظام الألوان وهوية شعار "سودرا للخدمات اللوجستية | SUDRA - Sea Freight & Logistics"
class AppTheme {
  // اللون الأساسي (التيركوازي / الزمردي البحري)
  static const Color primaryTeal = Color(0xFF178386);
  static const Color primaryTealDark = Color(0xFF126C70);
  static const Color primaryTealLight = Color(0xFF2FA2A5);

  // اللون الثانوي (الذهبي الفاخر)
  static const Color secondaryGold = Color(0xFFD1AA72);
  static const Color secondaryGoldLight = Color(0xFFE1C7A2);

  // التوافقية مع المتغيرات السابقة
  static const Color primaryGreen = primaryTeal;
  static const Color primaryGreenDark = primaryTealDark;
  static const Color primaryGreenLight = primaryTealLight;
  static const Color primaryRed = primaryTeal;
  static const Color accentBurgundy = secondaryGold;
  static const Color accentBurgundyDark = Color(0xFFB88E52);

  // الخلفيات والبطاقات والنصوص
  static const Color scaffoldBackground = Color(0xFFF7F7F7);
  static const Color cardBackground = Colors.white;
  static const Color textDark = Color(0xFF142D2D);
  static const Color textMuted = Color(0xFF7C8987);
  static const Color borderColor = Color(0xFFE5EBE9);

  // التدرجات اللونية الفاخرة
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFF178386), Color(0xFF126C70)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient goldGradient = LinearGradient(
    colors: [Color(0xFFD1AA72), Color(0xFFE1C7A2)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient greenGradient = primaryGradient;
  static const LinearGradient burgundyGradient = primaryGradient;

  // الثيم العام
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      fontFamily: 'Cairo',
      scaffoldBackgroundColor: scaffoldBackground,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primaryTeal,
        primary: primaryTeal,
        secondary: secondaryGold,
        surface: scaffoldBackground,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
        iconTheme: IconThemeData(color: textDark),
        titleTextStyle: TextStyle(
          fontFamily: 'Cairo',
          fontSize: 18,
          fontWeight: FontWeight.bold,
          color: textDark,
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryTeal,
          foregroundColor: Colors.white,
          elevation: 2,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          textStyle: const TextStyle(
            fontFamily: 'Cairo',
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 15),
        hintStyle: const TextStyle(
          fontFamily: 'Cairo',
          fontSize: 13.5,
          color: Color(0xFF94A3B8),
          fontWeight: FontWeight.w400,
        ),
        labelStyle: const TextStyle(
          fontFamily: 'Cairo',
          fontSize: 13.5,
          color: textDark,
          fontWeight: FontWeight.w600,
        ),
        prefixIconColor: primaryTeal,
        suffixIconColor: textMuted,
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Color(0xFFE2E8F0), width: 1.2),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: primaryTeal, width: 1.6),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Color(0xFFEF4444), width: 1.2),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Color(0xFFEF4444), width: 1.6),
        ),
        errorStyle: const TextStyle(
          fontFamily: 'Cairo',
          fontSize: 11.5,
          color: Color(0xFFEF4444),
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
