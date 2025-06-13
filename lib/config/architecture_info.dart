/// TSH Unified Architecture System - Information Constants
/// 
/// Spider Hand Technical Company (شركة يد العنكبوت التقنية)
/// TSH Unified Architecture System - Mobile Ecosystem v2.0.0
/// 
/// Author: TSH Technical Team
/// Date: 2025-06-04
/// 
/// This file contains all architectural system information and constants
/// used throughout the application for branding and system identification.

class ArchitectureInfo {
  // System Architecture Information
  static const String systemName = 'TSH Unified Architecture System';
  static const String systemNameArabic = 'نظام المعمارية الموحد لشركة يد العنكبوت التقنية';
  static const String architectureVersion = '2.0.0';
  static const String mobileEcosystemVersion = '2.0.0';
  static const String releaseDate = '2025-06-04';
  static const String authorTeam = 'TSH Technical Team';
  
  // Company Information
  static const String companyName = 'Spider Hand Technical Company';
  static const String companyNameArabic = 'شركة يد العنكبوت التقنية';
  static const String companyShortName = 'TSH';
  static const String companyDomain = 'tsh.tech';
  
  // Architecture Components
  static const List<String> systemComponents = [
    'Enterprise Governance System',
    'Mobile Ecosystem',
    'Integration Central (Zoho-Odoo)',
    'Specialized Architectural Governance',
    'Security & Compliance',
    'Infrastructure Management',
    'Analytics & Reporting',
    'Unified Control Center',
    'Documentation & Knowledge',
  ];
  
  // Mobile Applications in Ecosystem
  static const Map<String, Map<String, String>> mobileApps = {
    'tsh_salesperson': {
      'name': 'TSH Salesperson',
      'nameArabic': 'مندوب المبيعات',
      'description': 'Sales management and customer relations',
      'api': '/api/mobile/salesperson/',
      'status': 'active',
    },
    'tsh_inventory': {
      'name': 'TSH Inventory',
      'nameArabic': 'إدارة المخزون',
      'description': 'Inventory and warehouse management',
      'api': '/api/mobile/inventory/',
      'status': 'active',
    },
    'tsh_clients': {
      'name': 'TSH Clients',
      'nameArabic': 'إدارة العملاء',
      'description': 'Customer relationship management',
      'api': '/api/mobile/clients/',
      'status': 'active',
    },
    'tsh_partner': {
      'name': 'TSH Partner',
      'nameArabic': 'إدارة الشركاء',
      'description': 'Partner and supplier management',
      'api': '/api/mobile/partner/',
      'status': 'active',
    },
    'tsh_retailer_pos': {
      'name': 'TSH Retailer POS',
      'nameArabic': 'نقاط البيع',
      'description': 'Point of sale and retail management',
      'api': '/api/mobile/pos/',
      'status': 'active',
    },
  };
  
  // System Features
  static const List<String> systemFeatures = [
    'AI-Powered Architecture Monitoring',
    'Compliance Validation',
    'Performance Analytics',
    'Unified API Gateway',
    'Real-time Integration',
    'Security Management',
    'Mobile-First Design',
    'Multilingual Support',
  ];
  
  // Server Configuration
  static const Map<String, String> serverInfo = {
    'production_server': 'http://138.68.89.104:8069',
    'database': 'nootshitup',
    'backup_database': 'odtshbrain',
    'api_version': 'v2.0',
    'cors_proxy': 'http://0.0.0.0:3000',
    'web_app': 'http://0.0.0.0:8080',
  };
  
  // Architecture Governance Rules
  static const Map<String, String> governanceRules = {
    'data_source': 'Zoho is the source of truth',
    'sync_requirement': 'Odoo must be updated to match Zoho',
    'analysis_requirement': 'Always perform analysis between source and target',
    'logging_requirement': 'Generate diff and logs for all operations',
    'duplication_rule': 'Check existing logic before writing new functions',
    'warehouse_rule': 'DO NOT MODIFY warehouse mapping without architecture team approval',
  };
  
  // Development Guidelines
  static const Map<String, String> developmentGuidelines = {
    'code_style': 'Follow Flutter/Dart best practices',
    'architecture_pattern': 'API Gateway with unified response format',
    'security_requirement': 'Apply security checks for all operations',
    'testing_requirement': 'Write tests for all new functionality',
    'documentation_requirement': 'Document all changes and additions',
    'multilingual_requirement': 'Support Arabic and English languages',
  };
  
  // Contact Information
  static const Map<String, String> contactInfo = {
    'support_email': 'kha89ahm@gmail.com',
    'technical_team': 'TSH Technical Team',
    'architecture_team': 'TSH Architecture Team',
    'support_hours': '24/7',
    'documentation_url': '/docs/',
  };
  
  // Version History
  static const List<Map<String, String>> versionHistory = [
    {
      'version': '2.0.0',
      'date': '2025-06-04',
      'description': 'Unified Architecture System Implementation',
      'changes': 'Complete system unification, new branding, enhanced features',
    },
    {
      'version': '1.0.0',
      'date': '2024-12-01',
      'description': 'Initial TSH Salesperson App Release',
      'changes': 'Basic functionality, Odoo integration, core features',
    },
  ];
  
  // Legal Information
  static const Map<String, String> legalInfo = {
    'license': 'LGPL-3.0',
    'copyright': '© 2025 Spider Hand Technical Company',
    'privacy_policy': 'Available upon request',
    'terms_of_service': 'Available upon request',
  };
  
  /// Get current app information by app key
  static Map<String, String>? getAppInfo(String appKey) {
    return mobileApps[appKey];
  }
  
  /// Get system summary
  static Map<String, dynamic> getSystemSummary() {
    return {
      'company': companyName,
      'system': systemName,
      'version': architectureVersion,
      'release_date': releaseDate,
      'apps_count': mobileApps.length,
      'components_count': systemComponents.length,
      'features_count': systemFeatures.length,
    };
  }
  
  /// Get complete system info for debugging
  static Map<String, dynamic> getCompleteSystemInfo() {
    return {
      'architecture': {
        'system_name': systemName,
        'version': architectureVersion,
        'release_date': releaseDate,
        'author': authorTeam,
      },
      'company': {
        'name': companyName,
        'name_arabic': companyNameArabic,
        'short_name': companyShortName,
        'domain': companyDomain,
      },
      'mobile_ecosystem': {
        'version': mobileEcosystemVersion,
        'apps': mobileApps,
        'total_apps': mobileApps.length,
      },
      'system_info': {
        'components': systemComponents,
        'features': systemFeatures,
        'server_info': serverInfo,
      },
      'governance': {
        'rules': governanceRules,
        'guidelines': developmentGuidelines,
      },
      'contact': contactInfo,
      'legal': legalInfo,
    };
  }
}