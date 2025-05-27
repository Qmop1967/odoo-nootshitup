# 🔐 Codemagic Environment Variables Setup - TSH Salesperson App

## 📋 Overview
This guide shows you exactly how to configure the environment variables in Codemagic based on your keystore credentials.

## 🔑 Android Signing Configuration

### Step 1: Upload Android Keystore to Codemagic

1. **Go to Codemagic Dashboard**
2. **Navigate to**: Teams → Integrations → Code signing identities
3. **Click**: "Add key"
4. **Upload**: Your `tsh-salesperson-key.jks` file
5. **Configure with these exact values**:

```
Reference name: tsh_keystore
Keystore password: Zcbm.97531tsh
Key alias: my-key-alias
Key password: [your-key-password-from-CM_KEY_PASSWORD]
```

### Step 2: Environment Variable Groups

#### A. Development Variables (`tsh_dev_vars`)
```yaml
Variables:
  FLUTTER_VERSION: "3.24.5"
  APP_ENV: "development"
  API_BASE_URL: "https://dev-api.tsh-company.com"
  ENABLE_ANALYTICS: "false"
  DEBUG_MODE: "true"
```

#### B. Production Variables (`tsh_prod_vars`)
```yaml
Variables:
  FLUTTER_VERSION: "3.24.5"
  APP_ENV: "production"
  API_BASE_URL: "https://api.tsh-company.com"
  ENABLE_ANALYTICS: "true"
  DEBUG_MODE: "false"
  SENTRY_DSN: "your-sentry-dsn-here"
```

#### C. Google Play Credentials (`google_play_credentials`)
```yaml
Variables:
  GCLOUD_SERVICE_ACCOUNT_CREDENTIALS: |
    {
      "type": "service_account",
      "project_id": "your-google-cloud-project-id",
      "private_key_id": "your-private-key-id",
      "private_key": "-----BEGIN PRIVATE KEY-----\nyour-private-key-content\n-----END PRIVATE KEY-----\n",
      "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
      "client_id": "your-client-id",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
    }
  GOOGLE_PLAY_TRACK: "internal"
```

#### D. App Store Credentials (`app_store_credentials`)
```yaml
Variables:
  APP_STORE_CONNECT_ISSUER_ID: "your-issuer-id"
  APP_STORE_CONNECT_KEY_IDENTIFIER: "your-key-identifier"
  APP_STORE_CONNECT_PRIVATE_KEY: |
    -----BEGIN PRIVATE KEY-----
    your-app-store-connect-private-key-content
    -----END PRIVATE KEY-----
```

## 🔧 How Your App Uses These Variables

### Android Build Configuration
Your `android/app/build.gradle` is configured to automatically detect and use:

```gradle
signingConfigs {
    release {
        // Codemagic automatically provides these environment variables:
        // - CM_KEYSTORE (path to your uploaded keystore)
        // - CM_KEY_ALIAS (from your keystore configuration)
        // - CM_KEY_PASSWORD (from your keystore configuration)
        // - CM_KEYSTORE_PASSWORD (from your keystore configuration)
        
        def useCodemagic = System.getenv("CM_KEYSTORE") != null
        
        if (useCodemagic) {
            keyAlias = System.getenv("CM_KEY_ALIAS") ?: "my-key-alias"
            keyPassword = System.getenv("CM_KEY_PASSWORD")
            storeFile = file(System.getenv("CM_KEYSTORE"))
            storePassword = System.getenv("CM_KEYSTORE_PASSWORD")
        } else {
            // Falls back to local key.properties for development
            keyAlias = keystoreProperties['keyAlias']
            keyPassword = keystoreProperties['keyPassword']
            storeFile = file(keystoreProperties['storeFile'])
            storePassword = keystoreProperties['storePassword']
        }
    }
}
```

## 📱 Store Integration Setup

### Google Play Store Setup

#### 1. Create Service Account
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project: `tsh-salesperson-app`
3. Enable **Google Play Android Developer API**
4. Create service account with **Editor** role
5. Download JSON key file

