import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/odoo_service.dart';
import '../models/sale_order.dart';
import '../widgets/bottom_nav.dart';
import '../widgets/side_menu.dart';

class SaleOrdersPage extends StatefulWidget {
  const SaleOrdersPage({super.key});

  @override
  State<SaleOrdersPage> createState() => _SaleOrdersPageState();
}

class _SaleOrdersPageState extends State<SaleOrdersPage> {
  List<SaleOrder> _orders = [];
  bool _isLoading = true;
  String _selectedState = 'All';
  final _currencyFormatter = NumberFormat.currency(symbol: '\$');
  final _odooService = OdooService();

  @override
  void initState() {
    super.initState();
    _loadOrders();
  }

  Future<void> _loadOrders() async {
    setState(() => _isLoading = true);
    
    try {
      final orders = await _odooService.getSaleOrders();
      setState(() {
        _orders = orders;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading orders: $e')),
        );
      }
    }
  }

  List<String> get _states {
    final states = _orders.map((o) => o.stateDisplay).toSet().toList();
    states.sort();
    return ['All', ...states];
  }

  List<SaleOrder> get _filteredOrders {
    if (_selectedState == 'All') return _orders;
    return _orders.where((order) => order.stateDisplay == _selectedState).toList();
  }

  Color _getStateColor(String state) {
    switch (state) {
      case 'draft':
        return Colors.grey;
      case 'sent':
        return Colors.blue;
      case 'sale':
        return Colors.green;
      case 'done':
        return Colors.teal;
      case 'cancel':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  IconData _getStateIcon(String state) {
    switch (state) {
      case 'draft':
        return Icons.edit;
      case 'sent':
        return Icons.send;
      case 'sale':
        return Icons.check_circle;
      case 'done':
        return Icons.lock;
      case 'cancel':
        return Icons.cancel;
      default:
        return Icons.shopping_cart;
    }
  }

  void _showOrderDetails(SaleOrder order) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(order.name),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Customer:', style: TextStyle(fontWeight: FontWeight.bold)),
            Text(order.partnerName),
            const SizedBox(height: 8),
            const Text('Order Date:', style: TextStyle(fontWeight: FontWeight.bold)),
            Text(DateFormat('MMM dd, yyyy').format(order.dateOrder)),
            const SizedBox(height: 8),
            const Text('Total Amount:', style: TextStyle(fontWeight: FontWeight.bold)),
            Text(
              _currencyFormatter.format(order.amountTotal),
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1E88E5),
              ),
            ),
            const SizedBox(height: 8),
            const Text('Status:', style: TextStyle(fontWeight: FontWeight.bold)),
            Row(
              children: [
                Icon(
                  _getStateIcon(order.state),
                  color: _getStateColor(order.state),
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  order.stateDisplay,
                  style: TextStyle(
                    color: _getStateColor(order.state),
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            const Text('Order ID:', style: TextStyle(fontWeight: FontWeight.bold)),
            Text(order.id.toString()),
          ],
        ),
        actions: [
          if (_odooService.isAdmin && order.state == 'draft')
            TextButton(
              onPressed: () {
                Navigator.pop(context);
                // TODO: Edit order functionality
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Edit order feature coming soon')),
                );
              },
              child: const Text('Edit'),
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
    return Scaffold(
      appBar: AppBar(
        title: const Text('Sale Orders'),
        backgroundColor: const Color(0xFF1E88E5),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadOrders,
          ),
        ],
      ),
      drawer: const SideMenu(),
      body: Column(
        children: [
          // State Filter
          Container(
            height: 50,
            margin: const EdgeInsets.all(16),
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: _states.length,
              itemBuilder: (context, index) {
                final state = _states[index];
                final isSelected = state == _selectedState;
                
                return Container(
                  margin: const EdgeInsets.only(right: 8),
                  child: FilterChip(
                    label: Text(state),
                    selected: isSelected,
                    onSelected: (selected) {
                      setState(() {
                        _selectedState = state;
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
          
          // Summary Card
          Container(
            margin: const EdgeInsets.symmetric(horizontal: 16),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFFFF9800), Color(0xFFF57C00)],
              ),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                const Icon(Icons.shopping_cart, color: Colors.white, size: 32),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Total Orders',
                        style: TextStyle(color: Colors.white70),
                      ),
                      Text(
                        '${_orders.length}',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    const Text(
                      'Total Value',
                      style: TextStyle(color: Colors.white70, fontSize: 12),
                    ),
                    Text(
                      _currencyFormatter.format(
                        _orders.fold(0.0, (sum, order) => sum + order.amountTotal)
                      ),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Orders List
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : RefreshIndicator(
                    onRefresh: _loadOrders,
                    child: _filteredOrders.isEmpty
                        ? Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(
                                  _selectedState != 'All' ? Icons.filter_list_off : Icons.shopping_cart_outlined,
                                  size: 64,
                                  color: Colors.grey,
                                ),
                                const SizedBox(height: 16),
                                Text(
                                  _selectedState != 'All'
                                      ? 'No orders with status "$_selectedState"'
                                      : 'No sale orders found',
                                  style: const TextStyle(fontSize: 18, color: Colors.grey),
                                ),
                                if (_selectedState != 'All') ...[
                                  const SizedBox(height: 8),
                                  TextButton(
                                    onPressed: () {
                                      setState(() {
                                        _selectedState = 'All';
                                      });
                                    },
                                    child: const Text('Show all orders'),
                                  ),
                                ],
                              ],
                            ),
                          )
                        : ListView.builder(
                            itemCount: _filteredOrders.length,
                            itemBuilder: (context, index) {
                              final order = _filteredOrders[index];
                              return Card(
                                margin: const EdgeInsets.symmetric(
                                  horizontal: 16.0,
                                  vertical: 4.0,
                                ),
                                child: ListTile(
                                  leading: CircleAvatar(
                                    backgroundColor: _getStateColor(order.state),
                                    child: Icon(
                                      _getStateIcon(order.state),
                                      color: Colors.white,
                                      size: 20,
                                    ),
                                  ),
                                  title: Text(
                                    order.name,
                                    style: const TextStyle(fontWeight: FontWeight.bold),
                                  ),
                                  subtitle: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Row(
                                        children: [
                                          const Icon(Icons.person, size: 16, color: Colors.grey),
                                          const SizedBox(width: 4),
                                          Expanded(child: Text(order.partnerName)),
                                        ],
                                      ),
                                      Row(
                                        children: [
                                          const Icon(Icons.calendar_today, size: 16, color: Colors.grey),
                                          const SizedBox(width: 4),
                                          Text(DateFormat('MMM dd, yyyy').format(order.dateOrder)),
                                        ],
                                      ),
                                      const SizedBox(height: 4),
                                      Row(
                                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                        children: [
                                          Text(
                                            _currencyFormatter.format(order.amountTotal),
                                            style: const TextStyle(
                                              fontWeight: FontWeight.bold,
                                              color: Color(0xFFFF9800),
                                              fontSize: 16,
                                            ),
                                          ),
                                          Container(
                                            padding: const EdgeInsets.symmetric(
                                              horizontal: 8,
                                              vertical: 2,
                                            ),
                                            decoration: BoxDecoration(
                                              color: _getStateColor(order.state).withOpacity(0.2),
                                              borderRadius: BorderRadius.circular(12),
                                            ),
                                            child: Text(
                                              order.stateDisplay,
                                              style: TextStyle(
                                                color: _getStateColor(order.state),
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
                                  onTap: () => _showOrderDetails(order),
                                ),
                              );
                            },
                          ),
                  ),
          ),
        ],
      ),
      bottomNavigationBar: const BottomNav(currentIndex: 3),
    );
  }
}