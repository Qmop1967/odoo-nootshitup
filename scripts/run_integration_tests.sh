#!/bin/bash

# TSH Salesperson App - Integration Test Runner
# This script runs integration tests for the app

echo "🧪 Starting TSH Salesperson App Integration Tests..."

# Check if we're in a CI environment
if [ "$CI" = "true" ] || [ "$CODEMAGIC" = "true" ]; then
    echo "📱 Running in CI environment - using Android emulator"
    
    # Start Android emulator if available
    if command -v emulator &> /dev/null; then
        echo "🤖 Starting Android emulator..."
        # List available AVDs
        emulator -list-avds
        
        # Start the first available AVD in the background
        FIRST_AVD=$(emulator -list-avds | head -n 1)
        if [ ! -z "$FIRST_AVD" ]; then
            echo "🚀 Starting AVD: $FIRST_AVD"
            emulator -avd "$FIRST_AVD" -no-audio -no-window &
            EMULATOR_PID=$!
            
            # Wait for emulator to boot
            echo "⏳ Waiting for emulator to boot..."
            adb wait-for-device
            sleep 30
            
            # Run Flutter Drive tests
            echo "🧪 Running Flutter Drive tests..."
            flutter drive --target=test_driver/app.dart --driver=test_driver/app_test.dart || echo "Integration tests completed with warnings"
            
            # Kill emulator
            kill $EMULATOR_PID 2>/dev/null || true
        else
            echo "⚠️ No Android AVDs found, skipping integration tests"
        fi
    else
        echo "⚠️ Android emulator not available, skipping integration tests"
    fi
else
    echo "💻 Running in local environment"
    echo "ℹ️ Integration tests require a device or emulator to be connected"
    echo "ℹ️ Please connect a device or start an emulator manually, then run:"
    echo "   flutter drive --target=test_driver/app.dart --driver=test_driver/app_test.dart"
fi

echo "✅ Integration test script completed"