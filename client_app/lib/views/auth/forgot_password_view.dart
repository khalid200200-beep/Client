import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../state/client_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/custom_button.dart';
import '../../widgets/custom_text_field.dart';

class ForgotPasswordView extends StatefulWidget {
  const ForgotPasswordView({super.key});

  @override
  State<ForgotPasswordView> createState() => _ForgotPasswordViewState();
}

class _ForgotPasswordViewState extends State<ForgotPasswordView> {
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
      final state = Provider.of<ClientState>(context, listen: false);
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
      final state = Provider.of<ClientState>(context, listen: false);
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
      final state = Provider.of<ClientState>(context, listen: false);
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
              'تم تحديث كلمة المرور بنجاح. يمكنك الآن تسجيل الدخول باستخدام كلمة المرور الجديدة.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 13, color: AppTheme.textMuted, height: 1.4),
            ),
            actions: [
              Center(
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primaryRed),
                  onPressed: () {
                    Navigator.pop(ctx);
                    Navigator.pop(context); // العودة لصفحة تسجيل الدخول
                  },
                  child: const Text('تسجيل الدخول الآن 🔑', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
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
    final clientState = Provider.of<ClientState>(context);

    return Scaffold(
      backgroundColor: AppTheme.scaffoldBackground,
      appBar: AppBar(
        title: const Text('استعادة كلمة المرور 🔐', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
        child: Column(
          children: [
            // مؤشر الخطوات
            _buildStepIndicator(),
            const SizedBox(height: 28),

            if (_currentStep == 1) _buildStep1Email(clientState),
            if (_currentStep == 2) _buildStep2Otp(clientState),
            if (_currentStep == 3) _buildStep3NewPassword(clientState),
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
        Container(width: 40, height: 2, color: _currentStep >= 2 ? AppTheme.primaryRed : Colors.grey.shade300),
        _buildStepBadge(2, 'الرمز', _currentStep >= 2),
        Container(width: 40, height: 2, color: _currentStep >= 3 ? AppTheme.primaryRed : Colors.grey.shade300),
        _buildStepBadge(3, 'كلمة المرور', _currentStep >= 3),
      ],
    );
  }

  Widget _buildStepBadge(int step, String label, bool active) {
    return Column(
      children: [
        CircleAvatar(
          radius: 14,
          backgroundColor: active ? AppTheme.primaryRed : Colors.grey.shade300,
          child: Text(
            '$step',
            style: TextStyle(color: active ? Colors.white : Colors.grey.shade600, fontSize: 12, fontWeight: FontWeight.bold),
          ),
        ),
        const SizedBox(height: 4),
        Text(label, style: TextStyle(fontSize: 11, color: active ? AppTheme.primaryRed : AppTheme.textMuted, fontWeight: FontWeight.w600)),
      ],
    );
  }

  // الخطوة 1
  Widget _buildStep1Email(ClientState state) {
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
            const Icon(Icons.mark_email_read_outlined, size: 50, color: AppTheme.primaryRed),
            const SizedBox(height: 12),
            const Text(
              'أدخل بريدك الإلكتروني المسجل',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              'سنقوم بإرسال رمز تحقق مكوّن من 6 أرقام إلى بريدك الإلكتروني لاستعادة حسابك.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 12.5, color: AppTheme.textMuted, height: 1.4),
            ),
            const SizedBox(height: 24),
            CustomTextField(
              label: 'البريد الإلكتروني',
              hint: 'example@domain.com',
              controller: _emailController,
              keyboardType: TextInputType.emailAddress,
              prefixIcon: const Icon(Icons.email_outlined, color: AppTheme.textMuted),
              validator: (v) {
                if (v == null || v.trim().isEmpty) return 'يرجى إدخال البريد الإلكتروني';
                if (!v.contains('@') || !v.contains('.')) return 'يرجى إدخال بريد إلكتروني صحيح';
                return null;
              },
            ),
            const SizedBox(height: 24),
            state.isLoading
                ? const Center(child: CircularProgressIndicator(color: AppTheme.primaryRed))
                : CustomRedButton(
                    text: 'إرسال رمز التحقق ✉️',
                    onPressed: _sendOtp,
                  ),
          ],
        ),
      ),
    );
  }

  // الخطوة 2
  Widget _buildStep2Otp(ClientState state) {
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
            const Icon(Icons.phonelink_lock_rounded, size: 50, color: AppTheme.primaryGreen),
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
              style: const TextStyle(fontSize: 12.5, color: AppTheme.textMuted, height: 1.4),
            ),
            const SizedBox(height: 24),
            CustomTextField(
              label: 'رمز التحقق (6 أرقام)',
              hint: '000000',
              controller: _otpController,
              keyboardType: TextInputType.number,
              prefixIcon: const Icon(Icons.security_rounded, color: AppTheme.textMuted),
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
                    style: TextStyle(fontSize: 12, color: _resendCountdown == 0 ? AppTheme.primaryRed : AppTheme.textMuted),
                  ),
                ),
                TextButton(
                  onPressed: () => setState(() => _currentStep = 1),
                  child: const Text('تغيير البريد ✏️', style: TextStyle(fontSize: 12, color: AppTheme.textMuted)),
                ),
              ],
            ),
            const SizedBox(height: 20),
            state.isLoading
                ? const Center(child: CircularProgressIndicator(color: AppTheme.primaryRed))
                : CustomRedButton(
                    text: 'تحقق من الرمز ✅',
                    onPressed: _verifyOtp,
                  ),
          ],
        ),
      ),
    );
  }

  // الخطوة 3
  Widget _buildStep3NewPassword(ClientState state) {
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
            const Icon(Icons.lock_reset_rounded, size: 50, color: AppTheme.primaryRed),
            const SizedBox(height: 12),
            const Text(
              'تعيين كلمة مرور جديدة',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              'يجب أن تتكون كلمة المرور من 8 خانات على الأقل لضمان أمان الحساب.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 12.5, color: AppTheme.textMuted, height: 1.4),
            ),
            const SizedBox(height: 24),
            CustomTextField(
              label: 'كلمة المرور الجديدة',
              controller: _newPasswordController,
              obscureText: _obscurePassword,
              prefixIcon: const Icon(Icons.lock_outline, color: AppTheme.textMuted),
              suffixIcon: IconButton(
                icon: Icon(_obscurePassword ? Icons.visibility_off : Icons.visibility, color: AppTheme.textMuted),
                onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
              ),
              validator: (v) {
                if (v == null || v.trim().isEmpty) return 'يرجى إدخال كلمة المرور';
                if (v.trim().length < 8) return 'كلمة المرور يجب أن لا تقل عن 8 خانات';
                return null;
              },
            ),
            const SizedBox(height: 16),
            CustomTextField(
              label: 'تأكيد كلمة المرور الجديدة',
              controller: _confirmPasswordController,
              obscureText: _obscureConfirmPassword,
              prefixIcon: const Icon(Icons.lock_outline, color: AppTheme.textMuted),
              suffixIcon: IconButton(
                icon: Icon(_obscureConfirmPassword ? Icons.visibility_off : Icons.visibility, color: AppTheme.textMuted),
                onPressed: () => setState(() => _obscureConfirmPassword = !_obscureConfirmPassword),
              ),
              validator: (v) {
                if (v == null || v.trim().isEmpty) return 'يرجى تأكيد كلمة المرور';
                if (v.trim() != _newPasswordController.text.trim()) return 'كلمة المرور وتأكيدها غير متطابقين';
                return null;
              },
            ),
            const SizedBox(height: 24),
            state.isLoading
                ? const Center(child: CircularProgressIndicator(color: AppTheme.primaryRed))
                : CustomRedButton(
                    text: 'حفظ وتحديث كلمة المرور 🔐',
                    onPressed: _resetPassword,
                  ),
          ],
        ),
      ),
    );
  }
}
