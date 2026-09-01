import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../theme/app_theme.dart';
import '../../widgets/custom_button.dart';
import '../../widgets/custom_text_field.dart';
import '../../state/client_state.dart';
import '../auth/signup_view.dart';
import '../auth/forgot_password_view.dart';
import '../../main.dart';

/// شاشة تسجيل دخول العميل بالبريد الإلكتروني أو الهاتف مع الربط الحقيقي بالـ API
class LoginView extends StatefulWidget {
  const LoginView({super.key});

  @override
  State<LoginView> createState() => _LoginViewState();
}

class _LoginViewState extends State<LoginView> {
  final _formKey = GlobalKey<FormState>();
  final _identifierController = TextEditingController();
  final _passwordController = TextEditingController();

  @override
  void dispose() {
    _identifierController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _submitLogin() async {
    if (_formKey.currentState!.validate()) {
      final clientState = Provider.of<ClientState>(context, listen: false);
      final success = await clientState.login(
        _identifierController.text.trim(),
        _passwordController.text.trim(),
      );

      if (!mounted) return;

      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('أهلاً بك ${clientState.currentUser.name}! تم تسجيل الدخول بنجاح 🚀'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => const ClientMainWrapper()),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ ${clientState.errorMessage ?? "بيانات الدخول غير صحيحة"}'),
            backgroundColor: Colors.red.shade700,
            duration: const Duration(seconds: 4),
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
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const SizedBox(height: 30),

                // شعار التطبيق
                Center(
                  child: Container(
                    width: 90,
                    height: 90,
                    decoration: BoxDecoration(
                      color: AppTheme.primaryRed.withOpacity(0.08),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.local_shipping_rounded,
                      size: 46,
                      color: AppTheme.primaryRed,
                    ),
                  ),
                ),
                const SizedBox(height: 20),

                // نصوص الترحيب
                const Center(
                  child: Text(
                    'تسجيل الدخول',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.w900,
                      color: AppTheme.textDark,
                    ),
                  ),
                ),
                const SizedBox(height: 6),
                const Center(
                  child: Text(
                    'أدخل بريدك الإلكتروني أو رقم جوالك لمتابعة شحناتك',
                    style: TextStyle(fontSize: 13.5, color: AppTheme.textMuted),
                  ),
                ),
                const SizedBox(height: 36),

                // 1. حقل البريد الإلكتروني / الجوال
                CustomTextField(
                  label: 'البريد الإلكتروني أو رقم الجوال',
                  hint: 'name@domain.com أو 05xxxxxxxx',
                  controller: _identifierController,
                  keyboardType: TextInputType.emailAddress,
                  prefixIcon: const Icon(Icons.mail_outline_rounded, color: AppTheme.textMuted),
                  validator: (v) => v == null || v.isEmpty ? 'الرجاء إدخال البريد الإلكتروني أو رقم الجوال' : null,
                ),
                const SizedBox(height: 16),

                // 2. حقل كلمة المرور
                CustomTextField(
                  label: 'كلمة المرور',
                  hint: '••••••••',
                  controller: _passwordController,
                  isPassword: true,
                  prefixIcon: const Icon(Icons.lock_outline_rounded, color: AppTheme.textMuted),
                  validator: (v) => v == null || v.isEmpty ? 'الرجاء إدخال كلمة المرور' : null,
                ),

                // نسيت كلمة المرور
                Align(
                  alignment: Alignment.centerLeft,
                  child: TextButton(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (_) => const ForgotPasswordView()),
                      );
                    },
                    child: const Text(
                      'نسيت كلمة المرور؟',
                      style: TextStyle(fontSize: 12.5, color: AppTheme.primaryRed, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
                const SizedBox(height: 20),

                // زر تسجيل الدخول
                clientState.isLoading
                    ? const Center(child: CircularProgressIndicator(color: AppTheme.primaryRed))
                    : CustomRedButton(
                        text: 'تسجيل الدخول 🚀',
                        onPressed: _submitLogin,
                        trailingIcon: const Icon(Icons.arrow_forward_rounded, color: Colors.white, size: 18),
                      ),

                const SizedBox(height: 40),

                // الانتقال لإنشاء حساب جديد
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text(
                      'ليس لديك حساب؟ ',
                      style: TextStyle(color: AppTheme.textMuted, fontSize: 14),
                    ),
                    GestureDetector(
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(builder: (context) => const SignupView()),
                        );
                      },
                      child: const Text(
                        'إنشاء حساب جديد',
                        style: TextStyle(
                          color: AppTheme.primaryRed,
                          fontWeight: FontWeight.w900,
                          fontSize: 14,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
