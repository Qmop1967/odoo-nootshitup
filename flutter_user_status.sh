#!/bin/bash

echo "=== Flutter Non-Root User Setup Status ==="
echo ""

# Check if flutter user exists
if id "flutter" &>/dev/null; then
    echo "✅ Flutter user account: EXISTS"
    echo "   Username: flutter"
    echo "   Home: /home/flutter"
    echo "   Groups: $(groups flutter)"
else
    echo "❌ Flutter user account: NOT FOUND"
    exit 1
fi

# Check project files
if [ -f "/home/flutter/pubspec.yaml" ]; then
    echo "✅ Flutter project: FOUND in /home/flutter/"
    echo "   Project files copied successfully"
else
    echo "❌ Flutter project: NOT FOUND in /home/flutter/"
fi

# Check file ownership
OWNER=$(stat -c '%U' /home/flutter 2>/dev/null)
if [ "$OWNER" = "flutter" ]; then
    echo "✅ File ownership: CORRECT (flutter user owns files)"
else
    echo "❌ File ownership: INCORRECT (owned by $OWNER)"
fi

# Test Flutter installation
echo ""
echo "=== Flutter Installation Test ==="
if sudo -u flutter flutter --version >/dev/null 2>&1; then
    echo "✅ Flutter command: WORKING"
    FLUTTER_VERSION=$(sudo -u flutter flutter --version 2>/dev/null | head -1)
    echo "   Version: $FLUTTER_VERSION"
else
    echo "❌ Flutter command: FAILED"
fi

# Test Flutter doctor
echo ""
echo "=== Flutter Doctor Summary ==="
cd /home/flutter
sudo -u flutter flutter doctor 2>/dev/null | grep -E "^\[|Doctor found"

echo ""
echo "=== Quick Start Commands ==="
echo "To start developing with the flutter user:"
echo ""
echo "1. Switch to flutter user:"
echo "   sudo su - flutter"
echo ""
echo "2. Navigate to project:"
echo "   cd /home/flutter"
echo ""
echo "3. Install dependencies:"
echo "   flutter pub get"
echo ""
echo "4. Run the app:"
echo "   flutter run -d linux"
echo ""
echo "=== Security Note ==="
echo "✅ You are now set up to use Flutter safely without root privileges!"
echo "❌ Never run 'flutter' commands as root user again."
echo "" 