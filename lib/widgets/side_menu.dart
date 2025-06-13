/// TSH Salesperson Side Menu - Spider Hand Technical Company
/// شركة يد العنكبوت التقنية
/// 
/// TSH Unified Architecture System - Mobile Ecosystem v2.0.0
/// Author: TSH Technical Team | Date: 2025-06-04

import 'package:flutter/material.dart';
import '../services/odoo_service.dart';
import '../pages/salesperson_dashboard.dart';
import '../pages/clients_page.dart';
import '../pages/items_page.dart';
import '../pages/sale_orders_page.dart';
import '../pages/invoices_page.dart';
import '../pages/collection_receipts_page.dart';
import '../pages/transfers_tracking_page.dart';
import '../pages/about_page.dart';
import '../pages/login_page.dart';
import '../config/app_config.dart';

class SideMenu extends StatelessWidget {
  const SideMenu({super.key});

  @override
  Widget build(BuildContext context) {
    final odooService = OdooService();

    return Drawer(
      child: Column(
        children: [
          DrawerHeader(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [Color(0xFF1E88E5), Color(0xFF1565C0)],
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                const CircleAvatar(
                  radius: 30,
                  backgroundColor: Colors.white,
                  child: Icon(Icons.person, size: 40, color: Color(0xFF1E88E5)),
                ),
                const SizedBox(height: 12),
                Text(
                  odooService.userName ?? 'مندوب المبيعات',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                if (odooService.userEmail != null)
                  Text(
                    odooService.userEmail!,
                    style: const TextStyle(color: Colors.white70, fontSize: 12),
                  ),
              ],
            ),
          ),
          Expanded(
            child: ListView(
              padding: EdgeInsets.zero,
              children: [
                _buildMenuItem(
                  context,
                  icon: Icons.dashboard,
                  title: 'لوحة التحكم',
                  onTap: () =>
                      _navigateTo(context, const SalespersonDashboard()),
                ),
                _buildMenuItem(
                  context,
                  icon: Icons.people,
                  title: 'العملاء',
                  onTap: () => _navigateTo(context, const ClientsPage()),
                ),
                _buildMenuItem(
                  context,
                  icon: Icons.inventory,
                  title: 'المنتجات',
                  onTap: () => _navigateTo(context, const ItemsPage()),
                ),
                _buildMenuItem(
                  context,
                  icon: Icons.shopping_cart,
                  title: 'الطلبات',
                  onTap: () => _navigateTo(context, const SaleOrdersPage()),
                ),
                _buildMenuItem(
                  context,
                  icon: Icons.receipt,
                  title: 'الفواتير',
                  onTap: () => _navigateTo(context, const InvoicesPage()),
                ),
                const Divider(),
                _buildMenuItem(
                  context,
                  icon: Icons.payment,
                  title: 'وصولات القبض',
                  onTap: () =>
                      _navigateTo(context, const CollectionReceiptsPage()),
                ),
                _buildMenuItem(
                  context,
                  icon: Icons.swap_horiz,
                  title: 'متابعة الحوالات',
                  onTap: () =>
                      _navigateTo(context, const TransfersTrackingPage()),
                ),
                const Divider(),
                _buildMenuItem(
                  context,
                  icon: Icons.settings,
                  title: 'الإعدادات',
                  onTap: () {
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('الإعدادات قيد التطوير')),
                    );
                  },
                ),
                _buildMenuItem(
                  context,
                  icon: Icons.help,
                  title: 'المساعدة',
                  onTap: () {
                    Navigator.pop(context);
                    _showHelpDialog(context);
                  },
                ),
                _buildMenuItem(
                  context,
                  icon: Icons.info,
                  title: 'حول التطبيق',
                  onTap: () => _navigateTo(context, const AboutPage()),
                ),
              ],
            ),
          ),
          const Divider(),
          _buildMenuItem(
            context,
            icon: Icons.logout,
            title: 'تسجيل الخروج',
            onTap: () => _logout(context),
            isDestructive: true,
          ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }

  Widget _buildMenuItem(
    BuildContext context, {
    required IconData icon,
    required String title,
    required VoidCallback onTap,
    bool isDestructive = false,
  }) {
    return ListTile(
      leading: Icon(
        icon,
        color: isDestructive ? Colors.red : const Color(0xFF1E88E5),
      ),
      title: Text(
        title,
        style: TextStyle(
          color: isDestructive ? Colors.red : null,
          fontWeight: FontWeight.w500,
        ),
      ),
      onTap: onTap,
      dense: true,
    );
  }

  void _navigateTo(BuildContext context, Widget page) {
    Navigator.pop(context); // Close drawer
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => page),
    );
  }

  void _showHelpDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('المساعدة'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(AppConfig.appDisplayName),
            const SizedBox(height: 4),
            Text(AppConfig.companyNameArabic),
            const SizedBox(height: 8),
            Text('الإصدار: v${AppConfig.appVersion}'),
            Text('نظام: ${AppConfig.systemName}'),
            const SizedBox(height: 8),
            const Text('الميزات الرئيسية:'),
            const Text('• إدارة العملاء المخصصين'),
            const Text('• عرض المنتجات من المخازن المرتبطة'),
            const Text('• متابعة الطلبات والفواتير'),
            const Text('• إدارة وصولات القبض'),
            const Text('• التسوية الشاملة للمبالغ'),
            const Text('• متابعة الحوالات المالية'),
            const SizedBox(height: 8),
            const Text('للدعم التقني: kha89ahm@gmail.com'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('موافق'),
          ),
        ],
      ),
    );
  }

  void _logout(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('تسجيل الخروج'),
        content: const Text('هل أنت متأكد من تسجيل الخروج؟'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context); // Close dialog
              Navigator.pop(context); // Close drawer
              OdooService().logout();
              Navigator.pushAndRemoveUntil(
                context,
                MaterialPageRoute(builder: (context) => const LoginPage()),
                (route) => false,
              );
            },
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('تسجيل الخروج'),
          ),
        ],
      ),
    );
  }
}
