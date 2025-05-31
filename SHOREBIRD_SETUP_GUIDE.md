# Shorebird Setup Guide for CodeMagic

## Overview
This guide helps you set up Shorebird code push functionality with CodeMagic CI/CD for the TSH Salesperson App.

## What is Shorebird?
Shorebird enables over-the-air updates for Flutter apps, allowing you to push code changes without going through app store review processes.

## Prerequisites
1. Shorebird account (sign up at https://shorebird.dev)
2. CodeMagic account with your Flutter project
3. App already published to stores (for production updates)

## Step 1: Shorebird Account Setup

### 1.1 Create Shorebird Account
```bash
# Install Shorebird CLI locally (for initial setup)
curl --proto '=https' --tlsv1.2 https://raw.githubusercontent.com/shorebirdtech/install/main/install.sh -sSf | bash

# Login to Shorebird
shorebird login

# Create your app
shorebird apps create
```

### 1.2 Get Your App ID
After creating the app, you'll get an app ID like: `com.tsh.sales.tsh_salesperson_app`

## Step 2: Project Configuration (Already Done)

✅ **shorebird.yaml** - Created with correct app ID
```yaml
app_id: com.tsh.sales.tsh_salesperson_app
flavors:
```

✅ **pubspec.yaml** - Added shorebird.yaml as asset
```yaml
flutter:
  assets:
    - shorebird.yaml
```

✅ **App Config** - Enabled Shorebird in `lib/config/app_config.dart`

## Step 3: CodeMagic Configuration

### 3.1 Environment Variables
Add these to your CodeMagic workflow:

```
SHOREBIRD_TOKEN=<your_shorebird_token>
```

To get your token:
```bash
# Run locally after login
shorebird login
cat ~/.shorebird/credentials.json
```

### 3.2 CodeMagic Build Scripts

#### For Android Release (with Shorebird):
```bash
#!/bin/bash
echo "🚀 Building Android with Shorebird..."

# Install Shorebird
curl --proto '=https' --tlsv1.2 https://raw.githubusercontent.com/shorebirdtech/install/main/install.sh -sSf | bash
export PATH="$HOME/.shorebird/bin:$PATH"

# Verify Shorebird installation
shorebird --version

# Authenticate with token
echo "$SHOREBIRD_TOKEN" > ~/.shorebird/credentials.json

# Clean and get dependencies
flutter clean
flutter pub get

# Create Shorebird release
shorebird release android --verbose

echo "✅ Shorebird Android release completed"
```

#### For iOS Release (with Shorebird):
```bash
#!/bin/bash
echo "🍎 Building iOS with Shorebird..."

# Install Shorebird
curl --proto '=https' --tlsv1.2 https://raw.githubusercontent.com/shorebirdtech/install/main/install.sh -sSf | bash
export PATH="$HOME/.shorebird/bin:$PATH"

# Verify Shorebird installation
shorebird --version

# Authenticate with token
echo "$SHOREBIRD_TOKEN" > ~/.shorebird/credentials.json

# Clean and get dependencies
flutter clean
flutter pub get

# Create Shorebird release
shorebird release ios --verbose

echo "✅ Shorebird iOS release completed"
```

### 3.3 Patch Deployment Script
For pushing updates after initial release:

```bash
#!/bin/bash
echo "🔄 Deploying Shorebird patch..."

# Install Shorebird
curl --proto '=https' --tlsv1.2 https://raw.githubusercontent.com/shorebirdtech/install/main/install.sh -sSf | bash
export PATH="$HOME/.shorebird/bin:$PATH"

# Authenticate
echo "$SHOREBIRD_TOKEN" > ~/.shorebird/credentials.json

# Deploy patch for Android
shorebird patch android --verbose

# Deploy patch for iOS
shorebird patch ios --verbose

echo "✅ Patches deployed successfully"
```

## Step 4: Workflow Setup in CodeMagic UI

### 4.1 Initial Release Workflow
1. **Name**: "Shorebird Release"
2. **Trigger**: Manual or on tag
3. **Scripts**: Use the release scripts above
4. **Environment Variables**: Add `SHOREBIRD_TOKEN`

### 4.2 Patch Deployment Workflow
1. **Name**: "Shorebird Patch"
2. **Trigger**: On push to main branch
3. **Scripts**: Use the patch script above
4. **Environment Variables**: Add `SHOREBIRD_TOKEN`

## Step 5: Testing Shorebird Setup

### 5.1 Local Testing
```bash
# Test Shorebird commands locally
shorebird doctor
shorebird apps list
shorebird releases list
```

### 5.2 CodeMagic Testing
1. Trigger the "Shorebird Release" workflow
2. Check logs for successful release creation
3. Verify release appears in Shorebird console

## Step 6: App Integration

### 6.1 Initialize Shorebird in App
Add to your main app initialization:

```dart
// In main.dart or app initialization
import 'package:shorebird_code_push/shorebird_code_push.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Shorebird
  if (AppConfig.enableCodePush) {
    await ShorebirdCodePush.instance.initialize();
  }
  
  runApp(MyApp());
}
```

### 6.2 Check for Updates
```dart
// Check for updates periodically
Future<void> checkForUpdates() async {
  if (!AppConfig.enableCodePush) return;
  
  final isUpdateAvailable = await ShorebirdCodePush.instance.isNewPatchAvailableForDownload();
  
  if (isUpdateAvailable) {
    // Show update dialog or download automatically
    await ShorebirdCodePush.instance.downloadUpdateIfAvailable();
  }
}
```

## Step 7: Deployment Strategy

### 7.1 Initial App Store Release
1. Build and submit to App Store/Play Store using standard Flutter build
2. Once approved and live, create first Shorebird release
3. This establishes the baseline for future patches

### 7.2 Subsequent Updates
1. **Minor Updates**: Use Shorebird patches (instant deployment)
2. **Major Updates**: Use app store updates (with review)
3. **Critical Fixes**: Use Shorebird patches for immediate deployment

## Step 8: Monitoring and Rollback

### 8.1 Monitor Deployments
- Check Shorebird console for deployment status
- Monitor app crash reports after patches
- Track user adoption of patches

### 8.2 Rollback if Needed
```bash
# Rollback to previous version
shorebird patch android --rollback
shorebird patch ios --rollback
```

## Troubleshooting

### Common Issues

#### 1. "App not found" Error
- Verify app ID in `shorebird.yaml` matches Shorebird console
- Ensure you're authenticated with correct account

#### 2. "shorebird.yaml not found as asset"
- Verify `shorebird.yaml` is listed in `pubspec.yaml` assets
- Run `flutter clean && flutter pub get`

#### 3. Authentication Errors
- Check `SHOREBIRD_TOKEN` environment variable
- Verify token is valid and not expired

#### 4. Build Failures
- Ensure Flutter version compatibility
- Check Shorebird CLI version
- Verify all dependencies are compatible

## Best Practices

1. **Test Patches Thoroughly**: Always test patches before deployment
2. **Gradual Rollout**: Use Shorebird's rollout features for gradual deployment
3. **Monitor Performance**: Watch for performance impacts after patches
4. **Backup Strategy**: Keep track of working versions for rollback
5. **Documentation**: Document all patches and their purposes

## Security Considerations

1. **Secure Token Storage**: Keep Shorebird tokens secure in CodeMagic
2. **Code Signing**: Ensure patches maintain code signing integrity
3. **Review Process**: Implement review process for patch deployments
4. **Access Control**: Limit who can deploy patches

## Success Indicators

✅ Shorebird CLI installed and authenticated
✅ App created in Shorebird console
✅ CodeMagic builds complete successfully
✅ Patches deploy without errors
✅ App receives and applies updates

This setup enables you to push instant updates to your TSH Salesperson App without waiting for app store approval! 