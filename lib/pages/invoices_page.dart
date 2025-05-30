import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/odoo_service.dart';
import '../models/invoice.dart';
import '../widgets/bottom_nav.dart';
import '../widgets/side_menu.dart';

class InvoicesPage extends StatefulWidget {
  const InvoicesPage({super.key});

  @override
  State<InvoicesPage> createState() => _InvoicesPageState();
}

class _InvoicesPageState extends State<InvoicesPage> {
  List<Invoice> _invoices = [];
  bool _isLoading = true;
  String _selectedPaymentState = 'All';
  final _currencyFormatter = NumberFormat.currency(symbol: '\$');
  final _odooService = OdooService();

  @override
  void initState() {
    super.initState();
    _loadInvoices();
  }

  Future<void> _loadInvoices() async {
    setState(() => _isLoading = true);
    
    try {
      final invoices = await _odooService.getInvoices();
      setState(() {
        _invoices = invoices;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading invoices: $e')),
        );
      }
    }
  }

  List<String> get _paymentStates {
    final states = _invoices.map((i) => i.paymentStateDisplay).toSet().toList();
    states.sort();
    return ['All', ...states];
  }

  List<Invoice> get _filteredInvoices {
    if (_selectedPaymentState == 'All') return _invoices;
    return _invoices.where((invoice) => invoice.paymentStateDisplay == _selectedPaymentState).toList();
  }

