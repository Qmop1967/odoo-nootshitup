class AppConfig {
  // App Information
  static const String appName = 'TSH Salesperson';
  static const String appVersion = '1.0.0';
  static const String appBuildNumber = '1';

  // Default Odoo Configuration
  static const String defaultOdooUrl = 'https://demo.odoo.com';
  static const String defaultDatabase = 'demo';

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

  // Shorebird Configuration
  static const String shorebirdAppId = 'tsh-salesperson-app';
  static const bool enableCodePush = true;

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
}