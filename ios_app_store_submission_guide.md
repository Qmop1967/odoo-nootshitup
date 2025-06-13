# 🍎 TSH Salesperson - Direct Apple App Store Submission Guide

## 📋 **Prerequisites Checklist**

### **1. Apple Developer Account**
- [ ] Active Apple Developer Program membership ($99/year)
- [ ] Access to [Apple Developer Portal](https://developer.apple.com)
- [ ] Access to [App Store Connect](https://appstoreconnect.apple.com)

### **2. Development Environment**
- [ ] macOS computer (required for iOS builds)
- [ ] Xcode 15.0+ installed
- [ ] Flutter SDK properly configured
- [ ] iOS Simulator or physical iOS device for testing

### **3. App Information**
- **App Name**: TSH Salesperson
- **Bundle ID**: `com.tsh.sales.tshSalespersonApp`
- **Version**: 2.0.0 (Build 2)
- **Company**: Spider Hand Technical Company (شركة يد العنكبوت التقنية)

## 🔧 **Step 1: Configure iOS Project**

### **Update Bundle Identifier (if needed)**
1. Open `ios/Runner.xcworkspace` in Xcode
2. Select Runner project → Runner target
3. Go to "Signing & Capabilities" tab
4. Verify Bundle Identifier: `com.tsh.sales.tshSalespersonApp`

### **Configure App Icons**
1. Prepare app icons in required sizes:
   - 1024x1024 (App Store)
   - 180x180 (iPhone 6 Plus, 6s Plus, 7 Plus, 8 Plus, X, XS, XS Max, 11 Pro Max)
   - 120x120 (iPhone 6, 6s, 7, 8, X, XS, XS Max, 11, 11 Pro, 12 mini, 12, 12 Pro, 12 Pro Max)
   - 87x87 (iPhone 6 Plus, 6s Plus, 7 Plus, 8 Plus)
   - 80x80 (iPhone 6, 6s, 7, 8, X, XS, XS Max, 11, 11 Pro, 12 mini, 12, 12 Pro, 12 Pro Max)
   - 58x58 (iPhone 6, 6s, 7, 8, X, XS, XS Max, 11, 11 Pro, 12 mini, 12, 12 Pro, 12 Pro Max)
   - 40x40 (iPhone 6, 6s, 7, 8, X, XS, XS Max, 11, 11 Pro, 12 mini, 12, 12 Pro, 12 Pro Max)
   - 29x29 (iPhone 6, 6s, 7, 8, X, XS, XS Max, 11, 11 Pro, 12 mini, 12, 12 Pro, 12 Pro Max)
   - 20x20 (iPhone 6, 6s, 7, 8, X, XS, XS Max, 11, 11 Pro, 12 mini, 12, 12 Pro, 12 Pro Max)

2. Add icons to `ios/Runner/Assets.xcassets/AppIcon.appiconset/`

## 🔐 **Step 2: Code Signing & Certificates**

### **Create Certificates in Apple Developer Portal**
1. Go to [Apple Developer Portal](https://developer.apple.com/account)
2. Navigate to "Certificates, Identifiers & Profiles"
3. Create/verify these certificates:
   - **iOS Distribution Certificate** (for App Store)
   - **iOS Development Certificate** (for testing)

### **Create App ID**
1. In Developer Portal → Identifiers
2. Create App ID with Bundle ID: `com.tsh.sales.tshSalespersonApp`
3. Enable required capabilities (if any)

### **Create Provisioning Profiles**
1. **Development Profile**: For testing on devices
2. **Distribution Profile**: For App Store submission

### **Configure Xcode Signing**
1. Open `ios/Runner.xcworkspace` in Xcode
2. Select Runner project → Runner target
3. Go to "Signing & Capabilities"
4. Select your Apple Developer Team
5. Choose "Automatically manage signing" or configure manually

## 📱 **Step 3: Build for App Store**

### **Build Archive**
```bash
# Clean previous builds
flutter clean

# Get dependencies
flutter pub get

# Build iOS archive for App Store
flutter build ios --release --no-codesign

# Open Xcode workspace
open ios/Runner.xcworkspace
```

### **Create Archive in Xcode**
1. In Xcode, select "Any iOS Device" as destination
2. Go to Product → Archive
3. Wait for archive to complete
4. Xcode Organizer will open automatically

### **Upload to App Store Connect**
1. In Xcode Organizer, select your archive
2. Click "Distribute App"
3. Choose "App Store Connect"
4. Select "Upload"
5. Choose your distribution certificate and provisioning profile
6. Click "Upload"

## 🏪 **Step 4: App Store Connect Configuration**

### **Create App in App Store Connect**
1. Go to [App Store Connect](https://appstoreconnect.apple.com)
2. Click "My Apps" → "+" → "New App"
3. Fill in app information:
   - **Platform**: iOS
   - **Name**: TSH Salesperson
   - **Primary Language**: English (or Arabic)
   - **Bundle ID**: com.tsh.sales.tshSalespersonApp
   - **SKU**: tsh-salesperson-app (unique identifier)

### **App Information**
- **Name**: TSH Salesperson
- **Subtitle**: Professional Sales Management
- **Category**: Business
- **Content Rights**: Choose appropriate option

### **Pricing and Availability**
- **Price**: Free or set price
- **Availability**: Choose countries/regions
- **App Store Distribution**: Available on App Store

### **App Privacy**
- Complete privacy questionnaire
- Add privacy policy URL if required

### **App Review Information**
- **Contact Information**: Your contact details
- **Demo Account**: If app requires login
- **Notes**: Any special instructions for reviewers

### **Version Information**
- **Version**: 2.0.0
- **What's New**: Describe new features and improvements
- **Promotional Text**: Marketing text (optional)
- **Description**: Detailed app description
- **Keywords**: Relevant search keywords
- **Support URL**: Your support website
- **Marketing URL**: Your marketing website (optional)

### **Build Selection**
1. Go to "App Store" tab in your app
2. Click "+" next to "Build"
3. Select the uploaded build
4. Add export compliance information if required

### **Screenshots and Metadata**
1. **Screenshots**: Required for different device sizes
   - iPhone 6.7" (iPhone 14 Pro Max, 13 Pro Max, 12 Pro Max)
   - iPhone 6.5" (iPhone 11 Pro Max, XS Max)
   - iPhone 5.5" (iPhone 8 Plus, 7 Plus, 6s Plus, 6 Plus)
   - iPad Pro (6th Gen) 12.9"
   - iPad Pro (2nd Gen) 12.9"

2. **App Preview Videos** (optional but recommended)

## 🚀 **Step 5: Submit for Review**

### **Final Checklist**
- [ ] All required metadata completed
- [ ] Screenshots uploaded for all required device sizes
- [ ] Build selected and configured
- [ ] App privacy information completed
- [ ] Pricing and availability set
- [ ] App review information provided

### **Submit**
1. Click "Submit for Review"
2. Answer additional questions if prompted
3. Confirm submission

## ⏱️ **Review Process**

### **Timeline**
- **Review Time**: Typically 24-48 hours
- **Status Updates**: Available in App Store Connect
- **Notifications**: Email updates on status changes

### **Possible Outcomes**
1. **Approved**: App goes live automatically or on your chosen date
2. **Rejected**: Review feedback provided, fix issues and resubmit
3. **Metadata Rejected**: Fix metadata issues without new build
4. **Developer Rejected**: You can reject and resubmit

## 🛠️ **Common Issues and Solutions**

### **Build Issues**
- **Code Signing**: Ensure certificates and profiles are valid
- **Missing Icons**: Add all required icon sizes
- **Info.plist Issues**: Verify all required keys are present

### **Review Rejections**
- **Guideline Violations**: Follow App Store Review Guidelines
- **Missing Features**: Ensure app is fully functional
- **Privacy Issues**: Complete privacy questionnaire accurately

### **Metadata Issues**
- **Screenshots**: Must show actual app content
- **Description**: Must accurately describe app functionality
- **Keywords**: Must be relevant to app functionality

## 📞 **Support Resources**

- **Apple Developer Documentation**: [developer.apple.com](https://developer.apple.com)
- **App Store Connect Help**: [help.apple.com/app-store-connect](https://help.apple.com/app-store-connect)
- **App Store Review Guidelines**: [developer.apple.com/app-store/review/guidelines](https://developer.apple.com/app-store/review/guidelines)
- **Human Interface Guidelines**: [developer.apple.com/design/human-interface-guidelines](https://developer.apple.com/design/human-interface-guidelines)

## 🎯 **Next Steps After Approval**

1. **Monitor Performance**: Use App Store Connect analytics
2. **User Feedback**: Respond to user reviews
3. **Updates**: Regular updates with new features and bug fixes
4. **Marketing**: Promote your app through various channels

---

**Note**: This process requires a macOS computer with Xcode. If you don't have access to macOS, you'll need to use a Mac or consider cloud-based solutions like MacStadium or GitHub Actions with macOS runners. 