# CodeMagic Build Troubleshooting Guide

## Current Issue: Android Build Failed

Since you're using CodeMagic UI (not codemagic.yaml), here's how to diagnose and fix the build failure:

## Step 1: Check Build Logs

In CodeMagic UI:
1. Go to your failed build
2. Click on the build details
3. Look for the specific error message in the logs
4. Common error patterns to look for:

### Common Error Patterns:

#### A. Shorebird Authentication Error
```
Error: Authentication failed
Error: Could not find app with id: "com.tsh.sales.tsh_salesperson_app"
```

#### B. Missing Shorebird Token
```
Error: No authentication token found
Error: Please run 'shorebird login' first
```

#### C. Flutter Version Mismatch
```
Error: Flutter version X.X.X is not supported
Error: Shorebird requires Flutter version Y.Y.Y
```

#### D. Dependency Issues
```
Error: Could not resolve dependencies
Error: Package shorebird_code_push not found
```

## Step 2: Quick Fix Solutions

### Solution A: Add Missing Environment Variables

In CodeMagic UI → Your Workflow → Environment Variables, add:

```
SHOREBIRD_TOKEN=<your_token_here>
FLUTTER_VERSION=3.24.0
```

### Solution B: Use This Diagnostic Script

Replace your current build script with this diagnostic version:

```bash
#!/bin/bash
echo "🔍 Starting Android Build Diagnostics..."

# Check environment
echo "📋 Environment Check:"
echo "Flutter version: $(flutter --version)"
echo "Dart version: $(dart --version)"
echo "Working directory: $(pwd)"
echo "Available space: $(df -h .)"

# Check if Shorebird token is set
if [ -z "$SHOREBIRD_TOKEN" ]; then
    echo "❌ ERROR: SHOREBIRD_TOKEN environment variable not set"
    echo "Please add SHOREBIRD_TOKEN to your CodeMagic environment variables"
    exit 1
else
    echo "✅ SHOREBIRD_TOKEN is set"
fi

# Install Shorebird
echo "📦 Installing Shorebird..."
curl --proto '=https' --tlsv1.2 https://raw.githubusercontent.com/shorebirdtech/install/main/install.sh -sSf | bash
export PATH="$HOME/.shorebird/bin:$PATH"

# Verify Shorebird installation
echo "🔧 Verifying Shorebird installation..."
if command -v shorebird &> /dev/null; then
    echo "✅ Shorebird installed successfully"
    shorebird --version
else
    echo "❌ ERROR: Shorebird installation failed"
    exit 1
fi

# Authenticate with Shorebird
echo "🔐 Authenticating with Shorebird..."
echo "$SHOREBIRD_TOKEN" > ~/.shorebird/credentials.json

# Verify authentication
echo "🔍 Testing Shorebird authentication..."
if shorebird apps list &> /dev/null; then
    echo "✅ Shorebird authentication successful"
else
    echo "❌ ERROR: Shorebird authentication failed"
    echo "Please check your SHOREBIRD_TOKEN"
    exit 1
fi

# Check project configuration
echo "📁 Checking project configuration..."
if [ -f "shorebird.yaml" ]; then
    echo "✅ shorebird.yaml found"
    cat shorebird.yaml
else
    echo "❌ ERROR: shorebird.yaml not found"
    exit 1
fi

if [ -f "pubspec.yaml" ]; then
    echo "✅ pubspec.yaml found"
    echo "Checking for shorebird.yaml in assets..."
    if grep -q "shorebird.yaml" pubspec.yaml; then
        echo "✅ shorebird.yaml listed in assets"
    else
        echo "❌ ERROR: shorebird.yaml not listed in pubspec.yaml assets"
        exit 1
    fi
else
    echo "❌ ERROR: pubspec.yaml not found"
    exit 1
fi

# Clean and get dependencies
echo "🧹 Cleaning and getting dependencies..."
flutter clean
flutter pub get

# Check if dependencies resolved
if [ $? -eq 0 ]; then
    echo "✅ Dependencies resolved successfully"
else
    echo "❌ ERROR: Failed to resolve dependencies"
    exit 1
fi

# Try Shorebird release
echo "🚀 Attempting Shorebird release..."
shorebird release android --verbose

if [ $? -eq 0 ]; then
    echo "✅ Shorebird Android release completed successfully!"
else
    echo "❌ ERROR: Shorebird release failed"
    echo "Trying fallback Flutter build..."
    flutter build apk --release --verbose
    
    if [ $? -eq 0 ]; then
        echo "✅ Fallback Flutter build successful"
        echo "⚠️ Note: This is a standard Flutter build, not a Shorebird release"
    else
        echo "❌ ERROR: Both Shorebird and Flutter builds failed"
        exit 1
    fi
fi

echo "🎉 Build process completed!"
```

