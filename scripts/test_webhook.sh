#!/bin/bash

# 🔗 TSH Salesperson App - Webhook Test Script
# This script helps test your Codemagic webhook integration

echo "🔗 TSH Salesperson App - Webhook Integration Test"
echo "================================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

WEBHOOK_URL="https://api.codemagic.io/hooks/68322e9bb94731dd4aa3a9b5"

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo ""
echo "🔍 Testing webhook integration..."
echo ""

# 1. Check if we're in a git repository
echo "📁 1. Repository Validation"
echo "---------------------------"

if git rev-parse --git-dir > /dev/null 2>&1; then
    log_success "Git repository detected"
    
    # Get current branch
    CURRENT_BRANCH=$(git branch --show-current)
    log_info "Current branch: $CURRENT_BRANCH"
    
    # Get remote URL
    REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "No remote configured")
    log_info "Remote URL: $REMOTE_URL"
    
else
    log_error "Not in a git repository"
    echo "Please run this script from your project root directory."
    exit 1
fi

echo ""

# 2. Check webhook URL accessibility
echo "🌐 2. Webhook URL Validation"
echo "----------------------------"

log_info "Testing webhook URL: $WEBHOOK_URL"

if command -v curl &> /dev/null; then
    # Test webhook URL (expect 405 Method Not Allowed for GET request)
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$WEBHOOK_URL")
    
    if [ "$HTTP_CODE" = "405" ]; then
        log_success "Webhook URL is accessible (405 Method Not Allowed is expected for GET)"
    elif [ "$HTTP_CODE" = "200" ]; then
        log_success "Webhook URL is accessible"
    else
        log_warning "Webhook URL returned HTTP $HTTP_CODE"
    fi
else
    log_warning "curl not available, skipping URL test"
fi

echo ""

# 3. Check codemagic.yaml configuration
echo "📋 3. Codemagic Configuration"
echo "-----------------------------"

if [ -f "codemagic.yaml" ]; then
    log_success "codemagic.yaml found"
    
    # Check workflow triggers
    if grep -q "develop" codemagic.yaml; then
        log_success "Development workflow configured"
    else
        log_warning "Development workflow not found"
    fi
    
    if grep -q "main" codemagic.yaml; then
        log_success "Production workflow configured"
    else
        log_warning "Production workflow not found"
    fi
    
    if grep -q "feature/" codemagic.yaml; then
        log_success "Feature branch workflow configured"
    else
        log_warning "Feature branch workflow not found"
    fi
    
else
    log_error "codemagic.yaml not found"
fi

echo ""

# 4. Suggest test scenarios
echo "🧪 4. Test Scenarios"
echo "--------------------"

log_info "To test your webhook integration, try these scenarios:"
echo ""

echo "📝 Test Development Build:"
echo "   git checkout -b develop (if not exists)"
echo "   git push origin develop"
echo ""

echo "📝 Test Feature Build:"
echo "   git checkout -b feature/test-webhook"
echo "   echo '# Test change' >> README.md"
echo "   git add README.md"
echo "   git commit -m 'Test webhook trigger'"
echo "   git push origin feature/test-webhook"
echo ""

echo "📝 Test Production Build:"
echo "   git checkout main"
echo "   git push origin main"
echo "   # OR create a version tag:"
echo "   git tag v1.0.0"
echo "   git push origin v1.0.0"
echo ""

# 5. Check for recent commits
echo "📊 5. Recent Activity"
echo "--------------------"

log_info "Recent commits:"
git log --oneline -5 2>/dev/null || log_warning "Cannot read git log"

echo ""

# 6. Webhook setup instructions
echo "🔧 6. Webhook Setup Instructions"
echo "--------------------------------"

echo "To configure the webhook in your repository:"
echo ""

if [[ "$REMOTE_URL" == *"github.com"* ]]; then
    echo "📍 GitHub Setup:"
    echo "   1. Go to: Repository → Settings → Webhooks"
    echo "   2. Add webhook with URL: $WEBHOOK_URL"
    echo "   3. Content type: application/json"
    echo "   4. Events: Push, Pull requests, Create (tags)"
elif [[ "$REMOTE_URL" == *"gitlab.com"* ]]; then
    echo "📍 GitLab Setup:"
    echo "   1. Go to: Repository → Settings → Webhooks"
    echo "   2. Add webhook with URL: $WEBHOOK_URL"
    echo "   3. Triggers: Push, Tag push, Merge requests"
elif [[ "$REMOTE_URL" == *"bitbucket.org"* ]]; then
    echo "📍 Bitbucket Setup:"
    echo "   1. Go to: Repository → Settings → Webhooks"
    echo "   2. Add webhook with URL: $WEBHOOK_URL"
    echo "   3. Triggers: Repository push, Pull request events"
else
    echo "📍 Generic Git Setup:"
    echo "   Configure webhook in your git provider with:"
    echo "   URL: $WEBHOOK_URL"
    echo "   Events: Push, Pull requests, Tags"
fi

echo ""

# 7. Monitoring instructions
echo "📱 7. Build Monitoring"
echo "----------------------"

echo "After configuring the webhook:"
echo "✅ Monitor builds at: https://codemagic.io/apps"
echo "✅ Check email notifications at: kha89ahm@gmail.com"
echo "✅ View build logs and artifacts in Codemagic dashboard"

echo ""
echo "🎯 Summary"
echo "=========="
echo "Webhook URL: $WEBHOOK_URL"
echo "Current Branch: $CURRENT_BRANCH"
echo "Repository: $REMOTE_URL"
echo ""
echo "📖 For detailed setup instructions, see: CODEMAGIC_WEBHOOK_SETUP.md"
echo ""

log_success "Webhook test completed! Configure the webhook in your repository to start automated builds."