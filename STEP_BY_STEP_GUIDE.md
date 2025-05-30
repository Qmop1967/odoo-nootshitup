# 🚀 Step-by-Step Guide to Create Your Test Database

## Your Configuration (Auto-Detected)
- **Odoo URL**: `http://138.68.89.104:8069`
- **Source Database**: `odtshbrain`
- **Username**: `khaleel@tsh.sale`
- **Test Database**: `odtshbrain_test` (will be created)

## 📋 Method 1: Quick Script (Recommended)

1. **Run the quick script**:
   ```bash
   python3 quick_test_db.py
   ```

2. **When prompted, enter**:
   - Master/Admin Password (for database operations)
   - Password for khaleel@tsh.sale

3. **The script will**:
   - ✅ Connect to your Odoo instance
   - ✅ Create a backup of `odtshbrain`
   - ✅ Restore it as `odtshbrain_test`
   - ✅ Test the connection
   - ✅ Optionally anonymize sensitive data

## 📋 Method 2: Manual Web Interface

If the scripts don't work, you can do it manually:

1. **Go to Database Manager**:
   ```
   http://138.68.89.104:8069/web/database/manager
   ```

2. **Create Backup**:
   - Click "Backup" next to `odtshbrain`
   - Enter your master password
   - Download the backup file

3. **Restore as Test Database**:
   - Click "Restore Database"
   - Upload your backup file
   - Name it: `odtshbrain_test`
   - Enter master password
   - Click "Restore"

## 📋 Method 3: Using Existing Scripts

You can also modify your existing scripts:

1. **Edit one of your existing scripts** (like `create_moonlight_customer.py`)
2. **Change the database name** from `odtshbrain` to `odtshbrain_test`
3. **Test with the new database**

## 🔧 Troubleshooting

### If you get "Authentication Failed":
- Double-check your master password
- Verify the database name is correct
- Make sure Odoo is running at `http://138.68.89.104:8069`

### If you get "Database Already Exists":
- The script will ask if you want to drop and recreate
- Choose 'y' to proceed

### If backup fails:
- Check your master password
- Verify you have database management permissions
- Try the manual web interface method

## 🎯 What You'll Get

After successful completion:
- **New database**: `odtshbrain_test`
- **Same data**: Complete copy of your production data
- **Same login**: Use `khaleel@tsh.sale` with your regular password
- **Safe testing**: Make changes without affecting production

## 🔒 Security Notes

- The test database contains real production data
- Consider running data anonymization
- Don't use test data in production
- Clean up test databases when done

## 🚀 Next Steps After Creation

1. **Access your test database**:
   ```
   http://138.68.89.104:8069
   ```

2. **Login with**:
   - Username: `khaleel@tsh.sale`
   - Password: (your regular password)
   - Database: `odtshbrain_test`

3. **Test your changes safely**!

## 📞 Need Help?

If you encounter issues:
1. Check the error messages carefully
2. Try the manual web interface method
3. Verify your Odoo instance is accessible
4. Check that you have the correct passwords

---

**Ready to create your test database? Run: `python3 quick_test_db.py`**