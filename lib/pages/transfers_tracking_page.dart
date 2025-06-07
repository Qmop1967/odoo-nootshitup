import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/odoo_service.dart';
import '../models/money_transfer.dart';

class TransfersTrackingPage extends StatefulWidget {
  const TransfersTrackingPage({super.key});

  @override
  State<TransfersTrackingPage> createState() => _TransfersTrackingPageState();
}

class _TransfersTrackingPageState extends State<TransfersTrackingPage> {
  final _odooService = OdooService();
  final _currencyFormatter = NumberFormat.currency(symbol: 'د.ع ', decimalDigits: 0);
  final _dateFormatter = DateFormat('yyyy/MM/dd HH:mm');
  
  List<MoneyTransfer> _transfers = [];
  bool _isLoading = true;
  String _filterStatus = 'all'; // all, sent, received, pending

  @override
  void initState() {
    super.initState();
    _loadTransfers();
  }

  Future<void> _loadTransfers() async {
    setState(() => _isLoading = true);
    
    try {
      final transfers = await _odooService.getMoneyTransfers();
      setState(() {
        _transfers = transfers.map((data) => MoneyTransfer.fromJson(data)).toList();
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('خطأ في تحميل الحوالات: $e')),
        );
      }
    }
  }

  List<MoneyTransfer> get _filteredTransfers {
    if (_filterStatus == 'all') return _transfers;
    return _transfers.where((transfer) => transfer.status == _filterStatus).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('متابعة الحوالات'),
        backgroundColor: const Color(0xFF1E88E5),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadTransfers,
          ),
        ],
      ),
      body: Column(
        children: [
          _buildFilterChips(),
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _filteredTransfers.isEmpty
                    ? _buildEmptyState()
                    : RefreshIndicator(
                        onRefresh: _loadTransfers,
                        child: ListView.builder(
                          padding: const EdgeInsets.all(16.0),
                          itemCount: _filteredTransfers.length,
                          itemBuilder: (context, index) {
                            return _buildTransferCard(_filteredTransfers[index]);
                          },
                        ),
                      ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterChips() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: [
            _buildFilterChip('all', 'الكل', Icons.all_inclusive),
            const SizedBox(width: 8),
            _buildFilterChip('sent', 'مرسلة', Icons.send),
            const SizedBox(width: 8),
            _buildFilterChip('received', 'مستلمة', Icons.check_circle),
            const SizedBox(width: 8),
            _buildFilterChip('pending', 'معلقة', Icons.pending),
          ],
        ),
      ),
    );
  }

  Widget _buildFilterChip(String value, String label, IconData icon) {
    final isSelected = _filterStatus == value;
    return FilterChip(
      selected: isSelected,
      label: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16),
          const SizedBox(width: 4),
          Text(label),
        ],
      ),
      onSelected: (selected) {
        setState(() {
          _filterStatus = value;
        });
      },
      selectedColor: const Color(0xFF1E88E5).withOpacity(0.2),
      checkmarkColor: const Color(0xFF1E88E5),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.money_off,
            size: 64,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            'لا توجد حوالات',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'لم يتم إجراء أي حوالات مالية بعد',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[500],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTransferCard(MoneyTransfer transfer) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'حوالة رقم: ${transfer.transferNumber}',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        _dateFormatter.format(transfer.transferDate),
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
                _buildStatusIndicator(transfer),
              ],
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey.shade50,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('المبلغ:'),
                      Text(
                        _currencyFormatter.format(transfer.amount),
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                          color: Color(0xFF4CAF50),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('طريقة التحويل:'),
                      Text(_getTransferMethodName(transfer.transferMethod)),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('الوجهة:'),
                      const Text('خزنة الشركة الرئيسية'),
                    ],
                  ),
                ],
              ),
            ),
            if (transfer.notes != null && transfer.notes!.isNotEmpty) ...[
              const SizedBox(height: 12),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'ملاحظات:',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      transfer.notes!,
                      style: const TextStyle(fontSize: 12),
                    ),
                  ],
                ),
              ),
            ],
            if (transfer.isReceived && transfer.receivedDate != null) ...[
              const SizedBox(height: 12),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'تم الاستلام:',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                        color: Colors.green,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _dateFormatter.format(transfer.receivedDate!),
                      style: const TextStyle(fontSize: 12),
                    ),
                    if (transfer.receivedBy != null)
                      Text(
                        'بواسطة: ${transfer.receivedBy}',
                        style: const TextStyle(fontSize: 12),
                      ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildStatusIndicator(MoneyTransfer transfer) {
    Color color;
    IconData icon;
    String text;

    switch (transfer.status) {
      case 'received':
        color = Colors.green;
        icon = Icons.check_circle;
        text = 'مستلمة';
        break;
      case 'sent':
        color = Colors.orange;
        icon = Icons.send;
        text = 'مرسلة';
        break;
      case 'pending':
      default:
        color = Colors.red;
        icon = Icons.pending;
        text = 'معلقة';
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: 16,
            color: color,
          ),
          const SizedBox(width: 4),
          Text(
            text,
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  String _getTransferMethodName(String method) {
    const methods = {
      'altayf_exchange': 'شركة الطيف للصرافة',
      'development_bank': 'مصرف التنمية',
      'altayf_bank': 'مصرف الطيف',
      'master_rafidain': 'ماستر الرافدين',
      'zain_cash': 'زين كاش',
    };
    return methods[method] ?? method;
  }
}