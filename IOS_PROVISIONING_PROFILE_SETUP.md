# iOS Provisioning Profile Setup Guide

## Issue
Build failed with: "No matching profiles found for bundle identifier 'com.tsh.sales.tsh_salesperson_app' and distribution type 'app_store'"

## Solution Steps

### Step 1: Create App ID (if not exists)
1. Go to [Apple Developer Portal](https://developer.apple.com)
2. Navigate to **Certificates, Identifiers & Profiles**
3. Click **Identifiers** → **+** (Add new)
4. Select **App IDs** → **Continue**
5. Configure:
   - **Description:** TSH Salesperson App
   - **Bundle ID:** `com.tsh.sales.tsh_salesperson_app`
   - **Capabilities:** Select any needed (Push Notifications, etc.)
6. Click **Register**

### Step 2: Create Provisioning Profile
1. In Apple Developer Portal, go to **Profiles**
2. Click **+** (Add new profile)
3. Select **App Store** under Distribution
4. Click **Continue**
5. Configure:
   - **App ID:** Select `com.tsh.sales.tsh_salesperson_app`
   - **Certificate:** Select your iOS Distribution certificate
   - **Profile Name:** `TSH Salesperson App Store Profile`
6. Click **Generate**
7. **Download** the `.mobileprovision` file

### Step 3: Upload to CodeMagic (Optional)
You can upload the provisioning profile to CodeMagic, but with automatic signing it should work without manual upload.

### Step 4: Verify Bundle ID in Flutter
Check that your Flutter app uses the correct bundle ID:
- File: `ios/Runner.xcodeproj/project.pbxproj`
- Should contain: `PRODUCT_BUNDLE_IDENTIFIER = com.tsh.sales.tsh_salesperson_app;`

## Updated CodeMagic Configuration
✅ Added `xcode_project` and `xcode_scheme` for automatic signing
✅ Using automatic signing with App Store distribution type

## Next Steps
1. Create the App ID and Provisioning Profile in Apple Developer Portal
2. Trigger another build
3. The automatic signing should now work properly

## Alternative: Manual Signing
If automatic signing continues to fail, we can switch to manual signing by uploading the provisioning profile to CodeMagic.