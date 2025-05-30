#!/bin/bash

echo "🚀 Setting up Flutter Development Environment for TSH Salesperson App"
echo "=================================================================="

# Create the setup script for flutterdev user
cat > /home/flutterdev/setup_flutter_environment.sh << 'EOF'
#!/bin/bash

echo "🚀 Setting up Flutter Development Environment for TSH Salesperson App"
echo "=================================================================="

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential development tools
echo "🛠️ Installing development tools..."
sudo apt install -y \
    curl \
    git \
    unzip \
    xz-utils \
    zip \
    libglu1-mesa \
    build-essential \
    libssl-dev \
    pkg-config \
    libnss3-dev \
    libatk-bridge2.0-dev \
    libdrm2 \
    libxkbcommon0 \
    libgtk-3-dev

# Install Node.js (for MCP servers)
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python development tools
echo "🐍 Installing Python development tools..."
sudo apt install -y python3-pip python3-venv python3-dev

# Set up Flutter SDK
echo "📱 Setting up Flutter SDK..."
cd /home/flutterdev

# Download Flutter if not already present
if [ ! -d "flutter" ]; then
    echo "⬇️ Downloading Flutter SDK..."
    wget -q https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.24.5-stable.tar.xz
    tar xf flutter_linux_3.24.5-stable.tar.xz
    rm flutter_linux_3.24.5-stable.tar.xz
fi

# Add Flutter to PATH
echo "🔧 Configuring Flutter PATH..."
if ! grep -q "flutter/bin" ~/.bashrc; then
    echo 'export PATH="$PATH:/home/flutterdev/flutter/bin"' >> ~/.bashrc
fi

# Source the updated PATH
export PATH="$PATH:/home/flutterdev/flutter/bin"

# Install Android SDK
echo "📱 Setting up Android SDK..."
mkdir -p /home/flutterdev/Android/Sdk
cd /home/flutterdev/Android/Sdk

# Download Android command line tools
if [ ! -d "cmdline-tools" ]; then
    echo "⬇️ Downloading Android command line tools..."
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
    unzip -q commandlinetools-linux-11076708_latest.zip
    mkdir -p cmdline-tools/latest
    mv cmdline-tools/* cmdline-tools/latest/ 2>/dev/null || true
    rm commandlinetools-linux-11076708_latest.zip
fi

# Set Android environment variables
echo "🔧 Configuring Android environment..."
if ! grep -q "ANDROID_HOME" ~/.bashrc; then
    cat >> ~/.bashrc << 'ENVEOF'

# Android SDK
export ANDROID_HOME=/home/flutterdev/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/emulator
ENVEOF
fi

# Source the updated environment
export ANDROID_HOME=/home/flutterdev/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/emulator

# Accept Android licenses and install required packages
echo "📋 Accepting Android licenses..."
yes | sdkmanager --licenses 2>/dev/null || true

echo "📦 Installing Android SDK packages..."
sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0" 2>/dev/null || true

# Set up Flutter project dependencies
echo "📱 Setting up Flutter project..."
cd /home/flutterdev

# Get Flutter dependencies
echo "📦 Getting Flutter dependencies..."
flutter pub get

# Set up MCP environment
echo "🔧 Setting up MCP environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install mcp requests

# Make MCP server executable
chmod +x /home/flutterdev/mcp_servers/tsh_flutter_mcp.py

# Update MCP configuration for flutterdev user
echo "🔧 Updating MCP configuration..."
mkdir -p /home/flutterdev/.cursor

cat > /home/flutterdev/.cursor/mcp.json << 'MCPEOF'
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/home/flutterdev"
      ],
      "env": {}
    },
    "memory": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-memory"
      ],
      "env": {}
    },
    "git": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-git",
        "--repository",
        "/home/flutterdev"
      ],
      "env": {}
    },
    "tsh-flutter": {
      "command": "/home/flutterdev/.venv/bin/python",
      "args": [
        "/home/flutterdev/mcp_servers/tsh_flutter_mcp.py"
      ],
      "env": {
        "PYTHONPATH": "/home/flutterdev"
      }
    }
  }
}
MCPEOF

# Set proper permissions
sudo chown -R flutterdev:flutterdev /home/flutterdev/

echo ""
echo "✅ Flutter Development Environment Setup Complete!"
echo "=================================================="
echo ""
echo "👤 User Details:"
echo "   Username: flutterdev"
echo "   Password: FlutterTSH2024!"
echo "   Home Directory: /home/flutterdev"
echo ""
echo "📱 Flutter Setup:"
echo "   Flutter SDK: /home/flutterdev/flutter"
echo "   Android SDK: /home/flutterdev/Android/Sdk"
echo "   Project Location: /home/flutterdev"
echo ""
echo "🔧 MCP Configuration:"
echo "   Config File: /home/flutterdev/.cursor/mcp.json"
echo "   Custom Server: /home/flutterdev/mcp_servers/tsh_flutter_mcp.py"
echo ""
echo "🚀 Next Steps:"
echo "   1. Switch to flutterdev user: su - flutterdev"
echo "   2. Source environment: source ~/.bashrc"
echo "   3. Test Flutter: flutter doctor"
echo "   4. Run app: flutter run"
echo ""
echo "🔐 SSH Access:"
echo "   ssh flutterdev@your-server-ip"
echo "   Password: FlutterTSH2024!"
echo ""
echo "💡 Development Commands:"
echo "   flutter analyze          # Check code quality"
echo "   flutter test             # Run tests"
echo "   flutter build apk        # Build Android APK"
echo "   flutter build appbundle  # Build Android App Bundle"
echo ""
EOF

# Make the setup script executable
chmod +x /home/flutterdev/setup_flutter_environment.sh

# Set proper ownership
chown flutterdev:flutterdev /home/flutterdev/setup_flutter_environment.sh

echo "✅ Flutter user setup script created!"
echo "📍 Location: /home/flutterdev/setup_flutter_environment.sh"
echo ""
echo "🚀 To complete the setup:"
echo "   1. Switch to flutterdev user: su - flutterdev"
echo "   2. Run the setup script: ./setup_flutter_environment.sh"
echo ""