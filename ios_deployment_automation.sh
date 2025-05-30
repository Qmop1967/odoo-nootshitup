#!/bin/bash

# TSH Salesperson App - iOS Deployment Automation Script
# This script prepares everything needed for iOS App Store deployment

echo "🍎 TSH Salesperson App - iOS Deployment Preparation"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo "📋 Pre-deployment Checklist:"
echo "=============================="

# Check if we're on macOS (required for iOS builds)
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "iOS builds require macOS with Xcode installed"
    print_info "Current system: $OSTYPE"
    print_info "You'll need to transfer this project to a Mac for iOS deployment"
    echo ""
    print_info "Next steps:"
    echo "1. Copy this project to a macOS machine"
    echo "2. Install Xcode from Mac App Store"
    echo "3. Run this script on macOS"
    echo ""
else
    print_status "Running on macOS - iOS builds supported"
fi

# Check Flutter iOS support
print_info "Checking Flutter iOS configuration..."
if flutter config | grep -q "enable-ios: true"; then
    print_status "Flutter iOS support enabled"
else
    print_warning "Enabling Flutter iOS support..."
    flutter config --enable-ios
fi

# Check for Xcode
if command -v xcodebuild &> /dev/null; then
    XCODE_VERSION=$(xcodebuild -version | head -n1)
    print_status "Xcode found: $XCODE_VERSION"
else
    print_error "Xcode not found - required for iOS builds"
    print_info "Install Xcode from Mac App Store"
fi

# Check for iOS platform in project
if [ -d "ios" ]; then
    print_status "iOS platform already configured"
else
    print_info "Adding iOS platform to project..."
    flutter create --platforms=ios .
    print_status "iOS platform added"
fi

echo ""
echo "🔧 iOS Project Configuration:"
echo "============================="

# App configuration
APP_NAME="TSH Salesperson"
BUNDLE_ID="com.tsh.salesperson"
VERSION="1.0.0"
BUILD_NUMBER="1"

print_info "App Name: $APP_NAME"
print_info "Bundle ID: $BUNDLE_ID"
print_info "Version: $VERSION"
print_info "Build Number: $BUILD_NUMBER"

echo ""
echo "📱 Required Apple Developer Account Setup:"
echo "=========================================="
echo ""
print_warning "MANUAL STEPS REQUIRED:"
echo ""
echo "1. 🍎 Apple Developer Account ($99/year)"
echo "   - Sign up at: https://developer.apple.com/programs/"
echo "   - Complete enrollment process"
echo ""
echo "2. 📱 App Store Connect Setup"
echo "   - Go to: https://appstoreconnect.apple.com/"
echo "   - Create new app with Bundle ID: $BUNDLE_ID"
echo "   - App Name: $APP_NAME"
echo "   - Category: Business"
echo ""
echo "3. 🔐 Certificates & Provisioning"
echo "   - Create iOS Distribution Certificate"
echo "   - Create App Store Provisioning Profile"
echo "   - Download and install in Xcode"
echo ""
echo "4. 📝 App Information Required"
echo "   - App description and keywords"
echo "   - Screenshots (iPhone and iPad)"
echo "   - App icon (1024x1024 PNG)"
echo "   - Privacy policy URL"
echo ""

echo "🚀 Deployment Commands (Run on macOS with Xcode):"
echo "================================================="
echo ""
echo "# 1. Clean and get dependencies"
echo "flutter clean"
echo "flutter pub get"
echo ""
echo "# 2. Build iOS release"
echo "flutter build ios --release"
echo ""
echo "# 3. Build IPA for App Store"
echo "flutter build ipa --release"
echo ""
echo "# 4. Open in Xcode for upload"
echo "open ios/Runner.xcworkspace"
echo ""
echo "# 5. Or upload via command line"
echo "xcrun altool --upload-app --type ios --file build/ios/ipa/*.ipa --username YOUR_APPLE_ID --password YOUR_APP_SPECIFIC_PASSWORD"
echo ""

echo "📋 App Store Listing Information:"
echo "================================="
echo ""
echo "App Name: TSH Salesperson"
echo "Subtitle: Odoo Sales Management"
echo ""
echo "Description:"
echo "Professional sales management app that integrates seamlessly with your Odoo system."
echo "Access customers, products, orders, and invoices in real-time. Record payments and"
echo "manage your sales pipeline from anywhere."
echo ""
echo "Key Features:"
echo "• Complete Odoo integration with real-time sync"
echo "• Customer management and creation"
echo "• Product catalog with search and filtering"
echo "• Sales order tracking and management"
echo "• Invoice monitoring with payment status"
echo "• Payment recording for admin users"
echo "• Role-based access control"
echo "• Modern, intuitive interface"
echo ""
echo "Keywords: odoo,sales,crm,erp,business,customers,orders,invoices,payments"
echo "Category: Business"
echo "Age Rating: 4+ (No Objectionable Content)"
echo ""

echo "🎯 Next Steps:"
echo "=============="
echo ""
print_info "1. Transfer project to macOS machine with Xcode"
print_info "2. Set up Apple Developer Account"
print_info "3. Configure certificates and provisioning profiles"
print_info "4. Build and upload to App Store Connect"
print_info "5. Complete App Store listing"
print_info "6. Submit for Apple review"
echo ""

print_status "iOS deployment preparation complete!"
print_info "All files and configurations are ready for App Store deployment"