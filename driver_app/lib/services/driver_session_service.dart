import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class DriverSessionService {
  static const String _keyDriver = 'driver_user_data';
  static const String _keyToken = 'driver_auth_token_secure';
  static const String _keyIsPending = 'driver_is_pending';

  static const FlutterSecureStorage _secureStorage = FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );

  static Future<void> saveSession({
    required Map<String, dynamic> driverData,
    String? token,
    bool isPending = false,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyDriver, jsonEncode(driverData));
    await prefs.setBool(_keyIsPending, isPending);

    if (token != null && token.isNotEmpty) {
      try {
        await _secureStorage.write(key: _keyToken, value: token);
      } catch (_) {
        await prefs.setString(_keyToken, token);
      }
    }
  }

  static Future<Map<String, dynamic>?> getDriverData() async {
    final prefs = await SharedPreferences.getInstance();
    final jsonStr = prefs.getString(_keyDriver);
    if (jsonStr == null || jsonStr.isEmpty) return null;
    try {
      return jsonDecode(jsonStr) as Map<String, dynamic>;
    } catch (_) {
      return null;
    }
  }

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

  static Future<bool> isPending() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_keyIsPending) ?? false;
  }

  static Future<bool> isLoggedIn() async {
    final data = await getDriverData();
    return data != null;
  }

  static Future<void> clearSession() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_keyDriver);
    await prefs.remove(_keyToken);
    await prefs.remove(_keyIsPending);
    try {
      await _secureStorage.delete(key: _keyToken);
    } catch (_) {}
  }
}
