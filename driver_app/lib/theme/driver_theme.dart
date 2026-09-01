import 'package:flutter/material.dart';

/// ثيم وألوان تطبيق السائق - سودرا كابتن | SUDRA Captain
class DriverTheme {
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
  static const Color primaryBlue = primaryTeal;
  static const Color accentBurgundy = secondaryGold;

  // الخلفيات والنصوص
  static const Color scaffoldBackground = Color(0xFFF7F7F7);
  static const Color background = Color(0xFFF7F7F7);
  static const Color textDark = Color(0xFF142D2D);
  static const Color textMuted = Color(0xFF7C8987);

  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFF178386), Color(0xFF126C70)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient greenGradient = primaryGradient;

  static ThemeData get lightTheme => theme;

  static ThemeData get theme {
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
    );
  }
}
