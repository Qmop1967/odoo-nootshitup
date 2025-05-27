#!/bin/bash
set -e

echo "🔥 Firebase App Distribution Setup for TSH Salesperson App"
echo "=========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📱 App Information:${NC}"
echo "  Package Name: com.tsh.sales.tsh_salesperson_app"
echo "  Bundle ID: com.tsh.sales.tsh_salesperson_app"
echo ""

echo -e "${YELLOW}🔧 Setup Steps:${NC}"
echo ""

echo -e "${GREEN}1. Firebase Console Setup:${NC}"
echo "   • Go to: https://console.firebase.google.com/"
echo "   • Create a new project or select existing one"
echo "   • Project name suggestion: 'TSH Salesperson App'"
echo ""

echo -e "${GREEN}2. Add Android App:${NC}"
echo "   • Click 'Add app' → Android"
echo "   • Package name: com.tsh.sales.tsh_salesperson_app"
echo "   • App nickname: TSH Salesperson Android"
echo "   • Download google-services.json"
echo "   • Place it in: android/app/google-services.json"
echo ""

echo -e "${GREEN}3. Add iOS App:${NC}"
echo "   • Click 'Add app' → iOS"
echo "   • Bundle ID: com.tsh.sales.tsh_salesperson_app"
echo "   • App nickname: TSH Salesperson iOS"
echo "   • Download GoogleService-Info.plist"
echo "   • Place it in: ios/Runner/GoogleService-Info.plist"
echo ""

echo -e "${GREEN}4. Enable App Distribution:${NC}"
echo "   • In Firebase Console, go to 'App Distribution'"
echo "   • Click 'Get started'"
echo "   • Create tester groups:"
echo "     - tsh-testers (for QA team)"
echo "     - developers (for development team)"
echo ""

echo -e "${GREEN}5. Get Firebase CLI Token:${NC}"
echo "   • Install Firebase CLI: npm install -g firebase-tools"
echo "   • Login: firebase login:ci"
echo "   • Copy the token for Codemagic"
echo ""

echo -e "${GREEN}6. Configure Codemagic:${NC}"
echo "   • Go to Codemagic → Your App → Environment variables"
echo "   • Add these variables:"
echo "     - FIREBASE_TOKEN: [Your CLI token]"
echo "     - FIREBASE_ANDROID_APP_ID: [From Firebase console]"
echo "     - FIREBASE_IOS_APP_ID: [From Firebase console]"
echo ""

echo -e "${BLUE}📋 Checklist:${NC}"
echo "   □ Firebase project created"
echo "   □ Android app added to Firebase"
echo "   □ iOS app added to Firebase"
echo "   □ google-services.json downloaded and placed"
echo "   □ GoogleService-Info.plist downloaded and placed"
echo "   □ App Distribution enabled"
echo "   □ Tester groups created"
echo "   □ Firebase CLI token generated"
echo "   □ Codemagic environment variables configured"
echo ""

echo -e "${YELLOW}🔍 Finding App IDs:${NC}"
echo "   • Android App ID: In Firebase Console → Project Settings → General"
echo "   • iOS App ID: In Firebase Console → Project Settings → General"
echo "   • Look for 'App ID' in the app cards"
echo ""

echo -e "${GREEN}✅ Benefits of Firebase App Distribution:${NC}"
echo "   • 📱 Easy app installation for testers"
echo "   • 🔔 Automatic notifications for new builds"
echo "   • 👥 Organized tester groups"
echo "   • 📊 Download and crash analytics"
echo "   • 🔗 Direct download links"
echo ""

echo -e "${BLUE}🚀 Alternative: Manual Preview (No Firebase needed):${NC}"
echo "   • Codemagic will still build preview APKs"
echo "   • Download from Codemagic artifacts"
echo "   • Share APK files manually"
echo "   • Email notifications with download links"
echo ""

echo -e "${GREEN}🎉 Once setup is complete:${NC}"
echo "   • Push to preview/* or feature/* branches"
echo "   • Codemagic builds automatically"
echo "   • Testers get notified via Firebase"
echo "   • Easy testing and feedback cycle"
echo ""

echo "Setup complete! Check CODEMAGIC_PREVIEW_SETUP.md for detailed instructions."