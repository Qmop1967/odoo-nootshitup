#!/usr/bin/env python3
"""
Run this AFTER you set the master password in the web interface
"""

import xmlrpc.client
import time
import os

# Your configuration - UPDATE THE MASTER PASSWORD AFTER YOU SET IT
ODOO_URL = "http://138.68.89.104:8069"
SOURCE_DB = "odtshbrain"
USERNAME = "khaleel@tsh.sale"
USER_PASSWORD = "Zcbm.97531tsh"
TEST_DB = "odtshbrain_test"

# UPDATE THIS WITH THE MASTER PASSWORD YOU SET IN THE WEB INTERFACE
NEW_MASTER_PASSWORD = "ENTER_THE_MASTER_PASSWORD_YOU_SET"

def create_test_database_after_master_set():
    """Create test database after master password is set"""
    print("🚀 Creating Test Database (After Master Password Set)")
    print("=" * 55)
    
    if NEW_MASTER_PASSWORD == "ENTER_THE_MASTER_PASSWORD_YOU_SET":
        print("❌ Please update NEW_MASTER_PASSWORD in this script first!")
        print("   Edit the script and set NEW_MASTER_PASSWORD to what you set in web interface")
        return False
    
    print(f"📋 Configuration:")
    print(f"   Odoo URL: {ODOO_URL}")
    print(f"   Source DB: {SOURCE_DB}")
    print(f"   Test DB: {TEST_DB}")
    print(f"   Master Password: ✅ Set")
    print()
    
    try:
        print("🔄 Connecting to Odoo...")
        db_service = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/db')
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        
        # Test connection
        databases = db_service.list()
        print(f"✅ Connected! Found databases: {databases}")
        
        # Check if test database already exists
        if TEST_DB in databases:
            print(f"⚠️  Test database '{TEST_DB}' already exists!")
            print("🗑️  Dropping existing database...")
            result = db_service.drop(NEW_MASTER_PASSWORD, TEST_DB)
            if result:
                print("✅ Existing database dropped")
            else:
                print("❌ Failed to drop existing database")
                return False
        
        # Try duplicate first (faster)
        print(f"🔄 Attempting to duplicate '{SOURCE_DB}' to '{TEST_DB}'...")
        try:
            result = db_service.duplicate_database(NEW_MASTER_PASSWORD, SOURCE_DB, TEST_DB)
            if result:
                print(f"✅ Database duplicated successfully!")
                
                # Test authentication
                print("🔄 Testing authentication...")
                uid = common.authenticate(TEST_DB, USERNAME, USER_PASSWORD, {})
                if uid:
                    print(f"✅ Authentication successful! User ID: {uid}")
                    print(f"\n🎉 TEST DATABASE READY!")
                    print(f"📋 Access Details:")
                    print(f"   URL: {ODOO_URL}")
                    print(f"   Database: {TEST_DB}")
                    print(f"   Username: {USERNAME}")
                    print(f"   Password: {USER_PASSWORD}")
                    return True
                else:
                    print("❌ Authentication failed")
                    return False
            else:
                print("⚠️  Duplicate failed, trying backup/restore...")
        except Exception as e:
            print(f"⚠️  Duplicate failed: {e}")
            print("🔄 Trying backup/restore method...")
        
        # Fallback to backup/restore
        print(f"📦 Creating backup of '{SOURCE_DB}'...")
        backup_data = db_service.dump(NEW_MASTER_PASSWORD, SOURCE_DB, 'zip')
        
        if not backup_data:
            print("❌ Failed to create backup")
            return False
        
        backup_size_mb = len(backup_data) / (1024*1024)
        print(f"✅ Backup created! Size: {backup_size_mb:.1f} MB")
        
        # Save backup
        timestamp = int(time.time())
        backup_filename = f"odoo_backups/{SOURCE_DB}_backup_{timestamp}.zip"
        os.makedirs("odoo_backups", exist_ok=True)
        
        with open(backup_filename, 'wb') as f:
            f.write(backup_data)
        print(f"💾 Backup saved: {backup_filename}")
        
        # Restore as test database
        print(f"🔄 Restoring as '{TEST_DB}'...")
        result = db_service.restore(NEW_MASTER_PASSWORD, TEST_DB, backup_data, True)
        
        if result:
            print(f"✅ Test database restored successfully!")
            
            # Test authentication
            uid = common.authenticate(TEST_DB, USERNAME, USER_PASSWORD, {})
            if uid:
                print(f"✅ Authentication successful! User ID: {uid}")
                print(f"\n🎉 TEST DATABASE READY!")
                print(f"📋 Access Details:")
                print(f"   URL: {ODOO_URL}")
                print(f"   Database: {TEST_DB}")
                print(f"   Username: {USERNAME}")
                print(f"   Password: {USER_PASSWORD}")
                print(f"   Backup: {backup_filename}")
                return True
            else:
                print("❌ Authentication failed")
                return False
        else:
            print("❌ Failed to restore database")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Run this AFTER setting master password in web interface")
    print("📝 Don't forget to update NEW_MASTER_PASSWORD in this script")
    print()
    
    success = create_test_database_after_master_set()
    
    if success:
        print("\n🎊 SUCCESS! Your test database is ready!")
    else:
        print("\n❌ Failed to create test database")
        print("💡 Try using the web interface duplicate button")