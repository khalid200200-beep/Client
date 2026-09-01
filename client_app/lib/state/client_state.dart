import 'package:flutter/foundation.dart';
import '../models/order_model.dart';
import '../models/user_model.dart';
import '../models/banner_model.dart';
import '../services/api_service.dart';
import '../services/session_service.dart';

class ClientState extends ChangeNotifier {
  UserModel _currentUser = UserModel(
    id: '0',
    name: 'عميل',
    phone: '',
    city: 'الخرطوم',
  );

  bool _isLoggedIn = false;
  bool _isLoading = false;
  String? _errorMessage;

  List<BannerItem> _banners = [];
  List<OrderModel> _orders = [];

  UserModel get currentUser => _currentUser;
  bool get isLoggedIn => _isLoggedIn;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  List<BannerItem> get banners => List.unmodifiable(_banners);
  List<OrderModel> get orders => List.unmodifiable(_orders);

  ClientState() {
    checkExistingSession();
  }

  /// 1. التحقق من وجود جلسة مستخدم سابقة
  Future<bool> checkExistingSession() async {
    final savedUser = await ClientSessionService.getUser();
    if (savedUser != null) {
      _currentUser = savedUser;
      _isLoggedIn = true;
      notifyListeners();
      await fetchBanners();
      await fetchOrders();
      return true;
    }
    return false;
  }

  /// 2. تسجيل الدخول بالـ API الحقيقي مع عزل كامل للبيانات السابقة
  Future<bool> login(String emailOrPhone, String password) async {
    _isLoading = true;
    _errorMessage = null;
    _orders = []; // تفريغ أي طلبات سابقة فوراً
    notifyListeners();

    // تنظيف أي جلسات سابقة للتأكيد على عزل الحسابات
    await ClientSessionService.clearSession();

    final res = await ClientApiService.login(
      emailOrPhone: emailOrPhone.trim(),
      password: password.trim(),
    );

    _isLoading = false;
    if (res['success'] == true && res['data'] != null) {
      final userData = res['data'] as Map<String, dynamic>;
      final userRole = (userData['role'] ?? 'client').toString().toLowerCase();

      if (userRole != 'client') {
        _errorMessage = 'هذا الحساب مسجل كسائق/كابتن، يرجى استخدام تطبيق السائق.';
        _isLoggedIn = false;
        _orders = [];
        await ClientSessionService.clearSession();
        notifyListeners();
        return false;
      }

      _currentUser = UserModel(
        id: userData['id']?.toString() ?? '1',
        name: userData['name'] ?? 'عميل',
        email: userData['email'],
        phone: userData['phone'] ?? emailOrPhone,
        city: userData['city'] ?? 'الخرطوم',
        avatarUrl: userData['avatarUrl'],
      );
      _isLoggedIn = true;
      _orders = []; // التأكيد على نظافة قائمة الطلبات قبل الجلب

      // حفظ الجلسة الجديدة محلياً
      await ClientSessionService.saveSession(
        user: _currentUser,
        token: res['token'],
      );

      notifyListeners();
      await fetchBanners();
      await fetchOrders();
      return true;
    } else {
      _errorMessage = res['message'] ?? 'بيانات الدخول غير صحيحة';
      _orders = [];
      await ClientSessionService.clearSession();
      notifyListeners();
      return false;
    }
  }

  /// 2.1 إرسال رمز التحقق OTP للبريد الإلكتروني وواتساب للتسجيل
  Future<bool> sendOtp({required String email, String? phone, String actionType = 'register'}) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final res = await ClientApiService.sendOtp(email: email, phone: phone, actionType: actionType);
    _isLoading = false;

