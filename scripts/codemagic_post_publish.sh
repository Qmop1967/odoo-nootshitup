#!/bin/bash
set -e  # exit on first failed command
set -x  # print all executed commands to the log

echo "🚀 TSH Salesperson App - Post-publish script started"

# Log build information
echo "📱 App Version: ${CM_BUILD_VERSION:-Unknown}"
echo "🏗️ Build Number: ${CM_BUILD_NUMBER:-Unknown}"
echo "🌿 Branch: ${CM_BRANCH:-Unknown}"

# Create deployment log
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "📅 Published at: $TIMESTAMP"

# Send success notification
echo "✅ TSH Salesperson App published successfully!"

# Clean up build artifacts (keep only release files)
if [ -d "build/app/outputs/flutter-apk" ]; then
    find build/app/outputs/flutter-apk -name "*debug*" -type f -delete 2>/dev/null || true
fi

# Log completion
echo "🎉 Post-publish tasks completed successfully!"
echo "📊 Deployment Status: SUCCESS"