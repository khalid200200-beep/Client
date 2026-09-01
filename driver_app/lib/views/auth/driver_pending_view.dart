import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../theme/driver_theme.dart';
import '../../state/driver_state.dart';
import 'driver_login_view.dart';
import '../../main.dart';

/// شاشة حالة الحساب قيد المراجعة والاعتماد مع فحص حقيقي من السيرفر
class DriverPendingView extends StatefulWidget {
  final String name;
  final String email;
  final String phone;
  final String city;

  const DriverPendingView({
    super.key,
    required this.name,
    required this.email,
    required this.phone,
    required this.city,
  });

  @override
  State<DriverPendingView> createState() => _DriverPendingViewState();
}

class _DriverPendingViewState extends State<DriverPendingView> {
  bool _isChecking = false;

  Future<void> _checkStatus() async {
    setState(() => _isChecking = true);
    
    // فحص حقيقي مع السيرفر
    final driverState = Provider.of<DriverState>(context, listen: false);
    final res = await driverState.login(widget.email.isNotEmpty ? widget.email : widget.phone, '123456');

    if (!mounted) return;
    setState(() => _isChecking = false);

    if (res['success'] == true && res['isPending'] == false) {
      showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          title: const Row(
            children: [
              Icon(Icons.check_circle_rounded, color: Colors.green),
              SizedBox(width: 8),
              Text('تهانينا! تم التفعيل 🎉', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            ],
          ),
          content: const Text(
            'تمت مراجعة واعتماد حسابك بنجاح من إدارة سودرا للشحن (Sudra Express)! يمكنك الآن استلام وبدء توصيل الطلبات.',
            style: TextStyle(fontSize: 14, height: 1.5),
          ),
          actions: [
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: DriverTheme.primaryGreen, foregroundColor: Colors.white),
              onPressed: () {
                Navigator.pop(ctx);
                Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const DriverMainWrapper()));
              },
              child: const Text('دخول لوحة السائق 🚀'),
            ),
          ],
        ),
      );
    } else {
      showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          title: const Row(
            children: [
              Icon(Icons.hourglass_top_rounded, color: Colors.amber),
              SizedBox(width: 8),
              Text('حالة الحساب', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            ],
          ),
          content: const Text(
            'حسابك لا يزال قيد المراجعة في لوحة الإدارة. سيتم إشعارك فور الاعتماد.',
            style: TextStyle(fontSize: 14, height: 1.5),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('حسناً', style: TextStyle(fontWeight: FontWeight.bold, color: DriverTheme.primaryGreen)),
            ),
          ],
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: DriverTheme.scaffoldBackground,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // أيقونة الساعة والانتظار
              Center(
                child: Container(
                  width: 90,
                  height: 90,
                  decoration: BoxDecoration(
                    color: Colors.amber.shade50,
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.amber.shade200, width: 2),
                  ),
                  child: const Icon(
                    Icons.hourglass_empty_rounded,
                    size: 44,
                    color: Colors.amber,
                  ),
                ),
              ),
              const SizedBox(height: 20),

              const Center(
                child: Text(
                  'حسابك قيد المراجعة والاعتماد',
                  style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: DriverTheme.textDark),
                ),
              ),
              const SizedBox(height: 8),
              const Center(
                child: Text(
                  'تم استلام طلب انضمامك كمندوب لسودرا للشحن (Sudra Express) بنجاح! 🚚\nتقوم الإدارة بمراجعة بياناتك في لوحة التحكم.',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 13, color: DriverTheme.textMuted, height: 1.5),
                ),
              ),
              const SizedBox(height: 28),

              // كارد ملخص البيانات
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: Colors.grey.shade200),
                  boxShadow: [
                    BoxShadow(color: Colors.black.withOpacity(0.02), blurRadius: 10, offset: const Offset(0, 4)),
                  ],
                ),
                child: Column(
                  children: [
                    _buildRow('👤 المندوب:', widget.name),
                    const Divider(height: 16),
                    _buildRow('✉️ البريد الإلكتروني:', widget.email),
                    const Divider(height: 16),
                    _buildRow('📞 الجوال:', widget.phone),
                    const Divider(height: 16),
                    _buildRow('📍 المدينة:', widget.city),
                  ],
                ),
              ),
              const SizedBox(height: 28),

              // زر فحص الحالة
              _isChecking
                  ? const Center(child: CircularProgressIndicator(color: DriverTheme.primaryGreen))
                  : ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: DriverTheme.primaryGreen,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      ),
                      onPressed: _checkStatus,
                      icon: const Icon(Icons.refresh_rounded),
                      label: const Text('🔄 فحص حالة تفعيل الحساب الآن', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
                    ),
              const SizedBox(height: 12),

              // زر تسجيل الخروج
              OutlinedButton(
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  side: BorderSide(color: Colors.grey.shade300),
                ),
                onPressed: () {
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(builder: (_) => const DriverLoginView()),
                  );
                },
                child: const Text('تسجيل الخروج والعودة 🚪', style: TextStyle(color: DriverTheme.textMuted, fontWeight: FontWeight.bold)),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: DriverTheme.textDark)),
        Text(value, style: const TextStyle(fontSize: 13, color: DriverTheme.textMuted)),
      ],
    );
  }
}
