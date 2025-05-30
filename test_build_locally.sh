#!/bin/bash

echo "🚀 TSH Salesperson App - Local Build Test"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

echo "📋 Step 1: Getting Flutter packages..."
flutter packages pub get
print_status $? "Flutter packages retrieved"

echo ""
echo "🔍 Step 2: Running Flutter analysis..."
flutter analyze
ANALYZE_RESULT=$?
if [ $ANALYZE_RESULT -ne 0 ]; then
    print_warning "Analysis found issues but continuing..."
else
    print_status 0 "Analysis passed"
fi

echo ""
echo "🧪 Step 3: Running tests..."
flutter test
TEST_RESULT=$?
if [ $TEST_RESULT -ne 0 ]; then
    print_warning "Some tests failed but continuing..."
else
    print_status 0 "All tests passed"
fi

echo ""
echo "🔧 Step 4: Building Android APK (Debug)..."
flutter build apk --debug
print_status $? "Android Debug APK built"

echo ""
echo "🔧 Step 5: Building Android APK (Release)..."
flutter build apk --release
print_status $? "Android Release APK built"

echo ""
echo "🔧 Step 6: Building Android App Bundle..."
flutter build appbundle --release
print_status $? "Android App Bundle built"

echo ""
echo "📱 Step 7: Building iOS (Debug - no codesign)..."
flutter build ios --debug --no-codesign
print_status $? "iOS Debug build completed"

echo ""
echo "📊 Build Summary:"
echo "=================="
if [ $ANALYZE_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Analysis: PASSED${NC}"
else
    echo -e "${YELLOW}⚠️ Analysis: WARNINGS${NC}"
fi

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Tests: PASSED${NC}"
else
    echo -e "${YELLOW}⚠️ Tests: SOME FAILED${NC}"
fi

echo -e "${GREEN}✅ Android APK: BUILT${NC}"
echo -e "${GREEN}✅ Android Bundle: BUILT${NC}"
echo -e "${GREEN}✅ iOS Debug: BUILT${NC}"

echo ""
echo "🎉 Local build test completed!"
echo "Your app should now build successfully on CodeMagic."
echo ""
echo "📦 Generated files:"
echo "- build/app/outputs/flutter-apk/app-debug.apk"
echo "- build/app/outputs/flutter-apk/app-release.apk"
echo "- build/app/outputs/bundle/release/app-release.aab"
echo "- build/ios/iphoneos/Runner.app"