import 'package:flutter/foundation.dart';
import '../models/driver_order_model.dart';
import '../services/driver_api_service.dart';
import '../services/driver_session_service.dart';

class DriverState extends ChangeNotifier {
  String _driverName = 'كابتن بريد السودان';
  String _driverEmail = 'driver@sudra.sa';
  String _driverPhone = '0901234567';
  String _driverCity = 'الخرطوم';
  String _vehiclePlate = '';
  bool _isActive = true;
  bool _isLoading = false;
  String? _errorMessage;

  List<DriverOrderModel> _cityOrders = [];

  String get driverName => _driverName;
  String get driverEmail => _driverEmail;
  String get driverPhone => _driverPhone;
  String get driverCity => _driverCity;
  String get vehiclePlate => _vehiclePlate;
  bool get isActive => _isActive;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  List<DriverOrderModel> get cityOrders => List.unmodifiable(_cityOrders);

  DriverState() {
    checkExistingSession();
  }

  /// 1. التحقق من الجلسة السابقة
  Future<bool> checkExistingSession() async {
    final data = await DriverSessionService.getDriverData();
    if (data != null) {
      _driverName = data['name'] ?? _driverName;
      _driverEmail = data['email'] ?? _driverEmail;
      _driverPhone = data['phone'] ?? _driverPhone;
      _driverCity = data['city'] ?? _driverCity;
      _vehiclePlate = data['vehiclePlate'] ?? _vehiclePlate;
      _isActive = !(await DriverSessionService.isPending());
      notifyListeners();
      await fetchOrders();
      return true;
    }
    return false;
  }

  /// 2. تسجيل دخول السائق الحقيقي
  Future<Map<String, dynamic>> login(String emailOrPhone, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final res = await DriverApiService.login(
      emailOrPhone: emailOrPhone.trim(),
      password: password.trim(),
    );

    _isLoading = false;
    if (res['isPending'] == true) {
      _driverEmail = emailOrPhone;
      _isActive = false;
      await DriverSessionService.saveSession(
        driverData: {'email': emailOrPhone, 'name': _driverName, 'phone': _driverPhone, 'city': _driverCity},
        isPending: true,
      );
      notifyListeners();
      return res;
    }

    if (res['success'] == true && res['data'] != null) {
      final u = res['data'] as Map<String, dynamic>;
      final role = (u['role'] ?? 'driver').toString().toLowerCase();

      if (role != 'driver') {
        _errorMessage = 'هذا الحساب مسجل كعميل، يرجى استخدام تطبيق العميل أو التسجيل ككابتن.';
        _isActive = false;
        await DriverSessionService.clearSession();
        notifyListeners();
        return {
          'success': false,
          'message': _errorMessage,
        };
      }

      _driverName = u['name'] ?? _driverName;
      _driverEmail = u['email'] ?? emailOrPhone;
      _driverPhone = u['phone'] ?? _driverPhone;
      _driverCity = u['city'] ?? _driverCity;
      _vehiclePlate = u['vehicle_plate'] ?? u['vehiclePlate'] ?? _vehiclePlate;
      _isActive = true;

      await DriverSessionService.saveSession(
        driverData: {
          'name': _driverName,
          'email': _driverEmail,
          'phone': _driverPhone,
          'city': _driverCity,
          'vehiclePlate': _vehiclePlate,
        },
        token: res['token'],
        isPending: false,
      );

      notifyListeners();
      await fetchOrders();
      return res;
    } else {
      _errorMessage = res['message'] ?? 'بيانات الدخول غير صحيحة';
      await DriverSessionService.clearSession();
      notifyListeners();
      return res;
    }
  }

