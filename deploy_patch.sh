#!/bin/bash

# TSH Salesperson App - Quick Patch Deployment
# Use this script to deploy updates after the initial release

set -e

echo "🔄 TSH Salesperson App - Patch Deployment"
echo "========================================="

# Set up Shorebird path
export PATH="$HOME/.shorebird/bin:$PATH"

echo "📋 Checking current status..."
shorebird doctor

echo "🔧 Preparing patch..."
flutter clean
flutter pub get

echo "📦 Creating patch..."
shorebird patch android --no-confirm

echo "✅ Patch deployed successfully!"
echo ""
echo "📊 Deployment Status:"
echo "   • Patch created and uploaded"
echo "   • Users will receive update automatically"
echo "   • Monitor progress in Shorebird console"
echo ""
echo "🎯 Enhanced features in this patch:"
echo "   ✅ Improved Odoo integration"
echo "   ✅ Enhanced user interface"
echo "   ✅ Better error handling"
echo "   ✅ Performance optimizations"
echo ""
echo "🔗 Monitor at: https://console.shorebird.dev"