#!/bin/bash

# TSH Salesperson App - Shorebird Token Setup
# This script helps you get your Shorebird authentication token

echo "🚀 Setting up Shorebird for TSH Salesperson App..."

# Check if Shorebird is installed
if ! command -v shorebird &> /dev/null; then
    echo "📦 Installing Shorebird CLI..."
    curl --proto '=https' --tlsv1.2 https://raw.githubusercontent.com/shorebirdtech/install/main/install.sh -sSf | bash
    
    # Add to PATH for current session
    export PATH="$HOME/.shorebird/bin:$PATH"
    
    echo "✅ Shorebird CLI installed"
else
    echo "✅ Shorebird CLI already installed"
fi

# Check Shorebird version
echo "🔧 Shorebird version:"
shorebird --version

# Login to Shorebird
echo "🔐 Logging in to Shorebird..."
echo "This will open a browser window for authentication."
read -p "Press Enter to continue..."

shorebird login

if [ $? -eq 0 ]; then
    echo "✅ Successfully logged in to Shorebird"
else
    echo "❌ Failed to login to Shorebird"
    exit 1
fi

# Check if app exists
echo "📱 Checking for existing app..."
if shorebird apps list | grep -q "com.tsh.sales.tsh_salesperson_app"; then
    echo "✅ App 'com.tsh.sales.tsh_salesperson_app' already exists"
else
    echo "📱 Creating new Shorebird app..."
    echo "App ID: com.tsh.sales.tsh_salesperson_app"
    echo "Display Name: TSH Salesperson App"
    
    # Note: You may need to create the app manually in the console
    echo "⚠️  Please create the app manually at https://console.shorebird.dev"
    echo "   - App ID: com.tsh.sales.tsh_salesperson_app"
    echo "   - Display Name: TSH Salesperson App"
    read -p "Press Enter after creating the app in the console..."
fi

# Get the authentication token
echo "🔑 Getting your Shorebird token..."
if [ -f "$HOME/.shorebird/credentials.json" ]; then
    echo "✅ Token found!"
    echo ""
    echo "🔐 Your Shorebird Token (copy this to CodeMagic):"
    echo "=================================================="
    cat "$HOME/.shorebird/credentials.json"
    echo "=================================================="
    echo ""
    echo "📋 Steps to add to CodeMagic:"
    echo "1. Go to your CodeMagic workflow"
    echo "2. Navigate to Environment Variables"
    echo "3. Add a new variable:"
    echo "   Name: SHOREBIRD_TOKEN"
    echo "   Value: (paste the token above)"
    echo "4. Save the workflow"
    echo ""
    echo "✅ Setup complete!"
else
    echo "❌ Token file not found. Please try logging in again."
    exit 1
fi

# Test the token
echo "🧪 Testing token..."
if shorebird apps list &> /dev/null; then
    echo "✅ Token is working correctly"
else
    echo "❌ Token test failed"
fi

echo ""
echo "🎉 Shorebird setup complete!"
echo "Now you can use Shorebird with CodeMagic for over-the-air updates." 