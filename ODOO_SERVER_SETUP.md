# TSH Salesperson App - Odoo Server Setup Guide

## Quick Setup

To configure your app to connect to your Odoo server, you only need to update **one file**:

### 📁 File to Edit: `lib/config/app_config.dart`

Open the file and update these two lines:

```dart
// Replace these with your actual Odoo server details
static const String odooServerUrl = 'https://your-actual-server.com';
static const String odooDatabaseName = 'your-actual-database';
```

## 🔧 Configuration Examples

### For Odoo.com Hosted Instances:
```dart
static const String odooServerUrl = 'https://yourcompany.odoo.com';
static const String odooDatabaseName = 'yourcompany-main-123456';
```

### For Self-Hosted Odoo:
```dart
static const String odooServerUrl = 'https://odoo.yourcompany.com';
static const String odooDatabaseName = 'production';
```

### For Local Development:
```dart
static const String odooServerUrl = 'http://localhost:8069';
static const String odooDatabaseName = 'test_db';
```

## 📱 How Users Will Login

After configuration, users will see a simplified login screen with only:
- **Email field** (their Odoo login email)
- **Password field** (their Odoo password)

No need to enter server URL or database name - it's all configured automatically!

## 🔍 Finding Your Odoo Details

### Server URL:
- **Odoo.com**: Usually `https://yourcompany.odoo.com`
- **Self-hosted**: Your domain like `https://odoo.yourcompany.com`
- **Local**: Usually `http://localhost:8069`

### Database Name:
- **Odoo.com**: Check your Odoo URL or contact Odoo support
- **Self-hosted**: Ask your system administrator
- **Local**: The database name you created

## ✅ Testing the Configuration

1. Update the configuration file
2. Build and run the app
3. Try logging in with your admin email and password
4. If it works, you're all set! 🎉

## 🚨 Troubleshooting

If login fails:
1. Double-check the server URL (include `https://`)
2. Verify the database name is correct
3. Ensure your email and password are correct
4. Check if your Odoo server is accessible from the internet

## 📞 Need Help?

If you need help finding your Odoo server details:
- Contact your Odoo administrator
- Check your Odoo welcome email
- Look at your current Odoo browser URL when logged in 