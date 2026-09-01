import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../theme/driver_theme.dart';
import '../../state/driver_state.dart';
import 'driver_pending_view.dart';

/// شاشة تسجيل كابتن جديد مع الربط الحقيقي بالـ API
class DriverSignupView extends StatefulWidget {
  const DriverSignupView({super.key});

  @override
  State<DriverSignupView> createState() => _DriverSignupViewState();
}

class _DriverSignupViewState extends State<DriverSignupView> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController(text: 'أحمد كابتن التوصيل');
  final _emailController = TextEditingController(text: 'driver_new@sudra.sa');
  final _phoneController = TextEditingController(text: '0901234567');
  final _cityController = TextEditingController(text: 'الخرطوم');
  final _plateController = TextEditingController(text: 'خ 1234 - دباب تويوتا');
  final _passwordController = TextEditingController(text: '123456');

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _cityController.dispose();
    _plateController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _submitSignup() async {
    if (_formKey.currentState!.validate()) {
      final driverState = Provider.of<DriverState>(context, listen: false);
      final res = await driverState.register(
        name: _nameController.text.trim(),
        email: _emailController.text.trim(),
        phone: _phoneController.text.trim(),
        city: _cityController.text.trim(),
        vehiclePlate: _plateController.text.trim(),
        password: _passwordController.text.trim(),
      );

      if (!mounted) return;

      if (res['success'] == true) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('🎉 تم استلام طلبك بنجاح! بانتظار تفعيل الحساب من إدارة سودرا للشحن (Sudra)'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (context) => DriverPendingView(
              name: _nameController.text.trim(),
              email: _emailController.text.trim(),
              phone: _phoneController.text.trim(),
              city: _cityController.text.trim(),
            ),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ ${driverState.errorMessage ?? "فشل إرسال طلب التسجيل"}'),
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
      appBar: AppBar(
        title: const Text('انضمام كابتن جديد 🚚', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 17)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'طلب انضمام لأسطول التوصيل',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: DriverTheme.textDark),
              ),
              const SizedBox(height: 4),
              const Text(
                'أدخل بياناتك لإنشاء حساب كابتن ومراجعته من إدارة سودرا للشحن (Sudra)',
                style: TextStyle(fontSize: 12.5, color: DriverTheme.textMuted),
              ),
              const SizedBox(height: 24),

              TextFormField(
                controller: _nameController,
                decoration: InputDecoration(
                  labelText: 'الاسم الكامل للكابتن',
                  hintText: 'الاسم ثلاثي',
                  prefixIcon: const Icon(Icons.person_outline_rounded, color: DriverTheme.textMuted),
                  filled: true,
                  fillColor: Colors.white,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide(color: Colors.grey.shade300)),
                ),
                validator: (v) => v == null || v.isEmpty ? 'الرجاء إدخال الاسم' : null,
              ),
              const SizedBox(height: 14),

              TextFormField(
                controller: _emailController,
                keyboardType: TextInputType.emailAddress,
                decoration: InputDecoration(
                  labelText: 'البريد الإلكتروني',
                  hintText: 'captain@domain.com',
                  prefixIcon: const Icon(Icons.mail_outline_rounded, color: DriverTheme.textMuted),
                  filled: true,
                  fillColor: Colors.white,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide(color: Colors.grey.shade300)),
                ),
                validator: (v) => v == null || !v.contains('@') ? 'الرجاء إدخال بريد إلكتروني صحيح' : null,
              ),
              const SizedBox(height: 14),

              TextFormField(
                controller: _phoneController,
                keyboardType: TextInputType.phone,
                decoration: InputDecoration(
                  labelText: 'رقم الجوال',
                  hintText: '09xxxxxxxx أو 05xxxxxxxx',
                  prefixIcon: const Icon(Icons.phone_android_rounded, color: DriverTheme.textMuted),
                  filled: true,
                  fillColor: Colors.white,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide(color: Colors.grey.shade300)),
                ),
                validator: (v) => v == null || v.length < 9 ? 'الرجاء إدخال رقم هاتف صحيح' : null,
              ),
              const SizedBox(height: 14),

              TextFormField(
                controller: _cityController,
                decoration: InputDecoration(
                  labelText: 'المدينة ونطاق التغطية',
                  hintText: 'الخرطوم، بحري، أم درمان...',
                  prefixIcon: const Icon(Icons.location_on_outlined, color: DriverTheme.textMuted),
                  filled: true,
                  fillColor: Colors.white,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide(color: Colors.grey.shade300)),
                ),
                validator: (v) => v == null || v.isEmpty ? 'الرجاء إدخال المدينة' : null,
              ),
              const SizedBox(height: 14),

              TextFormField(
                controller: _plateController,
                decoration: InputDecoration(
                  labelText: 'نوع ولوحة المركبة',
                  hintText: 'خ 1234 أو فان هايس',
                  prefixIcon: const Icon(Icons.directions_car_outlined, color: DriverTheme.textMuted),
                  filled: true,
                  fillColor: Colors.white,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide(color: Colors.grey.shade300)),
                ),
              ),
              const SizedBox(height: 14),

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
                ),
                validator: (v) => v == null || v.length < 6 ? 'كلمة المرور يجب أن لا تقل عن 6 خانات' : null,
              ),
              const SizedBox(height: 24),

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
                      onPressed: _submitSignup,
                      child: const Text(
                        'إرسال طلب الانضمام ومراجعة الحساب 🚀',
                        style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                      ),
                    ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }
}
