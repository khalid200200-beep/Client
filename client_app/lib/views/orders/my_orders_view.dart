import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/order_model.dart';
import '../../state/client_state.dart';
import '../../theme/app_theme.dart';
import 'create_order_view.dart';

class MyOrdersView extends StatefulWidget {
  const MyOrdersView({super.key});

  @override
  State<MyOrdersView> createState() => _MyOrdersViewState();
}

class _MyOrdersViewState extends State<MyOrdersView> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        context.read<ClientState>().fetchOrders();
      }
    });
  }

  void _showImagePreview(String imageUrl) {
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
                    child: Center(child: CircularProgressIndicator(color: AppTheme.primaryRed)),
                  );
                },
                errorBuilder: (context, error, stackTrace) => const SizedBox(
                  height: 120,
                  child: Center(child: Text('تعذر تحميل الصورة', style: TextStyle(color: AppTheme.textMuted))),
                ),
              ),
            ),
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('إغلاق', style: TextStyle(color: AppTheme.primaryRed, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final clientState = Provider.of<ClientState>(context);
    final orders = clientState.orders;

    return Scaffold(
      backgroundColor: AppTheme.scaffoldBackground,
      appBar: AppBar(
        title: const Text('طلباتي وشحناتي 📦', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
      ),
      body: RefreshIndicator(
        onRefresh: () => clientState.fetchOrders(),
        color: AppTheme.primaryRed,
        child: orders.isEmpty
            ? SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                child: SizedBox(
                  height: MediaQuery.of(context).size.height * 0.7,
                  child: Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.local_shipping_outlined, size: 70, color: AppTheme.textMuted),
                        const SizedBox(height: 16),
                        const Text('لا توجد شحنات مسجلة حالياً', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 8),
                        const Text('اطلب شحنك الأول بضغطة زر واحدة!', style: TextStyle(color: AppTheme.textMuted, fontSize: 13)),
                        const SizedBox(height: 24),
                        ElevatedButton(
                          onPressed: () {
                            Navigator.push(context, MaterialPageRoute(builder: (_) => const CreateOrderView()));
                          },
                          style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primaryRed),
                          child: const Text('اطلب شحن الآن 🚀', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                        ),
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
                  return _buildOrderCard(order);
                },
              ),
      ),
    );
  }

  Widget _buildOrderCard(OrderModel order) {
    final List<String> orderImages = order.images.isNotEmpty
        ? order.images
        : (order.imagePath != null && order.imagePath!.isNotEmpty ? [order.imagePath!] : []);

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(22),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 12, offset: const Offset(0, 4))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('شحنة #${order.id}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              _buildBadge(order.status),
            ],
          ),
          const Divider(height: 20),
          Row(
            children: [
              const Icon(Icons.location_city_rounded, size: 18, color: AppTheme.textMuted),
              const SizedBox(width: 6),
              Text('المدينة: ${order.city}', style: const TextStyle(fontSize: 14)),
              const Spacer(),
              const Icon(Icons.inventory_2_outlined, size: 18, color: AppTheme.textMuted),
              const SizedBox(width: 6),
              Text('${order.packageCount} قطع', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
            ],
          ),
          const SizedBox(height: 8),
          Text('الملاحظات: ${order.notes}', style: const TextStyle(fontSize: 12, color: AppTheme.textMuted)),

          // عرض شريط الصور إذا وجدت
          if (orderImages.isNotEmpty) ...[
            const SizedBox(height: 12),
            const Text('الصور المرفقة:', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppTheme.textMuted)),
            const SizedBox(height: 6),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: orderImages.map((imgUrl) {
                  return GestureDetector(
                    onTap: () => _showImagePreview(imgUrl),
                    child: Container(
                      width: 64,
                      height: 64,
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
                          errorBuilder: (_, __, ___) => const Icon(Icons.broken_image, size: 24, color: AppTheme.textMuted),
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
                  const Text('المبلغ المسدد للمندوب:', style: TextStyle(fontSize: 12.5, fontWeight: FontWeight.bold, color: Color(0xFF15803D))),
                  Text('${order.collectedAmount!.toStringAsFixed(0)} ج.س / ر.س 💵', style: const TextStyle(fontSize: 13.5, fontWeight: FontWeight.w900, color: Color(0xFF15803D))),
                ],
              ),
            ),
          ],

          if (order.driverName != null) ...[
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(color: const Color(0xFFF6F8FD), borderRadius: BorderRadius.circular(12)),
              child: Row(
                children: [
                  const Icon(Icons.drive_eta_rounded, color: Colors.blue, size: 20),
                  const SizedBox(width: 8),
                  Text('الكابتن المعين: ${order.driverName} (${order.driverPhone ?? ""})',
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Colors.blue)),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildBadge(OrderStatus status) {
    Color bg = Colors.amber.shade50;
    Color fg = Colors.amber.shade900;
    if (status == OrderStatus.accepted) { bg = Colors.blue.shade50; fg = Colors.blue.shade900; }
    if (status == OrderStatus.loaded) { bg = Colors.green.shade50; fg = Colors.green.shade900; }
    if (status == OrderStatus.failed) { bg = Colors.red.shade50; fg = Colors.red.shade900; }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(12)),
      child: Text(status.titleArabic, style: TextStyle(color: fg, fontSize: 11, fontWeight: FontWeight.bold)),
    );
  }
}