    if (res['success'] == true) {
      notifyListeners();
      return true;
    } else {
      _errorMessage = res['message'] ?? 'فشل إرسال رمز التحقق';
      notifyListeners();
      return false;
    }
  }

  /// 2.2 التحقق من رمز OTP المدخل للتسجيل
  Future<bool> verifyOtp({required String email, required String otp}) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final res = await ClientApiService.verifyOtp(email: email, otp: otp);
    _isLoading = false;

    if (res['success'] == true) {
      notifyListeners();
      return true;
    } else {
      _errorMessage = res['message'] ?? 'رمز التحقق غير صحيح';
      notifyListeners();
      return false;
    }
  }

  /// 2.3 طلب استعادة كلمة المرور وإرسال رمز التحقق 6 أرقام
  Future<Map<String, dynamic>> sendResetPasswordOtp(String email) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final res = await ClientApiService.sendResetPasswordOtp(email.trim());
    _isLoading = false;
    if (res['success'] != true) {
      _errorMessage = res['message'] ?? 'فشل إرسال رمز استعادة كلمة المرور';
    }
    notifyListeners();
    return res;
  }

  /// 2.4 التحقق من كود الاستعادة والحصول على reset_token
  Future<Map<String, dynamic>> verifyResetPasswordOtp({required String email, required String otp}) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final res = await ClientApiService.verifyResetPasswordOtp(email: email.trim(), otp: otp.trim());
    _isLoading = false;
    if (res['success'] != true) {
      _errorMessage = res['message'] ?? 'رمز التحقق غير صحيح';
    }
    notifyListeners();
    return res;
  }

  /// 2.5 تعيين كلمة المرور الجديدة
  Future<Map<String, dynamic>> resetPassword({
    required String email,
    required String resetToken,
    required String newPassword,
    required String confirmPassword,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final res = await ClientApiService.resetPassword(
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

  /// 3. إنشاء حساب جديد بالـ API الحقيقي
  Future<bool> register({
    required String name,
    required String email,
    required String phone,
    required String city,
    required String password,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final res = await ClientApiService.register(
      name: name.trim(),
      email: email.trim(),
      phone: phone.trim(),
      city: city.trim(),
      password: password.trim(),
    );

    _isLoading = false;
    if (res['success'] == true && res['data'] != null) {
      final userData = res['data'] as Map<String, dynamic>;
      _currentUser = UserModel(
        id: userData['id']?.toString() ?? '1',
        name: userData['name'] ?? name,
        email: userData['email'] ?? email,
        phone: userData['phone'] ?? phone,
        city: userData['city'] ?? city,
      );
      _isLoggedIn = true;

      await ClientSessionService.saveSession(
        user: _currentUser,
        token: userData['token']?.toString(),
      );
      notifyListeners();
      await fetchBanners();
      await fetchOrders();
      return true;
    } else {
      _errorMessage = res['message'] ?? 'فشل إنشاء الحساب';
      notifyListeners();
      return false;
    }
  }

  /// 4. جلب البنرات الحية
  Future<void> fetchBanners() async {
    final liveBanners = await ClientApiService.getBanners();
    if (liveBanners.isNotEmpty) {
      _banners = liveBanners;
      notifyListeners();
    }
  }

  /// 5. جلب طلبات العميل الحية من السيرفر بشكل معزول ومخصص للمستخدم الحالي فقط
  Future<void> fetchOrders() async {
    if (!_isLoggedIn) {
      _orders = [];
      notifyListeners();
      return;
    }

    final clientId = int.tryParse(_currentUser.id);
    final userPhone = _currentUser.phone.trim();

    if ((clientId == null || clientId <= 0) && userPhone.isEmpty) {
      _orders = [];
      notifyListeners();
      return;
    }

    final allOrders = await ClientApiService.getOrders(
      phone: userPhone.isNotEmpty ? userPhone : null,
      clientId: (clientId != null && clientId > 0) ? clientId : null,
    );

    _orders = allOrders;
    notifyListeners();
  }

  /// 6. إنشاء طلب شحن مع السيرفر مع دعم الصور المتعددة
  Future<bool> createOrder({
    required String phone,
    required String city,
    required int packageCount,
    required String notes,
    String? imagePath,
    List<String>? images,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final clientId = int.tryParse(_currentUser.id);
    final res = await ClientApiService.createOrder(
      clientName: _currentUser.name.isNotEmpty ? _currentUser.name : 'عميل',
      clientPhone: phone,
      clientId: (clientId != null && clientId > 0) ? clientId : null,
      city: city,
      packageCount: packageCount,
      notes: notes,
      imagePath: imagePath,
      images: images,
    );

    _isLoading = false;
    if (res['success'] == true) {
      await fetchOrders();
      return true;
    } else {
      _errorMessage = res['message'] ?? 'فشل إنشاء الطلب';
      notifyListeners();
      return false;
    }
  }

  /// 7. حذف الحساب ومسح الجلسة
  Future<bool> deleteAccount() async {
    final success = await ClientApiService.deleteAccount(_currentUser.phone);
    if (success) {
      await ClientSessionService.clearSession();
      _isLoggedIn = false;
      _orders = [];
      _currentUser = UserModel(id: '0', name: '', phone: '', city: '');
      _errorMessage = null;
      notifyListeners();
    }
    return success;
  }

  /// 8. تسجيل الخروج وتفريغ كافة البيانات والـ Cache
  Future<void> logout() async {
    await ClientSessionService.clearSession();
    _isLoggedIn = false;
    _orders = [];
    _currentUser = UserModel(id: '0', name: '', phone: '', city: '');
    _errorMessage = null;
    notifyListeners();
  }
}
