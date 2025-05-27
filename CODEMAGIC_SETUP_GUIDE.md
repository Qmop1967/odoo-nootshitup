# 🚀 Codemagic Setup Guide - TSH Salesperson App

## 📋 Overview
This guide will help you set up automated building, testing, error detection, and store submission using Codemagic CI/CD.

## 🔧 Prerequisites

### 1. Codemagic Account Setup
1. **Sign up** at [codemagic.io](https://codemagic.io)
2. **Connect your GitHub repository**: `Qmop1967/TSH-Salesperson-App`
3. **Choose the Flutter app** template

### 2. Required Certificates & Keys
- ✅ Android signing keystore (`tsh-salesperson-key.jks`)
- ✅ iOS distribution certificate (for App Store)
- ✅ iOS provisioning profile
- ✅ Google Play Service Account JSON
- ✅ App Store Connect API key

## 🔐 Environment Variables Setup

### Step 1: Create Environment Variable Groups

#### A. `tsh_dev_vars` (Development)
```yaml
Variables:
  FLUTTER_VERSION: "3.24.5"
  APP_ENV: "development"
  API_BASE_URL: "https://dev-api.tsh-company.com"
  ENABLE_ANALYTICS: "false"
```

#### B. `tsh_prod_vars` (Production)
```yaml
Variables:
  FLUTTER_VERSION: "3.24.5"
  APP_ENV: "production"
  API_BASE_URL: "https://api.tsh-company.com"
  ENABLE_ANALYTICS: "true"
  SENTRY_DSN: "your-sentry-dsn"
```

#### C. `google_play_credentials`
```yaml
Variables:
  GCLOUD_SERVICE_ACCOUNT_CREDENTIALS: |
    {
      "type": "service_account",
      "project_id": "your-project-id",
      "private_key_id": "...",
      "private_key": "...",
      "client_email": "...",
      "client_id": "...",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token"
    }
  GOOGLE_PLAY_TRACK: "internal"  # or "alpha", "beta", "production"
```

#### D. `app_store_credentials`
```yaml
Variables:
  APP_STORE_CONNECT_ISSUER_ID: "your-issuer-id"
  APP_STORE_CONNECT_KEY_IDENTIFIER: "your-key-id"
  APP_STORE_CONNECT_PRIVATE_KEY: |
    -----BEGIN PRIVATE KEY-----
    your-private-key-content
    -----END PRIVATE KEY-----
```

### Step 2: Upload Signing Certificates

#### Android Signing (`tsh_keystore`)
1. Go to **Teams** → **Integrations** → **Code signing identities**
2. Click **Add key**
3. Upload your `tsh-salesperson-key.jks` file
4. Add the keystore details:
   ```
   Keystore password: [your-keystore-password]
   Key alias: [your-key-alias]
   Key password: [your-key-password]
   ```

#### iOS Signing
1. **Distribution Certificate**: Upload your `.p12` file
2. **Provisioning Profile**: Upload your `.mobileprovision` file
3. **Certificate Password**: Enter the password for your .p12 file

## 🔄 Workflow Configuration

### 1. Development Workflow
- **Triggers**: Push to `develop` or `feature/*` branches
- **Purpose**: Quick builds and testing
- **Outputs**: Debug APK/IPA, test reports, code analysis

### 2. Production Workflow
- **Triggers**: Push to `main` branch or version tags (`v*`)
- **Purpose**: Release builds and store submission
- **Outputs**: Release APK/AAB/IPA, automatic store submission

### 3. Hotfix Workflow
- **Triggers**: Push to `hotfix/*` branches
- **Purpose**: Emergency fixes
- **Outputs**: Quick release builds

### 4. Testing Workflow
- **Triggers**: Pull requests
- **Purpose**: Code quality checks
- **Outputs**: Test results, security audit

## 📱 Store Integration Setup

### Google Play Store Setup

#### 1. Create Service Account
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable **Google Play Android Developer API**
4. Create service account with **Editor** role
5. Download JSON key file

#### 2. Grant Play Console Access
1. Go to [Google Play Console](https://play.google.com/console)
2. **Setup** → **API access**
3. Link your Google Cloud project
4. Grant access to your service account
5. Set permissions: **Release manager** or **Admin**

### App Store Connect Setup

#### 1. Create API Key
1. Go to [App Store Connect](https://appstoreconnect.apple.com)
2. **Users and Access** → **Keys**
3. Click **Generate API Key**
4. Select **App Manager** role
5. Download the `.p8` key file

#### 2. Get Required IDs
- **Issuer ID**: Found in the Keys section
- **Key ID**: The ID of your generated key
- **Bundle ID**: `com.tsh.sales.tsh_salesperson_app`

## 🔍 Error Detection & Monitoring

### 1. Build Error Detection
The configuration automatically detects:
- ✅ Compilation errors
- ✅ Test failures
- ✅ Code analysis issues
- ✅ Security vulnerabilities
- ✅ Missing dependencies
- ✅ Signing issues

### 2. Quality Gates
Before any release, the system checks:
- ✅ All tests pass
- ✅ Code coverage meets threshold
- ✅ No critical security issues
- ✅ Proper app signing
- ✅ Version consistency

### 3. Notification Setup

#### Email Notifications
- **Success**: Build completion, successful deployment
- **Failure**: Build errors, test failures, deployment issues
- **Recipients**: `kha89ahm@gmail.com`

#### Slack Integration (Optional)
1. Create Slack app in your workspace
2. Get webhook URL
3. Add to Codemagic:
   ```yaml
   slack:
     channel: '#tsh-builds'
     webhook_url: 'your-webhook-url'
   ```

## 🚀 Deployment Strategy

### 1. Staged Rollout
- **Internal Testing**: 100% of internal testers
- **Alpha**: 10% of users
- **Beta**: 25% of users
- **Production**: 100% of users

### 2. Rollback Strategy
- **Automatic**: If crash rate > 2%
- **Manual**: Via Codemagic dashboard
- **Shorebird**: Instant code push for critical fixes

## 📊 Monitoring & Analytics

### 1. Build Metrics
- ✅ Build success rate
- ✅ Build duration
- ✅ Test coverage
- ✅ Code quality scores

### 2. App Performance
- ✅ Crash reporting (Firebase Crashlytics)
- ✅ Performance monitoring
- ✅ User analytics
- ✅ Store ratings

## 🔧 Advanced Configuration

### 1. Custom Build Scripts
Add custom scripts in `codemagic.yaml`:
```yaml
scripts:
  - name: Custom Security Scan
    script: |
      # Run custom security tools
      dart pub global activate security_scanner
      security_scanner scan lib/
```

### 2. Integration Tests
```yaml
scripts:
  - name: Integration Tests
    script: |
      flutter drive --target=test_driver/app.dart
```

### 3. Performance Testing
```yaml
scripts:
  - name: Performance Tests
    script: |
      flutter test integration_test/performance_test.dart
```

## 🚨 Troubleshooting

### Common Issues & Solutions

#### 1. Build Failures
```bash
# Check Flutter version compatibility
flutter doctor -v

# Clean and rebuild
flutter clean
flutter pub get
```

#### 2. Signing Issues
- ✅ Verify keystore password
- ✅ Check certificate expiration
- ✅ Validate bundle identifier

#### 3. Store Submission Failures
- ✅ Check app metadata
- ✅ Verify privacy policy
- ✅ Review store guidelines

### Debug Commands
```bash
# Local testing
flutter build appbundle --release --verbose

# Check dependencies
flutter pub deps

# Analyze code
flutter analyze --fatal-infos
```

## 📋 Checklist for First Setup

### Pre-Setup
- [ ] Codemagic account created
- [ ] Repository connected
- [ ] Android keystore ready
- [ ] iOS certificates ready
- [ ] Google Play service account created
- [ ] App Store Connect API key generated

### Configuration
- [ ] Environment variables configured
- [ ] Signing certificates uploaded
- [ ] Workflow triggers set
- [ ] Notification preferences set
- [ ] Store credentials added

### Testing
- [ ] Development build successful
- [ ] Production build successful
- [ ] Store submission test (draft)
- [ ] Notification system working
- [ ] Error detection working

### Go-Live
- [ ] Production deployment successful
- [ ] Store listing approved
- [ ] Monitoring active
- [ ] Team trained on process

## 🎯 Next Steps

1. **Complete the setup** using this guide
2. **Test with a development build** first
3. **Verify store integration** with draft submissions
4. **Train your team** on the new process
5. **Monitor and optimize** based on results

## 📞 Support

- **Codemagic Docs**: [docs.codemagic.io](https://docs.codemagic.io)
- **Flutter Docs**: [flutter.dev](https://flutter.dev)
- **Support Email**: `kha89ahm@gmail.com`

---

🚀 **Ready to automate your app deployment!** Follow this guide step by step for a smooth setup. 