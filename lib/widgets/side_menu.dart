import 'package:flutter/material.dart';
import '../services/odoo_service.dart';

class SideMenu extends StatelessWidget {
  const SideMenu({super.key});

  @override
  Widget build(BuildContext context) {
    final odoo = OdooService();
    return Drawer(
      child: ListView(
        children: [
          DrawerHeader(child: Text('Menu')),
          ListTile(
            leading: Icon(Icons.receipt),
            title: Text('Sale Orders'),
            onTap: () => Navigator.pushReplacementNamed(context, '/sale_orders'),
          ),
          ListTile(
            leading: Icon(Icons.receipt_long),
            title: Text('Invoices'),
            onTap: () => Navigator.pushReplacementNamed(context, '/invoices'),
          ),
          ListTile(
            leading: Icon(Icons.payment),
            title: Text('Payments Received'),
            onTap: () => Navigator.pushReplacementNamed(context, '/payments'),
          ),
          Divider(),
          ListTile(
            leading: Icon(Icons.logout),
            title: Text('Logout'),
            onTap: () async {
              await odoo.logout();
              Navigator.pushReplacementNamed(context, '/');
            },
          ),
        ],
      ),
    );
  }
} 