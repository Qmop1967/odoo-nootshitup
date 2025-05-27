# 🔗 Codemagic Webhook Integration - TSH Salesperson App

## 📋 Your Webhook Details

**Webhook URL**: `https://api.codemagic.io/hooks/68322e9bb94731dd4aa3a9b5`

This webhook will automatically trigger Codemagic builds when you push code to your repository.

## 🔧 Repository Setup

### For GitHub Repository

1. **Go to your GitHub repository**
2. **Navigate to**: Settings → Webhooks
3. **Click**: "Add webhook"
4. **Configure**:
   ```
   Payload URL: https://api.codemagic.io/hooks/68322e9bb94731dd4aa3a9b5
   Content type: application/json
   Secret: (leave empty or use your Codemagic secret)
   ```
5. **Select events**:
   - ✅ Push events
   - ✅ Pull request events
   - ✅ Create events (for tags)
6. **Click**: "Add webhook"

### For GitLab Repository

1. **Go to your GitLab repository**
2. **Navigate to**: Settings → Webhooks
3. **Add webhook**:
   ```
   URL: https://api.codemagic.io/hooks/68322e9bb94731dd4aa3a9b5
   Trigger: Push events, Tag push events, Merge request events
   ```

### For Bitbucket Repository

1. **Go to your Bitbucket repository**
2. **Navigate to**: Repository settings → Webhooks
3. **Add webhook**:
   ```
   Title: Codemagic Build Trigger
   URL: https://api.codemagic.io/hooks/68322e9bb94731dd4aa3a9b5
   Triggers: Repository push, Pull request created/updated
   ```

## 🚀 Build Triggers

Based on your `codemagic.yaml` configuration, this webhook will trigger:

### Development Builds
- **Trigger**: Push to `develop` or `feature/*` branches
- **Output**: Debug APK/IPA, test reports
- **Notification**: Email to `kha89ahm@gmail.com`

### Production Builds
- **Trigger**: Push to `main` branch or version tags (`v*`)
- **Output**: Release APK/AAB/IPA, automatic store submission
- **Notification**: Email to `kha89ahm@gmail.com`

### Hotfix Builds
- **Trigger**: Push to `hotfix/*` branches
- **Output**: Emergency release builds
- **Notification**: Email to `kha89ahm@gmail.com`

### Testing Builds
- **Trigger**: Pull requests to any branch
- **Output**: Test results, code analysis
- **Notification**: PR comments with build status

## 🧪 Testing Your Webhook

### Test Development Build
```bash
# Create and push to develop branch
git checkout -b develop
git push origin develop
```

### Test Production Build
```bash
# Push to main branch
git checkout main
git push origin main

# Or create a version tag
git tag v1.0.0
git push origin v1.0.0
```

### Test Feature Build
```bash
# Create and push feature branch
git checkout -b feature/new-feature
git push origin feature/new-feature
```

## 📊 Expected Workflow

1. **Code Push** → Webhook triggers → **Codemagic Build**
2. **Build Process**:
   - ✅ Environment setup (Flutter 3.24.5)
   - ✅ Dependencies installation
   - ✅ Code analysis and tests
   - ✅ Android/iOS build with signing
   - ✅ Store submission (production builds)
   - ✅ Email notification

## 🔍 Monitoring Builds

### Codemagic Dashboard
- **URL**: https://codemagic.io/apps
- **Monitor**: Build status, logs, artifacts
- **Download**: APK/AAB/IPA files

### Email Notifications
All build results will be sent to: `kha89ahm@gmail.com`
- ✅ Build success with download links
- ❌ Build failures with error details
- 📱 Store submission status

## 🚨 Troubleshooting

### Webhook Not Triggering
1. **Check webhook URL** is correctly configured
2. **Verify repository permissions** for Codemagic
3. **Check webhook delivery** in repository settings
4. **Ensure branch names match** your workflow triggers

### Build Failures
1. **Check Codemagic logs** for specific errors
2. **Verify keystore configuration** is uploaded correctly
3. **Ensure environment variables** are set properly
4. **Check Flutter version** compatibility

### Common Issues
```bash
# If webhook shows delivery failures
# Check the webhook URL is exactly:
https://api.codemagic.io/hooks/68322e9bb94731dd4aa3a9b5

# If builds don't trigger on specific branches
# Verify your codemagic.yaml workflow triggers match
```

## 📋 Webhook Verification

### Test Webhook Delivery
1. **Make a small change** to your repository
2. **Push to develop branch**
3. **Check webhook delivery** in repository settings
4. **Monitor Codemagic dashboard** for build start
5. **Verify email notification** is received

### Expected Response
- **HTTP 200**: Webhook received successfully
- **Build triggered**: Visible in Codemagic dashboard
- **Email sent**: Build status notification

## 🎯 Next Steps

1. **Configure webhook** in your repository settings
2. **Test with develop branch** push
3. **Verify build triggers** correctly
4. **Check email notifications** work
5. **Test production deployment** with main branch

## 📞 Support

- **Webhook ID**: `68322e9bb94731dd4aa3a9b5`
- **Email**: `kha89ahm@gmail.com`
- **Documentation**: This file and `CODEMAGIC_ENV_SETUP.md`

---

🔗 **Your webhook is ready!** Configure it in your repository to enable automatic CI/CD builds for your TSH Salesperson App.