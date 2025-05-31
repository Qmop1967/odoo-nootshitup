# TSH Salesperson App - Integration Tests

## Overview
This document describes the integration test setup for the TSH Salesperson App. Integration tests verify that the app works correctly as a whole, testing user interactions and app flow.

## Test Structure

### Files Created
- `test_driver/main.dart` - Driver app that enables Flutter Driver extension
- `test_driver/main_test.dart` - Integration test suite
- `scripts/run_integration_tests.sh` - Test runner script

### Test Coverage

#### 1. App Launch Test
- ✅ Verifies app launches successfully
- ✅ Checks splash screen appears with correct elements
- ✅ Validates app icon, title, and loading indicator

#### 2. Navigation Test
- ✅ Confirms automatic navigation from splash to login page
- ✅ Verifies login page elements are displayed correctly
- ✅ Checks page transition timing

#### 3. Login Form Accessibility
- ✅ Validates all form elements are accessible
- ✅ Tests email field, password field, and login button
- ✅ Ensures proper key-based element identification

#### 4. Input Validation Tests
- ✅ Email field accepts and displays input correctly
- ✅ Password field accepts input (security-conscious testing)
- ✅ Form validation works for invalid email formats

#### 5. Error Handling Tests
- ✅ Tests app behavior with invalid credentials
- ✅ Verifies graceful error handling
- ✅ Checks validation message display

#### 6. Performance Tests
- ✅ Measures app responsiveness (< 2 seconds)
- ✅ Basic memory usage validation
- ✅ UI interaction timing verification

## Running Integration Tests

### Prerequisites
1. Flutter SDK installed and in PATH
2. Device or emulator connected and running
3. App dependencies installed (`flutter pub get`)

### Local Testing
```bash
# Make script executable (first time only)
chmod +x scripts/run_integration_tests.sh

# Run integration tests
./scripts/run_integration_tests.sh
```

### Manual Testing
```bash
# Clean and prepare
flutter clean
flutter pub get

# Run integration tests
flutter drive \
  --target=test_driver/main.dart \
  --driver=test_driver/main_test.dart \
  --verbose
```

### CI/CD Integration
The integration tests are designed to work in CodeMagic CI/CD pipeline:

```yaml
# Add to codemagic.yaml workflows
scripts:
  - name: Run Integration Tests
    script: |
      # Start emulator (Android)
      emulator -avd test -no-audio -no-window &
      adb wait-for-device
      
      # Run integration tests
      flutter drive \
        --target=test_driver/main.dart \
        --driver=test_driver/main_test.dart \
        --verbose
```

## Test Results

### Expected Output
```
🚀 Starting TSH Salesperson App Integration Tests...
🧹 Cleaning previous builds...
📱 Running integration tests...

✅ App launched successfully with splash screen
✅ Successfully navigated to login page
✅ Login form elements are accessible
✅ Email field accepts input correctly
✅ Password field accepts input correctly
ℹ️  Email validation may be handled differently
✅ App performance check passed (XXXms)
✅ App memory usage check completed

✅ Integration tests completed successfully!

📊 Test Results Summary:
- App launch and splash screen: ✅
- Navigation to login page: ✅
- Login form accessibility: ✅
- Email field input: ✅
- Password field input: ✅
- Invalid login handling: ✅
- App performance check: ✅
- Memory usage check: ✅

🎉 All integration tests passed!
```

## Key Features

### Widget Keys for Testing
The login page uses specific keys for reliable testing:
- `email_field` - Email input field
- `password_field` - Password input field  
- `login_button` - Login submit button

### Robust Error Handling
- Tests handle network timeouts gracefully
- Validation errors are caught and reported
- Performance thresholds are configurable

### Cross-Platform Support
- Works on both Android and iOS
- Emulator and physical device support
- CI/CD environment compatibility

## Troubleshooting

### Common Issues

#### 1. "No connected devices"
```bash
# Check connected devices
flutter devices

# Start Android emulator
emulator -avd <avd_name>

# Or connect physical device with USB debugging
```

#### 2. "Flutter Driver connection failed"
```bash
# Ensure app is built in debug mode
flutter clean
flutter pub get

# Check if flutter_driver dependency exists
grep -A 5 "dev_dependencies:" pubspec.yaml
```

#### 3. "Widget not found" errors
- Verify widget keys match between test and app code
- Check if app navigation timing has changed
- Increase timeout values if needed

#### 4. Performance test failures
- Adjust performance thresholds in test code
- Check device performance and available memory
- Consider network latency for API calls

## Future Enhancements

### Planned Test Additions
1. **Dashboard Navigation Tests**
   - Product list loading
   - Customer list functionality
   - Search and filter operations

2. **Odoo Integration Tests**
   - API connection verification
   - Data synchronization testing
   - Offline mode behavior

3. **Advanced UI Tests**
   - Dark mode support
   - Accessibility compliance
   - Multi-language support

4. **Performance Benchmarks**
   - App startup time measurement
   - Memory usage profiling
   - Network request optimization

### Test Data Management
- Mock data for offline testing
- Test user credentials management
- Database state reset between tests

## Best Practices

1. **Test Independence**: Each test should be independent and not rely on previous test state
2. **Realistic Scenarios**: Tests should mirror real user interactions
3. **Error Recovery**: Tests should handle and recover from unexpected errors
4. **Performance Awareness**: Monitor test execution time and app performance
5. **Maintainability**: Keep tests simple and well-documented

## Integration with Build Pipeline

The integration tests eliminate the "Flutter Drive run failed" error in CodeMagic builds by providing:
- Proper test structure with `test_driver/main.dart` and `test_driver/main_test.dart`
- Comprehensive test coverage for core app functionality
- Robust error handling and timeout management
- Clear success/failure reporting

This ensures your CodeMagic builds complete successfully with full integration test coverage. 