#### 2. Grant Play Console Access
1. Go to [Google Play Console](https://play.google.com/console)
2. **Setup** → **API access**
3. Link your Google Cloud project
4. Grant access to your service account
5. Set permissions: **Release manager**

### App Store Connect Setup

#### 1. Create API Key
1. Go to [App Store Connect](https://appstoreconnect.apple.com)
2. **Users and Access** → **Keys**
3. Click **Generate API Key**
4. Name: `TSH Salesperson App CI/CD`
5. Role: **App Manager**
6. Download the `.p8` key file

#### 2. Get Required Information
- **Issuer ID**: Found in the Keys section header
- **Key ID**: The 10-character identifier of your generated key
- **Bundle ID**: `com.tsh.sales.tsh_salesperson_app`

## 🚀 Workflow Triggers

### Your Current Configuration
```yaml
# Development builds
- Push to: develop, feature/* branches
- Outputs: Debug APK/IPA, test reports

# Production builds  
- Push to: main branch
- Tag: v* (e.g., v1.0.0)
- Outputs: Release APK/AAB/IPA, store submission

# Hotfix builds
- Push to: hotfix/* branches
- Outputs: Emergency release builds

# Testing
- Pull requests: All branches
- Outputs: Test results, code analysis
```

## 🔍 Verification Steps

### 1. Test Your Configuration
```bash
# Run the setup validation script
./scripts/setup_codemagic.sh

# Run error detection
./scripts/error_detector.sh
```

### 2. Codemagic Build Test
1. **Push to develop branch** to trigger development workflow
2. **Check build logs** for signing configuration
3. **Verify artifacts** are generated correctly

### 3. Expected Build Output
```
✅ Android keystore loaded from CM_KEYSTORE
✅ Using key alias: my-key-alias
✅ Release APK signed successfully
✅ App Bundle signed successfully
✅ Ready for store submission
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Keystore Not Found
```
Error: CM_KEYSTORE environment variable not set
```
**Solution**: Ensure you've uploaded the keystore with reference name `tsh_keystore`

#### 2. Key Alias Mismatch
```
Error: Key alias 'my-key-alias' not found in keystore
```
**Solution**: Verify the key alias in your keystore matches `my-key-alias`

#### 3. Password Issues
```
Error: Keystore password incorrect
```
**Solution**: Verify the keystore password is `Zcbm.97531tsh`

### Debug Commands
```bash
# Check environment variables in Codemagic build
echo "CM_KEYSTORE: $CM_KEYSTORE"
echo "CM_KEY_ALIAS: $CM_KEY_ALIAS"
echo "CM_KEYSTORE_PASSWORD: [HIDDEN]"
echo "CM_KEY_PASSWORD: [HIDDEN]"

# Verify keystore contents
keytool -list -v -keystore $CM_KEYSTORE -storepass $CM_KEYSTORE_PASSWORD
```

## 📋 Setup Checklist

### Pre-Setup
- [ ] Android keystore file ready (`tsh-salesperson-key.jks`)
- [ ] Keystore password: `Zcbm.97531tsh`
- [ ] Key alias: `my-key-alias`
- [ ] Key password available

### Codemagic Configuration
- [ ] Keystore uploaded with reference name `tsh_keystore`
- [ ] Environment variable groups created
- [ ] Store credentials configured
- [ ] Workflow triggers set

### Testing
- [ ] Development build successful
- [ ] Production build successful
- [ ] Store submission test (draft)
- [ ] Signing verification passed

## 🎯 Next Steps

1. **Upload your keystore** to Codemagic with the exact configuration above
2. **Create environment variable groups** as specified
3. **Test with a development build** first
4. **Verify store credentials** work correctly
5. **Enable production deployment**

## 📞 Support

- **Keystore Issues**: Check password and alias configuration
- **Store Integration**: Verify API credentials and permissions
- **Build Failures**: Check build logs for specific error messages
- **Contact**: `kha89ahm@gmail.com`

---

🔐 **Your app is now configured for secure, automated deployment!** 