# 📱 Google Play Store Publishing Guide - TSH Salesperson App

## 🎯 Overview

This guide will help you publish your TSH Salesperson App to Google Play Store using automated Codemagic deployment.

## 📋 Prerequisites Checklist

### ✅ Already Complete
- [x] **App built and signed** with your keystore
- [x] **Codemagic CI/CD configured** with automated deployment
- [x] **Package name**: `com.tsh.sales.tsh_salesperson_app`
- [x] **Target SDK**: 35 (Android 14)
- [x] **Min SDK**: 21 (Android 5.0)

### 🔧 Still Needed
- [ ] **Google Play Console account** ($25 one-time fee)
- [ ] **App listing information** (descriptions, screenshots, etc.)
- [ ] **Google Cloud Service Account** for API access
- [ ] **Privacy Policy URL** (required for apps)
- [ ] **App content rating** questionnaire

## 🚀 Step-by-Step Publishing Process

### Step 1: Create Google Play Console Account

1. **Go to**: [Google Play Console](https://play.google.com/console)
2. **Sign in** with your Google account
3. **Pay the $25 registration fee** (one-time)
4. **Accept** the Developer Distribution Agreement
5. **Complete** your developer profile

### Step 2: Create Your App in Play Console

1. **Click**: "Create app"
2. **Configure**:
   ```
   App name: TSH Salesperson App
   Default language: English (United States)
   App or game: App
   Free or paid: Free (or Paid if you prefer)
   ```
3. **Declarations**:
   - [ ] User-generated content
   - [ ] Contains ads (if applicable)
   - [x] Designed for families (if appropriate)

### Step 3: Set Up Google Cloud Service Account

1. **Go to**: [Google Cloud Console](https://console.cloud.google.com)
2. **Create new project**: `tsh-salesperson-app`
3. **Enable API**: Google Play Android Developer API
4. **Create Service Account**:
   ```
   Name: tsh-app-deployment
   Role: Editor
   ```
5. **Generate JSON key** and download it
6. **Grant Play Console access**:
   - Go to Play Console → Setup → API access
   - Link your Google Cloud project
   - Grant access to your service account
   - Set permissions: **Release manager**

### Step 4: Configure Codemagic for Store Deployment

Add this to your Codemagic environment variables:

```yaml
# Google Play Store Credentials
GCLOUD_SERVICE_ACCOUNT_CREDENTIALS: |
  {
    "type": "service_account",
    "project_id": "tsh-salesperson-app",
    "private_key_id": "your-private-key-id",
    "private_key": "-----BEGIN PRIVATE KEY-----\nyour-private-key\n-----END PRIVATE KEY-----\n",
    "client_email": "tsh-app-deployment@tsh-salesperson-app.iam.gserviceaccount.com",
    "client_id": "your-client-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }

# Deployment Settings
GOOGLE_PLAY_TRACK: "internal"  # Start with internal testing
PACKAGE_NAME: "com.tsh.sales.tsh_salesperson_app"
```

### Step 5: Prepare App Store Listing

#### Required Information
```
App Name: TSH Salesperson App
Short Description: Professional sales management tool for TSH company representatives
Full Description: 
Comprehensive sales management application designed for TSH company sales representatives. 
Features include customer management, order tracking, inventory monitoring, and sales analytics. 
Streamline your sales process with real-time data synchronization and offline capabilities.

Category: Business
Content Rating: Everyone
Contact Email: kha89ahm@gmail.com
Privacy Policy: [Your privacy policy URL]
```

#### Required Assets
- **App Icon**: 512x512 PNG
- **Feature Graphic**: 1024x500 PNG
- **Screenshots**: At least 2 phone screenshots (16:9 or 9:16 ratio)
- **Optional**: Tablet screenshots, TV screenshots

### Step 6: Create Privacy Policy

Create a simple privacy policy (required for all apps):

```
Privacy Policy for TSH Salesperson App

This app collects and processes business data for sales management purposes.
Data is stored securely and used only for business operations.
No personal data is shared with third parties without consent.

Contact: kha89ahm@gmail.com
```

Host this on a public URL (GitHub Pages, your website, etc.)

## 🤖 Automated Deployment Process

Your Codemagic configuration will automatically:

### Development Builds (`develop` branch)
- Build debug APK
- Run tests and code analysis
- Email results to `kha89ahm@gmail.com`

### Production Builds (`main` branch or version tags)
- Build release AAB (Android App Bundle)
- Sign with your keystore
- Upload to Google Play Store (Internal Testing track)
- Send email notification with store link

## 🧪 Testing Strategy

### Phase 1: Internal Testing
```bash
# Create and push version tag
git tag v1.0.0
git push origin v1.0.0
```
- Codemagic builds and uploads to Internal Testing
- Test with up to 100 internal testers
- Fix any issues and iterate

### Phase 2: Closed Testing (Alpha)
- Promote from Internal Testing
- Test with limited external users
- Gather feedback and improve

### Phase 3: Open Testing (Beta)
- Open to public beta testers
- Collect reviews and ratings
- Final polishing

### Phase 4: Production Release
- Promote to Production track
- Staged rollout: 10% → 50% → 100%
- Monitor crash reports and reviews

## 📱 Quick Start Commands

### Build and Deploy to Internal Testing
```bash
# Ensure you're on main branch
git checkout main

# Create version tag
git tag v1.0.0
git push origin v1.0.0

# Codemagic will automatically:
# 1. Build release AAB
# 2. Sign with keystore
# 3. Upload to Google Play Internal Testing
# 4. Send email notification
```

### Manual Build (if needed)
```bash
# Build release AAB locally
flutter build appbundle --release

# Output will be: build/app/outputs/bundle/release/app-release.aab
```

## 🔍 Monitoring and Analytics

### Google Play Console
- **Statistics**: Downloads, ratings, reviews
- **Vitals**: Crash reports, ANRs, performance
- **User Feedback**: Reviews and ratings
- **Financial**: Revenue reports (if paid app)

### Codemagic Dashboard
- **Build History**: All deployments tracked
- **Artifacts**: Download AAB/APK files
- **Logs**: Detailed build and deployment logs
- **Notifications**: Email alerts for all builds

## 🚨 Troubleshooting

### Common Issues

#### 1. Service Account Permission Error
```
Error: The service account does not have permission
```
**Solution**: Ensure service account has "Release manager" role in Play Console

#### 2. Package Name Conflict
```
Error: Package name already exists
```
**Solution**: Your package name `com.tsh.sales.tsh_salesperson_app` should be unique

#### 3. Keystore Signing Error
```
Error: Failed to sign AAB
```
**Solution**: Verify keystore is uploaded correctly in Codemagic

#### 4. API Not Enabled
```
Error: Google Play Android Developer API not enabled
```
**Solution**: Enable the API in Google Cloud Console

## 📋 Pre-Launch Checklist

### Technical Requirements
- [ ] **Target SDK 35** (Android 14) - ✅ Already configured
- [ ] **64-bit support** - ✅ Flutter handles this
- [ ] **App Bundle format** - ✅ Codemagic builds AAB
- [ ] **Proper signing** - ✅ Your keystore configured

### Store Listing
- [ ] **App name and description** written
- [ ] **Screenshots** prepared (at least 2)
- [ ] **App icon** ready (512x512 PNG)
- [ ] **Feature graphic** created (1024x500 PNG)
- [ ] **Privacy policy** published online
- [ ] **Content rating** completed

### Legal and Compliance
- [ ] **Developer account** verified
- [ ] **Distribution agreement** accepted
- [ ] **App content** complies with policies
- [ ] **Contact information** provided

## 🎯 Next Steps

1. **Create Google Play Console account** ($25 fee)
2. **Set up Google Cloud Service Account** for API access
3. **Prepare app store listing** (descriptions, screenshots)
4. **Create and host privacy policy**
5. **Configure Codemagic credentials**
6. **Test deployment** with version tag
7. **Submit for review** and publish!

## 📞 Support

- **Email**: `kha89ahm@gmail.com`
- **Package**: `com.tsh.sales.tsh_salesperson_app`
- **Codemagic**: Automated deployment configured
- **Documentation**: This guide and Codemagic setup files

---

🚀 **Your app is ready for Google Play Store!** Follow this guide to get published with automated deployment.