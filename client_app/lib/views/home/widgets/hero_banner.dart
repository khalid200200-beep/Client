import 'dart:async';
import 'package:flutter/material.dart';
import '../../../models/banner_model.dart';
import '../../../theme/app_theme.dart';
import '../../../widgets/custom_button.dart';

/// سلايدر وبانر صور احترافي للواجهة الرئيسية مع نقاط المؤشر والتنقل التلقائي
class HomeHeroBanner extends StatefulWidget {
  final VoidCallback onOrderNowPressed;

  const HomeHeroBanner({super.key, required this.onOrderNowPressed});

  @override
  State<HomeHeroBanner> createState() => _HomeHeroBannerState();
}

class _HomeHeroBannerState extends State<HomeHeroBanner> {
  final PageController _pageController = PageController();
  int _currentPage = 0;
  Timer? _autoSlideTimer;

  // البانرات الترويجية (يمكن جلبها ديناميكياً من الـ API)
  final List<BannerItem> _banners = [
    BannerItem(
      title: 'شحنك يصل إليك',
      subtitle: 'بسرعة • أمان • موثوقية',
      badgeText: 'الأكثر طلباً ⭐',
      imageUrl: 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=800',
      buttonText: 'اطلب شحن الآن',
    ),
    BannerItem(
      title: 'خصم 20% على الشحن',
      subtitle: 'شحن فوري وآمن بين جميع المدن',
      badgeText: 'عرض محدود 🔥',
      imageUrl: 'https://images.unsplash.com/photo-1519003722824-194d4455a60c?w=800',
      buttonText: 'احصل على الخصم الآن',
    ),
    BannerItem(
      title: 'توصيل في نفس اليوم',
      subtitle: 'كباتن معتمدون بالقرب منك على مدار الساعة',
      badgeText: 'خدمة VIP ⚡',
      imageUrl: 'https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=800',
      buttonText: 'شحن فوري وسريع',
    ),
  ];

  @override
  void initState() {
    super.initState();
    // تقليب تلقائي كل 4 ثواني
    _autoSlideTimer = Timer.periodic(const Duration(seconds: 4), (timer) {
      if (_pageController.hasClients) {
        final nextPage = (_currentPage + 1) % _banners.length;
        _pageController.animateToPage(
          nextPage,
          duration: const Duration(milliseconds: 400),
          curve: Curves.easeInOut,
        );
      }
    });
  }

  @override
  void dispose() {
    _autoSlideTimer?.cancel();
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(28),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 16,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        children: [
          SizedBox(
            height: 330,
            child: PageView.builder(
              controller: _pageController,
              onPageChanged: (idx) => setState(() => _currentPage = idx),
              itemCount: _banners.length,
              itemBuilder: (context, index) {
                final banner = _banners[index];
                return _buildBannerSlide(banner);
              },
            ),
          ),

          // مؤشر النقاط التفاعلي (Dots Indicator)
          Padding(
            padding: const EdgeInsets.only(bottom: 14),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(_banners.length, (index) {
                final isSelected = _currentPage == index;
                return AnimatedContainer(
                  duration: const Duration(milliseconds: 250),
                  margin: const EdgeInsets.symmetric(horizontal: 3),
                  width: isSelected ? 22 : 6,
                  height: 6,
                  decoration: BoxDecoration(
                    color: isSelected ? AppTheme.primaryRed : Colors.grey.shade300,
                    borderRadius: BorderRadius.circular(4),
                  ),
                );
              }),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBannerSlide(BannerItem banner) {
    return Stack(
      children: [
        // صورة البانر مع التدرج اللوني
        ClipRRect(
          borderRadius: BorderRadius.circular(28),
          child: Container(
            height: 330,
            decoration: BoxDecoration(
              image: DecorationImage(
                image: NetworkImage(banner.imageUrl),
                fit: BoxFit.cover,
              ),
            ),
            child: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    Colors.white.withOpacity(0.92),
                    Colors.white.withOpacity(0.4),
                    Colors.black.withOpacity(0.6),
                  ],
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                ),
              ),
            ),
          ),
        ),

        // النصوص وشارة العرض والزر المتوهج
        Padding(
          padding: const EdgeInsets.fromLTRB(20, 20, 20, 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // شارة البانر (الذهبي الفاخر)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
                decoration: BoxDecoration(
                  color: AppTheme.secondaryGold,
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(color: AppTheme.secondaryGold.withOpacity(0.35), blurRadius: 8),
                  ],
                ),
                child: Text(
                  banner.badgeText,
                  style: const TextStyle(color: Colors.white, fontSize: 11.5, fontWeight: FontWeight.bold),
                ),
              ),
              const SizedBox(height: 10),

              // العنوان
              Text(
                banner.title,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.w900,
                  color: AppTheme.textDark,
                  letterSpacing: -0.5,
                ),
              ),
              const SizedBox(height: 4),

              // العنوان الفرعي
              Text(
                banner.subtitle,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF4A5568),
                ),
              ),

              const Spacer(),

              // زر الطلب المتوهج المخصص للبانر
              CustomRedButton(
                text: banner.buttonText,
                onPressed: widget.onOrderNowPressed,
                trailingIcon: const Icon(Icons.arrow_forward_rounded, color: Colors.white, size: 18),
              ),
              const SizedBox(height: 12),
            ],
          ),
        ),
      ],
    );
  }
}
