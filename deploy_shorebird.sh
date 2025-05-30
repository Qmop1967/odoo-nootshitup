#!/bin/bash

# TSH Salesperson App - Shorebird Deployment Script
# This script deploys the enhanced app features via Shorebird

set -e

echo "🚀 TSH Salesperson App - Shorebird Deployment"
echo "=============================================="

# Set up Shorebird path
export PATH="$HOME/.shorebird/bin:$PATH"

echo "📋 Checking Shorebird status..."
shorebird doctor

echo "🔧 Building enhanced app..."
flutter clean
flutter pub get

echo "📦 Creating Shorebird release..."
# First, let's try to create a release which will create the app if it doesn't exist
shorebird release android --no-confirm || {
    echo "⚠️  Release failed. This might be because the app doesn't exist yet."
    echo "📝 Please ensure you have:"
    echo "   1. Logged into Shorebird: shorebird login"
    echo "   2. Created the app in Shorebird console"
    echo "   3. Updated shorebird.yaml with correct app_id"
    exit 1
}

echo "✅ Shorebird release created successfully!"
echo ""
echo "🎯 Next steps:"
echo "1. Install the release APK on devices"
echo "2. Use 'shorebird patch android' for future updates"
echo "3. Monitor deployments in Shorebird console"
echo ""
echo "📱 Enhanced features now available:"
echo "   ✅ Odoo SSO integration"
echo "   ✅ Admin role detection"
echo "   ✅ Customer management"
echo "   ✅ Payment recording"
echo "   ✅ Real-time data sync"
echo ""
echo "🔗 Shorebird Console: https://console.shorebird.dev"