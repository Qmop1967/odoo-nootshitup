class SaleOrder {
  final int id;
  final String name;
  final String partnerName;
  final DateTime dateOrder;
  final double amountTotal;
  final String state;

  SaleOrder({
    required this.id,
    required this.name,
    required this.partnerName,
    required this.dateOrder,
    required this.amountTotal,
    required this.state,
  });

  factory SaleOrder.fromJson(Map<String, dynamic> json) {
    return SaleOrder(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      partnerName: json['partner_id'] is List 
          ? json['partner_id'][1] ?? 'Unknown'
          : 'Unknown',
      dateOrder: DateTime.tryParse(json['date_order'] ?? '') ?? DateTime.now(),
      amountTotal: (json['amount_total'] ?? 0.0).toDouble(),
      state: json['state'] ?? 'draft',
    );
  }

  String get stateDisplay {
    switch (state) {
      case 'draft':
        return 'Draft';
      case 'sent':
        return 'Quotation Sent';
      case 'sale':
        return 'Sales Order';
      case 'done':
        return 'Locked';
      case 'cancel':
        return 'Cancelled';
      default:
        return state;
    }
  }
} 