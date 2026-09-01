import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/constants/api_constants.dart';
import '../models/driver_order_model.dart';

/// خدمة الاتصال بالسيرفر والـ REST APIs الحقيقية الخاصة بالسائق
class DriverApiService {
  static const Duration _timeout = Duration(seconds: 15);

  static Map<String, dynamic> _safeParseJson(http.Response response) {
    try {
      final body = response.body.trim();
      if (body.isEmpty) {
        return {
          'success': response.statusCode >= 200 && response.statusCode < 300,
          'statusCode': response.statusCode,
          'message': 'استجابة فارغة من الخادم',
          'data': null,
        };
      }

      final decoded = jsonDecode(body);
      if (decoded is Map<String, dynamic>) {
        final rawData = decoded['data'];
        final rawUser = decoded['user'];
        final Map<String, dynamic>? dataMap = (rawData is Map<String, dynamic>)
            ? rawData
            : (rawUser is Map<String, dynamic> ? rawUser : null);

        final isPending = (response.statusCode == 403) || (dataMap?['is_active'] == 0);

        return {
          'success': (response.statusCode >= 200 && response.statusCode < 300) && (decoded['success'] != false),
          'isPending': isPending,
          'statusCode': response.statusCode,
          'message': decoded['message'] ?? (decoded['success'] == true ? 'تمت العملية بنجاح' : 'حدث خطأ في الخادم'),
          'data': rawData ?? rawUser,
          'user': rawUser ?? rawData,
          'token': decoded['token'] ?? dataMap?['token'],
        };
      }

      return {
        'success': response.statusCode >= 200 && response.statusCode < 300,
        'statusCode': response.statusCode,
        'message': 'استجابة غير متوقعة',
        'data': decoded,
      };
    } catch (e) {
      return {
        'success': false,
        'isPending': false,
        'statusCode': response.statusCode,
        'message': 'تعذر قراءة استجابة الخادم: صيغة غير صالحة',
        'raw': response.body.length > 200 ? response.body.substring(0, 200) : response.body,
      };
    }
  }

