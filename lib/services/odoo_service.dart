import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class OdooService {
  static const String baseUrl = 'http://138.68.89.104:8069';
  static const String database = 'odtshbrain';
  
  static final OdooService _instance = OdooService._internal();
  factory OdooService() => _instance;
  OdooService._internal();

  int? _userId;
  String? _sessionId;
  String? _userName;
  String? _userEmail;
  List<int> _assignedClientIds = [];
  List<int> _assignedWarehouseIds = [];
  List<String> _assignedRegions = [];

  int? get userId => _userId;
  String? get sessionId => _sessionId;
  String? get userName => _userName;
  String? get userEmail => _userEmail;
  List<int> get assignedClientIds => _assignedClientIds;
  List<int> get assignedWarehouseIds => _assignedWarehouseIds;
  List<String> get assignedRegions => _assignedRegions;

  bool get isLoggedIn => _userId != null && _sessionId != null;

  Future<Map<String, dynamic>> _makeRequest(String endpoint, Map<String, dynamic> data) async {
    final url = Uri.parse('$baseUrl$endpoint');
    final headers = {
      'Content-Type': 'application/json',
      if (_sessionId != null) 'Cookie': 'session_id=$_sessionId',
    };

    final response = await http.post(
      url,
      headers: headers,
      body: jsonEncode(data),
    );

    if (response.statusCode == 200) {
      final responseData = jsonDecode(response.body);
      if (responseData['error'] != null) {
        throw Exception(responseData['error']['message'] ?? 'Unknown error');
      }
      return responseData;
    } else {
      throw Exception('HTTP ${response.statusCode}: ${response.body}');
    }
  }

  Future<bool> login(String email, String password) async {
    try {
      final data = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
          'service': 'common',
          'method': 'authenticate',
          'args': [database, email, password, {}]
        },
        'id': 1,
      };

      final response = await _makeRequest('/jsonrpc', data);
      
      if (response['result'] != null && response['result'] != false) {
        _userId = response['result'];
        
        // Get user details and salesperson info
        await _getUserDetails();
        await _getSalespersonInfo();
        
        // Save session
        final prefs = await SharedPreferences.getInstance();
        await prefs.setInt('user_id', _userId!);
        await prefs.setString('user_email', email);
        
        return true;
      }
      return false;
    } catch (e) {
      print('Login error: $e');
      return false;
    }
  }

  Future<void> _getUserDetails() async {
    try {
      final data = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
          'service': 'object',
          'method': 'execute_kw',
          'args': [
            database,
            _userId,
            'password',
            'res.users',
            'read',
            [_userId],
            {'fields': ['name', 'email']}
          ]
        },
        'id': 1,
      };

      final response = await _makeRequest('/jsonrpc', data);
      if (response['result'] != null && response['result'].isNotEmpty) {
        final userInfo = response['result'][0];
        _userName = userInfo['name'];
        _userEmail = userInfo['email'];
      }
    } catch (e) {
      print('Error getting user details: $e');
    }
  }

  Future<void> _getSalespersonInfo() async {
    try {
      // Get salesperson record for current user
      final data = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
          'service': 'object',
          'method': 'execute_kw',
          'args': [
            database,
            _userId,
            'password',
            'res.partner',
            'search_read',
            [[['user_id', '=', _userId], ['is_salesperson', '=', true]]],
            {'fields': ['assigned_client_ids', 'assigned_warehouse_ids', 'assigned_regions']}
          ]
        },
        'id': 1,
      };

      final response = await _makeRequest('/jsonrpc', data);
      if (response['result'] != null && response['result'].isNotEmpty) {
        final salespersonInfo = response['result'][0];
        _assignedClientIds = List<int>.from(salespersonInfo['assigned_client_ids'] ?? []);
        _assignedWarehouseIds = List<int>.from(salespersonInfo['assigned_warehouse_ids'] ?? []);
        _assignedRegions = List<String>.from(salespersonInfo['assigned_regions'] ?? []);
      }
    } catch (e) {
      print('Error getting salesperson info: $e');
    }
  }

  Future<bool> loadSession() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final userId = prefs.getInt('user_id');
      final userEmail = prefs.getString('user_email');
      
      if (userId != null && userEmail != null) {
        _userId = userId;
        _userEmail = userEmail;
        await _getUserDetails();
        await _getSalespersonInfo();
        return true;
      }
      return false;
    } catch (e) {
      print('Error loading session: $e');
      return false;
    }
  }

  Future<void> logout() async {
    _userId = null;
    _sessionId = null;
    _userName = null;
    _userEmail = null;
    _assignedClientIds = [];
    _assignedWarehouseIds = [];
    _assignedRegions = [];
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }

  // Dashboard data with salesperson-specific filtering
  Future<Map<String, dynamic>> getSalespersonDashboardData() async {
    if (!isLoggedIn) throw Exception('Not logged in');

    try {
      // Get collection receipts for commission calculation
      final receiptsData = await getCollectionReceipts();
      final receipts = receiptsData.map((data) => {
        'amount': (data['amount'] ?? 0.0).toDouble(),
        'status': data['status'] ?? 'collected',
        'payment_type': data['payment_type'] ?? 'cash',
        'region': data['region'] ?? '',
        'is_settled': data['is_settled'] ?? false,
      }).toList();

      // Calculate totals
      double totalCommission = 0.0;
      double totalCashCollected = 0.0;
      double totalDigitalCollected = 0.0;
      double cashOnHand = 0.0;
      Map<String, double> outstandingByRegion = {};
      Map<String, Map<String, double>> collectionsByRegion = {};

      for (final receipt in receipts) {
        final amount = receipt['amount'] as double;
        final commission = amount * 0.0225; // 2.25%
        final paymentType = receipt['payment_type'] as String;
        final region = receipt['region'] as String;
        final isSettled = receipt['is_settled'] as bool;

        totalCommission += commission;

        if (!isSettled) {
          if (paymentType == 'cash') {
            totalCashCollected += amount;
            cashOnHand += amount;
          } else {
            totalDigitalCollected += amount;
          }

          // Regional breakdown
          if (!collectionsByRegion.containsKey(region)) {
            collectionsByRegion[region] = {'cash': 0.0, 'digital': 0.0};
          }
          collectionsByRegion[region]![paymentType == 'cash' ? 'cash' : 'digital'] = 
              (collectionsByRegion[region]![paymentType == 'cash' ? 'cash' : 'digital'] ?? 0.0) + amount;
        }
      }

      // Get outstanding amounts by region
      for (final region in _assignedRegions) {
        final outstanding = await _getOutstandingAmountForRegion(region);
        if (outstanding > 0) {
          outstandingByRegion[region] = outstanding;
        }
      }

      // Build regional summaries
      final regionalSummaries = collectionsByRegion.entries.map((entry) {
        return {
          'region': entry.key,
          'cash_collected': entry.value['cash'] ?? 0.0,
          'digital_collected': entry.value['digital'] ?? 0.0,
          'outstanding_amount': outstandingByRegion[entry.key] ?? 0.0,
          'clients_count': _assignedClientIds.length, // Simplified
          'last_update': DateTime.now().toIso8601String(),
        };
      }).toList();

      return {
        'total_commission': totalCommission,
        'total_cash_collected': totalCashCollected,
        'total_digital_collected': totalDigitalCollected,
        'cash_on_hand': cashOnHand,
        'outstanding_amounts': {
          'total': outstandingByRegion.values.fold(0.0, (sum, amount) => sum + amount),
          ...outstandingByRegion,
        },
        'regional_summaries': regionalSummaries,
      };
    } catch (e) {
      print('Error getting dashboard data: $e');
      throw Exception('Failed to load dashboard data');
    }
  }

  Future<double> _getOutstandingAmountForRegion(String region) async {
    // This would typically query invoices or account receivables
    // For now, return a mock value
    return 0.0;
  }

  // Get clients assigned to current salesperson
  Future<List<Map<String, dynamic>>> getClients() async {
    if (!isLoggedIn) throw Exception('Not logged in');

    try {
      final data = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
          'service': 'object',
          'method': 'execute_kw',
          'args': [
            database,
            _userId,
            'password',
            'res.partner',
            'search_read',
            [
              [
                ['id', 'in', _assignedClientIds],
                ['is_company', '=', true],
                ['customer_rank', '>', 0]
              ]
            ],
            {
              'fields': ['name', 'email', 'phone', 'street', 'city', 'country_id'],
              'order': 'name'
            }
          ]
        },
        'id': 1,
      };

      final response = await _makeRequest('/jsonrpc', data);
      return List<Map<String, dynamic>>.from(response['result'] ?? []);
    } catch (e) {
      print('Error getting clients: $e');
      return [];
    }
  }

  // Get products from assigned warehouses
  Future<List<Map<String, dynamic>>> getProducts() async {
    if (!isLoggedIn) throw Exception('Not logged in');

    try {
      final data = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
          'service': 'object',
          'method': 'execute_kw',
          'args': [
            database,
            _userId,
            'password',
            'product.product',
            'search_read',
            [
              [
                ['sale_ok', '=', true],
                ['active', '=', true]
              ]
            ],
            {
              'fields': ['name', 'list_price', 'standard_price', 'categ_id', 'qty_available'],
              'order': 'name'
            }
          ]
        },
        'id': 1,
      };

      final response = await _makeRequest('/jsonrpc', data);
      return List<Map<String, dynamic>>.from(response['result'] ?? []);
    } catch (e) {
      print('Error getting products: $e');
      return [];
    }
  }

  // Collection receipts management
  Future<List<Map<String, dynamic>>> getCollectionReceipts() async {
    if (!isLoggedIn) throw Exception('Not logged in');

    // Mock data for now - in real implementation, this would query custom collection receipt model
    return [
      {
        'id': 1,
        'receipt_number': 'RCP001',
        'client_id': 1,
        'client_name': 'شركة النجف التجارية',
        'amount': 500000.0,
        'payment_type': 'cash',
        'payment_method': 'cash',
        'collection_date': DateTime.now().subtract(const Duration(days: 1)).toIso8601String(),
        'region': 'النجف',
        'salesperson_id': _userId,
        'is_settled': false,
        'status': 'collected',
      },
      {
        'id': 2,
        'receipt_number': 'RCP002',
        'client_id': 2,
        'client_name': 'مؤسسة بابل للتجارة',
        'amount': 750000.0,
        'payment_type': 'digital',
        'payment_method': 'bank_transfer',
        'collection_date': DateTime.now().subtract(const Duration(days: 2)).toIso8601String(),
        'region': 'بابل',
        'salesperson_id': _userId,
        'is_settled': false,
        'status': 'collected',
      },
    ];
  }

  Future<void> createCollectionReceipt(Map<String, dynamic> receiptData) async {
    if (!isLoggedIn) throw Exception('Not logged in');

    // Mock implementation - in real app, this would create a record in Odoo
    await Future.delayed(const Duration(seconds: 1));
    print('Creating collection receipt: $receiptData');
  }

  // Money transfers management
  Future<List<Map<String, dynamic>>> getMoneyTransfers() async {
    if (!isLoggedIn) throw Exception('Not logged in');

    // Mock data for now
    return [
      {
        'id': 1,
        'transfer_number': 'TRF001',
        'amount': 1250000.0,
        'transfer_type': 'cash',
        'transfer_method': 'altayf_exchange',
        'transfer_date': DateTime.now().subtract(const Duration(days: 3)).toIso8601String(),
        'salesperson_id': _userId,
        'salesperson_name': _userName,
        'destination': 'main_treasury',
        'status': 'received',
        'received_date': DateTime.now().subtract(const Duration(days: 2)).toIso8601String(),
        'received_by': 'أحمد محمد',
      },
      {
        'id': 2,
        'transfer_number': 'TRF002',
        'amount': 800000.0,
        'transfer_type': 'digital',
        'transfer_method': 'development_bank',
        'transfer_date': DateTime.now().subtract(const Duration(days: 1)).toIso8601String(),
        'salesperson_id': _userId,
        'salesperson_name': _userName,
        'destination': 'main_treasury',
        'status': 'sent',
        'notes': 'تحويل عبر مصرف التنمية',
      },
    ];
  }

  Future<void> processComprehensiveSettlement(Map<String, dynamic> settlementData) async {
    if (!isLoggedIn) throw Exception('Not logged in');

    // Mock implementation - in real app, this would:
    // 1. Create money transfer record
    // 2. Update collection receipts status to 'settled'
    // 3. Create accounting entries
    await Future.delayed(const Duration(seconds: 2));
    print('Processing comprehensive settlement: $settlementData');
  }

  // Other existing methods...
  Future<List<Map<String, dynamic>>> getOrders() async {
    if (!isLoggedIn) throw Exception('Not logged in');

    try {
      final data = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
          'service': 'object',
          'method': 'execute_kw',
          'args': [
            database,
            _userId,
            'password',
            'sale.order',
            'search_read',
            [
              [
                ['partner_id', 'in', _assignedClientIds],
                ['state', 'in', ['draft', 'sent', 'sale']]
              ]
            ],
            {
              'fields': ['name', 'partner_id', 'amount_total', 'state', 'date_order'],
              'order': 'date_order desc'
            }
          ]
        },
        'id': 1,
      };

      final response = await _makeRequest('/jsonrpc', data);
      return List<Map<String, dynamic>>.from(response['result'] ?? []);
    } catch (e) {
      print('Error getting orders: $e');
      return [];
    }
  }

  Future<List<Map<String, dynamic>>> getInvoices() async {
    if (!isLoggedIn) throw Exception('Not logged in');

    try {
      final data = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
          'service': 'object',
          'method': 'execute_kw',
          'args': [
            database,
            _userId,
            'password',
            'account.move',
            'search_read',
            [
              [
                ['partner_id', 'in', _assignedClientIds],
                ['move_type', '=', 'out_invoice'],
                ['state', 'in', ['draft', 'posted']]
              ]
            ],
            {
              'fields': ['name', 'partner_id', 'amount_total', 'state', 'invoice_date', 'payment_state'],
              'order': 'invoice_date desc'
            }
          ]
        },
        'id': 1,
      };

      final response = await _makeRequest('/jsonrpc', data);
      return List<Map<String, dynamic>>.from(response['result'] ?? []);
    } catch (e) {
      print('Error getting invoices: $e');
      return [];
    }
  }
}