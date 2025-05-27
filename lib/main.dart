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
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Odoo Sales App',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: SplashScreen(),
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
  const SplashScreen({super.key});
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
    final odoo = OdooService();
    await odoo.loadSession();
    if (odoo.isAuthenticated) {
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