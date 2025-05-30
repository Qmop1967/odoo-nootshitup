#!/bin/bash

echo "Setting up Flutter development environment for non-root user..."

# Function to switch to flutter user
switch_to_flutter() {
    echo "Switching to flutter user..."
    echo "You can now run Flutter commands safely as a non-root user."
    echo ""
    echo "To switch to the flutter user, run:"
    echo "  sudo su - flutter"
    echo ""
    echo "Or to run a single command as flutter user:"
    echo "  sudo -u flutter [command]"
    echo ""
    echo "Example Flutter commands to try:"
    echo "  sudo -u flutter flutter --version"
    echo "  sudo -u flutter flutter doctor"
    echo "  cd /home/flutter && sudo -u flutter flutter pub get"
    echo "  cd /home/flutter && sudo -u flutter flutter run"
    echo ""
}

# Check if flutter user exists
if id "flutter" &>/dev/null; then
    echo "✓ Flutter user already exists"
    switch_to_flutter
else
    echo "✗ Flutter user does not exist. Please run this script as root to create it."
    exit 1
fi

# Check if project files exist in flutter user home
if [ -f "/home/flutter/pubspec.yaml" ]; then
    echo "✓ Flutter project found in /home/flutter/"
else
    echo "✗ Flutter project not found in /home/flutter/"
    echo "Copying project files..."
    if [ -f "./pubspec.yaml" ]; then
        cp -r ./* /home/flutter/ 2>/dev/null || true
        chown -R flutter:flutter /home/flutter/
        echo "✓ Project files copied to /home/flutter/"
    else
        echo "✗ No Flutter project found in current directory"
    fi
fi

echo ""
echo "=== Flutter Development Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Switch to flutter user: sudo su - flutter"
echo "2. Navigate to project: cd /home/flutter"
echo "3. Check Flutter setup: flutter doctor"
echo "4. Install dependencies: flutter pub get"
echo "5. Run the app: flutter run"
echo ""
echo "Note: Always use the 'flutter' user for Flutter development, never root!" 