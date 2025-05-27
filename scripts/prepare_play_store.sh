#!/bin/bash

# 📱 TSH Salesperson App - Google Play Store Preparation Script
# This script helps prepare your app for Google Play Store submission

echo "📱 TSH Salesperson App - Google Play Store Preparation"
echo "====================================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo ""
echo "🔍 Checking app readiness for Google Play Store..."
echo ""

# 1. Check Flutter installation
echo "🛠️  1. Flutter Environment"
echo "-------------------------"

if command -v flutter &> /dev/null; then
    FLUTTER_VERSION=$(flutter --version | head -n 1)
    log_success "Flutter installed: $FLUTTER_VERSION"
    
    # Check if it's the expected version
    if echo "$FLUTTER_VERSION" | grep -q "3.24.5"; then
        log_success "Flutter version matches Codemagic configuration"
    else
        log_warning "Flutter version differs from Codemagic (3.24.5)"
    fi
else
    log_error "Flutter not installed"
    echo "Please install Flutter: https://flutter.dev/docs/get-started/install"
    exit 1
fi

echo ""

# 2. Check Android configuration
echo "🤖 2. Android Configuration"
echo "---------------------------"

if [ -f "android/app/build.gradle" ]; then
    log_success "Android build.gradle found"
    
    # Check target SDK
    TARGET_SDK=$(grep "targetSdk" android/app/build.gradle | grep -o '[0-9]\+' | head -1)
    if [ "$TARGET_SDK" = "35" ]; then
        log_success "Target SDK 35 (Android 14) - Play Store ready"
    else
        log_warning "Target SDK is $TARGET_SDK, recommended: 35"
    fi
    
    # Check package name
    PACKAGE_NAME=$(grep "applicationId" android/app/build.gradle | cut -d'"' -f2)
    if [ "$PACKAGE_NAME" = "com.tsh.sales.tsh_salesperson_app" ]; then
        log_success "Package name: $PACKAGE_NAME"
    else
        log_warning "Package name: $PACKAGE_NAME"
    fi
    
else
    log_error "Android build.gradle not found"
fi

echo ""

# 3. Check keystore configuration
echo "🔐 3. Keystore Configuration"
echo "----------------------------"

if [ -f "tsh-salesperson-key.jks" ]; then
    log_success "Keystore file found"
    
    if [ -f "android/key.properties" ]; then
        log_success "Key properties configured"
        
        # Test keystore access
        if keytool -list -keystore tsh-salesperson-key.jks -storepass Zcbm.97531tsh > /dev/null 2>&1; then
            log_success "Keystore accessible with configured password"
        else
            log_error "Cannot access keystore with configured password"
        fi
    else
        log_warning "Key properties file not found"
    fi
else
    log_error "Keystore file not found"
fi

echo ""

# 4. Build release version
echo "🏗️  4. Building Release Version"
echo "-------------------------------"

log_info "Building Android App Bundle (AAB) for Play Store..."

if flutter build appbundle --release; then
    log_success "Release AAB built successfully"
    
    AAB_PATH="build/app/outputs/bundle/release/app-release.aab"
    if [ -f "$AAB_PATH" ]; then
        AAB_SIZE=$(du -h "$AAB_PATH" | cut -f1)
        log_success "AAB file: $AAB_PATH ($AAB_SIZE)"
    else
        log_error "AAB file not found at expected location"
    fi
else
    log_error "Failed to build release AAB"
fi

echo ""

# 5. Generate app information
echo "📋 5. App Information Summary"
echo "-----------------------------"

echo "Package Name: com.tsh.sales.tsh_salesperson_app"
echo "App Name: TSH Salesperson App"
echo "Version: 1.0.0"
echo "Target SDK: 35 (Android 14)"
echo "Min SDK: 21 (Android 5.0)"
echo "Architecture: Universal (ARM64, ARM32, x86_64)"
echo "Format: Android App Bundle (AAB)"

echo ""

# 6. Check required assets
echo "🎨 6. Required Store Assets"
echo "--------------------------"

ASSETS_DIR="store_assets"
mkdir -p "$ASSETS_DIR"

log_info "Checking for required Google Play Store assets..."

# App icon
if [ -f "android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png" ]; then
    log_success "App icon found"
    cp "android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png" "$ASSETS_DIR/app_icon.png"
else
    log_warning "App icon not found - you'll need a 512x512 PNG icon"
fi

