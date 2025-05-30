import 'package:flutter/material.dart';
import '../services/odoo_service.dart';
import '../pages/login_page.dart';

class SideMenu extends StatelessWidget {
  const SideMenu({super.key});

  @override
  Widget build(BuildContext context) {
    final odoo = OdooService();
    final userName = odoo.userInfo?['name'] ?? odoo.userEmail ?? 'User';
    
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          UserAccountsDrawerHeader(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [Color(0xFF1E88E5), Color(0xFF1565C0)],
              ),
            ),
            accountName: Text(
              userName,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            accountEmail: Text(odoo.userEmail ?? ''),
            currentAccountPicture: CircleAvatar(
              backgroundColor: Colors.white,
              child: Text(
                userName.substring(0, 1).toUpperCase(),
                style: const TextStyle(
                  color: Color(0xFF1E88E5),
                  fontWeight: FontWeight.bold,
                  fontSize: 20,
                ),
              ),
            ),
            otherAccountsPictures: [
              if (odoo.isAdmin)
                Container(
                  padding: const EdgeInsets.all(4),
                  decoration: BoxDecoration(
                    color: Colors.orange,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(
                    Icons.admin_panel_settings,
                    color: Colors.white,
                    size: 16,
                  ),
                ),
            ],
          ),
          ListTile(
            leading: const Icon(Icons.dashboard),
            title: const Text('Dashboard'),
            onTap: () {
              Navigator.pop(context);
              Navigator.pushReplacementNamed(context, '/dashboard');
            },
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.people),
            title: const Text('Customers'),
            onTap: () {
              Navigator.pop(context);
              Navigator.pushReplacementNamed(context, '/clients');
            },
          ),
          ListTile(
            leading: const Icon(Icons.inventory),
            title: const Text('Products'),
            onTap: () {
              Navigator.pop(context);
              Navigator.pushReplacementNamed(context, '/items');
            },
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.shopping_cart),
            title: const Text('Sale Orders'),
            onTap: () {
              Navigator.pop(context);
              Navigator.pushReplacementNamed(context, '/sale_orders');
            },
          ),
          ListTile(
            leading: const Icon(Icons.receipt_long),
            title: const Text('Invoices'),
            onTap: () {
              Navigator.pop(context);
              Navigator.pushReplacementNamed(context, '/invoices');
            },
          ),
          ListTile(
            leading: const Icon(Icons.payment),
            title: const Text('Payments Received'),
            onTap: () {
              Navigator.pop(context);
              Navigator.pushReplacementNamed(context, '/payments');
            },
          ),
          if (odoo.isAdmin) ...[
            const Divider(),
            Container(
              color: Colors.orange.withValues(alpha: 0.1),
              child: const ListTile(
                leading: Icon(Icons.admin_panel_settings, color: Colors.orange),
                title: Text(
                  'Admin Features',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.orange,
                  ),
                ),
              ),
            ),
            ListTile(
              leading: const Icon(Icons.person_add),
              title: const Text('Add Customer'),
              onTap: () {
                Navigator.pop(context);
                _showAddCustomerDialog(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.add_shopping_cart),
              title: const Text('Create Sale Order'),
              onTap: () {
                Navigator.pop(context);
                _showCreateOrderDialog(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.add_card),
              title: const Text('Record Payment'),
              onTap: () {
                Navigator.pop(context);
                _showRecordPaymentDialog(context);
              },
            ),
          ],
          const Divider(),
          ListTile(
            leading: const Icon(Icons.settings),
            title: const Text('Settings'),
            onTap: () {
              Navigator.pop(context);
              _showSettingsDialog(context);
            },
          ),
          ListTile(
            leading: const Icon(Icons.logout, color: Colors.red),
            title: const Text('Logout', style: TextStyle(color: Colors.red)),
            onTap: () async {
              await odoo.logout();
              if (context.mounted) {
                Navigator.of(context).pushAndRemoveUntil(
                  MaterialPageRoute(builder: (context) => const LoginPage()),
                  (route) => false,
                );
              }
            },
          ),
        ],
      ),
    );
  }

  void _showAddCustomerDialog(BuildContext context) {
    final nameController = TextEditingController();
    final emailController = TextEditingController();
    final phoneController = TextEditingController();
    final streetController = TextEditingController();
    final cityController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add New Customer'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                decoration: const InputDecoration(
                  labelText: 'Company Name *',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: emailController,
                decoration: const InputDecoration(
                  labelText: 'Email',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: phoneController,
                decoration: const InputDecoration(
                  labelText: 'Phone',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: streetController,
                decoration: const InputDecoration(
                  labelText: 'Street Address',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: cityController,
                decoration: const InputDecoration(
                  labelText: 'City',
                  border: OutlineInputBorder(),
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
            onPressed: () async {
              if (nameController.text.isNotEmpty) {
                final success = await OdooService().createCustomer(
                  name: nameController.text,
                  email: emailController.text.isEmpty ? null : emailController.text,
                  phone: phoneController.text.isEmpty ? null : phoneController.text,
                  street: streetController.text.isEmpty ? null : streetController.text,
                  city: cityController.text.isEmpty ? null : cityController.text,
                );
                
                if (context.mounted) {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(success ? 'Customer created successfully' : 'Failed to create customer'),
                      backgroundColor: success ? Colors.green : Colors.red,
                    ),
                  );
                }
              }
            },
            child: const Text('Create'),
          ),
        ],
      ),
    );
  }

  void _showCreateOrderDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Create Sale Order'),
        content: const Text('This feature will open a detailed order creation form.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              // TODO: Navigate to order creation page
            },
            child: const Text('Continue'),
          ),
        ],
      ),
    );
  }

  void _showRecordPaymentDialog(BuildContext context) {
    final amountController = TextEditingController();
    final referenceController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Record Payment'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
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
            TextField(
              controller: referenceController,
              decoration: const InputDecoration(
                labelText: 'Reference',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              // TODO: Implement payment recording
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Payment recording feature coming soon'),
                ),
              );
            },
            child: const Text('Record'),
          ),
        ],
      ),
    );
  }

  void _showSettingsDialog(BuildContext context) {
    final odoo = OdooService();
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Settings'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Server: ${odoo.baseUrl ?? 'Not connected'}'),
            const SizedBox(height: 8),
            Text('User: ${odoo.userEmail ?? 'Not logged in'}'),
            const SizedBox(height: 8),
            Text('Role: ${odoo.isAdmin ? 'Administrator' : 'Salesperson'}'),
            const SizedBox(height: 16),
            const Text(
              'TSH Salesperson App v1.0.0',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
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
  }
}