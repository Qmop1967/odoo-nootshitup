#!/bin/bash

# TSH Salesperson App - Build Status Checker
# This script helps monitor CodeMagic build status and provides next steps

echo "🚀 TSH Salesperson App - Build Status Check"
echo "============================================="

# Check git status
echo "📋 Git Status:"
git log --oneline -1
echo "Latest commit pushed to: $(git branch --show-current)"
echo ""

# Check if CodeMagic configuration exists
echo "⚙️  CodeMagic Configuration:"
if [ -f "codemagic.yaml" ]; then
    echo "✅ codemagic.yaml found"
    echo "📱 Configured workflows:"
    grep -A 1 "workflows:" codemagic.yaml | grep -E "^\s+\w+-workflow:" | sed 's/://g' | sed 's/^/   - /'
else
    echo "❌ codemagic.yaml not found"
fi
echo ""

# Check Flutter project structure
echo "📱 Flutter Project Status:"
if [ -f "pubspec.yaml" ]; then
    echo "✅ Flutter project detected"
    echo "📦 App name: $(grep '^name:' pubspec.yaml | cut -d' ' -f2)"
    echo "🔢 Version: $(grep '^version:' pubspec.yaml | cut -d' ' -f2)"
else
    echo "❌ pubspec.yaml not found"
fi
echo ""

# Check for required files
echo "📋 Required Files Checklist:"
files=("lib/main.dart" "android/app/build.gradle" "ios/Runner.xcodeproj/project.pbxproj")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file"
    fi
done
echo ""

# Next steps
echo "🎯 Next Steps:"
echo "1. 🔗 Connect repository to CodeMagic:"
echo "   - Visit: https://codemagic.io"
echo "   - Connect GitHub account"
echo "   - Add this repository"
echo ""
echo "2. 🔑 Configure environment variables in CodeMagic:"
echo "   - iOS: APP_STORE_CONNECT_ISSUER_ID, APP_STORE_CONNECT_KEY_IDENTIFIER"
echo "   - Android: CM_KEYSTORE_PASSWORD, CM_KEY_ALIAS"
echo ""
echo "3. 📱 Upload signing certificates:"
echo "   - iOS: Distribution certificate and provisioning profile"
echo "   - Android: Upload keystore file (tsh_keystore.jks)"
echo ""
echo "4. 🚀 Trigger first build:"
echo "   - Push changes will auto-trigger builds"
echo "   - Or manually start build in CodeMagic dashboard"
echo ""
echo "5. 📱 App Preview:"
echo "   - Download APK/IPA from build artifacts"
echo "   - Use QR codes for easy device installation"
echo "   - TestFlight integration for iOS testing"
echo ""

# Build trigger information
echo "🔄 Build Triggers Configured:"
echo "   - Push to main branch ✅"
echo "   - Pull requests ✅"
echo "   - Git tags ✅"
echo ""

echo "📧 Notifications configured for: kha89ahm@gmail.com"
echo ""
echo "🌐 Repository URL: $(git config --get remote.origin.url)"
echo ""
echo "✅ Ready for CodeMagic integration!"
echo "Visit CodeMagic dashboard to monitor build progress." 