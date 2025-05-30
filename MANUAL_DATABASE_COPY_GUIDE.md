# 🌐 Manual Database Copy Guide

Since the automated script encountered a master password issue, here's how to create your test database manually using the web interface.

## 🎯 Your Information
- **Odoo URL**: `http://138.68.89.104:8069`
- **Source Database**: `odtshbrain`
- **Target Database**: `odtshbrain_test`
- **Username**: `khaleel@tsh.sale`
- **User Password**: `Zcbm.97531tsh`

## 📋 Step-by-Step Manual Process

### Step 1: Access Database Manager
1. **Open your browser** and go to:
   ```
   http://138.68.89.104:8069/web/database/manager
   ```

2. **You should see** the database management interface with your database `odtshbrain` listed

### Step 2: Create Backup
1. **Click the "Backup" button** next to `odtshbrain`
2. **Enter the master password** when prompted
   - Try: `Zcbm.97531Tsh` (what we have)
   - If that doesn't work, you'll need to get the correct master password
3. **Select format**: Choose "zip" (recommended)
4. **Click "Backup"**
5. **Download the backup file** when it's ready

### Step 3: Restore as Test Database
1. **Click "Restore Database"** button
2. **Upload the backup file** you just downloaded
3. **Enter database name**: `odtshbrain_test`
4. **Enter master password** (same as backup step)
5. **Check "Copy database"** if available
6. **Click "Restore"**

### Step 4: Verify Test Database
1. **Wait for restore to complete** (may take several minutes)
2. **You should see** `odtshbrain_test` in the database list
3. **Click on the database** to access it
4. **Login with**:
   - Username: `khaleel@tsh.sale`
   - Password: `Zcbm.97531tsh`

## 🔧 If Master Password Doesn't Work

### Option A: Find the Correct Master Password
The master password might be different. Common locations to check:

1. **Odoo configuration file** (usually `/etc/odoo/odoo.conf`)
2. **Environment variables** on the server
3. **Docker configuration** if using containers
4. **Ask the system administrator**

### Option B: Alternative Methods

#### Method 1: PostgreSQL Direct Access
If you have database server access:
```bash
# Create backup
pg_dump odtshbrain > odtshbrain_backup.sql

# Create new database
createdb odtshbrain_test

# Restore backup
psql odtshbrain_test < odtshbrain_backup.sql
```

#### Method 2: Odoo CLI (if available)
```bash
# Create backup
odoo -d odtshbrain --stop-after-init --backup-db=backup.zip

# Restore as test database
odoo -d odtshbrain_test --stop-after-init --restore-db=backup.zip
```

#### Method 3: Data Export/Import
Instead of full database copy:
1. **Export specific modules/data** from production
2. **Create new database** from scratch
3. **Import the exported data**

## 🔍 Troubleshooting

### "Access Denied" Error
- **Master password is incorrect**
- **Database management is disabled**
- **User doesn't have admin rights**

### "Database Already Exists" Error
- **Drop the existing test database first**
- **Or choose a different name** like `odtshbrain_test2`

### Backup/Restore Takes Too Long
- **Large databases take time** (be patient)
- **Check server resources** (disk space, memory)
- **Try during off-peak hours**

## 🎯 What to Do Next

### If Manual Method Works:
1. ✅ You'll have `odtshbrain_test` database
2. ✅ Login with `khaleel@tsh.sale` / `Zcbm.97531tsh`
3. ✅ Test your changes safely
4. 🔒 Consider running data anonymization

### If Manual Method Fails:
1. 📞 Contact your system administrator
2. 🔑 Get the correct master password
3. 🛠️ Check if database management is enabled
4. 💻 Try PostgreSQL direct access if available

## 🔒 Data Anonymization (Optional)

After creating the test database, you can anonymize sensitive data:

```python
# Run this script to anonymize data
python3 anonymize_test_data.py
```

This will:
- Replace real emails with `test_user_X@example.com`
- Replace phone numbers with test numbers
- Keep data structure intact for testing

## 📞 Need Help?

If you're stuck:
1. **Try the web interface first** - it's the most reliable method
2. **Check with your system administrator** for the correct master password
3. **Consider alternative backup methods** if database management is restricted
4. **Focus on testing with existing database** if copying isn't possible

---

**Good luck with your database copy! 🚀**