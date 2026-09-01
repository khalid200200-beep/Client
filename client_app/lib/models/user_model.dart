class UserModel {
  final String id;
  final String name;
  final String? email;
  final String phone;
  final String city;
  final String? avatarUrl;

  UserModel({
    required this.id,
    required this.name,
    this.email,
    required this.phone,
    required this.city,
    this.avatarUrl,
  });

  UserModel copyWith({
    String? id,
    String? name,
    String? email,
    String? phone,
    String? city,
    String? avatarUrl,
  }) {
    return UserModel(
      id: id ?? this.id,
      name: name ?? this.name,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      city: city ?? this.city,
      avatarUrl: avatarUrl ?? this.avatarUrl,
    );
  }
}
