import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/driver_order_model.dart';
import '../state/driver_state.dart';
import '../theme/driver_theme.dart';

/// شاشة الأرباح المكتسبة والمحفظة وسجل الشحنات المكتملة
class DriverWalletView extends StatelessWidget {
  const DriverWalletView({super.key});

  @override
  Widget build(BuildContext context) {
    final driverState = Provider.of<DriverState>(context);
    final driverName = driverState.driverName;

    // استخراج الطلبات المكتملة أو المحملة التي تم تحصيل مبالغها
    final completedOrders = driverState.cityOrders.where((o) => 
      o.status == DriverOrderStatus.loaded || 
      o.status == DriverOrderStatus.delivered ||
      (o.collectedAmount != null && o.collectedAmount! > 0)
    ).toList();

    // حساب إجمالي الأرباح والمبالغ المحصلة
    double totalEarnings = 0.0;
    for (var o in completedOrders) {
      totalEarnings += (o.collectedAmount ?? 0.0);
    }

    return Scaffold(
      backgroundColor: DriverTheme.scaffoldBackground,
      appBar: AppBar(
        title: const Text('الأرباح المكتسبة والمحفظة 💰', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            tooltip: 'تحديث',
            onPressed: () => driverState.fetchOrders(),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => driverState.fetchOrders(),
        color: DriverTheme.primaryGreen,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // بطاقة الرصيد الإجمالي الفاخرة
              Container(
                padding: const EdgeInsets.all(22),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [DriverTheme.primaryGreen, Color(0xFF0F5A5D)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(
                      color: DriverTheme.primaryGreen.withOpacity(0.3),
                      blurRadius: 16,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'إجمالي الأرباح والمبالغ المحصلة',
                          style: TextStyle(color: Colors.white70, fontSize: 13, fontWeight: FontWeight.w600),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            '${completedOrders.length} طلب مكتمل',
                            style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Text(
                      '${totalEarnings.toStringAsFixed(2)} ر.س',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 32,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 0.5,
                      ),
                    ),
                    const SizedBox(height: 14),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.12),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.person_pin_rounded, color: Colors.white70, size: 18),
                          const SizedBox(width: 8),
                          Text(
                            'الكابتن: ${driverName.isNotEmpty ? driverName : "سائق معتمد"}',
                            style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.w600),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // عنوان قسم السجل
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'سجل الطلبات والمبالغ المحصلة',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: DriverTheme.textDark),
                  ),
                  Text(
                    '${completedOrders.length} عملية',
                    style: const TextStyle(fontSize: 13, color: DriverTheme.textMuted, fontWeight: FontWeight.w600),
                  ),
                ],
              ),

              const SizedBox(height: 14),

              // قائمة الطلبات المكتملة مع المبالغ والتاريخ
              if (completedOrders.isEmpty)
                Container(
                  padding: const EdgeInsets.all(32),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(22),
                    boxShadow: [
                      BoxShadow(color: Colors.black.withOpacity(0.02), blurRadius: 10),
                    ],
                  ),
                  child: const Column(
                    children: [
                      Icon(Icons.receipt_long_outlined, size: 54, color: DriverTheme.textMuted),
                      SizedBox(height: 14),
                      Text(
                        'لا توجد عمليات محصلة حتى الآن',
                        style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: DriverTheme.textDark),
                      ),
                      SizedBox(height: 6),
                      Text(
                        'عند قبول وتحميل وتسليم الشحنات، ستظهر تفاصيل المبالغ والتواريخ هنا تلقائياً.',
                        textAlign: TextAlign.center,
                        style: TextStyle(fontSize: 12, color: DriverTheme.textMuted, height: 1.4),
                      ),
                    ],
                  ),
                )
              else
                ListView.separated(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: completedOrders.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 12),
                  itemBuilder: (context, index) {
                    final order = completedOrders[index];
                    final amount = order.collectedAmount ?? 0.0;
                    final orderDate = order.loadedAt ?? (order.createdAt ?? 'تمت العملية');

                    return Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(18),
                        border: Border.all(color: Colors.grey.shade200),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.02),
                            blurRadius: 8,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Row(
                                children: [
                                  Container(
                                    padding: const EdgeInsets.all(8),
                                    decoration: BoxDecoration(
                                      color: Colors.green.shade50,
                                      shape: BoxShape.circle,
                                    ),
                                    child: const Icon(Icons.arrow_downward_rounded, color: Colors.green, size: 18),
                                  ),
                                  const SizedBox(width: 10),
                                  Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        'طلب #${order.id}',
                                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                                      ),
                                      const SizedBox(height: 2),
                                      Text(
                                        'العميل: ${order.clientName}',
                                        style: const TextStyle(fontSize: 12, color: DriverTheme.textMuted),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.end,
                                children: [
                                  Text(
                                    '+${amount.toStringAsFixed(2)} ر.س',
                                    style: const TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.w900,
                                      color: Colors.green,
                                    ),
                                  ),
                                  const SizedBox(height: 2),
                                  const Text(
                                    'مكتمل ومحصل ✅',
                                    style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.green),
                                  ),
                                ],
                              ),
                            ],
                          ),
                          const Divider(height: 20),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Row(
                                children: [
                                  const Icon(Icons.location_on_outlined, size: 14, color: DriverTheme.textMuted),
                                  const SizedBox(width: 4),
                                  Text(
                                    order.city,
                                    style: const TextStyle(fontSize: 12, color: DriverTheme.textMuted),
                                  ),
                                  const SizedBox(width: 10),
                                  Text(
                                    '(${order.packageCount} قطع)',
                                    style: const TextStyle(fontSize: 12, color: DriverTheme.textMuted),
                                  ),
                                ],
                              ),
                              Row(
                                children: [
                                  const Icon(Icons.access_time_rounded, size: 13, color: DriverTheme.textMuted),
                                  const SizedBox(width: 4),
                                  Text(
                                    orderDate,
                                    style: const TextStyle(fontSize: 11.5, color: DriverTheme.textMuted, fontWeight: FontWeight.w600),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ],
                      ),
                    );
                  },
                ),
            ],
          ),
        ),
      ),
    );
  }
}