  /// 2.1 طلب استعادة كلمة المرور وإرسال رمز 6 أرقام
  Future<Map<String, dynamic>> sendResetPasswordOtp(String email) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final res = await DriverApiService.sendResetPasswordOtp(email.trim());
    _isLoading = false;
    if (res['success'] != true) {
      _errorMessage = res['message'] ?? 'فشل إرسال رمز استعادة كلمة المرور';
    }
    notifyListeners();
    return res;
  }

  /// 2.2 التحقق من كود الاستعادة والحصول على reset_token
  Future<Map<String, dynamic>> verifyResetPasswordOtp({required String email, required String otp}) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final res = await DriverApiService.verifyResetPasswordOtp(email: email.trim(), otp: otp.trim());
    _isLoading = false;
    if (res['success'] != true) {
      _errorMessage = res['message'] ?? 'رمز التحقق غير صحيح';
    }
    notifyListeners();
    return res;
  }

  /// 2.3 تعيين كلمة المرور الجديدة
  Future<Map<String, dynamic>> resetPassword({
    required String email,
    required String resetToken,
    required String newPassword,
    required String confirmPassword,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final res = await DriverApiService.resetPassword(
      email: email.trim(),
      resetToken: resetToken.trim(),
      newPassword: newPassword.trim(),
      confirmPassword: confirmPassword.trim(),
    );
    _isLoading = false;
    if (res['success'] != true) {
      _errorMessage = res['message'] ?? 'فشل تحديث كلمة المرور';
    }
    notifyListeners();
    return res;
  }

  /// 3. تسجيل كابتن جديد
  Future<Map<String, dynamic>> register({
    required String name,
    required String email,
    required String phone,
    required String city,
    required String vehiclePlate,
    required String password,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final res = await DriverApiService.register(
      name: name.trim(),
      email: email.trim(),
      phone: phone.trim(),
      city: city.trim(),
      vehiclePlate: vehiclePlate.trim(),
      password: password.trim(),
    );

    _isLoading = false;
    if (res['success'] == true) {
      _driverName = name;
      _driverEmail = email;
      _driverPhone = phone;
      _driverCity = city;
      _vehiclePlate = vehiclePlate;
      _isActive = false;

      await DriverSessionService.saveSession(
        driverData: {
          'name': name,
          'email': email,
          'phone': phone,
          'city': city,
          'vehiclePlate': vehiclePlate,
        },
        isPending: true,
      );
      notifyListeners();
    } else {
      _errorMessage = res['message'] ?? 'فشل التسجيل';
      notifyListeners();
    }
    return res;
  }

  /// 4. جلب الشحنات الحية الخاصة بمدينة السائق
  Future<void> fetchOrders() async {
    final orders = await DriverApiService.getOrders(
      city: _driverCity.isNotEmpty ? _driverCity : null,
      driverPhone: _driverPhone.isNotEmpty ? _driverPhone : null,
    );
    _cityOrders = orders;
    notifyListeners();
  }

  /// 5. قبول الطلب مع السيرفر
  Future<bool> acceptOrder(String orderId) async {
    final res = await DriverApiService.acceptOrder(
      orderId: orderId,
      driverName: _driverName,
      driverPhone: _driverPhone,
    );

    if (res['success'] == true) {
      await fetchOrders();
      return true;
    }
    return false;
  }

  /// 6. رفض أو إخفاء الطلب
  void rejectOrder(String orderId) {
    _cityOrders.removeWhere((o) => o.id == orderId);
    notifyListeners();
  }

  /// 7. توثيق التحميل والمبلغ المحصل نقداً مع السيرفر
  Future<bool> markLoaded(String orderId, {required double collectedAmount}) async {
    final res = await DriverApiService.markLoaded(
      orderId: orderId,
      collectedAmount: collectedAmount,
    );

    if (res['success'] == true) {
      await fetchOrders();
      return true;
    }
    return false;
  }

  /// 8. توثيق تعذر الشحن مع السيرفر
  Future<bool> markFailed(String orderId, String reason) async {
    final res = await DriverApiService.markFailed(
      orderId: orderId,
      reason: reason,
    );

    if (res['success'] == true) {
      await fetchOrders();
      return true;
    }
    return false;
  }

  /// 9. حذف حساب السائق ومسح الجلسة
  Future<bool> deleteAccount() async {
    final success = await DriverApiService.deleteAccount(_driverPhone);
    if (success) {
      await DriverSessionService.clearSession();
      _isActive = false;
      _cityOrders.clear();
      notifyListeners();
    }
    return success;
  }

  /// 10. تسجيل الخروج
  Future<void> logout() async {
    await DriverSessionService.clearSession();
    _isActive = false;
    _cityOrders.clear();
    notifyListeners();
  }
}
