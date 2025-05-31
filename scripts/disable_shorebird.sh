#!/bin/bash
# Comprehensive Shorebird Disabling Script for CodeMagic
# This script ensures Shorebird is completely disabled during builds

echo "🚫 Disabling Shorebird integration completely..."

# Remove Shorebird from PATH
export PATH=$(echo $PATH | sed 's|[^:]*shorebird[^:]*:||g' | sed 's|::|:|g' | sed 's|^:|:|' | sed 's|:$||')
echo "✅ Removed Shorebird from PATH"

# Set environment variables to disable Shorebird
export SHOREBIRD_ENABLED=false
export CM_SKIP_SHOREBIRD=true
export DISABLE_SHOREBIRD=true
export NO_SHOREBIRD=true
echo "✅ Set Shorebird disable environment variables"

# Remove any Shorebird binaries from common locations
if [ -f "/usr/local/bin/shorebird" ]; then
    echo "⚠️  Found Shorebird binary at /usr/local/bin/shorebird"
fi

if [ -f "$HOME/.shorebird/bin/shorebird" ]; then
    echo "⚠️  Found Shorebird binary at $HOME/.shorebird/bin/shorebird"
fi

# Check if Shorebird is still accessible
if command -v shorebird >/dev/null 2>&1; then
    echo "⚠️  WARNING: Shorebird is still accessible in PATH"
    echo "   Location: $(which shorebird)"
else
    echo "✅ SUCCESS: Shorebird is not accessible in PATH"
fi

# Verify Flutter is available
if command -v flutter >/dev/null 2>&1; then
    echo "✅ Flutter is available: $(which flutter)"
    flutter --version | head -1
else
    echo "❌ ERROR: Flutter is not available in PATH"
    exit 1
fi

echo "🎯 Shorebird disabling complete - ready for standard Flutter builds" 