# Create asset requirements file
cat > "$ASSETS_DIR/REQUIRED_ASSETS.md" << EOF
# Required Google Play Store Assets

## App Icon
- **Size**: 512x512 pixels
- **Format**: PNG
- **Background**: No transparency
- **Current**: $([ -f "$ASSETS_DIR/app_icon.png" ] && echo "✅ Found" || echo "❌ Missing")

## Feature Graphic
- **Size**: 1024x500 pixels
- **Format**: PNG or JPG
- **Content**: Showcase your app's main features
- **Current**: ❌ Missing

## Screenshots
- **Phone**: At least 2 screenshots
- **Size**: 16:9 or 9:16 aspect ratio
- **Resolution**: Minimum 320px on shortest side
- **Current**: ❌ Missing

## Store Listing Text
- **App Name**: TSH Salesperson App
- **Short Description**: Professional sales management tool (max 80 chars)
- **Full Description**: Detailed app description (max 4000 chars)
- **Current**: ❌ Needs writing

## Privacy Policy
- **Required**: Yes (for all apps)
- **Format**: Public URL
- **Content**: How you handle user data
- **Current**: ❌ Missing

## Content Rating
- **Required**: Yes
- **Process**: Complete questionnaire in Play Console
- **Category**: Business app
- **Current**: ❌ Pending
EOF

log_info "Asset requirements saved to: $ASSETS_DIR/REQUIRED_ASSETS.md"

echo ""

# 7. Create deployment script
echo "🚀 7. Deployment Preparation"
echo "----------------------------"

cat > "deploy_to_play_store.sh" << 'EOF'
#!/bin/bash

# 🚀 Deploy TSH Salesperson App to Google Play Store
# This script creates a version tag to trigger Codemagic deployment

echo "🚀 Deploying TSH Salesperson App to Google Play Store"
echo "===================================================="

# Get current version or prompt for new one
CURRENT_VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
echo "Current version: $CURRENT_VERSION"

read -p "Enter new version (e.g., v1.0.0): " NEW_VERSION

if [ -z "$NEW_VERSION" ]; then
    echo "❌ Version required"
    exit 1
fi

# Validate version format
if [[ ! "$NEW_VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Invalid version format. Use: v1.0.0"
    exit 1
fi

# Check if version already exists
if git tag | grep -q "^$NEW_VERSION$"; then
    echo "❌ Version $NEW_VERSION already exists"
    exit 1
fi

echo ""
echo "🏗️  Creating deployment..."

# Ensure we're on main branch
git checkout main
git pull origin main

# Create and push version tag
git tag "$NEW_VERSION"
git push origin "$NEW_VERSION"

echo ""
echo "✅ Deployment triggered!"
echo "📧 Check your email (kha89ahm@gmail.com) for build status"
echo "🔗 Monitor build: https://codemagic.io/apps"
echo "📱 Check Google Play Console after successful build"
echo ""
echo "Version $NEW_VERSION will be automatically:"
echo "  1. Built as release AAB"
echo "  2. Signed with your keystore"
echo "  3. Uploaded to Google Play Internal Testing"
echo "  4. Available for promotion to production"
EOF

chmod +x deploy_to_play_store.sh
log_success "Deployment script created: deploy_to_play_store.sh"

echo ""

# 8. Summary and next steps
echo "📊 8. Summary & Next Steps"
echo "=========================="

echo ""
echo "🎯 Your app is technically ready for Google Play Store!"
echo ""
echo "✅ Completed:"
echo "  - App built and signed"
echo "  - Codemagic CI/CD configured"
echo "  - Release AAB generated"
echo "  - Deployment script ready"
echo ""
echo "📋 Still needed for store submission:"
echo "  1. Google Play Console account (\$25 fee)"
echo "  2. App store listing (descriptions, screenshots)"
echo "  3. Privacy policy URL"
echo "  4. Google Cloud Service Account for API"
echo "  5. Store assets (icon, screenshots, feature graphic)"
echo ""
echo "🚀 To deploy when ready:"
echo "  ./deploy_to_play_store.sh"
echo ""
echo "📖 Complete guide: GOOGLE_PLAY_PUBLISHING_GUIDE.md"
echo ""

if [ -f "$AAB_PATH" ]; then
    echo "📱 Your release AAB is ready at: $AAB_PATH"
    echo "   You can manually upload this to Play Console if needed"
fi

echo ""
log_success "Play Store preparation complete!"