import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../config/app_config.dart';
import 'odoo_service.dart';

class TSHSalespersonService {
  static String get baseUrl => AppConfig.effectiveOdooUrl;
  static String get database => AppConfig.odooDatabaseName;
  
  final OdooService _odooService = OdooService();

  // Get stored password
  Future<String> _getStoredPassword() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('user_password') ?? '';
  }

  // Make request to Odoo
  Future<Map<String, dynamic>> _makeRequest(String endpoint, Map<String, dynamic> data) async {
    final url = Uri.parse('$baseUrl$endpoint');
    final headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    print('🌐 TSH Service making request to: $url');

    try {
      final response = await http
          .post(url, headers: headers, body: jsonEncode(data))
          .timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        if (responseData['error'] != null) {
          throw Exception(responseData['error']['message'] ?? 'Unknown API error');
        }
        return responseData;
      } else {
        throw Exception('HTTP ${response.statusCode}: ${response.body}');
      }
    } catch (e) {
      print('💥 TSH Service request failed: $e');
      rethrow;
    }
  }

  // Get current user info (simulated salesperson data)
  Future<Map<String, dynamic>?> getCurrentSalesperson() async {
    if (!_odooService.isLoggedIn) {
      throw Exception('Not logged in');
    }

    try {
      print('👤 Creating virtual salesperson data for current user...');
      
      // Get current user info
      final password = await _getStoredPassword();
      final data = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
          'service': 'object',
          'method': 'execute_kw',
          'args': [
            database,
            _odooService.userId,
            password,
            'res.users',
            'read',
            [_odooService.userId],
            {
              'fields': ['id', 'name', 'email', 'phone', 'mobile', 'partner_id'],
            },
          ],
        },
        'id': 1,
      };

      final response = await _makeRequest('/jsonrpc', data);
      final userInfo = response['result'][0];
      
      // Create virtual salesperson data
      final virtualSalesperson = {
        'id': _odooService.userId,
        'name': userInfo['name'] ?? 'TSH Salesperson',
        'user_id': _odooService.userId,
        'phone': userInfo['phone'] ?? '+964 770 123 4567',
        'mobile': userInfo['mobile'] ?? '+964 770 123 4567',
        'email': userInfo['email'] ?? _odooService.userEmail,
        'assigned_regions': ['Baghdad', 'Karbala', 'Najaf'],
        'commission_rate': 5.0,
        'target_monthly': 50000.0,
        'target_yearly': 600000.0,
        'total_sales_current_month': 0.0,
        'total_sales_current_year': 0.0,
        'achievement_percentage': 0.0,
        'total_commission_earned': 0.0,
        'customer_count': 0,
        'assigned_customers': [],
        'active': true,
      };
      
      print('✅ Created virtual salesperson: ${virtualSalesperson['name']}');
      return virtualSalesperson;
    } catch (e) {
      print('❌ Error getting current salesperson: $e');
      return null;
    }
  }

  // Get all customers (since we don't have assignment logic)
  Future<List<Map<String, dynamic>>> getAssignedCustomers() async {
    try {
      print('👥 Fetching all customers for salesperson...');
      
      // Since we don't have the TSH Salesperson module, return all customers
      final customers = await _odooService.getCustomers(limit: 100);
      
      print('✅ Fetched ${customers.length} customers');
      return customers;
    } catch (e) {
      print('❌ Error getting customers: $e');
      // Fallback to empty list
      return [];
    }
  }

  // Get salesperson dashboard data
  Future<Map<String, dynamic>> getSalespersonDashboard() async {
    try {
      print('📊 Fetching salesperson dashboard data...');
      
      final salesperson = await getCurrentSalesperson();
      final assignedCustomers = await getAssignedCustomers();
      
      // Get recent orders
      final recentOrders = await _getRecentOrders();
      
      // Calculate performance metrics from actual data
      double totalSales = 0.0;
      double monthlyTarget = 50000.0;
      double yearlyTarget = 600000.0;
      
      for (var order in recentOrders) {
        totalSales += (order['amount_total'] ?? 0.0).toDouble();
      }
      
      double monthlyAchievement = monthlyTarget > 0 ? (totalSales / monthlyTarget * 100) : 0.0;
      double yearlyAchievement = yearlyTarget > 0 ? (totalSales / yearlyTarget * 100) : 0.0;
      double commissionEarned = totalSales * 0.05; // 5% commission
      
      return {
        'salesperson': salesperson,
        'assigned_customers_count': assignedCustomers.length,
        'recent_orders': recentOrders,
        'performance': {
          'monthly_target': monthlyTarget,
          'yearly_target': yearlyTarget,
          'monthly_sales': totalSales,
          'yearly_sales': totalSales,
          'monthly_achievement': monthlyAchievement,
          'yearly_achievement': yearlyAchievement,
          'commission_earned': commissionEarned,
        },
        'regions': ['Baghdad', 'Karbala', 'Najaf'],
        'last_updated': DateTime.now().toIso8601String(),
      };
    } catch (e) {
      print('❌ Error getting salesperson dashboard: $e');
      throw Exception('Failed to load salesperson dashboard');
    }
  }

  // Get recent orders
  Future<List<Map<String, dynamic>>> _getRecentOrders() async {
    try {
      final password = await _getStoredPassword();
      final data = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
          'service': 'object',
          'method': 'execute_kw',
          'args': [
            database,
            _odooService.userId,
            password,
            'sale.order',
            'search_read',
            [
              [['state', 'in', ['draft', 'sent', 'sale', 'done']]]
            ],
            {
              'fields': [
                'id',
                'name',
                'partner_id',
                'date_order',
                'amount_total',
                'state',
                'currency_id',
              ],
              'order': 'date_order desc',
              'limit': 20,
            },
          ],
        },
        'id': 1,
      };

      final response = await _makeRequest('/jsonrpc', data);
      return List<Map<String, dynamic>>.from(response['result'] ?? []);
    } catch (e) {
      print('❌ Error getting recent orders: $e');
      return [];
    }
  }

  // Get customer statistics
  Future<Map<String, dynamic>> getCustomerStats() async {
    try {
      final customers = await getAssignedCustomers();
      final orders = await _getRecentOrders();
      
      // Calculate stats
      int totalCustomers = customers.length;
      int activeCustomers = customers.where((c) => c['customer_rank'] != null && c['customer_rank'] > 0).length;
      int companiesCount = customers.where((c) => c['is_company'] == true).length;
      int individualsCount = totalCustomers - companiesCount;
      
      // Group by city
      Map<String, int> customersByCity = {};
      for (var customer in customers) {
        String city = customer['city'] ?? 'Unknown';
        customersByCity[city] = (customersByCity[city] ?? 0) + 1;
      }
      
      return {
        'total_customers': totalCustomers,
        'active_customers': activeCustomers,
        'companies': companiesCount,
        'individuals': individualsCount,
        'customers_by_city': customersByCity,
        'total_orders': orders.length,
        'recent_orders': orders.take(5).toList(),
      };
    } catch (e) {
      print('❌ Error getting customer stats: $e');
      return {
        'total_customers': 0,
        'active_customers': 0,
        'companies': 0,
        'individuals': 0,
        'customers_by_city': {},
        'total_orders': 0,
        'recent_orders': [],
      };
    }
  }
} 