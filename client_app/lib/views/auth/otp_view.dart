import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../theme/app_theme.dart';
import '../../widgets/custom_button.dart';
import '../../state/client_state.dart';
import '../../main.dart';

/// شاشة التحقق برمز OTP عبر البريد الإلكتروني
class OtpView extends StatefulWidget {
  final String email;
  final String phoneNumber;
  final String? userName;
  final String? city;
  final String? password;

  const OtpView({
    super.key,
    required this.email,
    required this.phoneNumber,
    this.userName,
    this.city,
    this.password,
  });

  @override
  State<OtpView> createState() => _OtpViewState();
}

class _OtpViewState extends State<OtpView> {
  final List<TextEditingController> _controllers = List.generate(4, (_) => TextEditingController());
  final List<FocusNode> _focusNodes = List.generate(4, (_) => FocusNode());
  int _secondsRemaining = 60;
  Timer? _timer;
  bool _isResending = false;

  @override
  void initState() {
    super.initState();
    _startCountdown();
  }

  void _startCountdown() {
    _timer?.cancel();
    setState(() => _secondsRemaining = 60);
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_secondsRemaining > 0) {
        setState(() => _secondsRemaining--);
      } else {
        timer.cancel();
      }
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    for (var c in _controllers) { c.dispose(); }
    for (var f in _focusNodes) { f.dispose(); }
    super.dispose();
  }

  String get _otpCode => _controllers.map((c) => c.text).join();

  Future<void> _verifyOtp() async {
    final code = _otpCode.trim();
    if (code.length < 4) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('⚠️ الرجاء إدخال رمز التحقق المكون من 4 أرقام'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    final clientState = Provider.of<ClientState>(context, listen: false);
    
    // التحقق من الرمز بالخادم
    final isVerified = await clientState.verifyOtp(email: widget.email, otp: code);

    if (!mounted) return;

    if (isVerified) {
      // إتمام تسجيل الحساب إذا توفرت بيانات التسجيل
      if (widget.password != null && widget.userName != null) {
        final registered = await clientState.register(
          name: widget.userName!,
          email: widget.email,
          phone: widget.phoneNumber,
          city: widget.city ?? 'الخرطوم',
          password: widget.password!,
        );

        if (!mounted) return;

        if (registered) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('🎉 تم التحقق وإنشاء الحساب بنجاح! مرحباً بك في تطبيق سودرا للشحن'),
              backgroundColor: Colors.green,
            ),
          );
          Navigator.pushAndRemoveUntil(
            context,
            MaterialPageRoute(builder: (context) => const ClientMainWrapper()),
            (route) => false,
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('❌ ${clientState.errorMessage ?? "حدث خطأ أثناء إتمام التسجيل"}'),
              backgroundColor: Colors.red.shade700,
            ),
          );
        }
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('🎉 تم التحقق بنجاح!'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pushAndRemoveUntil(
          context,
          MaterialPageRoute(builder: (context) => const ClientMainWrapper()),
          (route) => false,
        );
      }
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('❌ ${clientState.errorMessage ?? "رمز التحقق غير صحيح أو انتهت صلاحيته"}'),
          backgroundColor: Colors.red.shade700,
        ),
      );
    }
  }

  Future<void> _resendOtp() async {
    if (_secondsRemaining > 0 || _isResending) return;

    setState(() => _isResending = true);
    final clientState = Provider.of<ClientState>(context, listen: false);
    final success = await clientState.sendOtp(email: widget.email, actionType: 'register');
    setState(() => _isResending = false);

    if (!mounted) return;

    if (success) {
      _startCountdown();
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('📧 تم إرسال رمز تحقق جديد إلى بريدك الإلكتروني بنجاح'),
          backgroundColor: Colors.green,
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('❌ ${clientState.errorMessage ?? "تعذر إعادة إرسال الرمز"}'),
          backgroundColor: Colors.red.shade700,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final clientState = Provider.of<ClientState>(context);

    return Scaffold(
      backgroundColor: AppTheme.scaffoldBackground,
      appBar: AppBar(
        title: const Text('تأكيد البريد الإلكتروني', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 10),
            Center(
              child: Container(
                padding: const EdgeInsets.all(22),
                decoration: BoxDecoration(
                  color: AppTheme.primaryRed.withOpacity(0.08),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.mark_email_read_outlined, size: 52, color: AppTheme.primaryRed),
              ),
            ),
            const SizedBox(height: 24),
            const Center(
              child: Text(
                'أدخل رمز التحقق (OTP)',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: AppTheme.textDark),
              ),
            ),
            const SizedBox(height: 8),
            Center(
              child: Text(
                'تم إرسال كود التحقق إلى بريدك الإلكتروني:\n${widget.email}',
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 14, color: AppTheme.textMuted, height: 1.6),
              ),
            ),
            const SizedBox(height: 36),

            // خانات إدخال الرمز الأربعة
            Directionality(
              textDirection: TextDirection.ltr,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: List.generate(4, (index) {
                  return SizedBox(
                    width: 62,
                    height: 62,
                    child: TextField(
                      controller: _controllers[index],
                      focusNode: _focusNodes[index],
                      textAlign: TextAlign.center,
                      keyboardType: TextInputType.number,
                      maxLength: 1,
                      style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w900, color: AppTheme.primaryRed),
                      decoration: InputDecoration(
                        counterText: '',
                        filled: true,
                        fillColor: Colors.white,
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(16),
                          borderSide: BorderSide(color: Colors.grey.shade300, width: 1.5),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(16),
                          borderSide: const BorderSide(color: AppTheme.primaryRed, width: 2),
                        ),
                      ),
                      onChanged: (value) {
                        if (value.isNotEmpty && index < 3) {
                          _focusNodes[index + 1].requestFocus();
                        } else if (value.isEmpty && index > 0) {
                          _focusNodes[index - 1].requestFocus();
                        }
                        if (_otpCode.length == 4) {
                          _verifyOtp();
                        }
                      },
                    ),
                  );
                }),
              ),
            ),
            const SizedBox(height: 36),

            // زر التحقق
            clientState.isLoading
                ? const Center(child: CircularProgressIndicator(color: AppTheme.primaryRed))
                : CustomRedButton(
                    text: 'تأكيد الرمز والدخول 🚀',
                    onPressed: _verifyOtp,
                  ),
            const SizedBox(height: 32),

            // إعادة الإرسال مع المؤقت
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text('لم تستلم الرمز؟ ', style: TextStyle(color: AppTheme.textMuted, fontSize: 14)),
                _secondsRemaining > 0
                    ? Text(
                        'إعادة الإرسال بعد ($_secondsRemaining ثانية)',
                        style: const TextStyle(color: AppTheme.textMuted, fontWeight: FontWeight.bold, fontSize: 13),
                      )
                    : GestureDetector(
                        onTap: _resendOtp,
                        child: Text(
                          _isResending ? 'جاري الإرسال...' : 'إعادة الإرسال الآن 🔄',
                          style: const TextStyle(color: AppTheme.primaryRed, fontWeight: FontWeight.bold, fontSize: 14),
                        ),
                      ),
              ],
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }
}
