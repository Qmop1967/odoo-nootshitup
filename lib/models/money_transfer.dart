class MoneyTransfer {
  final int id;
  final String transferNumber;
  final double amount;
  final String transferType; // 'cash', 'digital'
  final String transferMethod; // 'altayf_exchange', 'development_bank', 'altayf_bank', 'master_rafidain', 'zain_cash'
  final DateTime transferDate;
  final int salespersonId;
  final String salespersonName;
  final String destination; // Usually 'main_treasury'
  final String status; // 'sent', 'received', 'pending'
  final String? receiptImage;
  final String? notes;
  final DateTime? receivedDate;
  final String? receivedBy;

  MoneyTransfer({
    required this.id,
    required this.transferNumber,
    required this.amount,
    required this.transferType,
    required this.transferMethod,
    required this.transferDate,
    required this.salespersonId,
    required this.salespersonName,
    required this.destination,
    this.status = 'sent',
    this.receiptImage,
    this.notes,
    this.receivedDate,
    this.receivedBy,
  });

  factory MoneyTransfer.fromJson(Map<String, dynamic> json) {
    return MoneyTransfer(
      id: json['id'] ?? 0,
      transferNumber: json['transfer_number'] ?? '',
      amount: (json['amount'] ?? 0.0).toDouble(),
      transferType: json['transfer_type'] ?? 'cash',
      transferMethod: json['transfer_method'] ?? 'altayf_exchange',
      transferDate: DateTime.parse(json['transfer_date'] ?? DateTime.now().toIso8601String()),
      salespersonId: json['salesperson_id'] ?? 0,
      salespersonName: json['salesperson_name'] ?? '',
      destination: json['destination'] ?? 'main_treasury',
      status: json['status'] ?? 'sent',
      receiptImage: json['receipt_image'],
      notes: json['notes'],
      receivedDate: json['received_date'] != null 
          ? DateTime.parse(json['received_date']) 
          : null,
      receivedBy: json['received_by'],
    );
  }

  bool get isReceived => status == 'received';
  bool get isPending => status == 'pending' || status == 'sent';
}