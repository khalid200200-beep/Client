class BannerItem {
  final String id;
  final String title;
  final String subtitle;
  final String badgeText;
  final String imageUrl;
  final String buttonText;

  BannerItem({
    this.id = '',
    required this.title,
    required this.subtitle,
    required this.badgeText,
    required this.imageUrl,
    required this.buttonText,
  });

  factory BannerItem.fromJson(Map<String, dynamic> json) {
    return BannerItem(
      id: json['id']?.toString() ?? '',
      title: json['title'] ?? '',
      subtitle: json['subtitle'] ?? '',
      badgeText: json['badge_text'] ?? json['badgeText'] ?? 'عرض خاص',
      imageUrl: json['image_url'] ?? json['imageUrl'] ?? '',
      buttonText: json['button_text'] ?? json['buttonText'] ?? 'اطلب شحن الآن',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'subtitle': subtitle,
      'badge_text': badgeText,
      'image_url': imageUrl,
      'button_text': buttonText,
    };
  }
}
