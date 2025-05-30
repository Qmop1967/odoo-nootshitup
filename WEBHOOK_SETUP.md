# 🔗 CodeMagic Webhook Setup Guide

## 🎯 Overview

This guide shows you how to set up automatic build feedback from CodeMagic using webhooks and API integration. You'll get real-time notifications and detailed error analysis for every build.

## 🚀 Quick Setup

### 1. **Install Dependencies**
```bash
chmod +x scripts/setup_build_monitoring.sh
./scripts/setup_build_monitoring.sh
```

### 2. **Configure Environment**
```bash
cp scripts/.env.template scripts/.env
# Edit scripts/.env with your credentials
```

### 3. **Get CodeMagic API Token**
1. Go to [CodeMagic Integrations](https://codemagic.io/teams/personal-account/integrations)
2. Click **"Create new token"**
3. Copy the token to your `.env` file

## 🔧 Setup Methods

### **Method 1: Webhook Receiver (Real-time)**

#### **A. Deploy Webhook Receiver**
```bash
# Local testing
python3 scripts/webhook_receiver.py

# Or deploy to cloud (Heroku, Railway, etc.)
```

#### **B. Configure CodeMagic Environment Variables**
In your CodeMagic app settings, add:
```
WEBHOOK_URL = https://your-domain.com/webhook/codemagic
WEBHOOK_TOKEN = your-secret-token
```

#### **C. Test Webhook**
```bash
curl -X POST https://your-domain.com/webhook/codemagic \
  -H "Authorization: Bearer your-secret-token" \
  -H "Content-Type: application/json" \
  -d '{"build_id":"test","status":"finished"}'
```

### **Method 2: Manual Log Fetching**

#### **Fetch Latest Build Logs**
```bash
export CODEMAGIC_API_TOKEN="your_token"
python3 scripts/fetch_build_logs.py
```

#### **Automated Fetching (Cron Job)**
```bash
# Add to crontab for every 10 minutes
*/10 * * * * cd /path/to/project && python3 scripts/fetch_build_logs.py
```

## 📊 What You Get

### **Automatic Analysis**
- ✅ **iOS signing errors** detection
- ✅ **Android build failures** analysis
- ✅ **Performance metrics** tracking
- ✅ **Success/failure** notifications
- ✅ **Detailed recommendations**

### **Real-time Notifications**
- 📧 **Email** (built into CodeMagic)
- 💬 **Slack** integration
- 🎮 **Discord** webhooks
- 📱 **Custom** endpoints

### **Build Reports**
```json
{
  "build_info": {
    "id": "build_123",
    "number": 15,
    "status": "failed",
    "workflow": "production",
    "duration": 1200
  },
  "analysis": {
    "ios_errors": [
      "No matching profiles found for bundle identifier"
    ],
    "android_errors": [],
    "success": false
  },
  "recommendations": [
    "Check iOS code signing configuration",
    "Verify Apple Developer account settings"
  ]
}
```

## 🔍 Error Detection Patterns

### **iOS Errors**
- Code signing failures
- Provisioning profile issues
- Certificate problems
- Xcode build errors
- CocoaPods issues

### **Android Errors**
- Gradle build failures
- Keystore problems
- Signing issues
- AAPT errors
- Dependency conflicts

## 🌐 Deployment Options

### **Option 1: Heroku (Free)**
```bash
# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set WEBHOOK_TOKEN=your-token

# Deploy
git add scripts/
git commit -m "Add webhook receiver"
git push heroku main
```

### **Option 2: Railway**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

### **Option 3: Local with ngrok**
```bash
# Install ngrok
# Start webhook receiver
python3 scripts/webhook_receiver.py &

# Expose to internet
ngrok http 5000

# Use the ngrok URL in CodeMagic
```

## 📱 Integration Examples

### **Slack Integration**
```python
# In webhook_receiver.py, uncomment Slack integration
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
```

### **Discord Integration**
```python
def send_to_discord(self, message):
    discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    payload = {"content": message}
    requests.post(discord_webhook_url, json=payload)
```

### **Email Integration**
```python
def send_email_alert(self, analysis, payload):
    # Use SendGrid, Mailgun, or SMTP
    pass
```

## 🧪 Testing Your Setup

### **Test API Access**
```bash
python3 scripts/fetch_build_logs.py
```

### **Test Webhook**
```bash
curl -X POST http://localhost:5000/webhook/codemagic \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

### **Check Health**
```bash
curl http://localhost:5000/health
```

## 📋 Environment Variables Reference

```bash
# Required
CODEMAGIC_API_TOKEN=your_api_token
CODEMAGIC_APP_ID=6835ef689ead500d866e20f7
WEBHOOK_TOKEN=your_secret_token

# Optional
WEBHOOK_URL=https://your-domain.com/webhook/codemagic
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
PORT=5000
```

## 🔒 Security Best Practices

1. **Use HTTPS** for webhook endpoints
2. **Verify webhook tokens** in your receiver
3. **Rotate tokens** regularly
4. **Limit API permissions** to read-only
5. **Monitor webhook logs** for suspicious activity

## 🆘 Troubleshooting

### **Common Issues**

**Webhook not receiving data:**
- Check WEBHOOK_URL in CodeMagic environment
- Verify webhook token matches
- Ensure endpoint is publicly accessible

**API token errors:**
- Regenerate token in CodeMagic
- Check token permissions
- Verify app ID is correct

**Build analysis missing:**
- Check log fetching permissions
- Verify build ID format
- Review API rate limits

### **Debug Commands**
```bash
# Test API connection
curl -H "X-Auth-Token: your_token" \
  "https://api.codemagic.io/builds?appId=your_app_id&limit=1"

# Check webhook logs
tail -f webhook_logs/*.json

# Validate webhook payload
python3 -m json.tool webhook_logs/latest.json
```

---

## 🎉 You're All Set!

Once configured, you'll automatically receive:
- ✅ **Real-time build notifications**
- ✅ **Detailed error analysis**
- ✅ **Actionable recommendations**
- ✅ **Performance insights**

Your builds will now provide automatic feedback to help you quickly identify and fix issues! 🚀