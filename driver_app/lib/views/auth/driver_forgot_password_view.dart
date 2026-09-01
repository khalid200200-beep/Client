import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../state/driver_state.dart';
import '../../theme/driver_theme.dart';

class DriverForgotPasswordView extends StatefulWidget {
  const DriverForgotPasswordView({super.key});

  @override
  State<DriverForgotPasswordView> createState() => _DriverForgotPasswordViewState();
}

class _DriverForgotPasswordViewState extends State<DriverForgotPasswordView> {
  int _currentStep = 1; // 1: Email, 2: OTP, 3: New Password

  final _emailFormKey = GlobalKey<FormState>();
  final _otpFormKey = GlobalKey<FormState>();
  final _pwdFormKey = GlobalKey<FormState>();

  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _otpController = TextEditingController();
  final TextEditingController _newPasswordController = TextEditingController();
  final TextEditingController _confirmPasswordController = TextEditingController();

  String _resetToken = '';
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;

  int _resendCountdown = 60;
  Timer? _countdownTimer;

  @override
  void dispose() {
    _emailController.dispose();
    _otpController.dispose();
    _newPasswordController.dispose();
    _confirmPasswordController.dispose();
    _countdownTimer?.cancel();
    super.dispose();
  }

  void _startTimer() {
    _countdownTimer?.cancel();
    setState(() => _resendCountdown = 60);
    _countdownTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_resendCountdown > 0) {
        setState(() => _resendCountdown--);
      } else {
        timer.cancel();
      }
    });
  }

  // الخطوة 1: إرسال رمز التحقق
  void _sendOtp() async {
    if (_emailFormKey.currentState!.validate()) {
      final state = Provider.of<DriverState>(context, listen: false);
      final email = _emailController.text.trim();
      final res = await state.sendResetPasswordOtp(email);

      if (!mounted) return;

      if (res['success'] == true) {
        setState(() => _currentStep = 2);
        _startTimer();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(res['message'] ?? 'تم إرسال رمز التحقق إلى بريدك الإلكتروني'),
            backgroundColor: Colors.green.shade700,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(res['message'] ?? 'حدث خطأ في إرسال الرمز'),
            backgroundColor: Colors.red.shade700,
          ),
        );
      }
    }
  }

  // الخطوة 2: التحقق من رمز OTP
  void _verifyOtp() async {
    if (_otpFormKey.currentState!.validate()) {
      final state = Provider.of<DriverState>(context, listen: false);
      final email = _emailController.text.trim();
      final otp = _otpController.text.trim();

      final res = await state.verifyResetPasswordOtp(email: email, otp: otp);

      if (!mounted) return;

      if (res['success'] == true && res['data'] != null) {
        final data = res['data'] as Map<String, dynamic>;
        setState(() {
          _resetToken = data['reset_token'] ?? '';
          _currentStep = 3;
        });
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(res['message'] ?? 'رمز التحقق غير صحيح أو منتهي الصلاحية'),
            backgroundColor: Colors.red.shade700,
          ),
        );
      }
    }
  }

  // الخطوة 3: تعيين كلمة المرور الجديدة
  void _resetPassword() async {
    if (_pwdFormKey.currentState!.validate()) {
      final state = Provider.of<DriverState>(context, listen: false);
      final email = _emailController.text.trim();
      final newPass = _newPasswordController.text.trim();
      final confirmPass = _confirmPasswordController.text.trim();

      final res = await state.resetPassword(
        email: email,
        resetToken: _resetToken,
        newPassword: newPass,
        confirmPassword: confirmPass,
      );

      if (!mounted) return;

      if (res['success'] == true) {
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (ctx) => AlertDialog(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
            title: const Column(
              children: [
                Icon(Icons.check_circle_rounded, color: Colors.green, size: 55),
                SizedBox(height: 12),
                Text('تم بنجاح! 🎉', textAlign: TextAlign.center, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              ],
            ),
            content: const Text(
              'تم تحديث كلمة مرور حساب الكابتن بنجاح. يمكنك الآن تسجيل الدخول باستخدام كلمة المرور الجديدة.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 13, color: DriverTheme.textMuted, height: 1.4),
            ),
            actions: [
              Center(
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: DriverTheme.primaryGreen,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                  onPressed: () {
                    Navigator.pop(ctx);
                    Navigator.pop(context);
                  },
                  child: const Text('تسجيل الدخول الآن 🔑', style: TextStyle(fontWeight: FontWeight.bold)),
                ),
              ),
            ],
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(res['message'] ?? 'فشل تحديث كلمة المرور'),
            backgroundColor: Colors.red.shade700,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final driverState = Provider.of<DriverState>(context);

    return Scaffold(
      backgroundColor: DriverTheme.scaffoldBackground,
      appBar: AppBar(
        title: const Text('استعادة كلمة المرور 🔐', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
        child: Column(
          children: [
            _buildStepIndicator(),
            const SizedBox(height: 28),

            if (_currentStep == 1) _buildStep1Email(driverState),
            if (_currentStep == 2) _buildStep2Otp(driverState),
            if (_currentStep == 3) _buildStep3NewPassword(driverState),
          ],
        ),
      ),
    );
  }

  Widget _buildStepIndicator() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        _buildStepBadge(1, 'البريد', _currentStep >= 1),
        Container(width: 40, height: 2, color: _currentStep >= 2 ? DriverTheme.primaryGreen : Colors.grey.shade300),
        _buildStepBadge(2, 'الرمز', _currentStep >= 2),
        Container(width: 40, height: 2, color: _currentStep >= 3 ? DriverTheme.primaryGreen : Colors.grey.shade300),
        _buildStepBadge(3, 'كلمة المرور', _currentStep >= 3),
      ],
    );
  }

  Widget _buildStepBadge(int step, String label, bool active) {
    return Column(
      children: [
        CircleAvatar(
          radius: 14,
          backgroundColor: active ? DriverTheme.primaryGreen : Colors.grey.shade300,
          child: Text(
            '$step',
            style: TextStyle(color: active ? Colors.white : Colors.grey.shade600, fontSize: 12, fontWeight: FontWeight.bold),
          ),
        ),
        const SizedBox(height: 4),
        Text(label, style: TextStyle(fontSize: 11, color: active ? DriverTheme.primaryGreen : DriverTheme.textMuted, fontWeight: FontWeight.w600)),
      ],
    );
  }

  Widget _buildStep1Email(DriverState state) {
    return Form(
      key: _emailFormKey,
      child: Container(
        padding: const EdgeInsets.all(22),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(24),
          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 16)],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Icon(Icons.mark_email_read_outlined, size: 50, color: DriverTheme.primaryGreen),
            const SizedBox(height: 12),
            const Text(
              'أدخل بريدك الإلكتروني المسجل',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              'سنقوم بإرسال رمز تحقق مكوّن من 6 أرقام إلى بريدك الإلكتروني لاستعادة حساب الكابتن.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 12.5, color: DriverTheme.textMuted, height: 1.4),
            ),
            const SizedBox(height: 24),
            TextFormField(
              controller: _emailController,
              keyboardType: TextInputType.emailAddress,
              decoration: InputDecoration(
                labelText: 'البريد الإلكتروني',
                hintText: 'driver@domain.com',
                prefixIcon: const Icon(Icons.email_outlined, color: DriverTheme.textMuted),
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide(color: Colors.grey.shade300)),
                enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide(color: Colors.grey.shade300)),
              ),
              validator: (v) {
                if (v == null || v.trim().isEmpty) return 'يرجى إدخال البريد الإلكتروني';
                if (!v.contains('@') || !v.contains('.')) return 'يرجى إدخال بريد إلكتروني صحيح';
                return null;
              },
            ),
            const SizedBox(height: 24),
            state.isLoading
                ? const Center(child: CircularProgressIndicator(color: DriverTheme.primaryGreen))
                : ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: DriverTheme.primaryGreen,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                    ),
                    onPressed: _sendOtp,
                    child: const Text('إرسال رمز التحقق ✉️', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  ),
          ],
        ),
      ),
    );
  }

  Widget _buildStep2Otp(DriverState state) {
    return Form(
      key: _otpFormKey,
      child: Container(
        padding: const EdgeInsets.all(22),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(24),
          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 16)],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Icon(Icons.phonelink_lock_rounded, size: 50, color: DriverTheme.primaryGreen),
            const SizedBox(height: 12),
            const Text(
              'أدخل رمز التحقق (OTP)',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              'تم إرسال رمز مكون من 6 أرقام إلى:\n${_emailController.text.trim()}',
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 12.5, color: DriverTheme.textMuted, height: 1.4),
            ),
            const SizedBox(height: 24),
            TextFormField(
              controller: _otpController,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: 'رمز التحقق (6 أرقام)',
                hintText: '000000',
                prefixIcon: const Icon(Icons.security_rounded, color: DriverTheme.textMuted),
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide(color: Colors.grey.shade300)),
                enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide(color: Colors.grey.shade300)),
              ),
              validator: (v) {
                if (v == null || v.trim().isEmpty) return 'يرجى إدخال رمز التحقق';
                if (v.trim().length != 6) return 'رمز التحقق يجب أن يكون 6 أرقام';
                return null;
              },
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                TextButton(
                  onPressed: _resendCountdown == 0 ? _sendOtp : null,
                  child: Text(
                    _resendCountdown == 0 ? 'إعادة إرسال الرمز 🔄' : 'إعادة الإرسال بعد ($_resendCountdown ثانية)',
                    style: TextStyle(fontSize: 12, color: _resendCountdown == 0 ? DriverTheme.primaryGreen : DriverTheme.textMuted),
                  ),
                ),
                TextButton(
                  onPressed: () => setState(() => _currentStep = 1),
                  child: const Text('تغيير البريد ✏️', style: TextStyle(fontSize: 12, color: DriverTheme.textMuted)),
                ),
              ],
            ),
            const SizedBox(height: 20),
            state.isLoading
                ? const Center(child: CircularProgressIndicator(color: DriverTheme.primaryGreen))
                : ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: DriverTheme.primaryGreen,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                    ),
                    onPressed: _verifyOtp,
                    child: const Text('تحقق من الرمز ✅', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  ),
          ],
        ),
      ),
    );
  }

  Widget _buildStep3NewPassword(DriverState state) {
    return Form(
      key: _pwdFormKey,
      child: Container(
        padding: const EdgeInsets.all(22),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(24),
          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 16)],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Icon(Icons.lock_reset_rounded, size: 50, color: DriverTheme.primaryGreen),
            const SizedBox(height: 12),
            const Text(
              'تعيين كلمة مرور جديدة',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              'يجب أن تتكون كلمة المرور من 8 خانات على الأقل لضمان أمان حساب الكابتن.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 12.5, color: DriverTheme.textMuted, height: 1.4),
            ),
            const SizedBox(height: 24),
            TextFormField(
              controller: _newPasswordController,
              obscureText: _obscurePassword,
              decoration: InputDecoration(
                labelText: 'كلمة المرور الجديدة',
                prefixIcon: const Icon(Icons.lock_outline, color: DriverTheme.textMuted),
                suffixIcon: IconButton(
                  icon: Icon(_obscurePassword ? Icons.visibility_off : Icons.visibility, color: DriverTheme.textMuted),
                  onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                ),
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide(color: Colors.grey.shade300)),
                enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide(color: Colors.grey.shade300)),
              ),
              validator: (v) {
                if (v == null || v.trim().isEmpty) return 'يرجى إدخال كلمة المرور';
                if (v.trim().length < 8) return 'كلمة المرور يجب أن لا تقل عن 8 خانات';
                return null;
              },
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _confirmPasswordController,
              obscureText: _obscureConfirmPassword,
              decoration: InputDecoration(
                labelText: 'تأكيد كلمة المرور الجديدة',
                prefixIcon: const Icon(Icons.lock_outline, color: DriverTheme.textMuted),
                suffixIcon: IconButton(
                  icon: Icon(_obscureConfirmPassword ? Icons.visibility_off : Icons.visibility, color: DriverTheme.textMuted),
                  onPressed: () => setState(() => _obscureConfirmPassword = !_obscureConfirmPassword),
                ),
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide(color: Colors.grey.shade300)),
                enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide(color: Colors.grey.shade300)),
              ),
              validator: (v) {
                if (v == null || v.trim().isEmpty) return 'يرجى تأكيد كلمة المرور';
                if (v.trim() != _newPasswordController.text.trim()) return 'كلمة المرور وتأكيدها غير متطابقين';
                return null;
              },
            ),
            const SizedBox(height: 24),
            state.isLoading
                ? const Center(child: CircularProgressIndicator(color: DriverTheme.primaryGreen))
                : ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: DriverTheme.primaryGreen,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                    ),
                    onPressed: _resetPassword,
                    child: const Text('حفظ وتحديث كلمة المرور 🔐', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  ),
          ],
        ),
      ),
    );
  }
}
