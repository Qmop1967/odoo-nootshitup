# 📱 TSH Salesperson App - iOS App Store Deployment Guide

## 🎯 Complete Guide to Publish Your App on iOS App Store

### 📋 **Prerequisites Checklist**

#### 1. **Apple Developer Account** (Required)
- [ ] **Apple Developer Program Membership** ($99/year)
  - Sign up at: https://developer.apple.com/programs/
  - Required for App Store distribution
  - Provides access to App Store Connect

#### 2. **Development Environment** (Required)
- [ ] **macOS Computer** (Required for iOS builds)
  - Xcode only runs on macOS
  - Cannot build iOS apps on Linux/Windows
- [ ] **Xcode** (Latest version from Mac App Store)
- [ ] **iOS Device** (for testing)
- [ ] **Valid Certificates & Provisioning Profiles**

#### 3. **App Store Connect Setup**
- [ ] **App Store Connect Account** (comes with Developer Account)
- [ ] **App Bundle ID** (unique identifier)
- [ ] **App Name** (must be unique on App Store)

---

## 🚀 **Step-by-Step iOS Deployment Process**

### **Phase 1: Prepare iOS Project**

#### 1. **Configure iOS Project Settings**
```bash
# On macOS with Xcode installed:
cd /path/to/your/project
flutter create --platforms=ios .
```

#### 2. **Update iOS Configuration Files**

**File: `ios/Runner/Info.plist`**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>$(DEVELOPMENT_LANGUAGE)</string>
    <key>CFBundleDisplayName</key>
    <string>TSH Salesperson</string>
    <key>CFBundleExecutable</key>
    <string>$(EXECUTABLE_NAME)</string>
    <key>CFBundleIdentifier</key>
    <string>com.tsh.salesperson</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>TSH Salesperson</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSRequiresIPhoneOS</key>
    <true/>
    <key>UILaunchStoryboardName</key>
    <string>LaunchScreen</string>
    <key>UIMainStoryboardFile</key>
    <string>Main</string>
    <key>UISupportedInterfaceOrientations</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
        <string>UIInterfaceOrientationLandscapeLeft</string>
        <string>UIInterfaceOrientationLandscapeRight</string>
    </array>
    <key>UISupportedInterfaceOrientations~ipad</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
        <string>UIInterfaceOrientationPortraitUpsideDown</string>
        <string>UIInterfaceOrientationLandscapeLeft</string>
        <string>UIInterfaceOrientationLandscapeRight</string>
    </array>
    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsArbitraryLoads</key>
        <true/>
    </dict>
    <key>NSInternetUsage</key>
    <string>This app requires internet access to sync with Odoo server</string>
</dict>
</plist>
```

### **Phase 2: App Store Connect Setup**

#### 1. **Create App in App Store Connect**
1. Go to https://appstoreconnect.apple.com/
2. Click "My Apps" → "+" → "New App"
3. Fill in app details:
   - **Platform**: iOS
   - **Name**: TSH Salesperson
   - **Primary Language**: English
   - **Bundle ID**: com.tsh.salesperson
   - **SKU**: TSH-SALESPERSON-001

#### 2. **App Information**
- **Category**: Business
- **Subcategory**: Productivity
- **Content Rights**: Your app does not use third-party content
- **Age Rating**: 4+ (No Objectionable Content)

#### 3. **App Privacy**
- **Data Collection**: Yes (customer data, business data)
- **Data Usage**: Business operations, analytics
- **Data Sharing**: No third-party sharing

### **Phase 3: Build and Upload**

#### 1. **Build iOS Release**
```bash
# On macOS:
flutter build ios --release

# Or build for App Store specifically:
flutter build ipa --release
```

#### 2. **Upload to App Store Connect**

**Option A: Using Xcode**
1. Open `ios/Runner.xcworkspace` in Xcode
2. Select "Any iOS Device" as target
3. Product → Archive
4. Upload to App Store Connect

**Option B: Using Command Line**
```bash
# Upload IPA file
xcrun altool --upload-app --type ios --file build/ios/ipa/tsh_salesperson_app.ipa --username your-apple-id@email.com --password your-app-specific-password
```

### **Phase 4: App Store Listing**

#### 1. **App Store Information**
```
App Name: TSH Salesperson
Subtitle: Odoo Sales Management
Description: 
Professional sales management app that integrates seamlessly with your Odoo system. 
Access customers, products, orders, and invoices in real-time. Record payments and 
manage your sales pipeline from anywhere.

Key Features:
• Complete Odoo integration with real-time sync
• Customer management and creation
• Product catalog with search and filtering
• Sales order tracking and management
• Invoice monitoring with payment status
• Payment recording for admin users
• Role-based access control
• Modern, intuitive interface
• Offline capability with sync

Perfect for sales teams using Odoo ERP system.

Keywords: odoo, sales, crm, erp, business, customers, orders, invoices, payments
```

#### 2. **Screenshots Required**
- **iPhone 6.7"** (iPhone 14 Pro Max): 1290 x 2796 pixels
- **iPhone 6.5"** (iPhone 11 Pro Max): 1242 x 2688 pixels
- **iPhone 5.5"** (iPhone 8 Plus): 1242 x 2208 pixels
- **iPad Pro 12.9"**: 2048 x 2732 pixels

#### 3. **App Icon Requirements**
- **1024x1024 pixels** (App Store)
- **PNG format, no transparency**
- **No rounded corners** (iOS adds them automatically)

### **Phase 5: Review and Release**

#### 1. **Submit for Review**
1. Complete all required fields in App Store Connect
2. Add screenshots and app icon
3. Set pricing (Free or Paid)
4. Submit for Apple Review

#### 2. **Review Process**
- **Timeline**: 24-48 hours (typically)
- **Common Rejections**: 
  - Missing privacy policy
  - Incomplete app functionality
  - Guideline violations
  - Technical issues

#### 3. **Release Options**
- **Automatic Release**: App goes live immediately after approval
- **Manual Release**: You control when app goes live
- **Scheduled Release**: Set specific date/time

---

## 🛠️ **iOS-Specific Configuration Files**

### **1. Create iOS Runner Configuration**