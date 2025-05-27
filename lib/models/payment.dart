class Payment {
  final int id;
  final String name;
  final String partnerName;
  final DateTime date;
  final double amount;
  final String state;

  Payment({
    required this.id,
    required this.name,
    required this.partnerName,
    required this.date,
    required this.amount,
    required this.state,
  });

  factory Payment.fromJson(Map<String, dynamic> json) {
    return Payment(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      partnerName: json['partner_id'] is List 
          ? json['partner_id'][1] ?? 'Unknown'
          : 'Unknown',
      date: DateTime.tryParse(json['date'] ?? '') ?? DateTime.now(),
      amount: (json['amount'] ?? 0.0).toDouble(),
      state: json['state'] ?? 'draft',
    );
  }

  String get stateDisplay {
    switch (state) {
      case 'draft':
        return 'Draft';
      case 'posted':
        return 'Posted';
      case 'sent':
        return 'Sent';
      case 'reconciled':
        return 'Reconciled';
      case 'cancelled':
        return 'Cancelled';
      default:
        return state;
    }
  }

  bool get isProcessed => state == 'posted' || state == 'reconciled';
}