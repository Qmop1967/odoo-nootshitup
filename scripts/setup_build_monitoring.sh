#!/bin/bash

# CodeMagic Build Monitoring Setup Script
# Sets up automatic build log fetching and analysis

echo "🔧 Setting up CodeMagic Build Monitoring..."

# Create necessary directories
mkdir -p scripts/webhook_logs
mkdir -p scripts/build_reports

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install requests flask python-dotenv

# Make scripts executable
chmod +x scripts/fetch_build_logs.py
chmod +x scripts/webhook_receiver.py

# Create environment file template
cat > scripts/.env.template << EOF
# CodeMagic API Configuration
CODEMAGIC_API_TOKEN=your_api_token_here
CODEMAGIC_APP_ID=6835ef689ead500d866e20f7

# Webhook Configuration
WEBHOOK_TOKEN=your_secret_webhook_token
WEBHOOK_URL=https://your-domain.com/webhook/codemagic

# Optional: Slack Integration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# Optional: Discord Integration
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK
EOF

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Copy scripts/.env.template to scripts/.env"
echo "2. Fill in your CodeMagic API token and other credentials"
echo "3. Set up webhook endpoint (see WEBHOOK_SETUP.md)"
echo "4. Test the setup with: python3 scripts/fetch_build_logs.py"
echo ""
echo "🔗 Get your CodeMagic API token from:"
echo "   https://codemagic.io/teams/personal-account/integrations"