import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../models/user_model.dart';

/// خدمة إدارة الجلسة والتخزين الآمن للعميل
class ClientSessionService {
  static const String _keyUser = 'client_user_data';
  static const String _keyToken = 'client_auth_token_secure';

  static const FlutterSecureStorage _secureStorage = FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );

  /// حفظ بيانات المستخدم في SharedPreferences والـ Token في SecureStorage
  static Future<void> saveSession({required UserModel user, String? token}) async {
    final prefs = await SharedPreferences.getInstance();
    final userMap = {
      'id': user.id,
      'name': user.name,
      'email': user.email ?? '',
      'phone': user.phone,
      'city': user.city,
      'avatarUrl': user.avatarUrl ?? '',
    };
    await prefs.setString(_keyUser, jsonEncode(userMap));

    if (token != null && token.isNotEmpty) {
      try {
        await _secureStorage.write(key: _keyToken, value: token);
      } catch (_) {
        // Fallback for environments where secure storage isn't available
        await prefs.setString(_keyToken, token);
      }
    }
  }

  /// استرجاع بيانات المستخدم المحفوظ
  static Future<UserModel?> getUser() async {
    final prefs = await SharedPreferences.getInstance();
    final userJson = prefs.getString(_keyUser);
    if (userJson == null || userJson.isEmpty) return null;

    try {
      final map = jsonDecode(userJson) as Map<String, dynamic>;
      return UserModel(
        id: map['id']?.toString() ?? '',
        name: map['name'] ?? '',
        email: map['email'],
        phone: map['phone'] ?? '',
        city: map['city'] ?? 'الخرطوم',
        avatarUrl: map['avatarUrl'],
      );
    } catch (_) {
      return null;
    }
  }

  /// استرجاع التوكن من التخزين الآمن
  static Future<String?> getToken() async {
    try {
      final secureToken = await _secureStorage.read(key: _keyToken);
      if (secureToken != null && secureToken.isNotEmpty) {
        return secureToken;
      }
    } catch (_) {}

    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyToken);
  }

  /// التحقق هل المستخدم مسجل دخول
  static Future<bool> isLoggedIn() async {
    final user = await getUser();
    return user != null;
  }

  /// مسح الجلسة وكافة البيانات المؤقتة عند تسجيل الخروج
  static Future<void> clearSession() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.clear();
    } catch (_) {}
    try {
      await _secureStorage.deleteAll();
    } catch (_) {}
  }
}
