class CollectionReceipt {
  final int id;
  final String receiptNumber;
  final int clientId;
  final String clientName;
  final double amount;
  final String paymentType; // 'cash' or 'digital'
  final String paymentMethod; // 'cash', 'bank_transfer', 'zain_cash', etc.
  final DateTime collectionDate;
  final String region;
  final int salespersonId;
  final bool isSettled;
  final String? transferReference;
  final String status; // 'collected', 'pending_settlement', 'settled'

  CollectionReceipt({
    required this.id,
    required this.receiptNumber,
    required this.clientId,
    required this.clientName,
    required this.amount,
    required this.paymentType,
    required this.paymentMethod,
    required this.collectionDate,
    required this.region,
    required this.salespersonId,
    this.isSettled = false,
    this.transferReference,
    this.status = 'collected',
  });

  factory CollectionReceipt.fromJson(Map<String, dynamic> json) {
    return CollectionReceipt(
      id: json['id'] ?? 0,
      receiptNumber: json['receipt_number'] ?? '',
      clientId: json['client_id'] ?? 0,
      clientName: json['client_name'] ?? '',
      amount: (json['amount'] ?? 0.0).toDouble(),
      paymentType: json['payment_type'] ?? 'cash',
      paymentMethod: json['payment_method'] ?? 'cash',
      collectionDate: DateTime.parse(json['collection_date'] ?? DateTime.now().toIso8601String()),
      region: json['region'] ?? '',
      salespersonId: json['salesperson_id'] ?? 0,
      isSettled: json['is_settled'] ?? false,
      transferReference: json['transfer_reference'],
      status: json['status'] ?? 'collected',
    );
  }

  double get commission => amount * 0.0225; // 2.25% commission
}