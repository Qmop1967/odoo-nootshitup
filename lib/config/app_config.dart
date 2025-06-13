/// TSH Salesperson App Configuration
/// 
/// Spider Hand Technical Company (شركة يد العنكبوت التقنية)
/// TSH Unified Architecture System - Mobile Ecosystem
/// 
/// Author: TSH Technical Team
/// Date: 2025-06-04
/// Architecture Version: 2.0.0
/// 
/// Update these values with your actual Odoo server details

import 'architecture_info.dart';

class AppConfig {
  // Odoo Server Configuration
  // TSH Odoo Server Details
  // Direct connection to Odoo server
  static const String odooServerUrl = 'http://138.68.89.104:8069';
  static const String odooDatabaseName = 'nootshitup';

  // Web-specific configuration for CORS proxy
  static const String corsProxyUrl = 'http://138.68.89.104:3000';
  static const String webOdooProxyUrl = 'http://138.68.89.104:3000/api/odoo';
  
  // Platform-specific URL getter
  static String get effectiveOdooUrl {
    // Check if running on web platform and use CORS proxy
    try {
      // Always use CORS proxy for web to avoid CORS issues
      // Check if we're in a web browser context
      if (Uri.base.scheme == 'http' || Uri.base.scheme == 'https') {
        print('🌐 Using CORS proxy URL: $webOdooProxyUrl');
        return webOdooProxyUrl;
      }
    } catch (e) {
      print('⚠️ Could not determine platform, using CORS proxy: $e');
      // If we can't determine the platform, assume web and use CORS proxy
      return webOdooProxyUrl;
    }
    print('📱 Using direct Odoo URL: $odooServerUrl');
    return odooServerUrl;
  }

  // Warehouse Configuration - CRITICAL ARCHITECTURE RULE
  // DO NOT MODIFY WITHOUT ARCHITECTURE TEAM APPROVAL
  static const Map<String, String> warehouseMapping = {
    'sales_representatives': 'main_wholesale_warehouse', // مخزن الجملة
    'sales_partners': 'retail_store_warehouse', // مخزن المتجر
    'customer_app': 'retail_store_warehouse', // مخزن المتجر
    'web_store': 'retail_store_warehouse', // مخزن المتجر
    'website': 'retail_store_warehouse', // مخزن المتجر
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

  // Company Information (from Architecture System)
  static String get companyName => ArchitectureInfo.companyName;
  static String get companyNameArabic => ArchitectureInfo.companyNameArabic;
  static String get systemName => ArchitectureInfo.systemName;
  static String get systemVersion => ArchitectureInfo.architectureVersion;
  static String get architectureVersion => ArchitectureInfo.architectureVersion;
  static String get authorTeam => ArchitectureInfo.authorTeam;
  static String get releaseDate => ArchitectureInfo.releaseDate;
  
  // App Information
  static const String appName = 'TSH Salesperson';
  static const String appDisplayName = 'TSH Salesperson - مندوب المبيعات';
  static const String appVersion = '2.0.0';
  static const String appBuildNumber = '2';
  static const String appDescription = 'TSH Salesperson App with Odoo Integration';
  static const String appTagline = 'Powered by TSH Unified Architecture System';

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
  static const String networkErrorMessage =
      'Network connection error. Please check your internet connection.';
  static const String authErrorMessage =
      'Authentication failed. Please check your credentials.';
  static const String serverErrorMessage =
      'Server error. Please try again later.';
  static const String unknownErrorMessage =
      'An unexpected error occurred. Please try again.';

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
