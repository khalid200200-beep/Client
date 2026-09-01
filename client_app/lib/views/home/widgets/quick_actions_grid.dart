import 'package:flutter/material.dart';
import '../../../theme/app_theme.dart';

class QuickActionsGrid extends StatelessWidget {
  final VoidCallback onMyOrdersTap;
  final VoidCallback onTrackTap;
  final VoidCallback onSupportTap;

  const QuickActionsGrid({
    super.key,
    required this.onMyOrdersTap,
    required this.onTrackTap,
    required this.onSupportTap,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(child: _buildActionCard('طلباتي', Icons.inventory_2_outlined, onMyOrdersTap)),
        const SizedBox(width: 12),
        Expanded(child: _buildActionCard('تتبع الشحنة', Icons.location_on_outlined, onTrackTap)),
        const SizedBox(width: 12),
        Expanded(child: _buildActionCard('الدعم', Icons.headset_mic_outlined, onSupportTap)),
      ],
    );
  }

  Widget _buildActionCard(String title, IconData icon, VoidCallback onTap) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 12, offset: const Offset(0, 4)),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(20),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 20),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(icon, size: 32, color: AppTheme.primaryTeal),
                const SizedBox(height: 10),
                Text(title, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppTheme.textDark)),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class BottomPromoCard extends StatelessWidget {
  final VoidCallback onTap;

  const BottomPromoCard({super.key, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(22),
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 14, offset: const Offset(0, 4)),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(22),
          onTap: onTap,
          child: Row(
            children: [
              Container(
                width: 70,
                height: 70,
                decoration: BoxDecoration(
                  color: const Color(0xFFF2F8F8),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: const Stack(
                  alignment: Alignment.center,
                  children: [
                    Icon(Icons.location_pin, color: AppTheme.primaryTeal, size: 32),
                    Positioned(bottom: 6, right: 6, child: Icon(Icons.delivery_dining_rounded, size: 20, color: AppTheme.textMuted)),
                  ],
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFAF3E8),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: AppTheme.secondaryGoldLight),
                      ),
                      child: const Text('⚡ سريع وآمن', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFFB88E52))),
                    ),
                    const SizedBox(height: 6),
                    const Text('مندوبنا يصل إليك', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppTheme.textDark)),
                    const SizedBox(height: 2),
                    const Text('اطلب وأنت في مكانك', style: TextStyle(fontSize: 12, color: AppTheme.textMuted)),
                    const SizedBox(height: 4),
                    const Row(
                      children: [
                        Text('اطلب الآن', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.primaryTeal)),
                        SizedBox(width: 4),
                        Icon(Icons.arrow_forward_rounded, size: 14, color: AppTheme.primaryTeal),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
