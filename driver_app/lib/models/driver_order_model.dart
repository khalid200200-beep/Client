enum DriverOrderStatus {
  pending,
  accepted,
  loaded,
  failed,
  delivered,
}

class DriverOrderModel {
  final String id;
  final String clientName;
  final String clientPhone;
  final String city;
  final int packageCount;
  final String? imagePath;
  final List<String> images;
  final String notes;
  final DriverOrderStatus status;
  final String? failureReason;
  final double? collectedAmount;
  final String? createdAt;
  final String? loadedAt;

  DriverOrderModel({
    required this.id,
    required this.clientName,
    required this.clientPhone,
    required this.city,
    required this.packageCount,
    this.imagePath,
    this.images = const [],
    required this.notes,
    this.status = DriverOrderStatus.pending,
    this.failureReason,
    this.collectedAmount,
    this.createdAt,
    this.loadedAt,
  });

  factory DriverOrderModel.fromJson(Map<String, dynamic> json) {
    DriverOrderStatus parseStatus(String? s) {
      switch (s) {
        case 'accepted': return DriverOrderStatus.accepted;
        case 'loaded': return DriverOrderStatus.loaded;
        case 'failed': return DriverOrderStatus.failed;
        case 'delivered': return DriverOrderStatus.delivered;
        default: return DriverOrderStatus.pending;
      }
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

    return DriverOrderModel(
      id: json['order_code']?.toString() ?? (json['id']?.toString() ?? 'ORD-0000'),
      clientName: json['client_name'] ?? json['clientName'] ?? json['client'] ?? 'عميل',
      clientPhone: json['client_phone'] ?? json['clientPhone'] ?? json['phone'] ?? '',
      city: json['city'] ?? json['pickupCity'] ?? 'الخرطوم',
      packageCount: int.tryParse(json['package_count']?.toString() ?? json['packageCount']?.toString() ?? '1') ?? 1,
      imagePath: parsedImagesList.isNotEmpty ? parsedImagesList.first : singleImage?.toString(),
      images: parsedImagesList,
      notes: json['notes'] ?? 'لا توجد ملاحظات إضافية',
      status: parseStatus(json['status']),
      failureReason: json['failure_reason'] ?? json['failureReason'] ?? json['failReason'],
      collectedAmount: double.tryParse(json['collected_amount']?.toString() ?? json['collectedAmount']?.toString() ?? '0') ?? 0.0,
      createdAt: json['created_at']?.toString() ?? json['createdAt']?.toString(),
      loadedAt: json['loaded_at']?.toString() ?? json['loadedAt']?.toString(),
    );
  }

  DriverOrderModel copyWith({
    String? id,
    String? clientName,
    String? clientPhone,
    String? city,
    int? packageCount,
    String? imagePath,
    List<String>? images,
    String? notes,
    DriverOrderStatus? status,
    String? failureReason,
    double? collectedAmount,
  }) {
    return DriverOrderModel(
      id: id ?? this.id,
      clientName: clientName ?? this.clientName,
      clientPhone: clientPhone ?? this.clientPhone,
      city: city ?? this.city,
      packageCount: packageCount ?? this.packageCount,
      imagePath: imagePath ?? this.imagePath,
      images: images ?? this.images,
      notes: notes ?? this.notes,
      status: status ?? this.status,
      failureReason: failureReason ?? this.failureReason,
      collectedAmount: collectedAmount ?? this.collectedAmount,
    );
  }
}
