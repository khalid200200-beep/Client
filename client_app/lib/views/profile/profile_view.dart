import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../state/client_state.dart';
import '../../theme/app_theme.dart';
import '../auth/login_view.dart';

/// شاشة حساب العميل مع خاصية حذف الحساب الإلزامية لمتجر App Store
class ProfileView extends StatelessWidget {
  const ProfileView({super.key});

  void _confirmDeleteAccount(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Row(
          children: [
            Icon(Icons.warning_amber_rounded, color: Colors.red),
            SizedBox(width: 8),
            Text('حذف الحساب نهائياً', style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold)),
          ],
        ),
        content: const Text(
          'هل أنت متأكد من رغبتك في حذف حسابك وكافة بياناتك وسجلات شحناتك نهائياً؟ هذا الإجراء لا يمكن التراجع عنه وفق سياسة الخصوصية.',
          style: TextStyle(fontSize: 13, color: AppTheme.textDark, height: 1.5),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('إلغاء', style: TextStyle(color: AppTheme.textMuted)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            onPressed: () async {
              Navigator.pop(ctx);
              final clientState = Provider.of<ClientState>(context, listen: false);
              await clientState.deleteAccount();
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('تم حذف حسابك وكافة البيانات بنجاح'), backgroundColor: Colors.red),
                );
                Navigator.pushAndRemoveUntil(
                  context,
                  MaterialPageRoute(builder: (_) => const LoginView()),
                  (route) => false,
                );
              }
            },
            child: const Text('نعم، احذف حسابي', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final clientState = Provider.of<ClientState>(context);
    final user = clientState.currentUser;

    return Scaffold(
      backgroundColor: AppTheme.scaffoldBackground,
      appBar: AppBar(
        title: const Text('حسابي', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        child: Column(
          children: [
            // بطاقة بيانات العميل
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
                      shape: BoxShape.circle,
                      color: AppTheme.primaryTeal.withValues(alpha: 0.1),
                      border: Border.all(color: AppTheme.primaryTeal.withValues(alpha: 0.25), width: 1.5),
                    ),
                    child: const Icon(
                      Icons.person_rounded,
                      size: 34,
                      color: AppTheme.primaryTeal,
                    ),
                  ),
                  const SizedBox(width: 14),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(user.name, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 2),
                      Text(user.phone, style: const TextStyle(fontSize: 13, color: AppTheme.textMuted)),
                      Text('المدينة: ${user.city} 📍', style: const TextStyle(fontSize: 12, color: AppTheme.primaryRed, fontWeight: FontWeight.bold)),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // خيارات الحساب والخصوصية
            Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(22),
                boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 12)],
              ),
              child: Column(
                children: [
                  _buildListTile(Icons.shield_outlined, 'سياسة الخصوصية والشروط', () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('سياسة الخصوصية متوافقة مع شروط Apple و Google')),
                    );
                  }),
                  const Divider(height: 1),
                  _buildListTile(Icons.headset_mic_outlined, 'مركز المساعدة والدعم', () {}),
                  const Divider(height: 1),
                  _buildListTile(Icons.info_outline, 'عن التطبيق (الإصدار 1.0.0)', () {}),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // زر حذف الحساب الإلزامي لمتجر آبل
            OutlinedButton.icon(
              style: OutlinedButton.styleFrom(
                side: const BorderSide(color: Colors.redAccent),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
              ),
              icon: const Icon(Icons.delete_forever_outlined, color: Colors.red),
              label: const Text('حذف الحساب نهائياً (Account Deletion)', style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold, fontSize: 13)),
              onPressed: () => _confirmDeleteAccount(context),
            ),

            const SizedBox(height: 12),

            // زر تسجيل الخروج تحت زر حذف الحساب
            OutlinedButton.icon(
              style: OutlinedButton.styleFrom(
                side: BorderSide(color: Colors.grey.shade300),
                backgroundColor: Colors.grey.shade50,
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
          'هل ترغب بتسجيل الخروج من حسابك والعودة لصفحة الدخول؟',
          style: TextStyle(fontSize: 13, color: AppTheme.textDark, height: 1.5),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('إلغاء', style: TextStyle(color: AppTheme.textMuted)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: AppTheme.textDark),
            onPressed: () async {
              Navigator.pop(ctx);
              final clientState = Provider.of<ClientState>(context, listen: false);
              await clientState.logout();
              if (context.mounted) {
                Navigator.pushAndRemoveUntil(
                  context,
                  MaterialPageRoute(builder: (_) => const LoginView()),
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

  Widget _buildListTile(IconData icon, String title, VoidCallback onTap) {
    return ListTile(
      leading: Icon(icon, color: AppTheme.textDark, size: 22),
      title: Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
      trailing: const Icon(Icons.arrow_forward_ios_rounded, size: 14, color: AppTheme.textMuted),
      onTap: onTap,
    );
  }
}
