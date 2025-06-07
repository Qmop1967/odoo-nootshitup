class Salesperson {
  final int id;
  final String name;
  final String email;
  final String phone;
  final List<int> assignedClientIds;
  final List<int> assignedWarehouseIds;
  final List<String> assignedRegions;
  final double commissionRate; // 2.25%
  final bool isActive;

  Salesperson({
    required this.id,
    required this.name,
    required this.email,
    required this.phone,
    required this.assignedClientIds,
    required this.assignedWarehouseIds,
    required this.assignedRegions,
    this.commissionRate = 2.25,
    this.isActive = true,
  });

  factory Salesperson.fromJson(Map<String, dynamic> json) {
    return Salesperson(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'] ?? '',
      assignedClientIds: List<int>.from(json['assigned_client_ids'] ?? []),
      assignedWarehouseIds: List<int>.from(json['assigned_warehouse_ids'] ?? []),
      assignedRegions: List<String>.from(json['assigned_regions'] ?? []),
      commissionRate: (json['commission_rate'] ?? 2.25).toDouble(),
      isActive: json['is_active'] ?? true,
    );
  }
}