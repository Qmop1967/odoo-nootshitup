/// TSH Salesperson App - About Page
/// Spider Hand Technical Company (شركة يد العنكبوت التقنية)
/// 
/// TSH Unified Architecture System - Mobile Ecosystem v2.0.0
/// Author: TSH Technical Team | Date: 2025-06-04

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../config/app_config.dart';
import '../config/architecture_info.dart';

class AboutPage extends StatelessWidget {
  const AboutPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('حول التطبيق'),
        backgroundColor: const Color(0xFF1E88E5),
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildAppInfoCard(context),
            const SizedBox(height: 16),
            _buildCompanyInfoCard(context),
            const SizedBox(height: 16),
            _buildArchitectureInfoCard(context),
            const SizedBox(height: 16),
            _buildSystemFeaturesCard(context),
            const SizedBox(height: 16),
            _buildContactInfoCard(context),
            const SizedBox(height: 16),
            _buildVersionHistoryCard(context),
            const SizedBox(height: 16),
            _buildLegalInfoCard(context),
          ],
        ),
      ),
    );
  }

  Widget _buildAppInfoCard(BuildContext context) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.phone_android, color: Color(0xFF1E88E5)),
                const SizedBox(width: 8),
                Text(
                  'معلومات التطبيق',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: const Color(0xFF1E88E5),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _buildInfoRow('اسم التطبيق', AppConfig.appName),
            _buildInfoRow('الاسم المعروض', AppConfig.appDisplayName),
            _buildInfoRow('الإصدار', 'v${AppConfig.appVersion}'),
            _buildInfoRow('رقم البناء', AppConfig.appBuildNumber),
            _buildInfoRow('الوصف', AppConfig.appDescription),
            _buildInfoRow('الشعار', AppConfig.appTagline),
          ],
        ),
      ),
    );
  }

  Widget _buildCompanyInfoCard(BuildContext context) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.business, color: Color(0xFF1E88E5)),
                const SizedBox(width: 8),
                Text(
                  'معلومات الشركة',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: const Color(0xFF1E88E5),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _buildInfoRow('اسم الشركة', AppConfig.companyName),
            _buildInfoRow('الاسم العربي', AppConfig.companyNameArabic),
            _buildInfoRow('الاسم المختصر', ArchitectureInfo.companyShortName),
            _buildInfoRow('النطاق', ArchitectureInfo.companyDomain),
            _buildInfoRow('الفريق التقني', AppConfig.authorTeam),
          ],
        ),
      ),
    );
  }

  Widget _buildArchitectureInfoCard(BuildContext context) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.architecture, color: Color(0xFF1E88E5)),
                const SizedBox(width: 8),
                Text(
                  'معلومات المعمارية',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: const Color(0xFF1E88E5),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _buildInfoRow('اسم النظام', AppConfig.systemName),
            _buildInfoRow('الاسم العربي', ArchitectureInfo.systemNameArabic),
            _buildInfoRow('إصدار المعمارية', AppConfig.architectureVersion),
            _buildInfoRow('إصدار النظام البيئي', ArchitectureInfo.mobileEcosystemVersion),
            _buildInfoRow('تاريخ الإصدار', AppConfig.releaseDate),
            const SizedBox(height: 12),
            Text(
              'مكونات النظام (${ArchitectureInfo.systemComponents.length}):',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            ...ArchitectureInfo.systemComponents.map((component) => 
              Padding(
                padding: const EdgeInsets.only(left: 16.0, bottom: 4.0),
                child: Row(
                  children: [
                    const Icon(Icons.check_circle, size: 16, color: Colors.green),
                    const SizedBox(width: 8),
                    Expanded(child: Text(component, style: const TextStyle(fontSize: 12))),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSystemFeaturesCard(BuildContext context) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.star, color: Color(0xFF1E88E5)),
                const SizedBox(width: 8),
                Text(
                  'مميزات النظام',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: const Color(0xFF1E88E5),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ...ArchitectureInfo.systemFeatures.map((feature) => 
              Padding(
                padding: const EdgeInsets.only(bottom: 8.0),
                child: Row(
                  children: [
                    const Icon(Icons.star_border, size: 16, color: Color(0xFF1E88E5)),
                    const SizedBox(width: 8),
                    Expanded(child: Text(feature)),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildContactInfoCard(BuildContext context) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.contact_support, color: Color(0xFF1E88E5)),
                const SizedBox(width: 8),
                Text(
                  'معلومات الاتصال',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: const Color(0xFF1E88E5),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _buildInfoRow('البريد الإلكتروني', ArchitectureInfo.contactInfo['support_email']!),
            _buildInfoRow('الفريق التقني', ArchitectureInfo.contactInfo['technical_team']!),
            _buildInfoRow('فريق المعمارية', ArchitectureInfo.contactInfo['architecture_team']!),
            _buildInfoRow('ساعات الدعم', ArchitectureInfo.contactInfo['support_hours']!),
            _buildInfoRow('التوثيق', ArchitectureInfo.contactInfo['documentation_url']!),
          ],
        ),
      ),
    );
  }

  Widget _buildVersionHistoryCard(BuildContext context) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.history, color: Color(0xFF1E88E5)),
                const SizedBox(width: 8),
                Text(
                  'تاريخ الإصدارات',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: const Color(0xFF1E88E5),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ...ArchitectureInfo.versionHistory.map((version) => 
              Card(
                margin: const EdgeInsets.only(bottom: 8.0),
                color: Colors.grey[50],
                child: Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'الإصدار ${version['version']}',
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          Text(
                            version['date']!,
                            style: TextStyle(color: Colors.grey[600], fontSize: 12),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        version['description']!,
                        style: const TextStyle(fontWeight: FontWeight.w500),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        version['changes']!,
                        style: TextStyle(color: Colors.grey[700], fontSize: 12),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLegalInfoCard(BuildContext context) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.gavel, color: Color(0xFF1E88E5)),
                const SizedBox(width: 8),
                Text(
                  'المعلومات القانونية',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: const Color(0xFF1E88E5),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _buildInfoRow('الترخيص', ArchitectureInfo.legalInfo['license']!),
            _buildInfoRow('حقوق الطبع والنشر', ArchitectureInfo.legalInfo['copyright']!),
            _buildInfoRow('سياسة الخصوصية', ArchitectureInfo.legalInfo['privacy_policy']!),
            _buildInfoRow('شروط الخدمة', ArchitectureInfo.legalInfo['terms_of_service']!),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          Expanded(
            child: GestureDetector(
              onTap: () {
                Clipboard.setData(ClipboardData(text: value));
                // Note: ScaffoldMessenger context might not be available here
              },
              child: Text(
                value,
                style: TextStyle(color: Colors.grey[700]),
              ),
            ),
          ),
        ],
      ),
    );
  }
}