### Solution C: Alternative Shorebird Setup

If the above fails, try this alternative approach:

```bash
#!/bin/bash
echo "🔄 Alternative Shorebird Setup..."

# Set up environment
export SHOREBIRD_CACHE="$HOME/.shorebird"
export PATH="$SHOREBIRD_CACHE/bin:$PATH"

# Download and install Shorebird manually
mkdir -p "$SHOREBIRD_CACHE"
cd "$SHOREBIRD_CACHE"

# Download Shorebird CLI
curl -L -o shorebird.tar.gz "https://github.com/shorebirdtech/shorebird/releases/latest/download/shorebird-linux-x64.tar.gz"
tar -xzf shorebird.tar.gz
chmod +x bin/shorebird

# Verify installation
./bin/shorebird --version

# Set up credentials
mkdir -p "$HOME/.shorebird"
echo "$SHOREBIRD_TOKEN" > "$HOME/.shorebird/credentials.json"

# Return to project directory
cd "$CM_BUILD_DIR"

# Clean and build
flutter clean
flutter pub get
./bin/shorebird release android --verbose
```

## Step 3: Get Your Shorebird Token

If you don't have a Shorebird token yet:

### Option 1: Local Setup (Recommended)
```bash
# Install Shorebird locally
curl --proto '=https' --tlsv1.2 https://raw.githubusercontent.com/shorebirdtech/install/main/install.sh -sSf | bash

# Login (this will open a browser)
shorebird login

# Create your app (if not already created)
shorebird apps create

# Get your token
cat ~/.shorebird/credentials.json
```

### Option 2: Web Console
1. Go to https://console.shorebird.dev
2. Sign in with your account
3. Go to Settings → API Tokens
4. Create a new token
5. Copy the token value

## Step 4: CodeMagic UI Configuration

### Environment Variables to Add:
```
SHOREBIRD_TOKEN=<your_actual_token>
FLUTTER_VERSION=3.24.0
SHOREBIRD_CACHE=/Users/builder/.shorebird
```

### Build Script Order:
1. **Pre-build script**: Environment setup and diagnostics
2. **Build script**: The diagnostic script above
3. **Post-build script**: Artifact verification

## Step 5: Common Issues and Solutions

### Issue 1: "App not found"
**Solution**: Verify your app ID in Shorebird console matches `shorebird.yaml`

### Issue 2: "Authentication failed"
**Solution**: 
- Check SHOREBIRD_TOKEN is correctly set
- Verify token hasn't expired
- Try regenerating token

### Issue 3: "Flutter version mismatch"
**Solution**: 
- Set FLUTTER_VERSION environment variable
- Use compatible Flutter version (3.22.0 or later)

### Issue 4: "shorebird.yaml not found as asset"
**Solution**: Already fixed in your project ✅

## Step 6: Fallback Strategy

If Shorebird continues to fail, use this hybrid approach:

```bash
#!/bin/bash
echo "🔄 Hybrid Build Strategy..."

# Try Shorebird first
if shorebird release android --verbose; then
    echo "✅ Shorebird release successful"
else
    echo "⚠️ Shorebird failed, falling back to Flutter build"
    flutter build apk --release --verbose
    
    # Still create APK for distribution
    if [ -f "build/app/outputs/flutter-apk/app-release.apk" ]; then
        echo "✅ Flutter APK created successfully"
    else
        echo "❌ Build completely failed"
        exit 1
    fi
fi
```

## Next Steps

1. **Copy the diagnostic script** to your CodeMagic build step
2. **Add the SHOREBIRD_TOKEN** environment variable
3. **Run the build** and check the detailed logs
4. **Share the specific error message** if it still fails

The diagnostic script will tell us exactly what's going wrong! 