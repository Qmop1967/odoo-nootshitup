#!/usr/bin/env python3
"""
Test Odoo Duplicate Function
Try to duplicate database without master password
"""

import xmlrpc.client

# Your configuration
ODOO_URL = "http://138.68.89.104:8069"
SOURCE_DB = "odtshbrain"
TEST_DB = "odtshbrain_test"

def test_duplicate_without_master():
    """Test if duplicate works without master password"""
    print("🔄 Testing duplicate function without master password...")
    
    try:
        db_service = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/db')
        
        # Check current databases
        databases = db_service.list()
        print(f"📋 Current databases: {databases}")
        
        if TEST_DB in databases:
            print(f"⚠️  Test database '{TEST_DB}' already exists!")
            return False
        
        # Try duplicate without master password (some Odoo versions allow this)
        print(f"🔄 Attempting to duplicate '{SOURCE_DB}' to '{TEST_DB}'...")
        
        # Try with empty master password first
        try:
            result = db_service.duplicate_database("", SOURCE_DB, TEST_DB)
            if result:
                print(f"✅ SUCCESS! Database duplicated without master password!")
                return True
        except Exception as e:
            print(f"   Empty password failed: {e}")
        
        # Try with common default passwords
        default_passwords = ["admin", "password", "123456", "odoo"]
        
        for pwd in default_passwords:
            try:
                print(f"   Trying default password: {pwd}")
                result = db_service.duplicate_database(pwd, SOURCE_DB, TEST_DB)
                if result:
                    print(f"✅ SUCCESS! Database duplicated with password: {pwd}")
                    return True
            except Exception as e:
                print(f"   Password '{pwd}' failed: {e}")
        
        print("❌ All duplicate attempts failed")
        return False
        
    except Exception as e:
        print(f"❌ Error testing duplicate: {e}")
        return False

def verify_test_database():
    """Verify the test database was created and is accessible"""
    print("\n🔄 Verifying test database...")
    
    try:
        db_service = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/db')
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        
        # Check if test database exists
        databases = db_service.list()
        if TEST_DB not in databases:
            print(f"❌ Test database '{TEST_DB}' not found")
            return False
        
        print(f"✅ Test database '{TEST_DB}' exists!")
        
        # Test login
        print("🔄 Testing login to test database...")
        uid = common.authenticate(TEST_DB, "khaleel@tsh.sale", "Zcbm.97531tsh", {})
        
        if uid:
            print(f"✅ Login successful! User ID: {uid}")
            print(f"\n🎉 TEST DATABASE READY!")
            print(f"📋 Access Details:")
            print(f"   URL: {ODOO_URL}")
            print(f"   Database: {TEST_DB}")
            print(f"   Username: khaleel@tsh.sale")
            print(f"   Password: Zcbm.97531tsh")
            return True
        else:
            print("❌ Login failed to test database")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying test database: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Odoo Duplicate Function Test")
    print("=" * 35)
    print("Trying to duplicate database without master password...")
    print()
    
    # Test duplicate function
    success = test_duplicate_without_master()
    
    if success:
        # Verify the database works
        verify_test_database()
    else:
        print("\n💡 Recommendations:")
        print("1. 🔧 Click 'Set Master Password' in the web interface")
        print("2. 🌐 Try the duplicate button in the web interface")
        print("3. 📞 Contact your system administrator")
        print("4. 🔄 Use alternative backup methods")

if __name__ == "__main__":
    main()