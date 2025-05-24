import 'package:flutter/material.dart';
import 'pages/login_page.dart';
import 'pages/dashboard_page.dart';
import 'pages/items_page.dart';
import 'pages/clients_page.dart';
import 'pages/sale_orders_page.dart';
import 'pages/invoices_page.dart';
import 'pages/payments_page.dart';
import 'services/odoo_service.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  final OdooService odoo = OdooService('https://your-odoo-domain.com');

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Odoo Sales App',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: SplashScreen(odoo: odoo),
      routes: {
        '/dashboard': (context) => DashboardPage(),
        '/items': (context) => ItemsPage(),
        '/clients': (context) => ClientsPage(),
        '/sale_orders': (context) => SaleOrdersPage(),
        '/invoices': (context) => InvoicesPage(),
        '/payments': (context) => PaymentsPage(),
      },
    );
  }
}

class SplashScreen extends StatefulWidget {
  final OdooService odoo;
  const SplashScreen({required this.odoo});
  @override
  _SplashScreenState createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _checkSession();
  }

  void _checkSession() async {
    await widget.odoo.loadSession();
    if (widget.odoo._sessionId != null) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => DashboardPage()),
      );
    } else {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => LoginPage()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(child: CircularProgressIndicator()),
    );
  }
} 