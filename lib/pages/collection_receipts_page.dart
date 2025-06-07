import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/odoo_service.dart';
import '../models/collection_receipt.dart';
import '../widgets/bottom_nav.dart';

class CollectionReceiptsPage extends StatefulWidget {
  const CollectionReceiptsPage({super.key});

  @override
  State<CollectionReceiptsPage> createState() => _CollectionReceiptsPageState();
}

class _CollectionReceiptsPageState extends State<CollectionReceiptsPage> {
  final _odooService = OdooService();
  final _currencyFormatter = NumberFormat.currency(symbol: 'د.ع ', decimalDigits: 0);
  final _dateFormatter = DateFormat('yyyy/MM/dd');
  
  List<CollectionReceipt> _receipts = [];
  bool _isLoading = true;
  String _filterStatus = 'all';
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _loadReceipts();
  }

  Future<void> _loadReceipts() async {
    setState(() => _isLoading = true);
    
    try {
      final receipts = await _odooService.getCollectionReceipts();
      setState(() {
        _receipts = receipts.map((data) => CollectionReceipt.fromJson(data)).toList();
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('خطأ في تحميل وصولات القبض: $e')),
        );
      }
    }
  }

  List<CollectionReceipt> get _filteredReceipts {
    var filtered = _receipts;
    
    if (_filterStatus != 'all') {
      filtered = filtered.where((receipt) => receipt.status == _filterStatus).toList();
    }
    
    if (_searchQuery.isNotEmpty) {
      filtered = filtered.where((receipt) =>
          receipt.clientName.toLowerCase().contains(_searchQuery.toLowerCase()) ||
          receipt.receiptNumber.toLowerCase().contains(_searchQuery.toLowerCase())).toList();
    }
    
    return filtered;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('وصولات القبض'),
        backgroundColor: const Color(0xFF1E88E5),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: _showCreateReceiptDialog,
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadReceipts,
          ),
        ],
      ),
      body: Column(
        children: [
          _buildSearchAndFilter(),
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _filteredReceipts.isEmpty
                    ? _buildEmptyState()
                    : RefreshIndicator(
                        onRefresh: _loadReceipts,
                        child: ListView.builder(
                          padding: const EdgeInsets.all(16.0),
                          itemCount: _filteredReceipts.length,
                          itemBuilder: (context, index) {
                            return _buildReceiptCard(_filteredReceipts[index]);
                          },
                        ),
                      ),
          ),
        ],
      ),
      bottomNavigationBar: const BottomNav(currentIndex: 4),
    );
  }

  Widget _buildSearchAndFilter() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          TextField(
            decoration: const InputDecoration(
              hintText: 'البحث في وصولات القبض...',
              prefixIcon: Icon(Icons.search),
              border: OutlineInputBorder(),
            ),
            onChanged: (value) {
              setState(() {
                _searchQuery = value;
              });
            },
          ),
          const SizedBox(height: 12),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildFilterChip('all', 'الكل'),
                const SizedBox(width: 8),
                _buildFilterChip('collected', 'مستحصل'),
                const SizedBox(width: 8),
                _buildFilterChip('pending_settlement', 'بانتظار التسوية'),
                const SizedBox(width: 8),
                _buildFilterChip('settled', 'مسوى'),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterChip(String value, String label) {
    final isSelected = _filterStatus == value;
    return FilterChip(
      selected: isSelected,
      label: Text(label),
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
            Icons.receipt_long,
            size: 64,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            'لا توجد وصولات قبض',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'لم يتم إنشاء أي وصولات قبض بعد',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[500],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildReceiptCard(CollectionReceipt receipt) {
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
                        'وصل رقم: ${receipt.receiptNumber}',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        receipt.clientName,
                        style: const TextStyle(
                          fontSize: 14,
                          color: Color(0xFF1E88E5),
                        ),
                      ),
                    ],
                  ),
                ),
                _buildStatusBadge(receipt.status),
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
                        _currencyFormatter.format(receipt.amount),
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
                      const Text('العمولة:'),
                      Text(
                        _currencyFormatter.format(receipt.commission),
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Color(0xFFFF9800),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('نوع الدفع:'),
                      Text(_getPaymentTypeText(receipt.paymentType)),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('المنطقة:'),
                      Text(receipt.region),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('التاريخ:'),
                      Text(_dateFormatter.format(receipt.collectionDate)),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusBadge(String status) {
    Color color;
    String text;

    switch (status) {
      case 'collected':
        color = Colors.blue;
        text = 'مستحصل';
        break;
      case 'pending_settlement':
        color = Colors.orange;
        text = 'بانتظار التسوية';
        break;
      case 'settled':
        color = Colors.green;
        text = 'مسوى';
        break;
      default:
        color = Colors.grey;
        text = status;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        text,
        style: TextStyle(
          color: color,
          fontSize: 12,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  String _getPaymentTypeText(String paymentType) {
    switch (paymentType) {
      case 'cash':
        return 'نقدي';
      case 'digital':
        return 'رقمي';
      default:
        return paymentType;
    }
  }

  void _showCreateReceiptDialog() {
    showDialog(
      context: context,
      builder: (context) => const CreateReceiptDialog(),
    ).then((result) {
      if (result == true) {
        _loadReceipts();
      }
    });
  }
}

class CreateReceiptDialog extends StatefulWidget {
  const CreateReceiptDialog({super.key});

  @override
  State<CreateReceiptDialog> createState() => _CreateReceiptDialogState();
}

class _CreateReceiptDialogState extends State<CreateReceiptDialog> {
  final _formKey = GlobalKey<FormState>();
  final _amountController = TextEditingController();
  final _notesController = TextEditingController();
  final _odooService = OdooService();
  
  String _selectedClient = '';
  String _selectedPaymentType = 'cash';
  String _selectedPaymentMethod = 'cash';
  bool _isLoading = false;
  List<Map<String, dynamic>> _clients = [];

  @override
  void initState() {
    super.initState();
    _loadClients();
  }

  Future<void> _loadClients() async {
    try {
      final clients = await _odooService.getClients();
      setState(() {
        _clients = clients;
        if (_clients.isNotEmpty) {
          _selectedClient = _clients.first['id'].toString();
        }
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('خطأ في تحميل العملاء: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('إنشاء وصل قبض جديد'),
      content: SizedBox(
        width: double.maxFinite,
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              DropdownButtonFormField<String>(
                value: _selectedClient.isNotEmpty ? _selectedClient : null,
                decoration: const InputDecoration(
                  labelText: 'العميل',
                  border: OutlineInputBorder(),
                ),
                items: _clients.map((client) {
                  return DropdownMenuItem<String>(
                    value: client['id'].toString(),
                    child: Text(client['name']),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedClient = value!;
                  });
                },
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'يرجى اختيار العميل';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _amountController,
                decoration: const InputDecoration(
                  labelText: 'المبلغ',
                  border: OutlineInputBorder(),
                  suffixText: 'د.ع',
                ),
                keyboardType: TextInputType.number,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'يرجى إدخال المبلغ';
                  }
                  if (double.tryParse(value) == null || double.parse(value) <= 0) {
                    return 'يرجى إدخال مبلغ صحيح';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                value: _selectedPaymentType,
                decoration: const InputDecoration(
                  labelText: 'نوع الدفع',
                  border: OutlineInputBorder(),
                ),
                items: const [
                  DropdownMenuItem(value: 'cash', child: Text('نقدي')),
                  DropdownMenuItem(value: 'digital', child: Text('رقمي')),
                ],
                onChanged: (value) {
                  setState(() {
                    _selectedPaymentType = value!;
                    _selectedPaymentMethod = value == 'cash' ? 'cash' : 'bank_transfer';
                  });
                },
              ),
              const SizedBox(height: 16),
              if (_selectedPaymentType == 'digital')
                DropdownButtonFormField<String>(
                  value: _selectedPaymentMethod,
                  decoration: const InputDecoration(
                    labelText: 'طريقة الدفع',
                    border: OutlineInputBorder(),
                  ),
                  items: const [
                    DropdownMenuItem(value: 'bank_transfer', child: Text('حوالة مصرفية')),
                    DropdownMenuItem(value: 'zain_cash', child: Text('زين كاش')),
                    DropdownMenuItem(value: 'master_card', child: Text('ماستر كارد')),
                  ],
                  onChanged: (value) {
                    setState(() {
                      _selectedPaymentMethod = value!;
                    });
                  },
                ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _notesController,
                decoration: const InputDecoration(
                  labelText: 'ملاحظات (اختياري)',
                  border: OutlineInputBorder(),
                ),
                maxLines: 2,
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('إلغاء'),
        ),
        ElevatedButton(
          onPressed: _isLoading ? null : _createReceipt,
          child: _isLoading
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('إنشاء'),
        ),
      ],
    );
  }

  Future<void> _createReceipt() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final receiptData = {
        'client_id': int.parse(_selectedClient),
        'amount': double.parse(_amountController.text),
        'payment_type': _selectedPaymentType,
        'payment_method': _selectedPaymentMethod,
        'notes': _notesController.text.trim(),
      };

      await _odooService.createCollectionReceipt(receiptData);

      if (mounted) {
        Navigator.pop(context, true);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('تم إنشاء وصل القبض بنجاح'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('خطأ في إنشاء وصل القبض: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  void dispose() {
    _amountController.dispose();
    _notesController.dispose();
    super.dispose();
  }
}