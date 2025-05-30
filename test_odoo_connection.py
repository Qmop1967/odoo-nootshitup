#!/usr/bin/env python3
"""
Odoo Connection Diagnostic Tool
Tests various connection methods and permissions
"""

import xmlrpc.client
import requests

# Your configuration
ODOO_URL = "http://138.68.89.104:8069"
SOURCE_DB = "odtshbrain"
USERNAME = "khaleel@tsh.sale"
MASTER_PASSWORD = "Zcbm.97531Tsh"
USER_PASSWORD = "Zcbm.97531tsh"

def test_basic_connection():
    """Test basic connection to Odoo"""
    print("🔄 Testing basic connection...")
    try:
        response = requests.get(f"{ODOO_URL}/web/database/manager", timeout=10)
        if response.status_code == 200:
            print("✅ Odoo web interface is accessible")
            return True
        else:
            print(f"❌ Web interface returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Odoo: {e}")
        return False

def test_database_list():
    """Test database listing"""
    print("🔄 Testing database listing...")
    try:
        db_service = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/db')
        databases = db_service.list()
        print(f"✅ Found databases: {databases}")
        return databases
    except Exception as e:
        print(f"❌ Cannot list databases: {e}")
        return None

def test_user_authentication():
    """Test user authentication"""
    print("🔄 Testing user authentication...")
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(SOURCE_DB, USERNAME, USER_PASSWORD, {})
        if uid:
            print(f"✅ User authentication successful! User ID: {uid}")
            return uid
        else:
            print("❌ User authentication failed")
            return None
    except Exception as e:
        print(f"❌ User authentication error: {e}")
        return None

def test_master_password():
    """Test master password with different operations"""
    print("🔄 Testing master password...")
    try:
        db_service = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/db')
        
        # Try to get server version (usually doesn't require master password)
        try:
            version = db_service.server_version()
            print(f"✅ Server version: {version}")
        except:
            print("⚠️  Cannot get server version")
        
        # Try database operations that require master password
        print("   Testing database management permissions...")
        
        # Test 1: Try to duplicate (safest test)
        try:
            # This should fail gracefully if master password is wrong
            result = db_service.duplicate_database(MASTER_PASSWORD, SOURCE_DB, "test_temp_db")
            print("✅ Master password appears correct (duplicate test)")
            
            # Clean up test database if it was created
            try:
                db_service.drop(MASTER_PASSWORD, "test_temp_db")
                print("✅ Cleaned up test database")
            except:
                pass
                
        except Exception as e:
            if "Access Denied" in str(e):
                print("❌ Master password is incorrect")
                return False
            elif "already exists" in str(e):
                print("✅ Master password appears correct (database exists)")
                return True
            else:
                print(f"⚠️  Database operation error: {e}")
                return None
        
        return True
        
    except Exception as e:
        print(f"❌ Master password test error: {e}")
        return False

def test_backup_permissions():
    """Test backup creation with smaller operations"""
    print("🔄 Testing backup permissions...")
    try:
        db_service = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/db')
        
        # Try a small backup operation
        print("   Attempting small backup test...")
        backup_data = db_service.dump(MASTER_PASSWORD, SOURCE_DB, 'zip')
        
        if backup_data:
            size_mb = len(backup_data) / (1024*1024)
            print(f"✅ Backup test successful! Size: {size_mb:.1f} MB")
            return True
        else:
            print("❌ Backup returned empty data")
            return False
            
    except Exception as e:
        print(f"❌ Backup test failed: {e}")
        return False

def suggest_solutions():
    """Suggest alternative solutions"""
    print("\n💡 Alternative Solutions:")
    print("=" * 30)
    
    print("1. 🌐 Manual Web Interface Method:")
    print(f"   • Go to: {ODOO_URL}/web/database/manager")
    print(f"   • Click 'Backup' next to '{SOURCE_DB}'")
    print(f"   • Enter master password: {MASTER_PASSWORD}")
    print(f"   • Download the backup file")
    print(f"   • Click 'Restore Database'")
    print(f"   • Upload backup and name it: {SOURCE_DB}_test")
    
    print("\n2. 🔧 Check Odoo Configuration:")
    print("   • Verify database management is enabled")
    print("   • Check if master password is set correctly in Odoo config")
    print("   • Ensure your user has database management rights")
    
    print("\n3. 📞 Contact Administrator:")
    print("   • Ask for the correct master password")
    print("   • Request database management permissions")
    print("   • Ask them to create the test database for you")
    
    print("\n4. 🐳 Alternative Backup Methods:")
    print("   • If you have server access, use pg_dump directly")
    print("   • Use Odoo CLI if available")
    print("   • Export data modules instead of full database")

def main():
    """Main diagnostic function"""
    print("🔍 Odoo Connection Diagnostic Tool")
    print("=" * 40)
    print("This will test your Odoo connection and permissions")
    print()
    
    # Test basic connection
    if not test_basic_connection():
        print("\n❌ Basic connection failed. Check if Odoo is running.")
        return
    
    # Test database listing
    databases = test_database_list()
    if not databases:
        print("\n❌ Cannot list databases. Check XML-RPC access.")
        return
    
    if SOURCE_DB not in databases:
        print(f"\n❌ Source database '{SOURCE_DB}' not found!")
        print(f"Available databases: {databases}")
        return
    
    # Test user authentication
    uid = test_user_authentication()
    if not uid:
        print(f"\n❌ User authentication failed for {USERNAME}")
        print("Check username and password")
        return
    
    # Test master password
    master_ok = test_master_password()
    if master_ok is False:
        print(f"\n❌ Master password appears to be incorrect")
        print("The master password might be different from what we have")
    elif master_ok is True:
        print(f"\n✅ Master password appears correct")
        
        # Test backup if master password works
        backup_ok = test_backup_permissions()
        if backup_ok:
            print(f"\n🎉 All tests passed! Database copying should work.")
            print(f"Try running the automated script again.")
        else:
            print(f"\n⚠️  Master password works but backup failed")
            print("Database management might be disabled")
    
    # Always show alternative solutions
    suggest_solutions()

if __name__ == "__main__":
    main()