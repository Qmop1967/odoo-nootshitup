# TSH Salesperson App - Development Setup Guide

## Prerequisites

### Required Software
- Flutter SDK 3.32.0 or later
- Android Studio or VS Code with Flutter extensions
- Android SDK (API level 35)
- Git

### Optional Tools
- Shorebird CLI (for code push updates)
- Firebase CLI (if using Firebase services)

## Initial Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd tsh-salesperson-app
```

### 2. Install Dependencies
```bash
flutter pub get
```

### 3. Configure Odoo Connection
Edit `lib/config/app_config.dart` and update:
- `defaultOdooUrl`: Your Odoo server URL
- `defaultDatabase`: Your Odoo database name

### 4. Android Setup
1. Ensure Android SDK is installed with API level 35
2. Create a keystore for signing (production builds):
   ```bash
   keytool -genkey -v -keystore android/app/tsh-salesperson-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias tsh-salesperson
   ```
3. Update `android/key.properties` with your keystore details

### 5. Shorebird Setup (Optional)
1. Install Shorebird CLI
2. Login to Shorebird: `shorebird login`
3. Update `shorebird.yaml` with your app IDs and keys

## Development Workflow

### Running the App
```bash
# Debug mode
flutter run

# Release mode
flutter run --release
```

### Building the App
```bash
# Use the provided build script
./build_app.sh

# Or manually:
flutter build apk --release
flutter build appbundle --release
```

### Code Analysis
```bash
flutter analyze
```

### Testing
```bash
flutter test
```

## Project Structure

```
lib/
├── config/          # App configuration
├── models/          # Data models
├── pages/           # UI screens
├── services/        # API services
├── widgets/         # Reusable UI components
└── main.dart        # App entry point

android/             # Android-specific files
ios/                 # iOS-specific files (if needed)
```

## Key Features

### Authentication
- Odoo session-based authentication
- Persistent session storage
- Automatic session validation

### Dashboard
- Real-time sales data
- Regional breakdown
- Quick statistics

### Data Management
- Products/Items listing
- Customer management
- Sales orders tracking
- Invoice management
- Payment tracking

### Offline Support
- Session persistence
- Cached data display
- Graceful error handling

## Configuration Files

### `lib/config/app_config.dart`
Central configuration for:
- API endpoints
- UI settings
- Feature flags
- Error messages

### `shorebird.yaml`
Code push configuration for instant updates

### `android/app/build.gradle`
Android build configuration

## Troubleshooting

### Build Issues
1. **Gradle Plugin Version**: Ensure Android Gradle Plugin is 8.3.0+
2. **SDK Version**: Use Android SDK API level 35
3. **Dependencies**: Run `flutter pub get` after any pubspec.yaml changes

### Authentication Issues
1. Verify Odoo server URL and database name
2. Check network connectivity
3. Ensure Odoo user has proper permissions

### Performance Issues
1. Use release builds for performance testing
2. Monitor memory usage with Flutter Inspector
3. Optimize API calls and data loading

## Deployment

### Google Play Store
1. Build AAB: `flutter build appbundle --release`
2. Upload to Google Play Console
3. Follow Play Store guidelines

### Code Push Updates
1. Make code changes
2. Create Shorebird patch: `shorebird patch android`
3. Users receive updates automatically

## Best Practices

### Code Quality
- Follow Dart/Flutter style guidelines
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions small and focused

### Error Handling
- Always handle API errors gracefully
- Provide user-friendly error messages
- Log errors for debugging

### Performance
- Use const constructors where possible
- Implement lazy loading for large lists
- Cache frequently accessed data
- Optimize image loading

### Security
- Never commit sensitive data (keys, passwords)
- Use environment variables for configuration
- Validate all user inputs
- Implement proper session management

## Support

For development questions or issues:
1. Check this documentation
2. Review Flutter documentation
3. Check Odoo API documentation
4. Create an issue in the project repository