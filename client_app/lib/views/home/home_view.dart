import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../state/client_state.dart';
import '../../theme/app_theme.dart';
import '../orders/create_order_view.dart';
import '../orders/my_orders_view.dart';
import 'widgets/hero_banner.dart';
import 'widgets/quick_actions_grid.dart';

class HomeView extends StatelessWidget {
  final VoidCallback onOpenOrdersTab;

  const HomeView({super.key, required this.onOpenOrdersTab});

  void _navigateToCreateOrder(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const CreateOrderView()),
    );
  }

  @override
  Widget build(BuildContext context) {
    final clientState = Provider.of<ClientState>(context);
    final user = clientState.currentUser;

    return Scaffold(
      backgroundColor: AppTheme.scaffoldBackground,
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 1. الشريط العلوي (الاسم والمدينة والإشعارات)
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 46,
                        height: 46,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: AppTheme.primaryTeal.withValues(alpha: 0.1),
                          border: Border.all(color: AppTheme.primaryTeal.withValues(alpha: 0.25), width: 1.5),
                        ),
                        child: const Icon(
                          Icons.person_rounded,
                          size: 26,
                          color: AppTheme.primaryTeal,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Text(
                                'مرحباً ${user.name}',
                                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.textDark),
                              ),
                              const SizedBox(width: 4),
                              const Text('👋', style: TextStyle(fontSize: 14)),
                            ],
                          ),
                          const SizedBox(height: 2),
                          Row(
                            children: [
                              Text(
                                user.city,
                                style: const TextStyle(fontSize: 12, color: AppTheme.textMuted, fontWeight: FontWeight.w600),
                              ),
                              const SizedBox(width: 4),
                              const Icon(Icons.location_on, size: 14, color: AppTheme.secondaryGold),
                            ],
                          ),
                        ],
                      ),
                    ],
                  ),
                  Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 10),
                      ],
                    ),
                    child: Stack(
                      alignment: Alignment.center,
                      children: [
                        const Icon(Icons.notifications_none_rounded, color: AppTheme.textDark, size: 24),
                        Positioned(
                          top: 10,
                          right: 11,
                          child: Container(
                            width: 8,
                            height: 8,
                            decoration: const BoxDecoration(color: AppTheme.secondaryGold, shape: BoxShape.circle),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 20),

              // 2. البانر الترويجي الكبير ثلاثي الأبعاد
              HomeHeroBanner(
                onOrderNowPressed: () => _navigateToCreateOrder(context),
              ),

              const SizedBox(height: 20),

              // 3. شبكة الإجراءات السريعة (طلباتي - تتبع الشحنة - الدعم)
              QuickActionsGrid(
                onMyOrdersTap: onOpenOrdersTab,
                onTrackTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const MyOrdersView()),
                  );
                },
                onSupportTap: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('خدمة عملاء سودرا متاحة 24/7 لمساعدتكم 🤝')),
                  );
                },
              ),

              const SizedBox(height: 20),

              // 4. بطاقة الترويج السفلية (مندوبنا يصل إليك)
              BottomPromoCard(
                onTap: () => _navigateToCreateOrder(context),
              ),

              const SizedBox(height: 24),

              // 5. قسم خدماتنا (خدمات لوجستية - شحن بري - شحن جوي - شحن بحري)
              const Text(
                'خدماتنا',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.textDark),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(child: _buildServiceItem('خدمات\nلوجستية', Icons.inventory_2_outlined, context)),
                  const SizedBox(width: 8),
                  Expanded(child: _buildServiceItem('شحن بري', Icons.local_shipping_outlined, context)),
                  const SizedBox(width: 8),
                  Expanded(child: _buildServiceItem('شحن جوي', Icons.flight_takeoff_rounded, context)),
                  const SizedBox(width: 8),
                  Expanded(child: _buildServiceItem('شحن بحري', Icons.directions_boat_rounded, context)),
                ],
              ),

              const SizedBox(height: 30),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildServiceItem(String label, IconData icon, BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 4),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.02), blurRadius: 10, offset: const Offset(0, 3)),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 28, color: AppTheme.primaryTeal),
          const SizedBox(height: 8),
          Text(
            label,
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.textDark, height: 1.2),
          ),
        ],
      ),
    );
  }
}
