import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/odoo_service.dart';
import '../models/payment.dart';
import '../models/client.dart';
import '../widgets/bottom_nav.dart';
import '../widgets/side_menu.dart';

class PaymentsPage extends StatefulWidget {
  const PaymentsPage({super.key});

  @override
  State<PaymentsPage> createState() => _PaymentsPageState();
}

class _PaymentsPageState extends State<PaymentsPage> {
  List<Payment> _payments = [];
  List<Client> _clients = [];
  bool _isLoading = true;
  final _currencyFormatter = NumberFormat.currency(symbol: '\$');
  final _odooService = OdooService();

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    
    try {
      final payments = await _odooService.getPayments();
      final clients = await _odooService.getClients();
      
      setState(() {
        _payments = payments;
        _clients = clients;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading data: $e')),
        );
      }
    }
  }

  Color _getStateColor(String state) {
    switch (state) {
      case 'draft':
        return Colors.grey;
      case 'posted':
        return Colors.green;
      case 'sent':
        return Colors.blue;
      case 'reconciled':
        return Colors.teal;
      case 'cancelled':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  IconData _getPaymentIcon(String state) {
    switch (state) {
      case 'posted':
        return Icons.check_circle;
      case 'reconciled':
        return Icons.account_balance;
      case 'cancelled':
        return Icons.cancel;
      default:
        return Icons.payment;
    }
  }

  void _showRecordPaymentDialog() {
    final amountController = TextEditingController();
    final referenceController = TextEditingController();
    Client? selectedClient;
    String selectedPaymentMethod = 'cash';

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Record Payment'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                DropdownButtonFormField<Client>(
                  value: selectedClient,
                  decoration: const InputDecoration(
                    labelText: 'Customer *',
                    border: OutlineInputBorder(),
                  ),
                  items: _clients.map((client) => DropdownMenuItem(
                    value: client,
                    child: Text(client.name),
                  )).toList(),
                  onChanged: (client) {
                    setDialogState(() {
                      selectedClient = client;
                    });
                  },
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: amountController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'Amount *',
                    border: OutlineInputBorder(),
                    prefixText: '\$ ',
                  ),
                ),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  value: selectedPaymentMethod,
                  decoration: const InputDecoration(
                    labelText: 'Payment Method',
                    border: OutlineInputBorder(),
                  ),
                  items: const [
                    DropdownMenuItem(value: 'cash', child: Text('Cash')),
                    DropdownMenuItem(value: 'check', child: Text('Check')),
                    DropdownMenuItem(value: 'bank_transfer', child: Text('Bank Transfer')),
                    DropdownMenuItem(value: 'credit_card', child: Text('Credit Card')),
                  ],
                  onChanged: (value) {
                    setDialogState(() {
                      selectedPaymentMethod = value!;
                    });
                  },
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: referenceController,
                  decoration: const InputDecoration(
                    labelText: 'Reference',
                    border: OutlineInputBorder(),
                    hintText: 'Payment reference or memo',
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: selectedClient != null && amountController.text.isNotEmpty
                  ? () async {
                      final amount = double.tryParse(amountController.text);
                      if (amount != null && amount > 0) {
                        final success = await _odooService.createPayment(
                          partnerId: selectedClient!.id,
                          amount: amount,
                          paymentMethod: selectedPaymentMethod,
                          reference: referenceController.text.isEmpty 
                              ? null 
                              : referenceController.text,
                        );
                        
                        if (context.mounted) {
                          Navigator.pop(context);
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text(success 
                                  ? 'Payment recorded successfully' 
                                  : 'Failed to record payment'),
                              backgroundColor: success ? Colors.green : Colors.red,
                            ),
                          );
                          
                          if (success) {
                            _loadData(); // Refresh the list
                          }
                        }
                      }
                    }
                  : null,
              child: const Text('Record Payment'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Payments Received'),
        backgroundColor: const Color(0xFF1E88E5),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
          ),
        ],
      ),
      drawer: const SideMenu(),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadData,
              child: Column(
                children: [
                  // Summary Card
                  Container(
                    margin: const EdgeInsets.all(16),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF4CAF50), Color(0xFF45A049)],
                      ),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.account_balance_wallet, 
                            color: Colors.white, size: 32),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'Total Payments',
                                style: TextStyle(color: Colors.white70),
                              ),
                              Text(
                                _currencyFormatter.format(
                                  _payments.fold(0.0, (sum, payment) => sum + payment.amount)
                                ),
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 24,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                        ),
                        Text(
                          '${_payments.length} payments',
                          style: const TextStyle(color: Colors.white70),
                        ),
                      ],
                    ),
                  ),
                  
                  // Payments List
                  Expanded(
                    child: _payments.isEmpty
                        ? const Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(Icons.payment, size: 64, color: Colors.grey),
                                SizedBox(height: 16),
                                Text(
                                  'No payments found',
                                  style: TextStyle(fontSize: 18, color: Colors.grey),
                                ),
                              ],
                            ),
                          )
                        : ListView.builder(
                            itemCount: _payments.length,
                            itemBuilder: (context, index) {
                              final payment = _payments[index];

                              return Card(
                                margin: const EdgeInsets.symmetric(
                                  horizontal: 16.0,
                                  vertical: 4.0,
                                ),
                                child: ListTile(
                                  leading: CircleAvatar(
                                    backgroundColor: _getStateColor(payment.state),
                                    child: Icon(
                                      _getPaymentIcon(payment.state),
                                      color: Colors.white,
                                      size: 20,
                                    ),
                                  ),
                                  title: Text(
                                    payment.name,
                                    style: const TextStyle(fontWeight: FontWeight.bold),
                                  ),
                                  subtitle: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text('Customer: ${payment.partnerName}'),
                                      Text('Date: ${DateFormat('MMM dd, yyyy').format(payment.date)}'),
                                      const SizedBox(height: 4),
                                      Row(
                                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                        children: [
                                          Text(
                                            _currencyFormatter.format(payment.amount),
                                            style: const TextStyle(
                                              fontWeight: FontWeight.bold,
                                              color: Color(0xFF4CAF50),
                                              fontSize: 16,
                                            ),
                                          ),
                                          Container(
                                            padding: const EdgeInsets.symmetric(
                                              horizontal: 8,
                                              vertical: 2,
                                            ),
                                            decoration: BoxDecoration(
                                              color: _getStateColor(payment.state).withOpacity(0.2),
                                              borderRadius: BorderRadius.circular(12),
                                            ),
                                            child: Text(
                                              payment.stateDisplay,
                                              style: TextStyle(
                                                color: _getStateColor(payment.state),
                                                fontSize: 12,
                                                fontWeight: FontWeight.bold,
                                              ),
                                            ),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                  trailing: payment.isProcessed
                                      ? const Icon(Icons.check_circle, color: Colors.green)
                                      : const Icon(Icons.arrow_forward_ios),
                                  onTap: () {
                                    // Show payment details
                                    showDialog(
                                      context: context,
                                      builder: (context) => AlertDialog(
                                        title: Text('Payment Details'),
                                        content: Column(
                                          mainAxisSize: MainAxisSize.min,
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text('Payment: ${payment.name}'),
                                            Text('Customer: ${payment.partnerName}'),
                                            Text('Amount: ${_currencyFormatter.format(payment.amount)}'),
                                            Text('Date: ${DateFormat('MMM dd, yyyy').format(payment.date)}'),
                                            Text('Status: ${payment.stateDisplay}'),
                                          ],
                                        ),
                                        actions: [
                                          TextButton(
                                            onPressed: () => Navigator.pop(context),
                                            child: const Text('Close'),
                                          ),
                                        ],
                                      ),
                                    );
                                  },
                                ),
                              );
                            },
                          ),
                  ),
                ],
              ),
            ),
      floatingActionButton: _odooService.isAdmin
          ? FloatingActionButton(
              onPressed: _showRecordPaymentDialog,
              backgroundColor: const Color(0xFF4CAF50),
              child: const Icon(Icons.add, color: Colors.white),
            )
          : null,
      bottomNavigationBar: const BottomNav(currentIndex: 4),
    );
  }
}