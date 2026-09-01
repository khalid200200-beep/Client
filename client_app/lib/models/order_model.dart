enum OrderStatus {
  pending,
  accepted,
  loaded,
  failed,
  delivered,
}

extension OrderStatusExt on OrderStatus {
  String get titleArabic {
    switch (this) {
      case OrderStatus.pending: return 'بانتظار سائق ⏳';
      case OrderStatus.accepted: return 'تم القبول - السائق في الطريق 🚚';
      case OrderStatus.loaded: return 'تم التحميل والاستلام بنجاح ✅';
      case OrderStatus.failed: return 'تعذر الشحن ❌';
      case OrderStatus.delivered: return 'تم التوصيل';
    }
  }
}

class OrderModel {
  final String id;
  final String clientName;
  final String clientPhone;
  final String city;
  final int packageCount;
  final String? imagePath;
  final List<String> images;
  final String notes;
  final DateTime createdAt;
  final OrderStatus status;
  final String? driverName;
  final String? driverPhone;
  final String? failureReason;
  final double? collectedAmount;

  OrderModel({
    required this.id,
    required this.clientName,
    required this.clientPhone,
    required this.city,
    required this.packageCount,
    this.imagePath,
    this.images = const [],
    required this.notes,
    required this.createdAt,
    this.status = OrderStatus.pending,
    this.driverName,
    this.driverPhone,
    this.failureReason,
    this.collectedAmount,
  });

  factory OrderModel.fromJson(Map<String, dynamic> json) {
    OrderStatus parseStatus(String? s) {
      switch (s) {
        case 'accepted': return OrderStatus.accepted;
        case 'loaded': return OrderStatus.loaded;
        case 'failed': return OrderStatus.failed;
        case 'delivered': return OrderStatus.delivered;
        default: return OrderStatus.pending;
      }
    }

    DateTime parseDate(dynamic d) {
      if (d == null) return DateTime.now();
      if (d is String) {
        return DateTime.tryParse(d) ?? DateTime.now();
      }
      return DateTime.now();
    }

    List<String> parseImages(dynamic imgs, dynamic singleImg) {
      final list = <String>[];
      if (imgs is List) {
        for (final item in imgs) {
          if (item != null && item.toString().trim().isNotEmpty) {
            list.add(item.toString().trim());
          }
        }
      }
      if (list.isEmpty && singleImg != null && singleImg.toString().trim().isNotEmpty) {
        list.add(singleImg.toString().trim());
      }
      return list;
    }

    final singleImage = json['image_path'] ?? json['imagePath'] ?? json['image'];
    final parsedImagesList = parseImages(json['images'], singleImage);

    return OrderModel(
      id: json['order_code']?.toString() ?? (json['id']?.toString() ?? 'ORD-0000'),
      clientName: json['client_name'] ?? json['clientName'] ?? json['client'] ?? 'عميل',
      clientPhone: json['client_phone'] ?? json['clientPhone'] ?? json['phone'] ?? '',
      city: json['city'] ?? json['pickupCity'] ?? 'الخرطوم',
      packageCount: int.tryParse(json['package_count']?.toString() ?? json['packageCount']?.toString() ?? '1') ?? 1,
      imagePath: parsedImagesList.isNotEmpty ? parsedImagesList.first : singleImage?.toString(),
      images: parsedImagesList,
      notes: json['notes'] ?? 'لا توجد ملاحظات',
      createdAt: parseDate(json['created_at']),
      status: parseStatus(json['status']),
      driverName: json['driver_name'] ?? json['driverName'] ?? json['driver'],
      driverPhone: json['driver_phone'] ?? json['driverPhone'],
      failureReason: json['failure_reason'] ?? json['failureReason'] ?? json['failReason'],
      collectedAmount: double.tryParse(json['collected_amount']?.toString() ?? json['collectedAmount']?.toString() ?? '0') ?? 0.0,
    );
  }

  OrderModel copyWith({
    String? id,
    String? clientName,
    String? clientPhone,
    String? city,
    int? packageCount,
    String? imagePath,
    List<String>? images,
    String? notes,
    DateTime? createdAt,
    OrderStatus? status,
    String? driverName,
    String? driverPhone,
    String? failureReason,
    double? collectedAmount,
  }) {
    return OrderModel(
      id: id ?? this.id,
      clientName: clientName ?? this.clientName,
      clientPhone: clientPhone ?? this.clientPhone,
      city: city ?? this.city,
      packageCount: packageCount ?? this.packageCount,
      imagePath: imagePath ?? this.imagePath,
      images: images ?? this.images,
      notes: notes ?? this.notes,
      createdAt: createdAt ?? this.createdAt,
      status: status ?? this.status,
      driverName: driverName ?? this.driverName,
      driverPhone: driverPhone ?? this.driverPhone,
      failureReason: failureReason ?? this.failureReason,
      collectedAmount: collectedAmount ?? this.collectedAmount,
    );
  }
}
