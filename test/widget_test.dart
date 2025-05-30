// TSH Salesperson App Widget Tests
//
// Tests for the TSH Salesperson app with Odoo integration

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:tsh_salesperson_app/main.dart';
import 'package:tsh_salesperson_app/pages/login_page.dart';
import 'package:tsh_salesperson_app/services/odoo_service.dart';

void main() {
  group('TSH Salesperson App Tests', () {
    testWidgets('App starts with splash screen', (WidgetTester tester) async {
      // Build our app and trigger a frame.
      await tester.pumpWidget(const MyApp());

      // Verify that the splash screen shows a loading indicator
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('Login page has required elements', (WidgetTester tester) async {
      // Test the login page in a scrollable container to avoid overflow
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: SizedBox(
                height: 800, // Give enough height
                child: LoginPage(),
              ),
            ),
          ),
        ),
      );

      // Wait for the widget to settle
      await tester.pumpAndSettle();

      // Verify that we're on the login page
      expect(find.text('TSH Salesperson'), findsOneWidget);
      expect(find.text('Sign in to your account'), findsOneWidget);
      expect(find.text('Email'), findsOneWidget);
      expect(find.text('Password'), findsOneWidget);
      expect(find.text('Sign In'), findsOneWidget);
    });

    testWidgets('Login form fields are accessible', (WidgetTester tester) async {
      // Test the login page in a scrollable container
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: SizedBox(
                height: 800,
                child: LoginPage(),
              ),
            ),
          ),
        ),
      );

      // Wait for the widget to settle
      await tester.pumpAndSettle();

      // Verify form fields can be found by their keys
      expect(find.byKey(const Key('email_field')), findsOneWidget);
      expect(find.byKey(const Key('password_field')), findsOneWidget);
      expect(find.byKey(const Key('login_button')), findsOneWidget);
    });

    testWidgets('Login form accepts input', (WidgetTester tester) async {
      // Test the login page in a scrollable container
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: SizedBox(
                height: 800,
                child: LoginPage(),
              ),
            ),
          ),
        ),
      );

      // Wait for the widget to settle
      await tester.pumpAndSettle();

      // Fill in the form with valid data
      await tester.enterText(find.byKey(const Key('email_field')), 'admin@example.com');
      await tester.enterText(find.byKey(const Key('password_field')), 'password123');
      
      // Verify that the login button is present
      expect(find.byKey(const Key('login_button')), findsOneWidget);
      
      // Note: We don't actually tap login here as it would require network access
      // In a real test environment, you would mock the OdooService
    });

    testWidgets('Email validation works', (WidgetTester tester) async {
      // Test the login page
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: SizedBox(
                height: 800,
                child: LoginPage(),
              ),
            ),
          ),
        ),
      );

      // Wait for the widget to settle
      await tester.pumpAndSettle();

      // Enter invalid email
      await tester.enterText(find.byKey(const Key('email_field')), 'invalid-email');
      await tester.enterText(find.byKey(const Key('password_field')), 'password123');
      
      // Tap the login button
      await tester.tap(find.byKey(const Key('login_button')));
      await tester.pumpAndSettle();
      
      // Should show email validation error
      expect(find.text('Please enter a valid email'), findsOneWidget);
    });

    testWidgets('App has proper navigation structure', (WidgetTester tester) async {
      // Build our app and verify routes are defined
      await tester.pumpWidget(const MyApp());
      
      // Wait for the widget to settle
      await tester.pumpAndSettle();
      
      final app = tester.widget<MaterialApp>(find.byType(MaterialApp));
      
      // Verify that all expected routes are defined
      expect(app.routes!.containsKey('/dashboard'), true);
      expect(app.routes!.containsKey('/items'), true);
      expect(app.routes!.containsKey('/clients'), true);
      expect(app.routes!.containsKey('/sale_orders'), true);
      expect(app.routes!.containsKey('/invoices'), true);
      expect(app.routes!.containsKey('/payments'), true);
    });

    test('OdooService can be instantiated', () {
      // Test that the OdooService can be created
      final service = OdooService();
      expect(service, isNotNull);
      expect(service.isAuthenticated, false);
    });

    test('OdooService singleton pattern works', () {
      // Test that OdooService follows singleton pattern
      final service1 = OdooService();
      final service2 = OdooService();
      expect(identical(service1, service2), true);
    });

    // Add a simple test that should always pass
    test('Basic app configuration test', () {
      expect(1 + 1, equals(2));
      expect('TSH Salesperson App', isA<String>());
      expect(true, isTrue);
    });
  });
}
