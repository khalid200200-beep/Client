import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../theme/app_theme.dart';
import '../../widgets/custom_button.dart';
import '../../widgets/custom_text_field.dart';
import '../../state/client_state.dart';
import 'otp_view.dart';

/// شاشة إنشاء حساب جديد للعميل مع التحقق برمز OTP عبر البريد الإلكتروني
class SignupView extends StatefulWidget {
  const SignupView({super.key});

  @override
  State<SignupView> createState() => _SignupViewState();
}

class _SignupViewState extends State<SignupView> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  String _selectedCity = 'الرياض';

  final List<String> _cities = ['الخرطوم', 'بورتسودان', 'أم درمان', 'بحري', 'الرياض', 'جدة'];

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _submitSignUp() async {
    if (_formKey.currentState!.validate()) {
      final clientState = Provider.of<ClientState>(context, listen: false);
      final email = _emailController.text.trim();
      final name = _nameController.text.trim();
      final phone = _phoneController.text.trim();
      final password = _passwordController.text.trim();

      // إرسال رمز OTP إلى البريد الإلكتروني وواتساب
      final otpSent = await clientState.sendOtp(
        email: email,
        phone: phone,
        actionType: 'register',
      );

      if (!mounted) return;

      if (otpSent) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('📲 تم إرسال رمز التحقق (OTP) إلى بريدك وواتساب: $email'),
            backgroundColor: Colors.green,
          ),
        );

        // الانتقال لشاشة إدخال رمز التحقق
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => OtpView(
              email: email,
              phoneNumber: phone,
              userName: name,
              city: _selectedCity,
              password: password,
            ),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ ${clientState.errorMessage ?? "فشل إرسال رمز التحقق"}'),
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
      appBar: AppBar(
        title: const Text('إنشاء حساب جديد', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'انضم إلينا الآن',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: AppTheme.textDark),
              ),
              const SizedBox(height: 4),
              const Text(
                'أدخل بياناتك لإنشاء حساب وتأكيد بريدك الإلكتروني',
                style: TextStyle(fontSize: 13, color: AppTheme.textMuted),
              ),
              const SizedBox(height: 28),

              CustomTextField(
                label: 'الاسم الكامل',
                hint: 'أدخل اسمك الكريم',
                controller: _nameController,
                prefixIcon: const Icon(Icons.person_outline_rounded, color: AppTheme.textMuted),
                validator: (v) => v == null || v.isEmpty ? 'الرجاء إدخال الاسم' : null,
              ),
              const SizedBox(height: 16),

              CustomTextField(
                label: 'البريد الإلكتروني',
                hint: 'name@domain.com',
                controller: _emailController,
                keyboardType: TextInputType.emailAddress,
                prefixIcon: const Icon(Icons.mail_outline_rounded, color: AppTheme.textMuted),
                validator: (v) => v == null || !v.contains('@') ? 'الرجاء إدخال بريد إلكتروني صحيح' : null,
              ),
              const SizedBox(height: 16),

              CustomTextField(
                label: 'رقم الجوال',
                hint: '09xxxxxxxx أو 05xxxxxxxx',
                controller: _phoneController,
                keyboardType: TextInputType.phone,
                prefixIcon: const Icon(Icons.phone_android_rounded, color: AppTheme.textMuted),
                validator: (v) => v == null || v.length < 9 ? 'الرجاء إدخال رقم هاتف صحيح' : null,
              ),
              const SizedBox(height: 16),

              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('المدينة', style: TextStyle(fontSize: 13.5, fontWeight: FontWeight.w700, color: AppTheme.textDark)),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: Colors.grey.shade200, width: 1.2),
                    ),
                    child: DropdownButtonHideUnderline(
                      child: DropdownButton<String>(
                        isExpanded: true,
                        value: _selectedCity,
                        items: _cities.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
                        onChanged: (val) {
                          if (val != null) setState(() => _selectedCity = val);
                        },
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              CustomTextField(
                label: 'كلمة المرور',
                hint: '••••••••',
                controller: _passwordController,
                isPassword: true,
                prefixIcon: const Icon(Icons.lock_outline_rounded, color: AppTheme.textMuted),
                validator: (v) => v == null || v.length < 6 ? 'كلمة المرور يجب أن لا تقل عن 6 خانات' : null,
              ),
              const SizedBox(height: 32),

              clientState.isLoading
                  ? const Center(child: CircularProgressIndicator(color: AppTheme.primaryRed))
                  : CustomRedButton(
                      text: 'إنشاء الحساب وتأكيد البريد 🚀',
                      onPressed: _submitSignUp,
                    ),
            ],
          ),
        ),
      ),
    );
  }
}
