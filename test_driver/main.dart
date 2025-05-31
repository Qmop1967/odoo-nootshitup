// TSH Salesperson App - Integration Test Driver
// This file enables Flutter Driver for integration testing

import 'package:flutter_driver/driver_extension.dart';
import 'package:tsh_salesperson_app/main.dart' as app;

void main() {
  // Enable Flutter Driver extension
  enableFlutterDriverExtension();
  
  // Run the app
  app.main();
} 