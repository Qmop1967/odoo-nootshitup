# 🚀 Dual Store Publishing Setup Guide
## iOS App Store + Google Play Store

## 🎯 Overview
This guide will help you set up automatic publishing to both Apple App Store and Google Play Store simultaneously.

## 📱 Current Status
✅ **iOS builds**: Working (need code signing setup)
✅ **Android builds**: Working
✅ **Automatic triggering**: Working
✅ **App Store Connect integration**: Configured
❌ **Google Play credentials**: Need setup
❌ **iOS code signing**: Need dashboard configuration

## 🔧 Required Setup Steps

### **1. iOS App Store Setup (Almost Complete)**

#### **A. CodeMagic iOS Signing (REQUIRED)**
1. **Go to CodeMagic Dashboard** → Your App → **"Code signing identities"**
2. **Add iOS signing**:
   - **Distribution type**: `App Store`
   - **Bundle identifier**: `com.tsh.sales.tsh_salesperson_app`
   - **Team**: `38U844SAJ5`
   - **Signing method**: `Automatic`

#### **B. App Store Connect (DONE ✅)**
- ✅ API Key configured: `CQQG6Z8W5G`
- ✅ Integration: `tsh_app_store_connect`
- ✅ Team ID: `38U844SAJ5`

### **2. Google Play Store Setup (NEEDED)**

#### **A. Create Google Play Service Account**
1. **Go to Google Cloud Console**
2. **Create new project** or select existing
3. **Enable Google Play Developer API**
4. **Create Service Account**:
   - Name: `CodeMagic TSH Publisher`
   - Role: `Service Account User`
5. **Generate JSON key** and download

#### **B. Link Service Account to Google Play**
1. **Go to Google Play Console**
2. **Setup** → **API access**
3. **Link** your Google Cloud project
4. **Grant permissions** to service account:
   - **Release apps to testing tracks**
   - **Release apps to production**

#### **C. Upload Credentials to CodeMagic**
1. **Go to CodeMagic** → **Environment variables**
2. **Add to `google_play_credentials` group**:
   ```
   GCLOUD_SERVICE_ACCOUNT_CREDENTIALS = [paste JSON content]
   GOOGLE_PLAY_TRACK = internal
   ```

## 🚀 What Will Happen After Setup

### **Automatic Dual Publishing:**
1. **Push to main branch** or **create tag**
2. **CodeMagic builds**:
   - ✅ **Android APK** (for testing)
   - ✅ **Android AAB** (for Google Play)
   - ✅ **iOS IPA** (for App Store)
3. **Automatic publishing**:
   - 📱 **iOS** → **TestFlight** (internal testing)
   - 🤖 **Android** → **Google Play Internal Track**
4. **Email notifications** with download links

### **Publishing Tracks:**
- **iOS**: TestFlight → App Store (manual promotion)
- **Android**: Internal → Alpha → Beta → Production

## 📋 Environment Variables Needed

### **App Store (DONE ✅)**
```
APP_STORE_CONNECT_ISSUER_ID = c22afbce-e8dd-4bd6-8110-3db55b3d70f6
APP_STORE_CONNECT_KEY_IDENTIFIER = CQQG6Z8W5G
APP_STORE_CONNECT_PRIVATE_KEY = [your .p8 file content]
```

### **Google Play (NEEDED)**
```
GCLOUD_SERVICE_ACCOUNT_CREDENTIALS = [service account JSON]
GOOGLE_PLAY_TRACK = internal
```

## 🔍 Testing Your Setup

### **1. Manual Build Test**
1. **Click "Start new build"** in CodeMagic
2. **Select workflow**: `default-workflow`
3. **Expected results**:
   - ✅ iOS IPA uploaded to TestFlight
   - ✅ Android AAB uploaded to Google Play Internal

### **2. Automatic Build Test**
1. **Make a small change** and push to main
2. **Build should trigger automatically**
3. **Check both stores** for new builds

## 📱 Store-Specific Configuration

### **iOS App Store**
- **TestFlight**: Automatic upload ✅
- **App Store**: Manual promotion (set `submit_to_app_store: true` when ready)
- **Build processing**: 5-15 minutes after upload

### **Google Play Store**
- **Internal track**: Automatic upload (after setup)
- **Alpha/Beta**: Manual promotion in Play Console
- **Production**: Manual promotion in Play Console

## 🆘 Troubleshooting

### **iOS Issues**
- **"No valid code signing certificates"**: Set up iOS signing in CodeMagic dashboard
- **"Bundle identifier mismatch"**: Verify bundle ID matches exactly
- **"Team not found"**: Check Apple Developer team ID

### **Android Issues**
- **"Service account credentials error"**: Check JSON format and permissions
- **"Track not found"**: Verify track name (internal/alpha/beta/production)
- **"Upload failed"**: Check app signing configuration

## 🎉 Success Indicators

### **When Everything Works:**
- ✅ **Build completes** without errors
- ✅ **iOS app appears** in TestFlight
- ✅ **Android app appears** in Google Play Console
- ✅ **Email notifications** received
- ✅ **Artifacts downloadable** from CodeMagic

## 📞 Next Steps

1. **Set up iOS signing** in CodeMagic dashboard (5 minutes)
2. **Create Google Play service account** (15 minutes)
3. **Upload Google Play credentials** to CodeMagic (2 minutes)
4. **Test dual publishing** with a build
5. **Celebrate** your automated dual-store publishing! 🎉

---

**Once setup is complete, every push to main will automatically build and publish to both stores!** 🚀📱