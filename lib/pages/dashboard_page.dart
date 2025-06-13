/// TSH Salesperson Dashboard - Spider Hand Technical Company
/// شركة يد العنكبوت التقنية
/// 
/// TSH Unified Architecture System - Mobile Ecosystem v2.0.0
/// Author: TSH Technical Team | Date: 2025-06-04

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/odoo_service.dart';
import '../services/mock_odoo_service.dart';
import '../widgets/bottom_nav.dart';
import '../widgets/side_menu.dart';
import '../widgets/dashboard_widgets.dart';
import '../widgets/common_widgets.dart';
import '../config/app_config.dart';
import 'login_page.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();
  bool _isLoading = true;
  Map<String, dynamic> _dashboardData = {};
  final _currencyFormatter = NumberFormat.currency(symbol: '\$');
  final _odooService = OdooService();

  @override
  void initState() {
    super.initState();
    _loadDashboardData();
  }

  Future<void> _loadDashboardData() async {
    setState(() => _isLoading = true);

    try {
      Map<String, dynamic>? data;

      // Try real service first
      try {
        data = await _odooService.getBasicDashboardData();
        print('✅ Dashboard data loaded from real service');
      } catch (e) {
        print('❌ Real service failed, trying mock service: $e');
        // Fall back to mock service
        data = await MockOdooService().getDashboardData();
        print('✅ Dashboard data loaded from mock service');
      }

      setState(() {
        _dashboardData = data!;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error loading dashboard: $e')));
      }
    }
  }

  Future<void> _logout() async {
    await _odooService.logout();
    if (mounted) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (context) => const LoginPage()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: _scaffoldKey,
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('${AppConfig.appName} - Dashboard'),
            if (_odooService.userEmail != null)
              Text(
                _odooService.userEmail!,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.normal,
                ),
              ),
          ],
        ),
        backgroundColor: const Color(0xFF1E88E5),
        foregroundColor: Colors.white,
        leading: IconButton(
          icon: const Icon(Icons.menu),
          onPressed: () => _scaffoldKey.currentState?.openDrawer(),
        ),
        actions: [
          if (_odooService.isAdmin)
            Container(
              margin: const EdgeInsets.only(right: 8),
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.orange,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Text(
                'ADMIN',
                style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold),
              ),
            ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadDashboardData,
          ),
          IconButton(icon: const Icon(Icons.logout), onPressed: _logout),
        ],
      ),
      drawer: const SideMenu(),
      body: _isLoading
          ? const LoadingWidget(message: 'جاري تحميل البيانات...')
          : RefreshIndicator(
              onRefresh: _loadDashboardData,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildSystemInfoCard(),
                    const SizedBox(height: 16),
                    _buildUserWelcomeCard(),
                    const SizedBox(height: 16),
                    _buildDashboardStats(),
                    const SizedBox(height: 16),
                    _buildQuickActions(),
                    const SizedBox(height: 16),
                    _buildSalesChart(),
                    const SizedBox(height: 16),
                    _buildRecentActivity(),
                  ],
                ),
              ),
            ),
      bottomNavigationBar: const BottomNav(currentIndex: 0),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => Navigator.pushNamed(context, '/cart'),
        icon: const Icon(Icons.shopping_cart),
        label: const Text('السلة'),
        backgroundColor: Colors.green,
      ),
    );
  }

  Widget _buildSystemInfoCard() {
    return Card(
      elevation: 1,
      color: Colors.blue.shade50,
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Row(
          children: [
            Icon(
              Icons.architecture,
              color: Colors.blue.shade700,
              size: 20,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    AppConfig.companyName,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Colors.blue.shade800,
                    ),
                  ),
                  Text(
                    AppConfig.companyNameArabic,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.blue.shade600,
                    ),
                  ),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  'v${AppConfig.appVersion}',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue.shade700,
                  ),
                ),
                Text(
                  AppConfig.systemName,
                  style: TextStyle(
                    fontSize: 10,
                    color: Colors.blue.shade600,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildUserWelcomeCard() {
    final userName =
        _odooService.userInfo?['name'] ?? _odooService.userEmail ?? 'User';

    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            CircleAvatar(
              backgroundColor: const Color(0xFF1E88E5),
              child: Text(
                userName.substring(0, 1).toUpperCase(),
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Welcome back, $userName!',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Icon(
                        Icons.verified_user,
                        size: 16,
                        color: _odooService.isAdmin
                            ? Colors.orange
                            : Colors.green,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        _odooService.isAdmin ? 'Administrator' : 'Salesperson',
                        style: TextStyle(
                          color: _odooService.isAdmin
                              ? Colors.orange
                              : Colors.green,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            Icon(Icons.business_center, color: Colors.grey[400]),
          ],
        ),
      ),
    );
  }

  Widget _buildMainCard() {
    final totalAmount = _dashboardData['total_amount'] ?? 0.0;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24.0),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF1E88E5), Color(0xFF1565C0)],
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.blue.withOpacity(0.3),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Total Revenue',
                style: TextStyle(color: Colors.white70, fontSize: 16),
              ),
              Icon(
                Icons.account_balance_wallet,
                color: Colors.white70,
                size: 24,
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            _currencyFormatter.format(totalAmount),
            style: const TextStyle(
              color: Colors.white,
              fontSize: 32,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.trending_up, color: Colors.green, size: 16),
                    SizedBox(width: 4),
                    Text(
                      '+12.5%',
                      style: TextStyle(
                        color: Colors.green,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              const Text(
                'vs last month',
                style: TextStyle(color: Colors.white70),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildRegionalCards() {
    final regions = _dashboardData['regions'] as List<dynamic>? ?? [];

    if (regions.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16.0),
          child: Text('No regional data available'),
        ),
      );
    }

    return Column(
      children: regions.map<Widget>((region) {
        final name = region['name'] ?? 'Unknown Region';
        final amount = region['amount'] ?? 0.0;
        final orders = region['orders'] ?? 0;

        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          elevation: 2,
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: const Color(0xFF1E88E5).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(24),
                  ),
                  child: const Icon(
                    Icons.location_on,
                    color: Color(0xFF1E88E5),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        name,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '$orders orders',
                        style: TextStyle(color: Colors.grey[600], fontSize: 14),
                      ),
                    ],
                  ),
                ),
                Text(
                  _currencyFormatter.format(amount),
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                    color: Color(0xFF1E88E5),
                  ),
                ),
              ],
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildQuickStats() {
    final stats = [
      {
        'title': 'Active Orders',
        'value': _dashboardData['active_orders']?.toString() ?? '0',
        'icon': Icons.shopping_cart,
        'color': Colors.orange,
      },
      {
        'title': 'Pending Invoices',
        'value': _dashboardData['pending_invoices']?.toString() ?? '0',
        'icon': Icons.receipt,
        'color': Colors.red,
      },
      {
        'title': 'Total Clients',
        'value': _dashboardData['total_clients']?.toString() ?? '0',
        'icon': Icons.people,
        'color': Colors.green,
      },
      {
        'title': 'Products Sold',
        'value': _dashboardData['products_sold']?.toString() ?? '0',
        'icon': Icons.inventory,
        'color': Colors.purple,
      },
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Quick Stats',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            childAspectRatio: 1.5,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
          ),
          itemCount: stats.length,
          itemBuilder: (context, index) {
            final stat = stats[index];
            return Card(
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      stat['icon'] as IconData,
                      size: 32,
                      color: stat['color'] as Color,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      stat['value'] as String,
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      stat['title'] as String,
                      style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            );
          },
        ),
      ],
    );
  }

  Widget _buildDashboardStats() {
    final totalAmount = _dashboardData['total_amount'] ?? 0.0;
    final totalOrders = _dashboardData['total_orders'] ?? 0;
    final totalClients = _dashboardData['total_clients'] ?? 0;
    final monthlyGrowth = _dashboardData['monthly_growth'] ?? 0.0;

    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      childAspectRatio: 1.5,
      crossAxisSpacing: 8,
      mainAxisSpacing: 8,
      children: [
        DashboardCard(
          title: 'إجمالي المبيعات',
          value: _currencyFormatter.format(totalAmount),
          icon: Icons.attach_money,
          color: Colors.green,
          percentage: monthlyGrowth,
          onTap: () => Navigator.pushNamed(context, '/sale_orders'),
        ),
        DashboardCard(
          title: 'الطلبات',
          value: totalOrders.toString(),
          icon: Icons.shopping_cart,
          color: Colors.blue,
          onTap: () => Navigator.pushNamed(context, '/sale_orders'),
        ),
        DashboardCard(
          title: 'العملاء',
          value: totalClients.toString(),
          icon: Icons.people,
          color: Colors.orange,
          onTap: () => Navigator.pushNamed(context, '/clients'),
        ),
        DashboardCard(
          title: 'المنتجات',
          value: (_dashboardData['total_products'] ?? 0).toString(),
          icon: Icons.inventory,
          color: Colors.purple,
          onTap: () => Navigator.pushNamed(context, '/items'),
        ),
      ],
    );
  }

  Widget _buildQuickActions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'إجراءات سريعة',
          style: Theme.of(
            context,
          ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 4,
          childAspectRatio: 1,
          crossAxisSpacing: 8,
          mainAxisSpacing: 8,
          children: [
            QuickActionCard(
              title: 'طلب جديد',
              icon: Icons.add_shopping_cart,
              onTap: () => Navigator.pushNamed(context, '/sale_orders'),
              color: Colors.green,
            ),
            QuickActionCard(
              title: 'عميل جديد',
              icon: Icons.person_add,
              onTap: () => Navigator.pushNamed(context, '/clients'),
              color: Colors.blue,
            ),
            QuickActionCard(
              title: 'المنتجات',
              icon: Icons.inventory_2,
              onTap: () => Navigator.pushNamed(context, '/items'),
              color: Colors.orange,
            ),
            QuickActionCard(
              title: 'المدفوعات',
              icon: Icons.payment,
              onTap: () => Navigator.pushNamed(context, '/payments'),
              color: Colors.purple,
              badge: (_dashboardData['pending_payments'] ?? 0).toString(),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildSalesChart() {
    final salesData =
        _dashboardData['weekly_sales'] as List<Map<String, dynamic>>? ??
        [
          {'day': 'الأحد', 'amount': 1200.0},
          {'day': 'الاثنين', 'amount': 1800.0},
          {'day': 'الثلاثاء', 'amount': 1500.0},
          {'day': 'الأربعاء', 'amount': 2200.0},
          {'day': 'الخميس', 'amount': 1900.0},
          {'day': 'الجمعة', 'amount': 2500.0},
          {'day': 'السبت', 'amount': 1700.0},
        ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'تحليل المبيعات',
          style: Theme.of(
            context,
          ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        SalesChart(salesData: salesData),
      ],
    );
  }

  Widget _buildRecentActivity() {
    final activities =
        _dashboardData['recent_activities'] as List<Map<String, dynamic>>? ??
        [
          {
            'type': 'sale',
            'title': 'طلب جديد من أحمد محمد',
            'subtitle': 'طلب رقم SO001 - 150,000 د.ع',
            'time': DateTime.now().subtract(const Duration(minutes: 30)),
          },
          {
            'type': 'visit',
            'title': 'زيارة شركة الأنوار',
            'subtitle': 'اجتماع مع مدير المشتريات',
            'time': DateTime.now().subtract(const Duration(hours: 2)),
          },
          {
            'type': 'payment',
            'title': 'دفعة مستلمة',
            'subtitle': 'من عميل محمد علي - 75,000 د.ع',
            'time': DateTime.now().subtract(const Duration(hours: 4)),
          },
          {
            'type': 'call',
            'title': 'مكالمة مع فاطمة أحمد',
            'subtitle': 'مناقشة طلب جديد',
            'time': DateTime.now().subtract(const Duration(hours: 6)),
          },
        ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'النشاطات الحديثة',
          style: Theme.of(
            context,
          ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        RecentActivityCard(activities: activities),
      ],
    );
  }
}
