# Flutter Non-Root User Setup Guide

## Overview

This guide explains how to set up and use Flutter with a non-root user account for security and best practices. Running Flutter as root is strongly discouraged by the Flutter team.

## ✅ Setup Complete

A dedicated `flutter` user account has been created with the following setup:

- **Username**: `flutter`
- **Home Directory**: `/home/flutter`
- **Permissions**: Member of `sudo` group for administrative tasks when needed
- **Project Location**: `/home/flutter/` (TSH Salesperson app copied)

## 🔄 Switching to Flutter User

### Method 1: Switch User Session
```bash
# Switch to flutter user (recommended for development sessions)
sudo su - flutter

# You'll now be in the flutter user's home directory
pwd  # Should show: /home/flutter
```

### Method 2: Run Single Commands
```bash
# Run individual commands as flutter user
sudo -u flutter flutter --version
sudo -u flutter flutter doctor
```

### Method 3: Run Commands in Project Directory
```bash
# Navigate and run commands in the project directory
cd /home/flutter
sudo -u flutter flutter pub get
sudo -u flutter flutter run
```

## 🚀 Getting Started with Your Project

### 1. Switch to Flutter User
```bash
sudo su - flutter
```

### 2. Navigate to Project
```bash
cd /home/flutter
ls -la  # Verify project files are present
```

### 3. Check Flutter Setup
```bash
flutter doctor
```

### 4. Install Dependencies
```bash
flutter pub get
```

### 5. Run the App
```bash
# For desktop (Linux)
flutter run -d linux

# For Android (if device/emulator connected)
flutter run -d android

# List available devices
flutter devices
```

## 🛠️ Development Workflow

### Daily Development
1. **Always start by switching to flutter user**:
   ```bash
   sudo su - flutter
   cd /home/flutter
   ```

2. **Common Flutter commands**:
   ```bash
   flutter pub get          # Install dependencies
   flutter pub upgrade      # Upgrade dependencies
   flutter clean           # Clean build cache
   flutter build apk       # Build Android APK
   flutter build linux     # Build Linux desktop app
   flutter run             # Run in debug mode
   flutter test            # Run tests
   ```

### Code Editing
- You can edit code files as the flutter user
- Use your preferred editor (VS Code, Android Studio, etc.)
- Make sure the editor has access to the `/home/flutter` directory

### File Permissions
All project files are owned by the `flutter` user:
```bash
# Check file ownership
ls -la /home/flutter/

# If you need to fix permissions (run as root)
sudo chown -R flutter:flutter /home/flutter/
```

## 🔧 IDE Setup

### VS Code
1. Open VS Code as the flutter user or with proper permissions
2. Open the `/home/flutter` directory as your workspace
3. Install Flutter and Dart extensions

### Android Studio
1. Launch Android Studio
2. Open the `/home/flutter` project
3. Configure Flutter SDK path if needed

## 🐛 Troubleshooting

### Permission Issues
If you encounter permission errors:
```bash
# Fix ownership (run as root)
sudo chown -R flutter:flutter /home/flutter/

# Fix permissions
sudo chmod -R 755 /home/flutter/
```

### Flutter Doctor Issues
```bash
# Run as flutter user
sudo su - flutter
flutter doctor

# Accept Android licenses (if needed)
flutter doctor --android-licenses
```

### Snap Flutter Access
Flutter is installed via snap and should work with the flutter user. If you encounter issues:
```bash
# Check snap connections
snap connections flutter

# Refresh snap if needed
sudo snap refresh flutter
```

## 📁 Project Structure

Your TSH Salesperson app is located at:
```
/home/flutter/
├── android/
├── ios/
├── lib/
├── pubspec.yaml
├── README.md
└── ... (other project files)
```

## 🔒 Security Benefits

Using a non-root user provides:
- **Isolation**: Limits potential damage from security vulnerabilities
- **Best Practices**: Follows Flutter team recommendations
- **System Protection**: Prevents accidental system-wide changes
- **Multi-user Support**: Allows multiple developers on the same system

## 📝 Quick Reference Commands

```bash
# Switch to flutter user
sudo su - flutter

# Check Flutter version
flutter --version

# Run Flutter doctor
flutter doctor

# Install dependencies
flutter pub get

# Run app (desktop)
flutter run -d linux

# Build APK
flutter build apk

# Exit flutter user session
exit
```

## ⚠️ Important Notes

1. **Never run Flutter as root** - Always use the `flutter` user
2. **Project location** - Always work in `/home/flutter/`
3. **Permissions** - If you modify files as root, fix ownership with `chown`
4. **IDE access** - Ensure your IDE can access the flutter user's files
5. **Environment** - The flutter user has the same Flutter installation as root

## 🎯 Next Steps

1. Switch to the flutter user: `sudo su - flutter`
2. Navigate to your project: `cd /home/flutter`
3. Run Flutter doctor: `flutter doctor`
4. Install dependencies: `flutter pub get`
5. Start developing: `flutter run`

Your TSH Salesperson app is ready for development with the secure, non-root flutter user account! 