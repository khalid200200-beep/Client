import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/constants/api_constants.dart';
import '../models/order_model.dart';
import '../models/banner_model.dart';
import 'session_service.dart';

/// خدمة الاتصال بالسيرفر والـ APIs الحقيقية لتطبيق العميل مع طبقة حماية صارمة
class ClientApiService {
  static const Duration _timeout = Duration(seconds: 15);

  /// معالج فك تشفير JSON الآمن والمحصن ضد استجابات HTML والأخطاء
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

        return {
          'success': (response.statusCode >= 200 && response.statusCode < 300) && (decoded['success'] != false),
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
        'statusCode': response.statusCode,
        'message': 'تعذر قراءة استجابة الخادم: صيغة غير صالحة',
        'raw': response.body.length > 200 ? response.body.substring(0, 200) : response.body,
      };
    }
  }

  /// 1. تسجيل دخول العميل بالبريد الإلكتروني أو الهاتف مع عزل الصلاحيات
  static Future<Map<String, dynamic>> login({
    required String emailOrPhone,
    required String password,
  }) async {
    try {
      final url = Uri.parse("${ApiConstants.baseUrl}/auth/client/login");
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
        body: jsonEncode({
          'email': emailOrPhone,
          'phone': emailOrPhone,
          'identifier': emailOrPhone,
          'password': password,
          'role': 'client',
          'expected_role': 'client',
        }),
      ).timeout(_timeout);

      return _safeParseJson(response);
    } catch (e) {
      return {
        'success': false,
        'statusCode': 0,
        'message': 'تعذر الاتصال بالسيرفر: يرجى التحقق من اتصال الإنترنت',
      };
    }
  }

  /// 1.1 إرسال رمز التحقق OTP عبر البريد الإلكتروني وواتساب للتسجيل
  static Future<Map<String, dynamic>> sendOtp({
    required String email,
    String? phone,
    String actionType = 'register',
  }) async {
    try {
      final url = Uri.parse("${ApiConstants.baseUrl}/auth/send-otp");
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
        body: jsonEncode({
          'email': email,
          if (phone != null && phone.isNotEmpty) 'phone': phone,
          'type': actionType,
        }),
      ).timeout(_timeout);

      return _safeParseJson(response);
    } catch (e) {
      return {
        'success': false,
        'statusCode': 0,
        'message': 'تعذر الاتصال بالسيرفر لإرسال الرمز',
      };
    }
  }

  /// 1.2 التحقق من رمز OTP المدخل للتسجيل
  static Future<Map<String, dynamic>> verifyOtp({
    required String email,
    required String otp,
  }) async {
    try {
      final url = Uri.parse("${ApiConstants.baseUrl}/auth/verify-otp");
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
        'message': 'تعذر الاتصال بالسيرفر للتحقق من الرمز',
      };
    }
  }

  /// 1.3 طلب استعادة كلمة المرور وإرسال OTP 6 أرقام
  static Future<Map<String, dynamic>> sendResetPasswordOtp(String email) async {
    try {
      final url = Uri.parse("${ApiConstants.baseUrl}/auth/forgot-password");
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

  /// 1.4 التحقق من كود الاستعادة والحصول على رمز الاستعادة
  static Future<Map<String, dynamic>> verifyResetPasswordOtp({
    required String email,
    required String otp,
  }) async {
    try {
      final url = Uri.parse("${ApiConstants.baseUrl}/auth/verify-reset-otp");
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

  /// 1.5 تعيين كلمة المرور الجديدة
  static Future<Map<String, dynamic>> resetPassword({
    required String email,
    required String resetToken,
    required String newPassword,
    required String confirmPassword,
  }) async {
    try {
      final url = Uri.parse("${ApiConstants.baseUrl}/auth/reset-password");
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

  /// 2. تسجيل حساب عميل جديد
  static Future<Map<String, dynamic>> register({
    required String name,
    required String email,
    required String phone,
    required String password,
    String city = 'الخرطوم',
  }) async {
    try {
      final url = Uri.parse("${ApiConstants.baseUrl}/auth/register");
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
        body: jsonEncode({
          'name': name,
          'email': email,
          'phone': phone,
          'password': password,
          'city': city,
          'role': 'client',
        }),
      ).timeout(_timeout);

      return _safeParseJson(response);
    } catch (e) {
      return {
        'success': false,
        'statusCode': 0,
        'message': 'تعذر إنشاء الحساب: يرجى التحقق من اتصال الإنترنت',
      };
    }
  }

  /// 3. جلب قائمة طلبات الشحن الخاصة بالعميل مع دعم الفلترة برقم الجوال أو المعرف والتوكن
  static Future<List<OrderModel>> getOrders({String? phone, int? clientId}) async {
    try {
      final token = await ClientSessionService.getToken();
      String path = "${ApiConstants.baseUrl}/orders";
      final params = <String>[];
      if (phone != null && phone.trim().isNotEmpty) {
        params.add("phone=${Uri.encodeComponent(phone.trim())}");
      }
      if (clientId != null && clientId > 0) {
        params.add("client_id=$clientId");
      }
      if (params.isNotEmpty) {
        path += "?${params.join('&')}";
      }

      final url = Uri.parse(path);
      final headers = <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
        if (token != null && token.isNotEmpty) 'Authorization': 'Bearer $token',
      };

      final response = await http.get(url, headers: headers).timeout(_timeout);

      if (response.statusCode == 200) {
        final parsed = _safeParseJson(response);
        if (parsed['success'] == true && parsed['data'] is List) {
          final list = parsed['data'] as List;
          final List<OrderModel> orders = [];
          for (final item in list) {
            if (item is Map<String, dynamic>) {
              try {
                orders.add(OrderModel.fromJson(item));
              } catch (_) {}
            }
          }
          return orders;
        }
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  /// 4. إنشاء طلب شحن جديد مع دعم الصور المتعددة وتوثيق هوية العميل
  static Future<Map<String, dynamic>> createOrder({
    required String clientName,
    required String clientPhone,
    int? clientId,
    required String city,
    required int packageCount,
    required String notes,
    String? imagePath,
    List<String>? images,
  }) async {
    try {
      final token = await ClientSessionService.getToken();
      final url = Uri.parse("${ApiConstants.baseUrl}/orders");
      final List<String> effectiveImages = images ?? (imagePath != null && imagePath.isNotEmpty ? [imagePath] : []);

      final headers = <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
        if (token != null && token.isNotEmpty) 'Authorization': 'Bearer $token',
      };

      final response = await http.post(
        url,
        headers: headers,
        body: jsonEncode({
          'clientName': clientName,
          'clientPhone': clientPhone,
          'clientId': clientId,
          'city': city,
          'packageCount': packageCount,
          'notes': notes,
          'imagePath': imagePath,
          'images': effectiveImages,
        }),
      ).timeout(_timeout);

      return _safeParseJson(response);
    } catch (e) {
      return {
        'success': false,
        'statusCode': 0,
        'message': 'تعذر إرسال الطلب: يرجى التحقق من اتصال الإنترنت',
      };
    }
  }

  /// 5. جلب البانرات الترويجية الحية
  static Future<List<BannerItem>> getBanners() async {
    try {
      final url = Uri.parse("${ApiConstants.baseUrl}/banners");
      final response = await http.get(url).timeout(_timeout);

      if (response.statusCode == 200) {
        final parsed = _safeParseJson(response);
        if (parsed['success'] == true && parsed['data'] is List) {
          final list = parsed['data'] as List;
          return list.map((item) => BannerItem.fromJson(item as Map<String, dynamic>)).toList();
        }
      }
      return _getDefaultBanners();
    } catch (e) {
      return _getDefaultBanners();
    }
  }

  /// 6. حذف الحساب
  static Future<bool> deleteAccount(String phone, {int? userId}) async {
    try {
      final token = await ClientSessionService.getToken();
      final url = Uri.parse("${ApiConstants.baseUrl}/auth/delete_account");
      final headers = <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
        if (token != null && token.isNotEmpty) 'Authorization': 'Bearer $token',
      };

      final response = await http.post(
        url,
        headers: headers,
        body: jsonEncode({
          'phone': phone,
          'user_id': userId,
        }),
      ).timeout(_timeout);

      final parsed = _safeParseJson(response);
      return parsed['success'] == true;
    } catch (e) {
      return false;
    }
  }

  static List<BannerItem> _getDefaultBanners() {
    return [
      BannerItem(
        id: '1',
        title: 'سودرا للشحن السريع',
        subtitle: 'شحنك يصل إليك بسرعة وأمان وموثوقية',
        badgeText: 'الأكثر طلباً ⭐',
        imageUrl: 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=800',
        buttonText: 'اطلب شحن الآن',
      ),
      BannerItem(
        id: '2',
        title: 'تغطية شاملة لجميع المدن',
        subtitle: 'شحن آمن وفوري مع متابعة حية للطلب',
        badgeText: 'خدمة VIP ⚡',
        imageUrl: 'https://images.unsplash.com/photo-1519003722824-194d4455a60c?w=800',
        buttonText: 'احصل على العرض',
      ),
    ];
  }
}
