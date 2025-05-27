class Invoice {
  final int id;
  final String name;
  final String partnerName;
  final DateTime invoiceDate;
  final double amountTotal;
  final String state;
  final String paymentState;

  Invoice({
    required this.id,
    required this.name,
    required this.partnerName,
    required this.invoiceDate,
    required this.amountTotal,
    required this.state,
    required this.paymentState,
  });

  factory Invoice.fromJson(Map<String, dynamic> json) {
    return Invoice(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      partnerName: json['partner_id'] is List 
          ? json['partner_id'][1] ?? 'Unknown'
          : 'Unknown',
      invoiceDate: DateTime.tryParse(json['invoice_date'] ?? '') ?? DateTime.now(),
      amountTotal: (json['amount_total'] ?? 0.0).toDouble(),
      state: json['state'] ?? 'draft',
      paymentState: json['payment_state'] ?? 'not_paid',
    );
  }

  String get stateDisplay {
    switch (state) {
      case 'draft':
        return 'Draft';
      case 'posted':
        return 'Posted';
      case 'cancel':
        return 'Cancelled';
      default:
        return state;
    }
  }

  String get paymentStateDisplay {
    switch (paymentState) {
      case 'not_paid':
        return 'Not Paid';
      case 'in_payment':
        return 'In Payment';
      case 'paid':
        return 'Paid';
      case 'partial':
        return 'Partially Paid';
      case 'reversed':
        return 'Reversed';
      case 'invoicing_legacy':
        return 'Invoicing App Legacy';
      default:
        return paymentState;
    }
  }

  bool get isPaid => paymentState == 'paid';
  bool get isOverdue => !isPaid && invoiceDate.isBefore(DateTime.now().subtract(const Duration(days: 30)));
}