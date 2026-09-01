import 'package:flutter_test/flutter_test.dart';
import 'package:shipping_driver_app/models/driver_order_model.dart';

void main() {
  group('Driver App Unit Tests', () {
    test('DriverOrderModel parsing and status tests', () {
      final orderJson = {
        'id': 7,
        'order_code': 'ORD-5555',
        'client_name': 'سارة أحمد',
        'client_phone': '0912345678',
        'city': 'أم درمان',
        'package_count': 2,
        'notes': 'شحنة حساسة',
        'status': 'accepted',
        'collected_amount': 4500.0,
      };

      final order = DriverOrderModel.fromJson(orderJson);
      expect(order.id, 'ORD-5555');
      expect(order.clientName, 'سارة أحمد');
      expect(order.city, 'أم درمان');
      expect(order.packageCount, 2);
      expect(order.status, DriverOrderStatus.accepted);
      expect(order.collectedAmount, 4500.0);
    });

    test('DriverOrderModel copyWith tests', () {
      final order = DriverOrderModel(
        id: 'ORD-1111',
        clientName: 'محمد علي',
        clientPhone: '0987654321',
        city: 'الخرطوم',
        packageCount: 1,
        notes: 'طرد عادي',
      );

      final updated = order.copyWith(
        status: DriverOrderStatus.loaded,
        collectedAmount: 6000.0,
      );

      expect(updated.id, 'ORD-1111');
      expect(updated.status, DriverOrderStatus.loaded);
      expect(updated.collectedAmount, 6000.0);
    });
  });
}
