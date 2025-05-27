#!/bin/bash

# 🚀 Deploy TSH Salesperson App to Google Play Store
# This script creates a version tag to trigger Codemagic deployment

echo "🚀 Deploying TSH Salesperson App to Google Play Store"
echo "===================================================="

# Get current version or prompt for new one
CURRENT_VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
echo "Current version: $CURRENT_VERSION"

read -p "Enter new version (e.g., v1.0.0): " NEW_VERSION

if [ -z "$NEW_VERSION" ]; then
    echo "❌ Version required"
    exit 1
fi

# Validate version format
if [[ ! "$NEW_VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Invalid version format. Use: v1.0.0"
    exit 1
fi

# Check if version already exists
if git tag | grep -q "^$NEW_VERSION$"; then
    echo "❌ Version $NEW_VERSION already exists"
    exit 1
fi

echo ""
echo "🏗️  Creating deployment..."

# Ensure we're on main branch
git checkout main
git pull origin main

# Create and push version tag
git tag "$NEW_VERSION"
git push origin "$NEW_VERSION"

echo ""
echo "✅ Deployment triggered!"
echo "📧 Check your email (kha89ahm@gmail.com) for build status"
echo "🔗 Monitor build: https://codemagic.io/apps"
echo "📱 Check Google Play Console after successful build"
echo ""
echo "Version $NEW_VERSION will be automatically:"
echo "  1. Built as release AAB"
echo "  2. Signed with your keystore"
echo "  3. Uploaded to Google Play Internal Testing"
echo "  4. Available for promotion to production"
