# How to Disable Flutter Drive in CodeMagic

## Issue
CodeMagic is automatically running `flutter drive` tests even though we removed the `test_driver/` directory, causing build failures.

## Error Details
```
Flutter Drive run failed.
SessionNotCreatedException (500): session not created: This version of ChromeDriver only supports Chrome version 135
Current browser version is 134.0.6998.166
```

## Solution: Disable Flutter Drive in CodeMagic UI

### Method 1: Environment Variables (Recommended)
Add these environment variables to your CodeMagic workflow:

```
DISABLE_FLUTTER_DRIVE=true
SKIP_INTEGRATION_TESTS=true
CM_SKIP_FLUTTER_DRIVE=true
```

### Method 2: Custom Build Script
Replace your build script with this version that explicitly skips Flutter Drive:

```bash
#!/bin/bash
echo "🤖 Building Android APK with standard Flutter (No Flutter Drive)..."

# Disable Flutter Drive explicitly
export DISABLE_FLUTTER_DRIVE=true
export SKIP_INTEGRATION_TESTS=true

# Clean and get dependencies
flutter clean
flutter pub get

# Run ONLY unit tests (not integration tests)
echo "🧪 Running unit tests only..."
flutter test --no-integration

# Build Android APK
echo "📱 Building Android APK..."
flutter build apk --release --verbose

# Verify APK was created
if [ -f "build/app/outputs/flutter-apk/app-release.apk" ]; then
    echo "✅ Android APK built successfully"
    ls -la build/app/outputs/flutter-apk/
else
    echo "❌ APK build failed"
    exit 1
fi

echo "🎉 Android build completed successfully!"
echo "ℹ️  Flutter Drive tests skipped (integration tests disabled)"
```

### Method 3: CodeMagic Workflow Settings
In CodeMagic UI:

1. **Go to your workflow settings**
2. **Find "Testing" or "QA" section**
3. **Disable "Integration tests"** or **"Flutter Drive tests"**
4. **Keep "Unit tests" enabled**

### Method 4: Alternative Build Script (Safest)
Use this script that completely avoids any Flutter Drive commands:

```bash
#!/bin/bash
echo "🚀 Standard Flutter Build (Drive-Free)..."

# Explicitly prevent any drive commands
unset FLUTTER_DRIVE
export NO_FLUTTER_DRIVE=true

# Clean build
flutter clean
flutter pub get

# Unit tests only
echo "🧪 Running unit tests..."
if flutter test; then
    echo "✅ All unit tests passed"
else
    echo "❌ Unit tests failed"
    exit 1
fi

# Build APK
echo "📱 Building Android APK..."
if flutter build apk --release; then
    echo "✅ APK build successful"
    
    # Verify APK exists
    if [ -f "build/app/outputs/flutter-apk/app-release.apk" ]; then
        echo "✅ APK file verified"
        ls -la build/app/outputs/flutter-apk/app-release.apk
    fi
else
    echo "❌ APK build failed"
    exit 1
fi

echo "🎉 Build completed without Flutter Drive!"
```

## Quick Fix for Current Build

### Immediate Action:
1. **Go to CodeMagic UI**
2. **Edit your Android workflow**
3. **Replace the build script** with Method 4 above
4. **Add environment variables** from Method 1
5. **Save and trigger new build**

### Expected Success Output:
```
🚀 Standard Flutter Build (Drive-Free)...
🧪 Running unit tests...
00:05 +9: All tests passed!
✅ All unit tests passed
📱 Building Android APK...
✅ APK build successful
✅ APK file verified
-rw-r--r-- 1 builder builder 25M app-release.apk
🎉 Build completed without Flutter Drive!
```

## Why This Happens

CodeMagic automatically detects Flutter projects and tries to run:
1. **Unit tests** (`flutter test`) ✅ We want this
2. **Integration tests** (`flutter drive`) ❌ We disabled this
3. **Web tests** (`flutter test -d chrome`) ❌ Causing Chrome version issues

## Verification

After applying the fix, your build should:
- ✅ Run unit tests successfully (9/9 passing)
- ✅ Build APK without errors
- ❌ NOT attempt Flutter Drive
- ❌ NOT show Chrome/ChromeDriver errors

## Alternative: Create New Workflow

If the above doesn't work, create a completely new workflow in CodeMagic:
1. **Create new workflow**
2. **Name it "Standard Flutter Build"**
3. **Use the safe build script from Method 4**
4. **Don't enable any integration test options**

This ensures a clean slate without any cached Flutter Drive configurations. 