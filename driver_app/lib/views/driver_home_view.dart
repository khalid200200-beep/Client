import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/driver_order_model.dart';
import '../state/driver_state.dart';
import '../theme/driver_theme.dart';
import 'driver_wallet_view.dart';

class DriverHomeView extends StatefulWidget {
  const DriverHomeView({super.key});

  @override
  State<DriverHomeView> createState() => _DriverHomeViewState();
}

class _DriverHomeViewState extends State<DriverHomeView> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<DriverState>(context, listen: false).fetchOrders();
    });
  }

  void _showImagePreview(BuildContext context, String imageUrl) {
    showDialog(
      context: context,
      builder: (ctx) => Dialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ClipRRect(
              borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
              child: Image.network(
                imageUrl,
                fit: BoxFit.contain,
                loadingBuilder: (context, child, loadingProgress) {
                  if (loadingProgress == null) return child;
                  return const SizedBox(
                    height: 200,
                    child: Center(child: CircularProgressIndicator(color: DriverTheme.primaryGreen)),
                  );
                },
                errorBuilder: (context, error, stackTrace) => const SizedBox(
                  height: 120,
                  child: Center(child: Text('تعذر تحميل الصورة', style: TextStyle(color: DriverTheme.textMuted))),
                ),
              ),
            ),
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('إغلاق', style: TextStyle(color: DriverTheme.primaryGreen, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      ),
    );
  }

  void _showLoadedCashDialog(BuildContext context, String orderId) {
    final amountController = TextEditingController(text: '5000');
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Row(
          children: [
            Icon(Icons.payments_rounded, color: Colors.green),
            SizedBox(width: 8),
            Text('تأكيد الاستلام والمبلغ', style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold)),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'أدخل المبلغ النقدي الذي استلمته من العميل:',
              style: TextStyle(fontSize: 13, color: DriverTheme.textMuted),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: amountController,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: 'المبلغ المستلم نقداً',
                hintText: '5000',
                suffixText: 'ج.س / ر.س',
                prefixIcon: const Icon(Icons.attach_money_rounded, color: Colors.green),
                filled: true,
                fillColor: DriverTheme.scaffoldBackground,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(14)),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('إلغاء', style: TextStyle(color: DriverTheme.textMuted)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.green.shade700),
            onPressed: () async {
              final amt = double.tryParse(amountController.text.trim()) ?? 0.0;
              Navigator.pop(ctx);
              final success = await Provider.of<DriverState>(context, listen: false).markLoaded(orderId, collectedAmount: amt);
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(success ? 'تم تأكيد استلام الشحنة وتوثيق المبلغ ($amt) في السيرفر! ✅' : 'فشل التحديث في السيرفر'),
                    backgroundColor: success ? Colors.green : Colors.red,
                  ),
                );
              }
            },
            child: const Text('تأكيد التحميل والمبلغ ✅', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  void _showFailureDialog(BuildContext context, String orderId) {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Row(
          children: [
            Icon(Icons.error_outline_rounded, color: Colors.red),
            SizedBox(width: 8),
            Text('سبب تعذر الشحن', style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold)),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('الرجاء توضيح سبب عدم إتمام الشحن:', style: TextStyle(fontSize: 13, color: DriverTheme.textMuted)),
            const SizedBox(height: 12),
            TextField(
              controller: controller,
              maxLines: 2,
              decoration: InputDecoration(
                hintText: 'مثال: العميل لم يرد، إلغاء من العميل...',
                filled: true,
                fillColor: DriverTheme.scaffoldBackground,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(14)),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('إلغاء', style: TextStyle(color: DriverTheme.textMuted)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            onPressed: () async {
              final reason = controller.text.trim().isEmpty ? 'تعذر التواصل مع العميل' : controller.text.trim();
              Navigator.pop(ctx);
              final success = await Provider.of<DriverState>(context, listen: false).markFailed(orderId, reason);
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(success ? 'تم تسجيل وتحديث حالة تعذر الشحن في السيرفر ✅' : 'فشل التحديث في السيرفر'),
                    backgroundColor: success ? Colors.red.shade700 : Colors.red,
                  ),
                );
              }
            },
            child: const Text('تأكيد الإلغاء', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final driverState = Provider.of<DriverState>(context);
    final orders = driverState.cityOrders;

    return Scaffold(
      backgroundColor: DriverTheme.scaffoldBackground,
      appBar: AppBar(
        title: Column(
          children: [
            const Text('شحنات الكابتن المباشرة 🚚', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 17)),
            Text('المدينة: ${driverState.driverCity} 📍', style: const TextStyle(fontSize: 12, color: DriverTheme.textMuted)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.account_balance_wallet_rounded, color: DriverTheme.primaryGreen, size: 26),
            tooltip: 'الأرباح المكتسبة والمحفظة',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const DriverWalletView()),
              );
            },
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => driverState.fetchOrders(),
        color: DriverTheme.primaryGreen,
        child: orders.isEmpty
            ? SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                child: SizedBox(
                  height: MediaQuery.of(context).size.height * 0.7,
                  child: const Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.inbox_outlined, size: 60, color: DriverTheme.textMuted),
                        SizedBox(height: 12),
                        Text('لا توجد شحنات متاحة حالياً في السيرفر', style: TextStyle(color: DriverTheme.textMuted, fontWeight: FontWeight.bold)),
                        SizedBox(height: 6),
                        Text('اسحب الشاشة للأسفل لتحديث الطلبات 🔄', style: TextStyle(color: DriverTheme.textMuted, fontSize: 12)),
                      ],
                    ),
                  ),
                ),
              )
            : ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                itemCount: orders.length,
                itemBuilder: (context, index) {
                  final order = orders[index];
                  return _buildCard(context, order, driverState);
                },
              ),
      ),
    );
  }

  Widget _buildCard(BuildContext context, DriverOrderModel order, DriverState state) {
    final isPending = order.status == DriverOrderStatus.pending;
    final isAccepted = order.status == DriverOrderStatus.accepted;
    final isLoaded = order.status == DriverOrderStatus.loaded;
    final isFailed = order.status == DriverOrderStatus.failed;

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(22),
        border: isAccepted ? Border.all(color: DriverTheme.primaryBlue.withOpacity(0.5), width: 1.5) : null,
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 12, offset: const Offset(0, 4))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('طلب #${order.id}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              _buildBadge(order.status),
            ],
          ),
          const Divider(height: 20),
          Text('العميل: ${order.clientName} (${order.clientPhone})', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
          const SizedBox(height: 4),
          Text('عدد القطع: ${order.packageCount} | المدينة: ${order.city}', style: const TextStyle(fontSize: 13, color: DriverTheme.textMuted)),
          const SizedBox(height: 4),
          Text('الملاحظات: ${order.notes}', style: const TextStyle(fontSize: 12, color: DriverTheme.textMuted)),

          // شريط صور الشحنة للكابتن
          if (order.images.isNotEmpty || (order.imagePath != null && order.imagePath!.isNotEmpty)) ...[
            const SizedBox(height: 10),
            const Text('صور الشحنة المرفقة من العميل:', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: DriverTheme.textMuted)),
            const SizedBox(height: 6),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: (order.images.isNotEmpty ? order.images : [order.imagePath!]).map((imgUrl) {
                  return GestureDetector(
                    onTap: () => _showImagePreview(context, imgUrl),
                    child: Container(
                      width: 60,
                      height: 60,
                      margin: const EdgeInsets.only(left: 8),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: Colors.grey.shade300),
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(9),
                        child: Image.network(
                          imgUrl,
                          fit: BoxFit.cover,
                          errorBuilder: (_, __, ___) => const Icon(Icons.broken_image, size: 22, color: DriverTheme.textMuted),
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
            ),
          ],
          
          if (order.collectedAmount != null && order.collectedAmount! > 0) ...[
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: const Color(0xFFF0FDF4),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: const Color(0xFF86EFAC)),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('المبلغ المستلم من العميل:', style: TextStyle(fontSize: 12.5, fontWeight: FontWeight.bold, color: Color(0xFF15803D))),
                  Text('${order.collectedAmount!.toStringAsFixed(0)} ج.س / ر.س 💵', style: const TextStyle(fontSize: 13.5, fontWeight: FontWeight.w900, color: Color(0xFF15803D))),
                ],
              ),
            ),
          ],

          if (order.failureReason != null) ...[
            const SizedBox(height: 6),
            Text('سبب التعذر: ${order.failureReason}', style: const TextStyle(fontSize: 12, color: Colors.red, fontWeight: FontWeight.bold)),
          ],

          const SizedBox(height: 16),

          if (isPending) ...[
            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.green.shade600),
                    onPressed: () async {
                      final success = await state.acceptOrder(order.id);
                      if (context.mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text(success ? 'تم قبول الشحنة وحجزها لك بنجاح! 🚚' : 'تعذر قبول الشحنة (ربما قبلها سائق آخر)'),
                            backgroundColor: success ? Colors.green : Colors.red,
                          ),
                        );
                      }
                    },
                    child: const Text('قبول الطلب الحي ✅', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => state.rejectOrder(order.id),
                    child: const Text('إخفاء ❌', style: TextStyle(color: DriverTheme.textDark)),
                  ),
                ),
              ],
            ),
          ] else if (isAccepted) ...[
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(color: const Color(0xFFF0FDF4), borderRadius: BorderRadius.circular(14)),
              child: Column(
                children: [
                  const Text('عند الوصول للعميل واستلام الشحنة:', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.green)),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          style: ElevatedButton.styleFrom(backgroundColor: Colors.green.shade700),
                          icon: const Icon(Icons.check_circle, color: Colors.white, size: 18),
                          label: const Text('تم التحميل ✅', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
                          onPressed: () => _showLoadedCashDialog(context, order.id),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: ElevatedButton.icon(
                          style: ElevatedButton.styleFrom(backgroundColor: Colors.redAccent),
                          icon: const Icon(Icons.cancel, color: Colors.white, size: 18),
                          label: const Text('تعذر الشحن ❌', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
                          onPressed: () => _showFailureDialog(context, order.id),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ] else if (isLoaded) ...[
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(color: Colors.green.withOpacity(0.1), borderRadius: BorderRadius.circular(12)),
              child: const Center(
                child: Text('تم استلام وتحميل الشحنة بنجاح 🚚', style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold, fontSize: 13)),
              ),
            ),
          ] else if (isFailed) ...[
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(color: Colors.red.withOpacity(0.08), borderRadius: BorderRadius.circular(12)),
              child: const Center(
                child: Text('تعذر تحميل الشحنة / تم التوثيق في السيرفر', style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold, fontSize: 13)),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildBadge(DriverOrderStatus status) {
    Color bg = Colors.amber.shade50;
    Color fg = Colors.amber.shade900;
    String text = 'بانتظار سائق';
    if (status == DriverOrderStatus.accepted) { bg = Colors.blue.shade50; fg = Colors.blue.shade900; text = 'تم القبول'; }
    if (status == DriverOrderStatus.loaded) { bg = Colors.green.shade50; fg = Colors.green.shade900; text = 'تم التحميل'; }
    if (status == DriverOrderStatus.failed) { bg = Colors.red.shade50; fg = Colors.red.shade900; text = 'تعذر الشحن'; }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(12)),
      child: Text(text, style: TextStyle(color: fg, fontSize: 11, fontWeight: FontWeight.bold)),
    );
  }
}
