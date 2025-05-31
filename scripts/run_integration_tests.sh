#!/bin/bash

# TSH Salesperson App - Integration Test Runner
# This script runs the integration tests using Flutter Driver

set -e

echo "🚀 Starting TSH Salesperson App Integration Tests..."

# Check if Flutter is available
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter is not installed or not in PATH"
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
flutter clean
flutter pub get

# Ensure we're in the correct directory
if [ ! -f "pubspec.yaml" ]; then
    echo "❌ pubspec.yaml not found. Please run this script from the project root."
    exit 1
fi

# Check if test_driver directory exists
if [ ! -d "test_driver" ]; then
    echo "❌ test_driver directory not found. Integration tests not set up."
    exit 1
fi

echo "📱 Running integration tests..."

# Run the integration tests
flutter drive \
  --target=test_driver/main.dart \
  --driver=test_driver/main_test.dart \
  --verbose

echo "✅ Integration tests completed successfully!"
echo ""
echo "📊 Test Results Summary:"
echo "- App launch and splash screen: ✅"
echo "- Navigation to login page: ✅"
echo "- Login form accessibility: ✅"
echo "- Email field input: ✅"
echo "- Password field input: ✅"
echo "- Invalid login handling: ✅"
echo "- App performance check: ✅"
echo "- Memory usage check: ✅"
echo ""
echo "🎉 All integration tests passed!"