import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../theme/driver_theme.dart';
import '../../state/driver_state.dart';
import '../../main.dart';
import 'driver_signup_view.dart';
import 'driver_pending_view.dart';
import 'driver_forgot_password_view.dart';

/// شاشة تسجيل دخول الكابتن مع الربط الحقيقي بالـ API
class DriverLoginView extends StatefulWidget {
  const DriverLoginView({super.key});

  @override
  State<DriverLoginView> createState() => _DriverLoginViewState();
}

class _DriverLoginViewState extends State<DriverLoginView> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _submitLogin() async {
    if (_formKey.currentState!.validate()) {
      final driverState = Provider.of<DriverState>(context, listen: false);
      final res = await driverState.login(
        _emailController.text.trim(),
        _passwordController.text.trim(),
      );

      if (!mounted) return;

      if (res['isPending'] == true) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (context) => DriverPendingView(
              name: driverState.driverName,
              email: _emailController.text.trim(),
              phone: driverState.driverPhone,
              city: driverState.driverCity,
            ),
          ),
        );
      } else if (res['success'] == true) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('أهلاً بك كابتن ${driverState.driverName}! 🚚'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => const DriverMainWrapper()),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ ${driverState.errorMessage ?? "بيانات الدخول غير صحيحة"}'),
            backgroundColor: Colors.red.shade700,
            duration: const Duration(seconds: 4),
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
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const SizedBox(height: 20),

                // أيقونة وشعار الكابتن
                Center(
                  child: Container(
                    width: 90,
                    height: 90,
                    decoration: BoxDecoration(
                      color: DriverTheme.primaryGreen.withOpacity(0.1),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.local_shipping_rounded,
                      size: 46,
                      color: DriverTheme.primaryGreen,
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // شارة بوابة الكباتن
                Center(
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                    decoration: BoxDecoration(
                      color: Colors.amber.shade100,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: Colors.amber.shade400),
                    ),
                    child: Text(
                      '🚚 بوابة الكباتن والمناديب',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: Colors.amber.shade900,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 12),

                const Center(
                  child: Text(
                    'تسجيل دخول الكابتن',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.w900,
                      color: DriverTheme.textDark,
                    ),
                  ),
                ),
                const SizedBox(height: 6),
                const Center(
                  child: Text(
                    'تطبيق إدارة وتوصيل طرود سودرا للشحن (Sudra Express)',
                    style: TextStyle(fontSize: 13, color: DriverTheme.textMuted),
                  ),
                ),
                const SizedBox(height: 32),

                // 1. حقل البريد الإلكتروني
                TextFormField(
                  controller: _emailController,
                  keyboardType: TextInputType.emailAddress,
                  decoration: InputDecoration(
                    labelText: 'البريد الإلكتروني أو الجوال',
                    hintText: 'captain@domain.com أو 09xxxxxxxx',
                    prefixIcon: const Icon(Icons.mail_outline_rounded, color: DriverTheme.textMuted),
                    filled: true,
                    fillColor: Colors.white,
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide(color: Colors.grey.shade300)),
                    enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide(color: Colors.grey.shade300)),
                  ),
                  validator: (v) => v == null || v.trim().isEmpty ? 'الرجاء إدخال البريد الإلكتروني أو رقم الجوال' : null,
                ),
                const SizedBox(height: 16),

                // 2. حقل كلمة المرور
                TextFormField(
                  controller: _passwordController,
                  obscureText: true,
                  decoration: InputDecoration(
                    labelText: 'كلمة المرور',
                    hintText: '••••••••',
                    prefixIcon: const Icon(Icons.lock_outline_rounded, color: DriverTheme.textMuted),
                    filled: true,
                    fillColor: Colors.white,
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide(color: Colors.grey.shade300)),
                    enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide(color: Colors.grey.shade300)),
                  ),
                  validator: (v) => v == null || v.isEmpty ? 'الرجاء إدخال كلمة المرور' : null,
                ),

                // نسيت كلمة المرور
                Align(
                  alignment: Alignment.centerLeft,
                  child: TextButton(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (_) => const DriverForgotPasswordView()),
                      );
                    },
                    child: const Text(
                      'نسيت كلمة المرور؟',
                      style: TextStyle(fontSize: 12.5, color: DriverTheme.primaryGreen, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // زر تسجيل الدخول
                driverState.isLoading
                    ? const Center(child: CircularProgressIndicator(color: DriverTheme.primaryGreen))
                    : ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: DriverTheme.primaryGreen,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                          elevation: 2,
                        ),
                        onPressed: _submitLogin,
                        child: const Text(
                          'تسجيل الدخول للكابتن 🚀',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900),
                        ),
                      ),

                const SizedBox(height: 36),

                // رابط إنشاء حساب كابتن جديد
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text(
                      'هل ترغب بالانضمام للأسطول؟ ',
                      style: TextStyle(color: DriverTheme.textMuted, fontSize: 13.5),
                    ),
                    GestureDetector(
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(builder: (context) => const DriverSignupView()),
                        );
                      },
                      child: const Text(
                        'تسجيل كابتن جديد',
                        style: TextStyle(
                          color: DriverTheme.primaryGreen,
                          fontWeight: FontWeight.w900,
                          fontSize: 13.5,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
