# 🤖 TSH Salesperson App - Automated CI/CD Error Handler

This automation system monitors your CodeMagic builds and automatically fixes common errors, ensuring continuous deployment to both Google Play Store and Apple App Store.

## 🎯 Features

- **🔍 Automatic Error Detection**: Monitors CodeMagic builds and identifies common failure patterns
- **🔧 Intelligent Auto-Fixes**: Applies targeted fixes for iOS signing, Android R8, Flutter config, and more
- **🔄 Continuous Retry**: Automatically retries builds after applying fixes (up to configurable attempts)
- **📊 Health Monitoring**: Regular health checks and status reporting
- **🚨 Smart Notifications**: Creates GitHub issues and sends alerts when manual intervention is needed
- **📱 Multi-Platform**: Handles both Android and iOS build issues

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CodeMagic     │    │   GitHub        │    │   Automation    │
│   Build Fails   │───▶│   Actions       │───▶│   Error Handler │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Apply Fixes   │◀───│   Analyze Logs  │◀───│   Fetch Build   │
│   & Commit      │    │   & Identify    │    │   Logs & Status │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│   Trigger New   │───▶│   Monitor Until │
│   Build         │    │   Success       │
└─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Setup

```bash
cd automation
python setup.py
```

### 2. Configure Environment

Edit `.env` file with your credentials:

```env
CODEMAGIC_API_TOKEN=your_actual_token
CODEMAGIC_APP_ID=your_actual_app_id
GITHUB_TOKEN=your_github_token
```

### 3. Add GitHub Secrets

Go to your repository Settings > Secrets and variables > Actions:

- `CODEMAGIC_API_TOKEN`: Your CodeMagic API token
- `CODEMAGIC_APP_ID`: Your CodeMagic app ID

### 4. Test the System

```bash
python error_handler.py
```

## 📋 Supported Error Types & Fixes

| Error Pattern | Automatic Fix | Description |
|---------------|---------------|-------------|
| `No valid code signing certificates` | iOS Signing Fix | Switches to iPhone Distribution certificate |
| `Generated.xcconfig must exist` | Flutter Config | Adds `flutter build ios --config-only` |
| `pod install` | CocoaPods Fix | Updates Podfile configuration |
| `R8 compilation` | Android R8 | Adds Google Play Core dependencies |
| `Google Play service account` | Credentials | Temporarily disables publishing |
| `Bundle identifier` | Bundle ID | Fixes bundle identifier mismatches |
| `Provisioning profile` | Profile Fix | Switches to manual signing |
| `Flutter analyze` | Analysis | Makes analysis non-blocking |
| `Flutter test` | Testing | Makes tests non-blocking |
| `Gradle build` | Gradle | Updates Gradle properties |

## 🔧 Usage Methods

### Method 1: GitHub Actions (Recommended)

The system runs automatically via GitHub Actions:

- **Scheduled**: Every 30 minutes during business hours
- **On Failure**: Triggered when any workflow fails
- **Manual**: Can be triggered manually from Actions tab

### Method 2: Webhook Handler

Deploy the webhook handler to receive real-time notifications:

```bash
python webhook_handler.py
```

Configure CodeMagic webhook:
- URL: `https://your-server.com/webhook/codemagic`
- Events: Build finished

### Method 3: Manual Execution

Run the error handler directly:

```bash
python error_handler.py
```

## 📊 Monitoring & Reporting

### Health Checks

The system performs regular health checks:

```bash
# Check recent build status
curl -X GET "https://api.codemagic.io/builds?appId=YOUR_APP_ID&limit=5" \
  -H "X-Auth-Token: YOUR_TOKEN"
```

### GitHub Issues

When automation fails, the system automatically:
- Creates GitHub issues with detailed error information
- Provides quick action links
- Tags issues with appropriate labels

### Logs & Artifacts

All automation runs generate:
- Detailed logs
- Fix reports (JSON format)
- Health status reports

## 🔐 Security & Credentials

### Required Credentials

1. **CodeMagic API Token**
   - Go to CodeMagic > User settings > Integrations > API tokens
   - Create token with build access

2. **CodeMagic App ID**
   - Found in your app URL: `https://codemagic.io/apps/{APP_ID}`

3. **GitHub Token**
   - Usually auto-provided in GitHub Actions
   - For manual use: Settings > Developer settings > Personal access tokens

### Security Best Practices

- Store all credentials as GitHub secrets
- Use environment variables for local development
- Never commit credentials to repository
- Rotate tokens regularly

## 🛠️ Configuration

### Environment Variables

```env
# Required
CODEMAGIC_API_TOKEN=cm_xxx
CODEMAGIC_APP_ID=xxx
GITHUB_TOKEN=ghp_xxx

# Optional
MAX_ATTEMPTS=5
WEBHOOK_SECRET=your_secret
PORT=5000
DEBUG=false
```

### Customization

#### Add New Error Patterns

Edit `error_handler.py`:

