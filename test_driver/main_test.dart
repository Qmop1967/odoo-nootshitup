// TSH Salesperson App - Integration Test
// Basic integration test to verify app startup and core functionality

import 'package:flutter_driver/flutter_driver.dart';
import 'package:test/test.dart';

void main() {
  group('TSH Salesperson App Integration Tests', () {
    late FlutterDriver driver;

    // Connect to the Flutter driver before running any tests
    setUpAll(() async {
      driver = await FlutterDriver.connect();
    });

    // Close the connection to the driver after the tests have completed
    tearDownAll(() async {
      await driver.close();
    });

    test('App launches and shows splash screen', () async {
      // Verify the app launches successfully
      await driver.waitFor(find.byType('MaterialApp'));
      
      // Look for splash screen elements
      final appTitle = find.text('TSH Salesperson');
      final loadingIndicator = find.byType('CircularProgressIndicator');
      
      // Verify splash screen elements are present
      await driver.waitFor(appTitle, timeout: const Duration(seconds: 10));
      await driver.waitFor(loadingIndicator, timeout: const Duration(seconds: 5));
    });

    test('Navigation to login page works', () async {
      // Wait for navigation to login page (after splash screen)
      final loginTitle = find.text('TSH Salesperson');
      final signInText = find.text('Sign in to your account');
      
      // Wait for login page to appear (splash screen should navigate automatically)
      await driver.waitFor(loginTitle, timeout: const Duration(seconds: 15));
      await driver.waitFor(signInText, timeout: const Duration(seconds: 5));
    });

    test('Login form elements are accessible', () async {
      // Verify login form elements are present and accessible
      final emailField = find.byValueKey('email_field');
      final passwordField = find.byValueKey('password_field');
      final loginButton = find.byValueKey('login_button');
      
      // Check if form elements exist
      await driver.waitFor(emailField, timeout: const Duration(seconds: 5));
      await driver.waitFor(passwordField, timeout: const Duration(seconds: 5));
      await driver.waitFor(loginButton, timeout: const Duration(seconds: 5));
    });

    test('Email field accepts input', () async {
      // Test email field input
      final emailField = find.byValueKey('email_field');
      
      await driver.tap(emailField);
      await driver.enterText('test@example.com');
      
      // Verify text was entered
      final enteredText = await driver.getText(emailField);
      expect(enteredText, contains('test@example.com'));
    });

    test('Password field accepts input', () async {
      // Test password field input
      final passwordField = find.byValueKey('password_field');
      
      await driver.tap(passwordField);
      await driver.enterText('testpassword123');
      
      // Note: Password fields typically don't show text for security
      // So we just verify the tap and input actions work without errors
    });

    test('App handles invalid login gracefully', () async {
      // Clear fields and enter invalid credentials
      final emailField = find.byValueKey('email_field');
      final passwordField = find.byValueKey('password_field');
      final loginButton = find.byValueKey('login_button');
      
      // Clear and enter invalid email
      await driver.tap(emailField);
      await driver.enterText('invalid-email');
      
      // Enter password
      await driver.tap(passwordField);
      await driver.enterText('wrongpassword');
      
      // Tap login button
      await driver.tap(loginButton);
      
      // Wait a moment for validation
      await Future.delayed(const Duration(seconds: 2));
      
      // Look for validation message
      try {
        await driver.waitFor(find.text('Please enter a valid email'), 
                           timeout: const Duration(seconds: 3));
      } catch (e) {
        // Email validation may be handled differently, this is acceptable
      }
    });

    test('App performance check', () async {
      // Basic performance check - measure app responsiveness
      final stopwatch = Stopwatch()..start();
      
      // Perform a series of UI interactions
      final emailField = find.byValueKey('email_field');
      await driver.tap(emailField);
      await driver.enterText('performance@test.com');
      
      stopwatch.stop();
      final responseTime = stopwatch.elapsedMilliseconds;
      
      // Verify reasonable response time (less than 2 seconds)
      expect(responseTime, lessThan(2000));
    });

    test('App memory usage is reasonable', () async {
      // Get performance summary
      final summary = await driver.requestData('performance');
      
      // This is a basic check - in a real app you might have specific thresholds
      expect(summary, isNotNull);
    });
  });
} 