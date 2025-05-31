import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/client.dart';
import '../models/product.dart';
import '../models/sale_order.dart';
import '../models/invoice.dart';
import '../models/payment.dart';

class OdooService {
  static final OdooService _instance = OdooService._internal();
  factory OdooService() => _instance;
  OdooService._internal();

  String? _sessionId;
  String? _baseUrl;
  String? _database;
  int? _userId;
  String? _userEmail;
  bool _isAdmin = false;
  Map<String, dynamic>? _userInfo;
  final Map<String, String> _headers = {'Content-Type': 'application/json'};

  // Getters for session status
  bool get isAuthenticated => _sessionId != null && _baseUrl != null;
  String? get sessionId => _sessionId;
  String? get baseUrl => _baseUrl;
  int? get userId => _userId;
  String? get userEmail => _userEmail;
  bool get isAdmin => _isAdmin;
  Map<String, dynamic>? get userInfo => _userInfo;

  // Initialize with base URL
  void initialize(String baseUrl) {
    _baseUrl = baseUrl;
  }

  Future<void> saveSession() async {
    if (_sessionId != null && _baseUrl != null && _database != null) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('session_id', _sessionId!);
      await prefs.setString('base_url', _baseUrl!);
      await prefs.setString('database', _database!);
      if (_userId != null) {
        await prefs.setInt('user_id', _userId!);
      }
      if (_userEmail != null) {
        await prefs.setString('user_email', _userEmail!);
      }
      await prefs.setBool('is_admin', _isAdmin);
      if (_userInfo != null) {
        await prefs.setString('user_info', jsonEncode(_userInfo!));
      }
    }
  }

  Future<void> loadSession() async {
    final prefs = await SharedPreferences.getInstance();
    _sessionId = prefs.getString('session_id');
    _baseUrl = prefs.getString('base_url');
    _database = prefs.getString('database');
    _userId = prefs.getInt('user_id');
    _userEmail = prefs.getString('user_email');
    _isAdmin = prefs.getBool('is_admin') ?? false;
    
    final userInfoString = prefs.getString('user_info');
    if (userInfoString != null) {
      try {
        _userInfo = jsonDecode(userInfoString);
      } catch (e) {
        print('Error loading user info: $e');
      }
    }
    
    if (_sessionId != null) {
      _headers['Cookie'] = 'session_id=$_sessionId';
    }
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('session_id');
    await prefs.remove('base_url');
    await prefs.remove('database');
    await prefs.remove('user_id');
    await prefs.remove('user_email');
    await prefs.remove('is_admin');
    await prefs.remove('user_info');
    
    _sessionId = null;
    _baseUrl = null;
    _database = null;
    _userId = null;
    _userEmail = null;
    _isAdmin = false;
    _userInfo = null;
    _headers.remove('Cookie');
  }

  Future<bool> login(String baseUrl, String database, String username, String password) async {
    _baseUrl = baseUrl;
    _database = database;
    
    final url = Uri.parse('$baseUrl/web/session/authenticate');
    
    try {
      final response = await http.post(
        url,
        headers: _headers,
        body: jsonEncode({
          'params': {
            'db': database,
            'login': username,
            'password': password,
          }
        }),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['result'] != null && data['result']['uid'] != null) {
          _userId = data['result']['uid'];
          _userEmail = username;
          
          // Extract session_id from cookies
          final cookies = response.headers['set-cookie'];
          if (cookies != null) {
            final sessionMatch = RegExp(r'session_id=([^;]+);').firstMatch(cookies);
            if (sessionMatch != null) {
              _sessionId = sessionMatch.group(1);
              _headers['Cookie'] = 'session_id=$_sessionId';
              
              // Get user information and check admin privileges
              await _loadUserInfo();
              
              await saveSession();
              return true;
            }
          }
        }
      }
    } catch (e) {
      print('Login error: $e');
    }
    
    return false;
  }

  Future<void> _loadUserInfo() async {
    try {
      // Get current user information
      final userResult = await searchRead(
        'res.users',
        domain: [['id', '=', _userId]],
        fields: ['name', 'email', 'login', 'groups_id', 'partner_id'],
        limit: 1,
      );
      
      if (userResult.isNotEmpty) {
        _userInfo = userResult[0];
        
        // Check if user is admin by checking groups
        final groupIds = _userInfo?['groups_id'] ?? [];
        
        // Check for admin groups (Administration/Settings or Administration/Access Rights)
        final adminGroups = await searchRead(
          'res.groups',
          domain: [['id', 'in', groupIds], ['category_id.name', '=', 'Administration']],
          fields: ['name', 'category_id'],
        );
        
        _isAdmin = adminGroups.isNotEmpty;
        
        // Also check if user has Settings access
        if (!_isAdmin) {
          final settingsGroups = await searchRead(
            'res.groups',
            domain: [['id', 'in', groupIds], ['name', 'ilike', 'Settings']],
            fields: ['name'],
          );
          _isAdmin = settingsGroups.isNotEmpty;
        }
      }
    } catch (e) {
      print('Error loading user info: $e');
      _isAdmin = false;
    }
  }

  Future<Map<String, dynamic>> getDashboardData() async {
    if (_baseUrl == null || _sessionId == null) {
      throw Exception('Not authenticated');
    }

    try {
      // Get sales data
      final salesData = await searchRead(
        'sale.order',
        domain: [['state', 'in', ['sale', 'done']]],
        fields: ['amount_total', 'partner_id', 'date_order', 'state'],
        limit: 100,
      );

      // Get invoice data
      final invoiceData = await searchRead(
        'account.move',
        domain: [['move_type', '=', 'out_invoice'], ['state', '=', 'posted']],
        fields: ['amount_total', 'partner_id', 'invoice_date', 'payment_state'],
        limit: 100,
      );

      // Get client data with better error handling
      final clientData = await searchRead(
        'res.partner',
        domain: [['is_company', '=', true], ['customer_rank', '>', 0]],
        fields: ['name', 'country_id', 'email', 'phone'],
        limit: 100,
      );

      // Get product data with image support
      final productData = await searchRead(
        'product.product',
        domain: [['sale_ok', '=', true]],
        fields: ['name', 'list_price', 'image_1920', 'default_code', 'categ_id'],
        limit: 50,
      );

      // Calculate totals
      double totalRevenue = 0.0;
      for (var sale in salesData) {
        totalRevenue += (sale['amount_total'] ?? 0.0).toDouble();
      }

      // Calculate regional breakdown (simplified)
      Map<String, Map<String, dynamic>> regionMap = {};
      for (var sale in salesData) {
        String region = 'Unknown Region';
        if (sale['partner_id'] != null && sale['partner_id'] is List) {
          region = sale['partner_id'][1]?.toString().split(',').first ?? 'Unknown Region';
        }
        
        if (!regionMap.containsKey(region)) {
          regionMap[region] = {'name': region, 'amount': 0.0, 'orders': 0};
        }
        
        regionMap[region]!['amount'] = (regionMap[region]!['amount'] as double) + 
                                      (sale['amount_total'] ?? 0.0).toDouble();
        regionMap[region]!['orders'] = (regionMap[region]!['orders'] as int) + 1;
      }

      // Count pending invoices
      int pendingInvoices = 0;
      for (var invoice in invoiceData) {
        if (invoice['payment_state'] != 'paid') {
          pendingInvoices++;
        }
      }

      return {
        'total_amount': totalRevenue,
        'regions': regionMap.values.toList(),
        'active_orders': salesData.where((s) => s['state'] == 'sale').length,
        'pending_invoices': pendingInvoices,
        'total_clients': clientData.length,
        'products_sold': productData.length,
      };
    } catch (e) {
      print('Dashboard data error: $e');
      // Return mock data if API fails
      return {
        'total_amount': 125000.0,
        'regions': [
          {'name': 'North Region', 'amount': 45000.0, 'orders': 12},
          {'name': 'South Region', 'amount': 38000.0, 'orders': 8},
          {'name': 'East Region', 'amount': 42000.0, 'orders': 15},
        ],
        'active_orders': 25,
        'pending_invoices': 8,
        'total_clients': 45,
        'products_sold': 120,
      };
    }
  }

  Future<List<dynamic>> searchRead(String model, {List<dynamic>? domain, List<String>? fields, int? limit}) async {
    if (_baseUrl == null || _sessionId == null) {
      throw Exception('Not authenticated');
    }

    final url = Uri.parse('$_baseUrl/web/dataset/call_kw');
    
    try {
      final response = await http.post(
        url,
        headers: _headers,
        body: jsonEncode({
          'params': {
            'model': model,
            'method': 'search_read',
            'args': [domain ?? []],
            'kwargs': {
              'fields': fields ?? [],
              'limit': limit ?? 80,
            },
          }
        }),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['result'] != null) {
          return data['result'];
        }
      } else {
        print('Search read failed with status: ${response.statusCode}');
        print('Response body: ${response.body}');
      }
    } catch (e) {
      print('Search read error: $e');
    }
    
    return [];
  }

  Future<Map<String, dynamic>?> create(String model, Map<String, dynamic> values) async {
    if (_baseUrl == null || _sessionId == null) {
      throw Exception('Not authenticated');
    }

    final url = Uri.parse('$_baseUrl/web/dataset/call_kw');
    
    try {
      final response = await http.post(
        url,
        headers: _headers,
        body: jsonEncode({
          'params': {
            'model': model,
            'method': 'create',
            'args': [values],
            'kwargs': {},
          }
        }),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['result'];
      }
    } catch (e) {
      print('Create error: $e');
    }
    
    return null;
  }

  Future<bool> write(String model, List<int> ids, Map<String, dynamic> values) async {
    if (_baseUrl == null || _sessionId == null) {
      throw Exception('Not authenticated');
    }

    final url = Uri.parse('$_baseUrl/web/dataset/call_kw');
    
    try {
      final response = await http.post(
        url,
        headers: _headers,
        body: jsonEncode({
          'params': {
            'model': model,
            'method': 'write',
            'args': [ids, values],
            'kwargs': {},
          }
        }),
      );
      
      return response.statusCode == 200;
    } catch (e) {
      print('Write error: $e');
      return false;
    }
  }

  // Enhanced method to get products with images
  Future<List<Product>> getItems() async {
    try {
      final data = await searchRead(
        'product.product',
        domain: [['sale_ok', '=', true]],
        fields: ['name', 'list_price', 'default_code', 'categ_id', 'image_1920', 'image_medium', 'image_small'],
        limit: 100,
      );
      
      if (data.isEmpty) {
        print('No products found, returning mock data');
        // Return mock data if no products found
        return [
          Product.fromJson({
            'id': 1,
            'name': 'Sample Product 1',
            'list_price': 99.99,
            'default_code': 'PROD001',
            'categ_id': [1, 'Sample Category'],
            'image_1920': null,
          }),
          Product.fromJson({
            'id': 2,
            'name': 'Sample Product 2',
            'list_price': 149.99,
            'default_code': 'PROD002',
            'categ_id': [1, 'Sample Category'],
            'image_1920': null,
          }),
        ];
      }
      
      return data.map((item) => Product.fromJson(item)).toList();
    } catch (e) {
      print('Error fetching products: $e');
      // Return mock data on error
      return [
        Product.fromJson({
          'id': 1,
          'name': 'Sample Product 1',
          'list_price': 99.99,
          'default_code': 'PROD001',
          'categ_id': [1, 'Sample Category'],
          'image_1920': null,
        }),
        Product.fromJson({
          'id': 2,
          'name': 'Sample Product 2',
          'list_price': 149.99,
          'default_code': 'PROD002',
          'categ_id': [1, 'Sample Category'],
          'image_1920': null,
        }),
      ];
    }
  }

  // Enhanced method to get clients with better error handling
  Future<List<Client>> getClients() async {
    try {
      final data = await searchRead(
        'res.partner',
        domain: [['is_company', '=', true], ['customer_rank', '>', 0]],
        fields: ['name', 'email', 'phone', 'street', 'city', 'country_id', 'image_1920'],
        limit: 100,
      );
      
      if (data.isEmpty) {
        print('No clients found, returning mock data');
        // Return mock data if no clients found
        return [
          Client.fromJson({
            'id': 1,
            'name': 'Sample Client 1',
            'email': 'client1@example.com',
            'phone': '+1234567890',
            'street': '123 Main St',
            'city': 'Sample City',
            'country_id': [1, 'Sample Country'],
          }),
          Client.fromJson({
            'id': 2,
            'name': 'Sample Client 2',
            'email': 'client2@example.com',
            'phone': '+0987654321',
            'street': '456 Oak Ave',
            'city': 'Another City',
            'country_id': [1, 'Sample Country'],
          }),
        ];
      }
      
      return data.map((item) => Client.fromJson(item)).toList();
    } catch (e) {
      print('Error fetching clients: $e');
      // Return mock data on error
      return [
        Client.fromJson({
          'id': 1,
          'name': 'Sample Client 1',
          'email': 'client1@example.com',
          'phone': '+1234567890',
          'street': '123 Main St',
          'city': 'Sample City',
          'country_id': [1, 'Sample Country'],
        }),
        Client.fromJson({
          'id': 2,
          'name': 'Sample Client 2',
          'email': 'client2@example.com',
          'phone': '+0987654321',
          'street': '456 Oak Ave',
          'city': 'Another City',
          'country_id': [1, 'Sample Country'],
        }),
      ];
    }
  }

  // Helper method to get image URL for products
  String? getImageUrl(int productId, {String imageField = 'image_medium'}) {
    if (_baseUrl == null || _sessionId == null) return null;
    return '$_baseUrl/web/image/product.product/$productId/$imageField';
  }

  // Helper method to get image URL for partners/clients
  String? getPartnerImageUrl(int partnerId, {String imageField = 'image_medium'}) {
    if (_baseUrl == null || _sessionId == null) return null;
    return '$_baseUrl/web/image/res.partner/$partnerId/$imageField';
  }

  Future<List<SaleOrder>> getSaleOrders() async {
    final data = await searchRead(
      'sale.order',
      domain: [],
      fields: ['name', 'partner_id', 'date_order', 'amount_total', 'state'],
      limit: 100,
    );
    return data.map((item) => SaleOrder.fromJson(item)).toList();
  }

  Future<List<Invoice>> getInvoices() async {
    final data = await searchRead(
      'account.move',
      domain: [['move_type', '=', 'out_invoice']],
      fields: ['name', 'partner_id', 'invoice_date', 'amount_total', 'state', 'payment_state'],
      limit: 100,
    );
    return data.map((item) => Invoice.fromJson(item)).toList();
  }

  Future<List<Payment>> getPayments() async {
    final data = await searchRead(
      'account.payment',
      domain: [['payment_type', '=', 'inbound']],
      fields: ['name', 'partner_id', 'date', 'amount', 'state'],
      limit: 100,
    );
    return data.map((item) => Payment.fromJson(item)).toList();
  }

  // Create a new payment record
  Future<bool> createPayment({
    required int partnerId,
    required double amount,
    required String paymentMethod,
    String? reference,
    DateTime? date,
  }) async {
    try {
      final paymentData = {
        'partner_id': partnerId,
        'amount': amount,
        'payment_type': 'inbound',
        'partner_type': 'customer',
        'date': (date ?? DateTime.now()).toIso8601String().split('T')[0],
        'payment_method_line_id': 1, // Default payment method
        'ref': reference ?? 'Mobile Payment',
      };
      
      final result = await create('account.payment', paymentData);
      return result != null;
    } catch (e) {
      // Error creating payment: $e
      return false;
    }
  }

  // Create a new sale order
  Future<bool> createSaleOrder({
    required int partnerId,
    required List<Map<String, dynamic>> orderLines,
    String? reference,
  }) async {
    try {
      final orderData = {
        'partner_id': partnerId,
        'order_line': orderLines.map((line) => [
          0, 0, {
            'product_id': line['product_id'],
            'product_uom_qty': line['quantity'],
            'price_unit': line['price_unit'],
          }
        ]).toList(),
        'client_order_ref': reference,
      };
      
      final result = await create('sale.order', orderData);
      return result != null;
    } catch (e) {
      // Error creating sale order: $e
      return false;
    }
  }

  // Create a new customer
  Future<bool> createCustomer({
    required String name,
    String? email,
    String? phone,
    String? street,
    String? city,
    int? countryId,
  }) async {
    try {
      final customerData = {
        'name': name,
        'is_company': true,
        'customer_rank': 1,
        'email': email,
        'phone': phone,
        'street': street,
        'city': city,
        'country_id': countryId,
      };
      
      final result = await create('res.partner', customerData);
      return result != null;
    } catch (e) {
      // Error creating customer: $e
      return false;
    }
  }
}