#!/bin/bash

# 🚀 TSH Salesperson App - Codemagic Quick Setup
# This script helps you set up Codemagic integration quickly

echo "🚀 TSH Salesperson App - Codemagic Quick Setup"
echo "==============================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo -e "${BLUE}This script will help you set up Codemagic integration for automated building and deployment.${NC}"
echo ""

# Check if codemagic.yaml exists
if [ -f "codemagic.yaml" ]; then
    echo -e "${GREEN}✅ codemagic.yaml found${NC}"
else
    echo -e "${RED}❌ codemagic.yaml not found${NC}"
    echo "Please ensure you have the codemagic.yaml file in your project root."
    exit 1
fi

echo ""
echo "📋 Setup Checklist:"
echo "==================="

echo ""
echo "1. 🔐 Required Credentials & Certificates:"
echo "   □ Android keystore (tsh-salesperson-key.jks)"
echo "   □ Android key.properties file"
echo "   □ iOS distribution certificate (.p12)"
echo "   □ iOS provisioning profile (.mobileprovision)"
echo "   □ Google Play Service Account JSON"
echo "   □ App Store Connect API key (.p8)"

echo ""
echo "2. 🌐 Codemagic Account Setup:"
echo "   □ Account created at codemagic.io"
echo "   □ GitHub repository connected"
echo "   □ Flutter app template selected"

echo ""
echo "3. 🔧 Environment Variables to Configure:"
echo ""
echo "   📱 Development Group (tsh_dev_vars):"
echo "   - FLUTTER_VERSION: 3.24.5"
echo "   - APP_ENV: development"
echo "   - API_BASE_URL: https://dev-api.tsh-company.com"
echo "   - ENABLE_ANALYTICS: false"

echo ""
echo "   🚀 Production Group (tsh_prod_vars):"
echo "   - FLUTTER_VERSION: 3.24.5"
echo "   - APP_ENV: production"
echo "   - API_BASE_URL: https://api.tsh-company.com"
echo "   - ENABLE_ANALYTICS: true"
echo "   - SENTRY_DSN: your-sentry-dsn"

echo ""
echo "   📱 Google Play Credentials (google_play_credentials):"
echo "   - GCLOUD_SERVICE_ACCOUNT_CREDENTIALS: [JSON content]"
echo "   - GOOGLE_PLAY_TRACK: internal"

echo ""
echo "   🍎 App Store Credentials (app_store_credentials):"
echo "   - APP_STORE_CONNECT_ISSUER_ID: your-issuer-id"
echo "   - APP_STORE_CONNECT_KEY_IDENTIFIER: your-key-id"
echo "   - APP_STORE_CONNECT_PRIVATE_KEY: [.p8 key content]"

echo ""
echo "4. 📱 Store Setup:"
echo ""
echo "   Google Play Console:"
echo "   □ Service account created in Google Cloud Console"
echo "   □ Google Play Android Developer API enabled"
echo "   □ Service account linked to Play Console"
echo "   □ Permissions granted (Release manager/Admin)"

echo ""
echo "   App Store Connect:"
echo "   □ API key generated"
echo "   □ App Manager role assigned"
echo "   □ Bundle ID registered: com.tsh.sales.tsh_salesperson_app"

echo ""
echo "5. 🔄 Workflow Configuration:"
echo "   □ Development workflow (feature branches)"
echo "   □ Production workflow (main branch)"
echo "   □ Hotfix workflow (hotfix branches)"
echo "   □ Testing workflow (pull requests)"

echo ""
echo "6. 📧 Notifications:"
echo "   □ Email notifications configured"
echo "   □ Slack integration (optional)"

echo ""
echo -e "${YELLOW}📖 For detailed setup instructions, see: CODEMAGIC_SETUP_GUIDE.md${NC}"

echo ""
echo "🔍 Quick Validation:"
echo "===================="

# Check if required files exist
echo ""
echo "Checking project files..."

if [ -f "android/key.properties" ]; then
    echo -e "${GREEN}✅ Android signing configuration found${NC}"
else
    echo -e "${RED}❌ Android key.properties missing${NC}"
fi

if [ -f "tsh-salesperson-key.jks" ] || [ -f "android/app/tsh-salesperson-key.jks" ]; then
    echo -e "${GREEN}✅ Android keystore found${NC}"
else
    echo -e "${RED}❌ Android keystore missing${NC}"
fi

if [ -f "pubspec.yaml" ]; then
    echo -e "${GREEN}✅ pubspec.yaml found${NC}"
    
    # Check app version
    VERSION=$(grep "version:" pubspec.yaml | cut -d' ' -f2)
    echo -e "${BLUE}ℹ️  App version: $VERSION${NC}"
else
    echo -e "${RED}❌ pubspec.yaml missing${NC}"
fi

if [ -f "android/app/build.gradle" ]; then
    echo -e "${GREEN}✅ Android build configuration found${NC}"
    
    # Check package name
    PACKAGE_NAME=$(grep "applicationId" android/app/build.gradle | cut -d'"' -f2)
    echo -e "${BLUE}ℹ️  Package name: $PACKAGE_NAME${NC}"
else
    echo -e "${RED}❌ Android build.gradle missing${NC}"
fi

echo ""
echo "🚀 Next Steps:"
echo "=============="
echo ""
echo "1. Complete the Codemagic setup using CODEMAGIC_SETUP_GUIDE.md"
echo "2. Upload your certificates to Codemagic"
echo "3. Configure environment variables"
echo "4. Test with a development build"
echo "5. Set up store credentials"
echo "6. Enable automated deployment"

echo ""
echo -e "${GREEN}🎯 Once configured, your app will automatically:${NC}"
echo "   • Build on every push to main branch"
echo "   • Run tests and quality checks"
echo "   • Deploy to app stores"
echo "   • Send notifications on success/failure"
echo "   • Detect and report issues automatically"

echo ""
echo -e "${BLUE}📞 Need help? Check CODEMAGIC_SETUP_GUIDE.md or contact: kha89ahm@gmail.com${NC}"
echo "" 