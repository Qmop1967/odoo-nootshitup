/// TSH Salesperson App Configuration
/// 
/// Update these values with your actual Odoo server details
class AppConfig {
  // Odoo Server Configuration
  // TSH Odoo Server Details
  static const String odooServerUrl = 'http://138.68.89.104:8069';
  static const String odooDatabaseName = 'odtshbrain';
  
  // Warehouse Configuration - CRITICAL ARCHITECTURE RULE
  // DO NOT MODIFY WITHOUT ARCHITECTURE TEAM APPROVAL
  static const Map<String, String> warehouseMapping = {
    'sales_representatives': 'main_wholesale_warehouse',  // مخزن الجملة
    'sales_partners': 'retail_store_warehouse',          // مخزن المتجر
    'customer_app': 'retail_store_warehouse',            // مخزن المتجر
    'web_store': 'retail_store_warehouse',               // مخزن المتجر
    'website': 'retail_store_warehouse',                 // مخزن المتجر
  };
  
  // Warehouse Details
  static const Map<String, Map<String, String>> warehouseDetails = {
    'main_wholesale_warehouse': {
      'name': 'Main Wholesale Warehouse',
      'type': 'Wholesale',
      'location': 'سريع الدورة، بغداد',
      'description': 'مخزن الجملة الرئيسي - المندوبين الميدانيين',
      'target_users': 'Sales Representatives',
    },
    'retail_store_warehouse': {
      'name': 'Retail Store Warehouse', 
      'type': 'Retail',
      'location': 'الدورة، بغداد',
      'description': 'مخزن المتجر - شركاء البيع والزبائن',
      'target_users': 'Sales Partners, Store Staff, Customers',
    },
  };
  
  // App Information
  static const String appName = 'TSH Salesperson';
  static const String appVersion = '1.0.0';
  static const String appBuildNumber = '1';

  // Default Odoo Configuration
  static const String defaultOdooUrl = 'http://138.68.89.104:8069';
  static const String defaultDatabase = 'odtshbrain';

  // API Configuration
  static const int apiTimeout = 30; // seconds
  static const int maxRetries = 3;

  // UI Configuration
  static const int itemsPerPage = 50;
  static const int dashboardRefreshInterval = 300; // seconds (5 minutes)

  // Colors
  static const int primaryColorValue = 0xFF1E88E5;
  static const int secondaryColorValue = 0xFF1565C0;

  // Feature Flags
  static const bool enableOfflineMode = true;
  static const bool enablePushNotifications = true;
  static const bool enableAnalytics = false;

  // Development/Production Settings
  static const bool isDebugMode = true; // Set to false for production
  static const bool enableLogging = true;

  // Shorebird Configuration (Disabled)
  // static const String shorebirdAppId = 'com.tsh.sales.tsh_salesperson_app';
  static const bool enableCodePush = false;

  // Cache Configuration
  static const int cacheExpirationHours = 24;
  static const int maxCacheSize = 100; // MB

  // Security
  static const int sessionTimeoutMinutes = 480; // 8 hours
  static const bool requireBiometricAuth = false;

  // Regional Settings
  static const String defaultCurrency = 'USD';
  static const String defaultCurrencySymbol = '\$';
  static const String defaultDateFormat = 'MMM dd, yyyy';
  static const String defaultTimeFormat = 'HH:mm';

  // Error Messages
  static const String networkErrorMessage = 'Network connection error. Please check your internet connection.';
  static const String authErrorMessage = 'Authentication failed. Please check your credentials.';
  static const String serverErrorMessage = 'Server error. Please try again later.';
  static const String unknownErrorMessage = 'An unexpected error occurred. Please try again.';

  /// Validates if the configuration is properly set
  static bool get isConfigured {
    return odooServerUrl.isNotEmpty &&
           odooDatabaseName.isNotEmpty &&
           odooServerUrl != 'https://demo.odoo.com' &&
           odooDatabaseName != 'demo';
  }
  
  /// Returns a user-friendly error message if configuration is incomplete
  static String get configurationError {
    if (!isConfigured) {
      return 'Please update the Odoo server configuration in lib/config/app_config.dart';
    }
    return '';
  }
  
  /// Get warehouse for specific app type
  static String getWarehouseForApp(String appType) {
    return warehouseMapping[appType] ?? 'retail_store_warehouse';
  }
  
  /// Get warehouse details
  static Map<String, String>? getWarehouseDetails(String warehouseId) {
    return warehouseDetails[warehouseId];
  }
}