# CodeMagic Standard Flutter Build Configuration

## Overview
This guide configures CodeMagic for standard Flutter builds without Shorebird or Flutter Driver integration.

## Changes Made
✅ **Shorebird Disabled**:
- Removed `shorebird_code_push` dependency
- Removed `shorebird.yaml` file
- Disabled in `pubspec.yaml` and `app_config.dart`
- Renamed `.shorebird` to `.shorebird_disabled`

✅ **Flutter Driver Disabled**:
- Removed `flutter_driver` dependency
- Removed `test_driver/` directory
- No integration tests will run

## CodeMagic UI Configuration

### **Build Scripts**

#### **Android Build Script:**
```bash
#!/bin/bash
echo "🤖 Building Android APK with standard Flutter..."

# Clean and get dependencies
flutter clean
flutter pub get

# Run unit tests
flutter test

# Build Android APK
flutter build apk --release --verbose

# Verify APK was created
if [ -f "build/app/outputs/flutter-apk/app-release.apk" ]; then
    echo "✅ Android APK built successfully"
    ls -la build/app/outputs/flutter-apk/
else
    echo "❌ APK build failed"
    exit 1
fi

echo "🎉 Android build completed!"
```

#### **iOS Build Script:**
```bash
#!/bin/bash
echo "🍎 Building iOS IPA with standard Flutter..."

# Clean and get dependencies
flutter clean
flutter pub get

# Run unit tests
flutter test

# Build iOS
flutter build ios --release --no-codesign --verbose

# Build IPA
flutter build ipa --release --verbose

echo "✅ iOS build completed!"
```

### **Environment Variables**
No special environment variables needed for standard Flutter builds.

Optional:
```
FLUTTER_VERSION=3.24.0
```

### **Build Settings**
- **Flutter version**: 3.24.0 (or latest stable)
- **Build mode**: Release
- **Code signing**: Configure as needed for distribution

## Expected Build Output

### **Successful Android Build:**
```
🤖 Building Android APK with standard Flutter...
Running "flutter pub get" in /Users/builder/clone...
Running "flutter test"...
All tests passed!
Running "flutter build apk --release --verbose"...
✅ Android APK built successfully
-rw-r--r-- 1 builder builder 25M app-release.apk
🎉 Android build completed!
```

### **Successful iOS Build:**
```
🍎 Building iOS IPA with standard Flutter...
Running "flutter pub get" in /Users/builder/clone...
Running "flutter test"...
All tests passed!
Running "flutter build ios --release --no-codesign --verbose"...
Running "flutter build ipa --release --verbose"...
✅ iOS build completed!
```

## Artifacts

### **Android:**
- `build/app/outputs/flutter-apk/app-release.apk`
- `build/app/outputs/bundle/release/app-release.aab` (if building bundle)

### **iOS:**
- `build/ios/ipa/tsh_salesperson_app.ipa`

## Testing

### **Unit Tests Only:**
- `flutter test` runs all unit tests in `test/` directory
- No integration tests (Flutter Driver removed)
- Fast and reliable testing

### **Current Test Status:**
- ✅ 9 unit tests passing
- ❌ 0 integration tests (disabled)

## Deployment

### **Android:**
- Upload APK/AAB to Google Play Console
- Standard app store deployment process

### **iOS:**
- Upload IPA to App Store Connect
- Submit for TestFlight and App Store review

## Benefits of Standard Build

1. **Faster Builds**: No Shorebird installation overhead
2. **More Reliable**: Standard Flutter build process
3. **Simpler Setup**: No authentication tokens needed
4. **Universal Compatibility**: Works with all Flutter versions
5. **Easier Debugging**: Standard error messages and logs

## Migration Back to Shorebird (If Needed)

If you want to re-enable Shorebird later:
1. Restore `shorebird.yaml` file
2. Add `shorebird_code_push` dependency
3. Rename `.shorebird_disabled` back to `.shorebird`
4. Update `pubspec.yaml` and `app_config.dart`
5. Configure Shorebird token in CodeMagic

## Success Indicators

✅ Build completes without Shorebird errors
✅ APK/IPA files are generated
✅ Unit tests pass
✅ No authentication failures
✅ Standard Flutter build logs

This configuration provides a clean, reliable build process for your TSH Salesperson App! 