import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../state/driver_state.dart';
import '../theme/driver_theme.dart';
import 'auth/driver_login_view.dart';

class DriverProfileView extends StatelessWidget {
  const DriverProfileView({super.key});

  void _confirmDeleteAccount(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Row(
          children: [
            Icon(Icons.warning_amber_rounded, color: Colors.red),
            SizedBox(width: 8),
            Text('حذف حساب السائق', style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold)),
          ],
        ),
        content: const Text(
          'هل أنت متأكد من رغبتك في حذف حساب السائق وكافة بياناتك وسجلات رحلاتك نهائياً؟ هذا الإجراء لا يمكن التراجع عنه وفق سياسة الخصوصية ومتطلبات المتاجر.',
          style: TextStyle(fontSize: 13, height: 1.5),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('إلغاء', style: TextStyle(color: Colors.grey)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            onPressed: () async {
              Navigator.pop(ctx);
              final driverState = Provider.of<DriverState>(context, listen: false);
              await driverState.deleteAccount();
              if (context.mounted) {
                Navigator.pushAndRemoveUntil(
                  context,
                  MaterialPageRoute(builder: (_) => const DriverLoginView()),
                  (route) => false,
                );
              }
            },
            child: const Text('تأكيد الحذف', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  void _confirmLogout(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Row(
          children: [
            Icon(Icons.logout_rounded, color: Colors.black87),
            SizedBox(width: 8),
            Text('تسجيل الخروج', style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold)),
          ],
        ),
        content: const Text(
          'هل ترغب بتسجيل الخروج من حساب السائق والعودة لصفحة الدخول؟',
          style: TextStyle(fontSize: 13, height: 1.5),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('إلغاء', style: TextStyle(color: Colors.grey)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.black87),
            onPressed: () async {
              Navigator.pop(ctx);
              final driverState = Provider.of<DriverState>(context, listen: false);
              await driverState.logout();
              if (context.mounted) {
                Navigator.pushAndRemoveUntil(
                  context,
                  MaterialPageRoute(builder: (_) => const DriverLoginView()),
                  (route) => false,
                );
              }
            },
            child: const Text('تأكيد الخروج', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final driverState = Provider.of<DriverState>(context);

    return Scaffold(
      backgroundColor: DriverTheme.scaffoldBackground,
      appBar: AppBar(title: const Text('حساب الكابتن', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18))),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(22),
                boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 12)],
              ),
              child: Row(
                children: [
                  Container(
                    width: 60,
                    height: 60,
                    decoration: BoxDecoration(
                      color: DriverTheme.primaryBlue.withOpacity(0.1),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.local_shipping_rounded, color: DriverTheme.primaryBlue, size: 32),
                  ),
                  const SizedBox(width: 14),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(driverState.driverName, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 2),
                      Text(driverState.driverPhone, style: const TextStyle(fontSize: 13, color: DriverTheme.textMuted)),
                      Text('نطاق التغطية: ${driverState.driverCity} 📍', style: const TextStyle(fontSize: 12, color: DriverTheme.primaryBlue, fontWeight: FontWeight.bold)),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            
            // 1. زر حذف حساب السائق
            OutlinedButton.icon(
              style: OutlinedButton.styleFrom(
                side: const BorderSide(color: Colors.redAccent),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
              ),
              icon: const Icon(Icons.delete_forever_outlined, color: Colors.red),
              label: const Text('حذف حساب السائق نهائياً (App Store Requirement)', style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold, fontSize: 13)),
              onPressed: () => _confirmDeleteAccount(context),
            ),

            const SizedBox(height: 12),

            // 2. زر تسجيل الخروج تحت زر حذف الحساب
            OutlinedButton.icon(
              style: OutlinedButton.styleFrom(
                side: BorderSide(color: Colors.grey.shade300),
                backgroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
              ),
              icon: const Icon(Icons.logout_rounded, color: Colors.black87),
              label: const Text('تسجيل الخروج من الحساب 🚪', style: TextStyle(color: Colors.black87, fontWeight: FontWeight.bold, fontSize: 13.5)),
              onPressed: () => _confirmLogout(context),
            ),
          ],
        ),
      ),
    );
  }
}
