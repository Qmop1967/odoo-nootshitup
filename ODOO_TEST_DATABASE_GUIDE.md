# Odoo Test Database Creation Guide

This guide provides multiple methods to create a test copy of your Odoo production database for safe testing and development.

## 🚀 Quick Start

### Method 1: Automated Shell Script (Recommended)

```bash
./create_test_db.sh
```

This script will:
- ✅ Create a backup of your production database
- ✅ Restore it as a test database with a suffix (e.g., `_test`)
- ✅ Handle existing test databases
- ✅ Provide cleanup options

### Method 2: Python Script with Advanced Features

```bash
python3 create_odoo_test_database.py
```

This script provides:
- ✅ Database backup and restore
- ✅ Data anonymization for test environments
- ✅ Direct database duplication (if supported)
- ✅ Comprehensive error handling

## 📋 Prerequisites

### Required Information
- **Odoo URL**: Your Odoo instance URL (e.g., `https://your-company.odoo.com`)
- **Database Name**: Name of your production database
- **Master Password**: Odoo master/admin password
- **Login Credentials**: Username and password for database access

### System Requirements
- `curl` (for HTTP API calls)
- `python3` (for Python script)
- Network access to your Odoo instance

## 🔧 Detailed Methods

### Method 1: Shell Script (`create_test_db.sh`)

#### Features:
- **Multiple Backup Methods**: HTTP API, Odoo CLI, PostgreSQL direct
- **Automatic Fallback**: Tries different methods if one fails
- **Safety Checks**: Warns about existing databases
- **Cleanup Options**: Manages backup files

#### Usage:
```bash
# Make executable (if not already)
chmod +x create_test_db.sh

# Run the script
./create_test_db.sh
```

#### What it does:
1. **Prompts for connection details**
2. **Creates backup** using the best available method
3. **Checks for existing test database**
4. **Restores backup** as new test database
5. **Provides cleanup options**

### Method 2: Python Script (`create_odoo_test_database.py`)

#### Features:
- **Advanced Error Handling**: Detailed error messages and recovery
- **Data Anonymization**: Replaces sensitive data with test data
- **Direct Duplication**: Uses Odoo's native duplication if available
- **Comprehensive Logging**: Detailed progress information

#### Usage:
```bash
python3 create_odoo_test_database.py
```

#### Data Anonymization Features:
- Replaces real email addresses with `test_user_X@example.com`
- Can be extended to anonymize other sensitive fields
- Preserves data structure and relationships

### Method 3: Manual Web Interface

If automated methods don't work:

1. **Access Database Manager**
   ```
   https://your-odoo.com/web/database/manager
   ```

2. **Create Backup**
   - Click "Backup" next to your database
   - Choose "zip" format
   - Download the backup file

3. **Restore as Test Database**
   - Click "Restore Database"
   - Upload your backup file
   - Enter new database name (e.g., `your_db_test`)
   - Click "Restore"

### Method 4: Command Line (Advanced)

If you have direct server access:

#### Using Odoo CLI:
```bash
# Create backup
odoo -d production_db --stop-after-init --backup-db=backup.zip

# Restore as test database
odoo -d test_db --stop-after-init --restore-db=backup.zip
```

#### Using PostgreSQL directly:
```bash
# Create backup
pg_dump production_db > backup.sql

# Create new database
createdb test_db

# Restore backup
psql test_db < backup.sql
```

## 🔒 Security Considerations

### Data Anonymization
After creating a test database, consider anonymizing sensitive data:

```python
# Example anonymization (included in Python script)
- Customer emails → test_user_X@example.com
- Phone numbers → +1-555-0XXX
- Addresses → Generic test addresses
- Financial data → Zeroed or test values
```

### Access Control
- Use separate credentials for test databases
- Restrict test database access
- Regularly clean up old test databases
- Never use test data in production

## 📁 File Structure

```
your-project/
├── create_test_db.sh              # Shell script for database copying
├── create_odoo_test_database.py   # Python script with advanced features
├── odoo_backups/                  # Directory for backup files (created automatically)
│   ├── production_backup_20241201_143022.zip
│   └── ...
└── ODOO_TEST_DATABASE_GUIDE.md    # This guide
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Authentication Failed
```
❌ Authentication error: Access denied
```
**Solution**: Verify master password and database name

#### 2. Database Already Exists
```
⚠️ Database 'your_db_test' already exists!
```
**Solution**: Choose to drop existing database or use different name

#### 3. Backup Failed
```
❌ All backup methods failed!
```
**Solutions**:
- Check network connectivity
- Verify Odoo URL is correct
- Try manual backup via web interface
- Check server permissions

#### 4. Insufficient Permissions
```
❌ Permission denied
```
**Solutions**:
- Verify master password
- Check user has database management rights
- Contact system administrator

### Debug Steps

1. **Test Connection**:
   ```bash
   curl -I https://your-odoo.com/web/database/manager
   ```

2. **Check Database List**:
   ```bash
   curl -X POST "https://your-odoo.com/web/database/list" \
        -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","method":"call","params":{},"id":1}'
   ```

3. **Verify Backup File**:
   ```bash
   file backup.zip  # Should show "Zip archive data"
   unzip -l backup.zip  # List contents
   ```

## 📊 Best Practices

### Regular Testing
- Create test databases regularly
- Test major changes in test environment first
- Keep test databases updated with recent production data

### Naming Convention
```
production_db → production_db_test
company_main → company_main_dev
client_db → client_db_staging
```

### Cleanup Schedule
- Weekly: Remove old test databases
- Monthly: Clean backup files
- Quarterly: Review test database usage

### Documentation
- Document test database purposes
- Track which features are being tested
- Maintain test data scenarios

## 🔄 Automation Options

### Scheduled Backups
Create a cron job for regular test database updates:

```bash
# Add to crontab (crontab -e)
0 2 * * 1 /path/to/create_test_db.sh  # Weekly Monday 2 AM
```

### CI/CD Integration
Include test database creation in your deployment pipeline:

```yaml
# Example GitHub Actions
- name: Create Test Database
  run: |
    ./create_test_db.sh
    python3 anonymize_test_data.py
```

## 📞 Support

### Getting Help
1. Check this guide first
2. Review error messages carefully
3. Test with manual web interface
4. Contact your Odoo administrator
5. Check Odoo documentation

### Useful Resources
- [Odoo Database Management](https://www.odoo.com/documentation/16.0/administration/odoo_sh/getting_started/branches.html)
- [Odoo Backup/Restore](https://www.odoo.com/documentation/16.0/administration/maintain/backup_restore.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🎯 Next Steps

After creating your test database:

1. **Verify the copy** - Check that all data is present
2. **Anonymize sensitive data** - Run anonymization scripts
3. **Test your changes** - Use the test database for development
4. **Document test scenarios** - Keep track of what you're testing
5. **Clean up regularly** - Remove old test databases

---

**Happy Testing! 🚀**

Remember: Always test in a safe environment before making changes to production data.