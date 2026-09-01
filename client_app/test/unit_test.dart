import 'package:flutter_test/flutter_test.dart';
import 'package:shipping_client_app/models/order_model.dart';
import 'package:shipping_client_app/models/user_model.dart';
import 'package:shipping_client_app/models/banner_model.dart';

void main() {
  group('Client App Unit Tests', () {
    test('OrderModel serialization and status tests', () {
      final orderJson = {
        'id': 10,
        'order_code': 'ORD-9999',
        'client_name': 'خالد العميل',
        'client_phone': '0551234567',
        'city': 'الخرطوم',
        'package_count': 3,
        'image_path': 'data:image/jpeg;base64,abc',
        'notes': 'طرد مستعجل',
        'status': 'pending',
        'collected_amount': 0.0,
      };

      final order = OrderModel.fromJson(orderJson);
      expect(order.id, 'ORD-9999');
      expect(order.clientName, 'خالد العميل');
      expect(order.packageCount, 3);
      expect(order.status, OrderStatus.pending);
      expect(order.status.titleArabic, 'بانتظار سائق ⏳');
    });

    test('UserModel model construction tests', () {
      final user = UserModel(
        id: '5',
        name: 'خالد محمد',
        email: 'khalid@sudra.sa',
        phone: '0551122334',
        city: 'الخرطوم',
      );

      expect(user.id, '5');
      expect(user.name, 'خالد محمد');
      expect(user.email, 'khalid@sudra.sa');
      expect(user.city, 'الخرطوم');
    });

    test('BannerItem construction tests', () {
      final banner = BannerItem(
        id: '1',
        title: 'عرض خاص',
        subtitle: 'خصم الشحن السريع',
        badgeText: 'خصم 20%',
        imageUrl: 'https://app.sudra.sa/banner.jpg',
        buttonText: 'اطلب الآن',
      );

      expect(banner.id, '1');
      expect(banner.title, 'عرض خاص');
      expect(banner.badgeText, 'خصم 20%');
    });
  });
}
