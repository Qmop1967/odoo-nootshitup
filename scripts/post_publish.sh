#!/bin/bash
set -e  # exit on first failed command
set -x  # print all executed commands to the log

echo "🚀 Starting post-publish script for TSH Salesperson App"

# Get the current date and time for logging
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "📅 Post-publish started at: $TIMESTAMP"

# Check if we're in a CI environment
if [ -n "$CI" ]; then
    echo "🔧 Running in CI environment"
    
    # Log build information
    echo "📱 App Version: ${CM_BUILD_VERSION:-Unknown}"
    echo "🏗️ Build Number: ${CM_BUILD_NUMBER:-Unknown}"
    echo "🌿 Branch: ${CM_BRANCH:-Unknown}"
    echo "📦 Build Type: ${CM_BUILD_TYPE:-Unknown}"
fi

# Function to send notification (placeholder for future integrations)
send_notification() {
    local message="$1"
    echo "📢 Notification: $message"
    
    # TODO: Add integrations for:
    # - Slack notifications
    # - Email notifications
    # - Discord webhooks
    # - Teams notifications
}

# Function to update deployment status
update_deployment_status() {
    local status="$1"
    echo "📊 Deployment Status: $status"
    
    # Create a deployment log entry
    echo "{
        \"timestamp\": \"$TIMESTAMP\",
        \"status\": \"$status\",
        \"version\": \"${CM_BUILD_VERSION:-Unknown}\",
        \"build_number\": \"${CM_BUILD_NUMBER:-Unknown}\",
        \"branch\": \"${CM_BRANCH:-Unknown}\"
    }" >> deployment_log.json
}

# Function to clean up temporary files
cleanup_temp_files() {
    echo "🧹 Cleaning up temporary files..."
    
    # Remove build artifacts that are no longer needed
    if [ -d "build/app/outputs/flutter-apk" ]; then
        echo "📁 Cleaning APK build directory..."
        # Keep only the release APK, remove debug builds
        find build/app/outputs/flutter-apk -name "*debug*" -type f -delete 2>/dev/null || true
    fi
    
    if [ -d "build/app/outputs/bundle" ]; then
        echo "📁 Cleaning AAB build directory..."
        # Keep only release bundles
        find build/app/outputs/bundle -name "*debug*" -type f -delete 2>/dev/null || true
    fi
    
    echo "✅ Cleanup completed"
}

# Function to backup important files
backup_release_artifacts() {
    echo "💾 Backing up release artifacts..."
    
    BACKUP_DIR="release_backups/$(date '+%Y%m%d_%H%M%S')"
    mkdir -p "$BACKUP_DIR"
    
    # Backup APK if exists
    if [ -f "build/app/outputs/flutter-apk/app-release.apk" ]; then
        cp "build/app/outputs/flutter-apk/app-release.apk" "$BACKUP_DIR/"
        echo "📱 APK backed up to $BACKUP_DIR/"
    fi
    
    # Backup AAB if exists
    if [ -f "build/app/outputs/bundle/release/app-release.aab" ]; then
        cp "build/app/outputs/bundle/release/app-release.aab" "$BACKUP_DIR/"
        echo "📦 AAB backed up to $BACKUP_DIR/"
    fi
    
    # Backup pubspec.yaml for version tracking
    if [ -f "pubspec.yaml" ]; then
        cp "pubspec.yaml" "$BACKUP_DIR/"
        echo "📄 pubspec.yaml backed up"
    fi
    
    echo "✅ Backup completed"
}

# Function to update version tracking
update_version_tracking() {
    echo "📝 Updating version tracking..."
    
    # Extract version from pubspec.yaml
    if [ -f "pubspec.yaml" ]; then
        VERSION=$(grep "^version:" pubspec.yaml | cut -d' ' -f2)
        echo "📊 Current version: $VERSION"
        
        # Log the release
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Version $VERSION published successfully" >> release_history.log
    fi
    
    echo "✅ Version tracking updated"
}

# Function to generate release notes
generate_release_notes() {
    echo "📋 Generating release notes..."
    
    # Get the latest commits since last tag
    if git describe --tags --abbrev=0 >/dev/null 2>&1; then
        LAST_TAG=$(git describe --tags --abbrev=0)
        echo "🏷️ Last tag: $LAST_TAG"
        
        # Generate changelog
        git log --pretty=format:"- %s" "$LAST_TAG"..HEAD > latest_changes.md
        echo "📄 Latest changes saved to latest_changes.md"
    else
        echo "ℹ️ No previous tags found, skipping changelog generation"
    fi
    
    echo "✅ Release notes generated"
}

# Main execution flow
echo "🔄 Executing post-publish tasks..."

# Update deployment status to success
update_deployment_status "success"

# Send success notification
send_notification "✅ TSH Salesperson App published successfully!"

# Backup release artifacts
backup_release_artifacts

# Update version tracking
update_version_tracking

# Generate release notes
generate_release_notes

# Clean up temporary files
cleanup_temp_files

# Final success message
echo "🎉 Post-publish script completed successfully!"
echo "📅 Finished at: $(date '+%Y-%m-%d %H:%M:%S')"

# Optional: Create a success marker file
touch .post_publish_success

echo "✨ All post-publish tasks completed successfully!"