# 📱 iOS Publishing Setup Guide for TSH Salesperson App

## 🎯 Overview

This guide will help you set up iOS publishing for your TSH Salesperson app using CodeMagic. You'll be able to automatically build and submit your app to TestFlight and the App Store.

## 📋 Prerequisites

### 1. Apple Developer Account
- **Paid Apple Developer Program membership** ($99/year)
- **Admin access** to your Apple Developer account
- **App Store Connect access**

### 2. App Registration
Your app should be registered in App Store Connect with:
- **App Name**: TSH Salesperson
- **Bundle ID**: `com.tsh.sales.tsh_salesperson_app`
- **SKU**: Any unique identifier

## 🔑 Step 1: Create App Store Connect API Key

### In App Store Connect:
1. Go to **Users and Access** → **Keys**
2. Click **Generate API Key** or **+**
3. **Name**: `CodeMagic TSH Salesperson`
4. **Access**: `App Manager` or `Developer`
5. **Download** the `.p8` file immediately (you can't download it again!)
6. **Note down**:
   - **Issuer ID** (found at the top of the Keys page)
   - **Key ID** (the ID of your newly created key)

## 🏗️ Step 2: Set Up CodeMagic Integration

### In CodeMagic Dashboard:
1. Go to **Team settings** → **Integrations**
2. Click **Add integration** → **App Store Connect**
3. **Name**: `tsh_app_store_connect`
4. **Issuer ID**: (from Step 1)
5. **Key ID**: (from Step 1)
6. **Private Key**: Upload the `.p8` file from Step 1

## 📱 Step 3: iOS Signing Setup

### Option A: Automatic Signing (Recommended)
1. In CodeMagic, go to your app settings
2. **iOS code signing** → **Automatic**
3. Select your **Team**
4. **Bundle identifier**: `com.tsh.sales.tsh_salesperson_app`

### Option B: Manual Signing
If you prefer manual signing:
1. **Distribution Certificate**: Upload your Apple Distribution certificate
2. **Provisioning Profile**: Upload App Store provisioning profile
3. **Update** `ios/ExportOptions.plist` with your Team ID

## 🔧 Step 4: Configure Environment Variables

### In CodeMagic, add these to your `app_store_credentials` group:
```
APP_STORE_CONNECT_ISSUER_ID = your-issuer-id
APP_STORE_CONNECT_KEY_IDENTIFIER = your-key-id
APP_STORE_CONNECT_PRIVATE_KEY = your-private-key-content
```

## 📝 Step 5: Update Configuration Files

### Update `ios/ExportOptions.plist`:
Replace `YOUR_TEAM_ID` with your actual Apple Developer Team ID:
```xml
<key>teamID</key>
<string>YOUR_ACTUAL_TEAM_ID</string>
```

### Update Bundle Identifier (if different):
If you want a different bundle ID, update:
1. `ios/Runner.xcodeproj/project.pbxproj`
2. `ios/ExportOptions.plist`
3. `codemagic.yaml` environment variables

## 🚀 Step 6: Test the Setup

### Trigger a Build:
1. **Push to main branch** or **create a tag** (e.g., `v1.0.1`)
2. **Monitor the build** in CodeMagic dashboard
3. **Check for iOS build success**

### Expected Results:
- ✅ iOS IPA file generated
- ✅ Uploaded to TestFlight automatically
- ✅ Available for internal testing

## 📊 Step 7: App Store Submission

### For TestFlight (Internal Testing):
- Builds are automatically submitted to TestFlight
- Add internal testers in App Store Connect
- Testers receive email invitations

### For App Store (Public Release):
1. **Update** `codemagic.yaml`:
   ```yaml
   submit_to_app_store: true
   ```
2. **Prepare** App Store listing (screenshots, description, etc.)
3. **Submit** for review through CodeMagic or manually

## 🔍 Information You Need to Provide

Please provide the following information:

### 1. **Apple Developer Team ID**
- Found in: Apple Developer Account → Membership
- Format: `ABC123DEF4` (10 characters)

### 2. **App Store Connect API Key Details**
- **Issuer ID**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- **Key ID**: `ABCD123456`
- **Private Key**: Content of the `.p8` file

### 3. **Bundle Identifier Preference**
- Current: `com.tsh.sales.tsh_salesperson_app`
- Or specify your preferred bundle ID

### 4. **App Store Connect App Information**
- **App Name**: TSH Salesperson (or your preferred name)
- **Primary Language**: English (or your preference)
- **Category**: Business

## 🚨 Troubleshooting

### Common Issues:

**"No signing certificate found"**
- Ensure you have a valid Apple Distribution certificate
- Check that the certificate is not expired

**"Provisioning profile doesn't match"**
- Verify bundle identifier matches exactly
- Ensure provisioning profile includes your device/distribution

**"App Store Connect authentication failed"**
- Double-check API key details
- Ensure the key has proper permissions

## 📞 Next Steps

Once you provide the required information:
1. I'll update the configuration files with your details
2. We'll test the iOS build process
3. Set up automatic TestFlight distribution
4. Prepare for App Store submission

## 📋 Checklist

- [ ] Apple Developer Account active
- [ ] App registered in App Store Connect
- [ ] API Key created and downloaded
- [ ] Team ID identified
- [ ] CodeMagic integration configured
- [ ] Environment variables set
- [ ] Configuration files updated
- [ ] Test build successful
- [ ] TestFlight submission working

---

**Ready to proceed?** Please provide the Apple Developer information listed above, and I'll configure everything for you! 