  Color _getStateColor(String state) {
    switch (state) {
      case 'draft':
        return Colors.grey;
      case 'posted':
        return Colors.green;
      case 'cancel':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  Color _getPaymentStateColor(String paymentState) {
    switch (paymentState) {
      case 'paid':
        return Colors.green;
      case 'partial':
        return Colors.orange;
      case 'not_paid':
        return Colors.red;
      case 'in_payment':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }

  IconData _getInvoiceIcon(Invoice invoice) {
    if (invoice.isPaid) {
      return Icons.check_circle;
    } else if (invoice.isOverdue) {
      return Icons.warning;
    } else {
      return Icons.receipt_long;
    }
  }

  void _showInvoiceDetails(Invoice invoice) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(invoice.name),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Customer:', style: TextStyle(fontWeight: FontWeight.bold)),
            Text(invoice.partnerName),
            const SizedBox(height: 8),
            const Text('Invoice Date:', style: TextStyle(fontWeight: FontWeight.bold)),
            Text(DateFormat('MMM dd, yyyy').format(invoice.invoiceDate)),
            const SizedBox(height: 8),
            const Text('Amount:', style: TextStyle(fontWeight: FontWeight.bold)),
            Text(
              _currencyFormatter.format(invoice.amountTotal),
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1E88E5),
              ),
            ),
            const SizedBox(height: 8),
            const Text('Status:', style: TextStyle(fontWeight: FontWeight.bold)),
            Text(invoice.stateDisplay),
            const SizedBox(height: 8),
            const Text('Payment Status:', style: TextStyle(fontWeight: FontWeight.bold)),
            Row(
              children: [
                Icon(
                  _getInvoiceIcon(invoice),
                  color: _getPaymentStateColor(invoice.paymentState),
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  invoice.paymentStateDisplay,
                  style: TextStyle(
                    color: _getPaymentStateColor(invoice.paymentState),
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            if (invoice.isOverdue) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.red.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red.withOpacity(0.3)),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.warning, color: Colors.red, size: 16),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'This invoice is overdue',
                        style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
              ),
            ],
            const SizedBox(height: 8),
            const Text('Invoice ID:', style: TextStyle(fontWeight: FontWeight.bold)),
            Text(invoice.id.toString()),
          ],
        ),
        actions: [
          if (_odooService.isAdmin && !invoice.isPaid)
            TextButton(
              onPressed: () {
                Navigator.pop(context);
                // TODO: Record payment for this invoice
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Record payment feature coming soon')),
                );
              },
              child: const Text('Record Payment'),
            ),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final paidInvoices = _invoices.where((i) => i.isPaid).length;
    final overdueInvoices = _invoices.where((i) => i.isOverdue).length;
    final totalAmount = _invoices.fold(0.0, (sum, invoice) => sum + invoice.amountTotal);
    final paidAmount = _invoices.where((i) => i.isPaid).fold(0.0, (sum, invoice) => sum + invoice.amountTotal);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Invoices'),
        backgroundColor: const Color(0xFF1E88E5),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadInvoices,
          ),
        ],
      ),
      drawer: const SideMenu(),
      body: Column(
        children: [
          // Payment State Filter
          Container(
            height: 50,
            margin: const EdgeInsets.all(16),
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: _paymentStates.length,
              itemBuilder: (context, index) {
                final state = _paymentStates[index];
                final isSelected = state == _selectedPaymentState;
                
                return Container(
                  margin: const EdgeInsets.only(right: 8),
                  child: FilterChip(
                    label: Text(state),
                    selected: isSelected,
                    onSelected: (selected) {
                      setState(() {
                        _selectedPaymentState = state;
                      });
                    },
                    backgroundColor: Colors.grey[200],
                    selectedColor: const Color(0xFF1E88E5),
                    labelStyle: TextStyle(
                      color: isSelected ? Colors.white : Colors.black,
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                    ),
                  ),
                );
              },
            ),
          ),
          
          // Summary Cards
          Container(
            height: 120,
            margin: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF4CAF50), Color(0xFF45A049)],
                      ),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Row(
                          children: [
                            Icon(Icons.check_circle, color: Colors.white, size: 20),
                            SizedBox(width: 8),
                            Text(
                              'Paid',
                              style: TextStyle(color: Colors.white70, fontSize: 12),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          '$paidInvoices',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          _currencyFormatter.format(paidAmount),
                          style: const TextStyle(
                            color: Colors.white70,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFFF44336), Color(0xFFD32F2F)],
                      ),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Row(
                          children: [
                            Icon(Icons.warning, color: Colors.white, size: 20),
                            SizedBox(width: 8),
                            Text(
                              'Overdue',
                              style: TextStyle(color: Colors.white70, fontSize: 12),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          '$overdueInvoices',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          '${_invoices.length} total',
                          style: const TextStyle(
                            color: Colors.white70,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Invoices List
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : RefreshIndicator(
                    onRefresh: _loadInvoices,
                    child: _filteredInvoices.isEmpty
                        ? Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(
                                  _selectedPaymentState != 'All' ? Icons.filter_list_off : Icons.receipt_long_outlined,
                                  size: 64,
                                  color: Colors.grey,
                                ),
                                const SizedBox(height: 16),
                                Text(
                                  _selectedPaymentState != 'All'
                                      ? 'No invoices with payment status "$_selectedPaymentState"'
                                      : 'No invoices found',
                                  style: const TextStyle(fontSize: 18, color: Colors.grey),
                                ),
                                if (_selectedPaymentState != 'All') ...[
                                  const SizedBox(height: 8),
                                  TextButton(
                                    onPressed: () {
                                      setState(() {
                                        _selectedPaymentState = 'All';
                                      });
                                    },
                                    child: const Text('Show all invoices'),
                                  ),
                                ],
                              ],
                            ),
                          )
                        : ListView.builder(
                            itemCount: _filteredInvoices.length,
                            itemBuilder: (context, index) {
                              final invoice = _filteredInvoices[index];

                              return Card(
                                margin: const EdgeInsets.symmetric(
                                  horizontal: 16.0,
                                  vertical: 4.0,
                                ),
                                child: ListTile(
                                  leading: CircleAvatar(
                                    backgroundColor: _getPaymentStateColor(invoice.paymentState),
                                    child: Icon(
                                      _getInvoiceIcon(invoice),
                                      color: Colors.white,
                                      size: 20,
                                    ),
                                  ),
                                  title: Text(
                                    invoice.name,
                                    style: const TextStyle(fontWeight: FontWeight.bold),
                                  ),
                                  subtitle: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Row(
                                        children: [
                                          const Icon(Icons.person, size: 16, color: Colors.grey),
                                          const SizedBox(width: 4),
                                          Expanded(child: Text(invoice.partnerName)),
                                        ],
                                      ),
                                      Row(
                                        children: [
                                          const Icon(Icons.calendar_today, size: 16, color: Colors.grey),
                                          const SizedBox(width: 4),
                                          Text(DateFormat('MMM dd, yyyy').format(invoice.invoiceDate)),
                                          if (invoice.isOverdue) ...[
                                            const SizedBox(width: 8),
                                            const Icon(Icons.warning, size: 16, color: Colors.red),
                                            const Text(' OVERDUE', style: TextStyle(color: Colors.red, fontSize: 10, fontWeight: FontWeight.bold)),
                                          ],
                                        ],
                                      ),
                                      const SizedBox(height: 4),
                                      Row(
                                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                        children: [
                                          Text(
                                            _currencyFormatter.format(invoice.amountTotal),
                                            style: const TextStyle(
                                              fontWeight: FontWeight.bold,
                                              color: Color(0xFF1E88E5),
                                              fontSize: 16,
                                            ),
                                          ),
                                          Container(
                                            padding: const EdgeInsets.symmetric(
                                              horizontal: 8,
                                              vertical: 2,
                                            ),
                                            decoration: BoxDecoration(
                                              color: _getPaymentStateColor(invoice.paymentState).withOpacity(0.2),
                                              borderRadius: BorderRadius.circular(12),
                                            ),
                                            child: Text(
                                              invoice.paymentStateDisplay,
                                              style: TextStyle(
                                                color: _getPaymentStateColor(invoice.paymentState),
                                                fontSize: 12,
                                                fontWeight: FontWeight.bold,
                                              ),
                                            ),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                  trailing: const Icon(Icons.arrow_forward_ios),
                                  onTap: () => _showInvoiceDetails(invoice),
                                ),
                              );
                            },
                          ),
                  ),
          ),
        ],
      ),
      bottomNavigationBar: const BottomNav(currentIndex: 4),
    );
  }
}