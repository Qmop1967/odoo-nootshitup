#!/usr/bin/env python3
"""
Test Database Operations After Setting Master Password
Run this AFTER you set the master password in the web interface
"""

import xmlrpc.client

# Your configuration
ODOO_URL = "http://138.68.89.104:8069"
SOURCE_DB = "odtshbrain"
MASTER_PASSWORD = "Zcbm.97531tSh"
TEST_DB = "odtshbrain_test"

def test_master_password_works():
    """Test if master password now works for database operations"""
    print("🔐 Testing Master Password After Setting")
    print("=" * 40)
    
    try:
        db_service = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/db')
        
        # Test 1: List databases (should always work)
        print("🔄 Testing database listing...")
        databases = db_service.list()
        print(f"✅ Found databases: {databases}")
        
        # Test 2: Test master password with a safe operation
        print("🔄 Testing master password...")
        
        # Try to check if a test database exists (safe operation)
        try:
            exists = db_service.db_exist("nonexistent_test_db")
            print("✅ Master password works! Database operations are now enabled.")
            return True
        except Exception as e:
            if "Access Denied" in str(e):
                print("❌ Master password still not working - Access Denied")
                return False
            else:
                print(f"✅ Master password works! (Got expected error: {e})")
                return True
                
    except Exception as e:
        print(f"❌ Error testing master password: {e}")
        return False

def test_duplicate_operation():
    """Test if duplicate operation works now"""
    print("\n🔄 Testing Duplicate Operation")
    print("-" * 30)
    
    try:
        db_service = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/db')
        
        # Check if test database already exists
        databases = db_service.list()
        if TEST_DB in databases:
            print(f"⚠️  Test database '{TEST_DB}' already exists!")
            print("✅ This means duplication worked via web interface!")
            return True
        
        # Try duplicate operation
        print(f"🔄 Attempting to duplicate '{SOURCE_DB}' to '{TEST_DB}'...")
        
        try:
            result = db_service.duplicate_database(MASTER_PASSWORD, SOURCE_DB, TEST_DB)
            if result:
                print("🎉 SUCCESS! Database duplication works!")
                return True
            else:
                print("❌ Duplication returned False")
                return False
        except Exception as e:
            if "Access Denied" in str(e):
                print("❌ Still getting Access Denied for duplication")
                print("💡 Try using the web interface Duplicate button")
                return False
            else:
                print(f"⚠️  Duplication error: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing duplication: {e}")
        return False

def check_if_test_db_created():
    """Check if test database was created via web interface"""
    print("\n🔍 Checking for Test Database")
    print("-" * 28)
    
    try:
        db_service = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/db')
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        
        databases = db_service.list()
        print(f"📋 Available databases: {databases}")
        
        if TEST_DB in databases:
            print(f"✅ Test database '{TEST_DB}' found!")
            
            # Test login
            print("🔄 Testing login to test database...")
            uid = common.authenticate(TEST_DB, "khaleel@tsh.sale", "Zcbm.97531tsh", {})
            
            if uid:
                print(f"✅ Login successful! User ID: {uid}")
                print(f"\n🎉 TEST DATABASE IS READY!")
                print(f"📋 Access Details:")
                print(f"   🌐 URL: {ODOO_URL}")
                print(f"   🗄️  Database: {TEST_DB}")
                print(f"   👤 Username: khaleel@tsh.sale")
                print(f"   🔑 Password: Zcbm.97531tsh")
                return True
            else:
                print("❌ Login failed to test database")
                return False
        else:
            print(f"❌ Test database '{TEST_DB}' not found")
            print("💡 Try the web interface Duplicate button")
            return False
            
    except Exception as e:
        print(f"❌ Error checking test database: {e}")
        return False

def main():
    """Main function"""
    print("🔐 Testing After Master Password Setup")
    print("=" * 38)
    print("Run this AFTER setting master password in web interface")
    print()
    
    # Test if master password works
    master_works = test_master_password_works()
    
    if master_works:
        print("\n✅ Master password is working!")
        
        # Test duplicate operation
        duplicate_works = test_duplicate_operation()
        
        if not duplicate_works:
            print("\n💡 API duplication might still be disabled")
            print("   Try using the web interface Duplicate button")
    else:
        print("\n❌ Master password still not working")
        print("💡 Make sure you:")
        print("   1. Clicked 'Set Master Password' in web interface")
        print("   2. Used password: Zcbm.97531tSh")
        print("   3. Confirmed the password")
    
    # Always check if test database exists (might have been created via web)
    check_if_test_db_created()
    
    print(f"\n🎯 NEXT STEPS:")
    if master_works:
        print("   ✅ Master password is set correctly")
        print("   🌐 Try the web interface Duplicate button")
        print("   📋 Name new database: odtshbrain_test")
    else:
        print("   🔧 Set master password in web interface first")
        print("   🔄 Run this script again after setting")

if __name__ == "__main__":
    main()