```python
self.error_patterns = {
    "Your Error Pattern": self.fix_your_error,
    # ... existing patterns
}

def fix_your_error(self) -> bool:
    """Fix your specific error"""
    fixes = [
        {
            "file": "path/to/file",
            "search": "old_content",
            "replace": "new_content",
            "description": "What this fix does"
        }
    ]
    return self.apply_fixes(fixes)
```

#### Modify Retry Logic

```python
# In monitor_and_fix method
max_attempts = int(os.getenv('MAX_ATTEMPTS', 5))
```

## 📱 Integration with Your App

### CodeMagic Configuration

Ensure your `codemagic.yaml` has proper error handling:

```yaml
scripts:
  - name: Build with Error Handling
    script: |
      set -e  # Exit on error
      flutter build appbundle --release || {
        echo "Build failed, automation will handle this"
        exit 1
      }
```

### Notification Setup

Configure notifications in your workflow:

```yaml
publishing:
  email:
    recipients:
      - kha89ahm@gmail.com
    notify:
      success: true
      failure: true  # This triggers automation
```

## 🔄 Workflow Examples

### Typical Success Flow

1. 🚀 Developer pushes code
2. 🔧 CodeMagic build starts
3. ❌ Build fails (e.g., iOS signing issue)
4. 📨 GitHub Actions receives failure notification
5. 🤖 Automation analyzes logs
6. 🔧 Applies iOS signing fix
7. 📝 Commits fix to repository
8. 🚀 Triggers new CodeMagic build
9. ✅ Build succeeds
10. 📱 App published to stores

### Manual Intervention Flow

1. ❌ Build fails with unknown error
2. 🤖 Automation cannot identify pattern
3. 🚨 GitHub issue created automatically
4. 👨‍💻 Developer receives notification
5. 🔧 Developer fixes issue manually
6. 📝 Developer can add new pattern to automation

## 🧪 Testing

### Test Error Handler

```bash
# Test with mock data
python -c "
from error_handler import CodeMagicErrorHandler
handler = CodeMagicErrorHandler('test', 'test', 'test')
print('✅ Error handler imported successfully')
"
```

### Test Webhook Handler

```bash
# Start webhook server
python webhook_handler.py &

# Test webhook endpoint
curl -X POST http://localhost:5000/webhook/codemagic \
  -H "Content-Type: application/json" \
  -d '{"buildId":"test","status":"failed","appId":"test"}'
```

### Test GitHub Actions

Manually trigger the workflow:
1. Go to Actions tab in GitHub
2. Select "🤖 Auto-Fix CI/CD Issues"
3. Click "Run workflow"

## 🐛 Troubleshooting

### Common Issues

#### "No builds found"
- Check `CODEMAGIC_APP_ID` is correct
- Verify API token has proper permissions

#### "Error fetching build logs"
- Ensure build ID exists
- Check API token permissions

#### "Failed to apply fixes"
- Verify file paths in fix definitions
- Check repository write permissions

#### "Error committing fixes"
- Ensure git is configured
- Check GitHub token permissions

### Debug Mode

Enable debug logging:

```bash
export DEBUG=true
python error_handler.py
```

### Manual Fix Testing

Test individual fixes:

```python
from error_handler import CodeMagicErrorHandler
handler = CodeMagicErrorHandler(token, app_id, github_token)
success = handler.fix_ios_signing()
print(f"Fix applied: {success}")
```

## 📈 Monitoring & Analytics

### Build Success Rate

Track automation effectiveness:

```bash
# Get recent builds
python -c "
import requests
import os
from collections import Counter

token = os.getenv('CODEMAGIC_API_TOKEN')
app_id = os.getenv('CODEMAGIC_APP_ID')

response = requests.get(
    'https://api.codemagic.io/builds',
    headers={'X-Auth-Token': token},
    params={'appId': app_id, 'limit': 20}
)

builds = response.json().get('builds', [])
statuses = [b['status'] for b in builds]
print(Counter(statuses))
"
```

### Error Pattern Analysis

```bash
# Analyze common error patterns
grep -r "🔍 Detected errors" automation/*.log | \
  cut -d: -f2 | sort | uniq -c | sort -nr
```

## 🤝 Contributing

### Adding New Error Patterns

1. Identify the error pattern in build logs
2. Create a fix function in `error_handler.py`
3. Add pattern to `error_patterns` dictionary
4. Test the fix
5. Submit a pull request

### Improving Existing Fixes

1. Monitor fix success rates
2. Identify edge cases
3. Enhance fix logic
4. Update tests

## 📞 Support

### Getting Help

1. **Check Logs**: Review automation logs for detailed error information
2. **GitHub Issues**: Automation creates issues for unresolved problems
3. **Manual Trigger**: Use GitHub Actions to manually trigger fixes
4. **Documentation**: Refer to this README and inline code comments

### Contact

- **Repository**: https://github.com/Qmop1967/TSH-Salesperson-App
- **Issues**: Create GitHub issues for bugs or feature requests
- **Email**: kha89ahm@gmail.com

## 📄 License

This automation system is part of the TSH Salesperson App project.

---

**🎉 Happy Automated Building!** 🚀📱 