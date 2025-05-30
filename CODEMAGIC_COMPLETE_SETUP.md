# CodeMagic Complete Setup Guide for TSH Salesperson App

## 🚀 Overview
This guide covers the complete setup for building, previewing, and publishing the TSH Salesperson App using CodeMagic CI/CD.

## 📋 Prerequisites Checklist

### ✅ Repository Setup
- [x] Code committed and pushed to GitHub
- [x] CodeMagic configuration file (`codemagic.yaml`) present
- [x] Flutter project structure complete

### 🔑 Required Accounts & Credentials
- [ ] CodeMagic account connected to GitHub
- [ ] Apple Developer Account (for iOS)
- [ ] Google Play Console Account (for Android)
- [ ] App Store Connect API Key
- [ ] Android Keystore file

## 🛠️ CodeMagic Setup Steps

### 1. Connect Repository to CodeMagic

1. **Login to CodeMagic**: Visit [codemagic.io](https://codemagic.io)
2. **Connect GitHub**: Link your GitHub account
3. **Add Repository**: Select your TSH Salesperson App repository
4. **Configure Webhooks**: Enable automatic build triggers

### 2. Configure Environment Variables

#### iOS Configuration
```yaml
# Add these to CodeMagic environment variables:
APP_STORE_CONNECT_ISSUER_ID: "your-issuer-id"
APP_STORE_CONNECT_KEY_IDENTIFIER: "your-key-id"  
APP_STORE_CONNECT_PRIVATE_KEY: "-----BEGIN PRIVATE KEY-----..."
CERTIFICATE_PRIVATE_KEY: "-----BEGIN PRIVATE KEY-----..."
```

#### Android Configuration
```yaml
# Android signing configuration:
CM_KEYSTORE_PASSWORD: "Zcbm.97531tsh"
CM_KEY_ALIAS: "my-key-alias"
CM_KEY_PASSWORD: "Zcbm.97531tsh"
PACKAGE_NAME: "com.tsh.sales.tsh_salesperson_app"
```

### 3. Upload Signing Certificates

#### iOS Certificates
1. **Distribution Certificate**: Upload your iOS distribution certificate
2. **Provisioning Profile**: Upload App Store provisioning profile
3. **Bundle ID**: Ensure `com.tsh.sales.tsh_salesperson_app` is registered

#### Android Keystore
1. **Upload Keystore**: Upload your `tsh_keystore.jks` file
2. **Configure Passwords**: Set keystore and key passwords
3. **Verify Alias**: Confirm key alias matches configuration

## 📱 App Preview Setup

### CodeMagic App Preview Features
1. **Live Preview**: Test builds on real devices
2. **QR Code Access**: Easy distribution to testers
3. **Build Artifacts**: Download APK/IPA files directly
4. **Test Flight Integration**: Automatic TestFlight uploads

### Enable App Preview
```yaml
# Add to codemagic.yaml for preview builds
publishing:
  app_store_connect:
    submit_to_testflight: true
  email:
    recipients:
      - kha89ahm@gmail.com
    notify:
      success: true
      failure: true
```

## 🏪 Store Publishing Configuration

### iOS App Store Setup

#### 1. App Store Connect Configuration
```bash
# Required information:
- App Name: "TSH Salesperson"
- Bundle ID: com.tsh.sales.tsh_salesperson_app
- SKU: tsh-salesperson-app
- Primary Language: English
```

#### 2. App Information
- **Category**: Business
- **Content Rating**: 4+ (No objectionable content)
- **Privacy Policy**: Required for business apps
- **Support URL**: Your support website

#### 3. Build Upload Process
```yaml
# Automatic via CodeMagic:
publishing:
  app_store_connect:
    auth: integration
    submit_to_testflight: true
    submit_to_app_store: true
    release_type: AFTER_APPROVAL
```

### Android Play Store Setup

#### 1. Google Play Console Configuration
```bash
# App details:
- App Name: "TSH Salesperson"
- Package Name: com.tsh.sales.tsh_salesperson_app
- Category: Business
- Content Rating: Everyone
```

#### 2. Release Management
```yaml
# Configure in codemagic.yaml:
google_play:
  credentials: $GCLOUD_SERVICE_ACCOUNT_CREDENTIALS
  track: internal  # Start with internal testing
  submit_as_draft: true
```

## 🔄 Build Triggers

### Automatic Triggers
- **Push to main**: Triggers production builds
- **Pull Requests**: Triggers test builds
- **Tags**: Triggers release builds

### Manual Triggers
1. **CodeMagic Dashboard**: Start builds manually
2. **GitHub Actions**: Trigger via repository dispatch
3. **API Calls**: Use CodeMagic REST API

## 📊 Build Monitoring

### Build Status Tracking
- **Email Notifications**: Configured for success/failure
- **Slack Integration**: Optional team notifications
- **GitHub Status Checks**: PR build status

### Build Artifacts
- **Android**: APK and AAB files
- **iOS**: IPA files for distribution
- **Logs**: Complete build logs for debugging
- **Test Reports**: Unit and integration test results

## 🚀 Deployment Workflow

### Development Cycle
1. **Code Changes** → Push to feature branch
2. **Pull Request** → Triggers test build
3. **Merge to Main** → Triggers production build
4. **Store Review** → Automatic submission
5. **Release** → Available in stores

### Emergency Hotfixes
1. **Create Hotfix Branch**
2. **Fast-track Build** → Skip non-critical tests
3. **Direct Store Upload** → Expedited review request

## 🔧 Troubleshooting

### Common Issues

#### Build Failures
```bash
# Check these common causes:
- Missing dependencies in pubspec.yaml
- iOS certificate expiration
- Android keystore issues
- Environment variable configuration
```

#### Store Rejection
```bash
# Common rejection reasons:
- Missing privacy policy
- Incomplete app information
- Content rating issues
- Technical compliance problems
```

### Debug Commands
```bash
# Local testing:
flutter analyze
flutter test
flutter build apk --release
flutter build ios --release

# CodeMagic logs:
# Check build logs in CodeMagic dashboard
# Review artifact generation
# Verify signing configuration
```

## 📈 Post-Launch Monitoring

### Analytics Setup
- **Firebase Analytics**: User engagement tracking
- **Crashlytics**: Crash reporting and analysis
- **Performance Monitoring**: App performance metrics

### Update Management
- **Shorebird Integration**: Over-the-air updates
- **Version Management**: Semantic versioning
- **Release Notes**: User-facing change documentation

## 🎯 Next Steps

1. **Complete CodeMagic Setup**: Configure all environment variables
2. **Test Build Process**: Trigger initial builds
3. **Store Preparation**: Complete store listings
4. **Beta Testing**: Deploy to TestFlight/Internal Testing
5. **Production Release**: Submit for store review

## 📞 Support Resources

- **CodeMagic Documentation**: [docs.codemagic.io](https://docs.codemagic.io)
- **Flutter Documentation**: [flutter.dev](https://flutter.dev)
- **App Store Guidelines**: [developer.apple.com](https://developer.apple.com)
- **Play Store Policies**: [play.google.com/console](https://play.google.com/console)

---

**Status**: ✅ Repository pushed to GitHub - CodeMagic builds should trigger automatically
**Next Action**: Configure CodeMagic environment variables and certificates 