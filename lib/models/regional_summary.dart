class RegionalSummary {
  final String region;
  final double cashCollected;
  final double digitalCollected;
  final double totalCollected;
  final double outstandingAmount;
  final int clientsCount;
  final DateTime lastUpdate;

  RegionalSummary({
    required this.region,
    required this.cashCollected,
    required this.digitalCollected,
    required this.outstandingAmount,
    required this.clientsCount,
    required this.lastUpdate,
  }) : totalCollected = cashCollected + digitalCollected;

  factory RegionalSummary.fromJson(Map<String, dynamic> json) {
    return RegionalSummary(
      region: json['region'] ?? '',
      cashCollected: (json['cash_collected'] ?? 0.0).toDouble(),
      digitalCollected: (json['digital_collected'] ?? 0.0).toDouble(),
      outstandingAmount: (json['outstanding_amount'] ?? 0.0).toDouble(),
      clientsCount: json['clients_count'] ?? 0,
      lastUpdate: DateTime.parse(json['last_update'] ?? DateTime.now().toIso8601String()),
    );
  }

  bool get hasOutstanding => outstandingAmount > 0;
  bool get hasCollections => totalCollected > 0;
}