  /// 1. تسجيل دخول السائق مع التحقق وعزل الأدوار
  static Future<Map<String, dynamic>> login({
    required String emailOrPhone,
    required String password,
  }) async {
    try {
      final url = Uri.parse("${ApiConstants.authEndpoint}/driver/login");
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
        body: jsonEncode({
          'email': emailOrPhone,
          'phone': emailOrPhone,
          'identifier': emailOrPhone,
          'password': password,
          'role': 'driver',
          'expected_role': 'driver',
        }),
      ).timeout(_timeout);

      return _safeParseJson(response);
    } catch (e) {
      return {
        'success': false,
        'isPending': false,
        'statusCode': 0,
        'message': 'تعذر الاتصال بالسيرفر: يرجى التحقق من اتصال الإنترنت',
      };
    }
  }

  /// 1.1 طلب استعادة كلمة المرور وإرسال رمز التحقق 6 أرقام
  static Future<Map<String, dynamic>> sendResetPasswordOtp(String email) async {
    try {
      final url = Uri.parse("${ApiConstants.authEndpoint}/forgot-password");
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
        body: jsonEncode({
          'email': email,
        }),
      ).timeout(_timeout);

      return _safeParseJson(response);
    } catch (e) {
      return {
        'success': false,
        'statusCode': 0,
        'message': 'تعذر الاتصال بالسيرفر لطلب استعادة كلمة المرور',
      };
    }
  }

  /// 1.2 التحقق من كود الاستعادة والحصول على reset_token
  static Future<Map<String, dynamic>> verifyResetPasswordOtp({
    required String email,
    required String otp,
  }) async {
    try {
      final url = Uri.parse("${ApiConstants.authEndpoint}/verify-reset-otp");
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
        body: jsonEncode({
          'email': email,
          'otp': otp,
        }),
      ).timeout(_timeout);

      return _safeParseJson(response);
    } catch (e) {
      return {
        'success': false,
        'statusCode': 0,
        'message': 'تعذر الاتصال بالسيرفر للتحقق من رمز الاستعادة',
      };
    }
  }

  /// 1.3 تعيين كلمة المرور الجديدة
  static Future<Map<String, dynamic>> resetPassword({
    required String email,
    required String resetToken,
    required String newPassword,
    required String confirmPassword,
  }) async {
    try {
      final url = Uri.parse("${ApiConstants.authEndpoint}/reset-password");
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
        body: jsonEncode({
          'email': email,
          'reset_token': resetToken,
          'password': newPassword,
          'confirm_password': confirmPassword,
        }),
      ).timeout(_timeout);

      return _safeParseJson(response);
    } catch (e) {
      return {
        'success': false,
        'statusCode': 0,
        'message': 'تعذر الاتصال بالسيرفر لتحديث كلمة المرور',
      };
    }
  }

  /// 2. تسجيل كابتن جديد (Role: driver, is_active: 0)
  static Future<Map<String, dynamic>> register({
    required String name,
    required String email,
    required String phone,
    required String city,
    required String vehiclePlate,
    required String password,
  }) async {
    try {
      final url = Uri.parse("${ApiConstants.authEndpoint}/register");
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
        body: jsonEncode({
          'name': name,
          'email': email,
          'phone': phone,
          'city': city,
          'vehiclePlate': vehiclePlate,
          'password': password,
          'role': 'driver',
        }),
      ).timeout(_timeout);

      return _safeParseJson(response);
    } catch (e) {
      return {
        'success': false,
        'isPending': false,
        'statusCode': 0,
        'message': 'تعذر إرسال طلب الانضمام: يرجى التحقق من اتصال الإنترنت',
      };
    }
  }

  /// 3. جلب جميع الشحنات الحية الخاصة بمدينة السائق مع دعم الصور المتعددة
  static Future<List<DriverOrderModel>> getOrders({String? city, String? driverPhone}) async {
    try {
      String path = ApiConstants.ordersEndpoint;
      final params = <String>[];
      if (city != null && city.trim().isNotEmpty) {
        params.add("city=${Uri.encodeComponent(city.trim())}");
      }
      if (driverPhone != null && driverPhone.trim().isNotEmpty) {
        params.add("driver_phone=${Uri.encodeComponent(driverPhone.trim())}");
      }
      if (params.isNotEmpty) {
        path += "?${params.join('&')}";
      }

      final url = Uri.parse(path);
      final response = await http.get(url).timeout(_timeout);

      if (response.statusCode == 200) {
        final parsed = _safeParseJson(response);
        if (parsed['success'] == true && parsed['data'] is List) {
          final list = parsed['data'] as List;
          final List<DriverOrderModel> orders = [];
          for (final item in list) {
            if (item is Map<String, dynamic>) {
              try {
                orders.add(DriverOrderModel.fromJson(item));
              } catch (_) {}
            }
          }
          return orders;
        }
      }
    } catch (_) {}
    return [];
  }

  /// 4. قبول الطلب
  static Future<Map<String, dynamic>> acceptOrder({
    required String orderId,
    required String driverName,
    required String driverPhone,
  }) async {
    try {
      final url = Uri.parse("${ApiConstants.ordersEndpoint}/$orderId/accept");
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
        body: jsonEncode({
          'driverName': driverName,
          'driverPhone': driverPhone,
          'action': 'accept',
        }),
      ).timeout(_timeout);

      return _safeParseJson(response);
    } catch (e) {
      return {'success': false, 'message': 'خطأ في الاتصال: $e'};
    }
  }

  /// 5. توثيق التحميل والمبلغ المحصل نقداً
  static Future<Map<String, dynamic>> markLoaded({
    required String orderId,
    required double collectedAmount,
  }) async {
    try {
      final url = Uri.parse("${ApiConstants.ordersEndpoint}/$orderId/status");
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
        body: jsonEncode({
          'status': 'loaded',
          'collectedAmount': collectedAmount,
          'action': 'update_status',
        }),
      ).timeout(_timeout);

      return _safeParseJson(response);
    } catch (e) {
      return {'success': false, 'message': 'خطأ في الاتصال: $e'};
    }
  }

  /// 6. توثيق تعذر الشحن والسبب
  static Future<Map<String, dynamic>> markFailed({
    required String orderId,
    required String reason,
  }) async {
    try {
      final url = Uri.parse("${ApiConstants.ordersEndpoint}/$orderId/status");
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
        body: jsonEncode({
          'status': 'failed',
          'failureReason': reason,
          'action': 'update_status',
        }),
      ).timeout(_timeout);

      return _safeParseJson(response);
    } catch (e) {
      return {'success': false, 'message': 'خطأ في الاتصال: $e'};
    }
  }

  /// 7. توثيق التسليم النهائي
  static Future<Map<String, dynamic>> markDelivered({
    required String orderId,
    double collectedAmount = 0.0,
  }) async {
    try {
      final url = Uri.parse("${ApiConstants.ordersEndpoint}/$orderId/status");
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
        body: jsonEncode({
          'status': 'delivered',
          'collectedAmount': collectedAmount,
          'action': 'update_status',
        }),
      ).timeout(_timeout);

      return _safeParseJson(response);
    } catch (e) {
      return {'success': false, 'message': 'خطأ في الاتصال: $e'};
    }
  }

  /// 8. طلب حذف الحساب
  static Future<bool> deleteAccount(String phone) async {
    try {
      final url = Uri.parse("${ApiConstants.authEndpoint}/delete_account");
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'phone': phone}),
      ).timeout(_timeout);

      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
