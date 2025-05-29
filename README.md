# TSH Salesperson App

[![Build Status](https://api.codemagic.io/apps/YOUR_APP_ID/status_badge.svg)](https://codemagic.io/apps/YOUR_APP_ID/latest_build)

A comprehensive Flutter mobile application for TSH sales representatives to manage clients, products, orders, invoices, and payments through Odoo ERP integration.

## 🚀 Features

### 📱 Core Functionality
- **Dashboard**: Real-time sales metrics and regional breakdown
- **Client Management**: View and manage customer information
- **Product Catalog**: Browse and search available products
- **Sales Orders**: Create and track sales orders
- **Invoice Management**: View and manage customer invoices
- **Payment Tracking**: Monitor payment status and history

### 🔧 Technical Features
- **Odoo Integration**: Full ERP system connectivity
- **Offline Support**: Local data caching for offline access
- **Real-time Sync**: Automatic data synchronization
- **Responsive Design**: Optimized for mobile and tablet devices
- **Secure Authentication**: Session-based login with Odoo

## 📋 Requirements

- Flutter SDK 3.24.5 or higher
- Dart SDK 3.8.0 or higher
- Android SDK (for Android builds)
- Xcode (for iOS builds)
- Odoo ERP system (v14+ recommended)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd tsh_salesperson_app
```

### 2. Install Dependencies
```bash
flutter pub get
```

### 3. Configure Odoo Connection
Update the default server settings in `lib/pages/login_page.dart` or configure during app login.

### 4. Run the App
```bash
# Debug mode
flutter run

# Release mode
flutter run --release
```

## 🧪 Testing

### Unit Tests
```bash
flutter test
```

### Integration Tests
```bash
# With device/emulator connected
flutter drive --target=test_driver/app.dart --driver=test_driver/app_test.dart

# Or use the custom script
./scripts/run_integration_tests.sh
```

### Code Analysis
```bash
flutter analyze
```

## 📦 Building

### Android
```bash
# Debug APK
flutter build apk --debug

# Release APK
flutter build apk --release

# App Bundle (for Play Store)
flutter build appbundle --release
```

### iOS
```bash
# Debug
flutter build ios --debug

# Release
flutter build ios --release

# IPA (for App Store)
flutter build ipa --release
```

## 🔧 Configuration

### Environment Variables
The app supports the following environment configurations:

- `ODOO_SERVER_URL`: Default Odoo server URL
- `ODOO_DATABASE`: Default database name
- `DEBUG_MODE`: Enable debug logging

### Odoo Setup
Ensure your Odoo instance has the following modules installed:
- `sale_management`
- `account`
- `stock`
- `contacts`

## 📱 App Structure

```
lib/
├── config/          # App configuration
├── models/          # Data models
├── pages/           # UI screens
├── services/        # Business logic and API calls
├── widgets/         # Reusable UI components
└── main.dart        # App entry point

test/
├── widget_test.dart # Unit tests
└── test_driver/     # Integration tests

android/             # Android-specific code
ios/                 # iOS-specific code
```

## 🚀 CI/CD with Codemagic

This project is configured with Codemagic for automated building and deployment:

### Workflows
- **Development**: Feature branch testing and debug builds
- **Production**: Main branch releases to app stores
- **Hotfix**: Emergency fixes with fast deployment
- **Preview**: Quick preview builds for testing

### Build Artifacts
- Android APK and App Bundle
- iOS IPA files
- Test reports and coverage
- Code analysis reports

## 📊 Monitoring and Analytics

### Build Status
- Automated testing on every commit
- Code quality analysis
- Security vulnerability scanning
- Performance monitoring

### App Analytics
- User engagement tracking
- Crash reporting
- Performance metrics
- Feature usage statistics

## 🔒 Security

### Authentication
- Secure session management
- Token-based authentication with Odoo
- Automatic session refresh

### Data Protection
- Encrypted local storage
- Secure API communication (HTTPS)
- Data validation and sanitization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- Follow Dart/Flutter style guidelines
- Use meaningful variable and function names
- Add comments for complex logic
- Write tests for new features

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- Email: kha89ahm@gmail.com
- Create an issue in this repository
- Check the [documentation](docs/)

## 🔄 Changelog

### Version 1.0.0
- Initial release
- Odoo integration
- Core sales functionality
- Dashboard and reporting
- Mobile-optimized UI

## 🎯 Roadmap

### Upcoming Features
- [ ] Offline mode improvements
- [ ] Advanced reporting
- [ ] Push notifications
- [ ] Multi-language support
- [ ] Dark theme
- [ ] Biometric authentication

### Performance Improvements
- [ ] Image caching optimization
- [ ] Database query optimization
- [ ] UI rendering improvements
- [ ] Memory usage optimization

---

**Built with ❤️ using Flutter and Odoo** 