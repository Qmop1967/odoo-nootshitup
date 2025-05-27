#!/bin/bash

echo "🚀 TSH Salesperson App Build Script"
echo "=================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Warning: Running as root. Consider using a non-root user for Flutter development."
fi

# Clean and prepare
echo "📦 Cleaning project..."
flutter clean
flutter pub get

# Run analysis
echo "🔍 Running code analysis..."
flutter analyze

# Run tests (if any)
echo "🧪 Running tests..."
flutter test || echo "⚠️  No tests found or tests failed"

# Build debug APK first for testing
echo "🔧 Building debug APK for testing..."
flutter build apk --debug

# Build release APK
echo "🔧 Building release APK..."
flutter build apk --release

# Build Android App Bundle for Play Store
echo "📱 Building Android App Bundle..."
flutter build appbundle --release

echo "✅ Build complete!"
echo ""
echo "📁 Output files:"
echo "   Debug APK: build/app/outputs/flutter-apk/app-debug.apk"
echo "   Release APK: build/app/outputs/flutter-apk/app-release.apk"
echo "   AAB: build/app/outputs/bundle/release/app-release.aab"
echo ""
echo "🎯 Next steps:"
echo "   1. Test the debug APK on a device"
echo "   2. Test the release APK on a device"
echo "   3. Upload AAB to Google Play Console"
echo "   4. For iOS: flutter build ios --release"
echo ""
echo "📊 Build summary:"
ls -la build/app/outputs/flutter-apk/ 2>/dev/null || echo "   APK files not found"
ls -la build/app/outputs/bundle/release/ 2>/dev/null || echo "   AAB files not found"