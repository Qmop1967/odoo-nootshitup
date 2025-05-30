#!/usr/bin/env python3
"""
Check if test database was created via web interface
"""

import xmlrpc.client

# Your configuration
ODOO_URL = "http://138.68.89.104:8069"
USERNAME = "khaleel@tsh.sale"
USER_PASSWORD = "Zcbm.97531tsh"
TEST_DB = "odtshbrain_test"

def check_test_database():
    """Check if test database exists and is accessible"""
    print("🔍 Checking for Test Database")
    print("=" * 30)
    
    try:
        # Check if database exists
        db_service = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/db')
        databases = db_service.list()
        
        print(f"📋 Available databases: {databases}")
        
        if TEST_DB in databases:
            print(f"✅ Test database '{TEST_DB}' found!")
            
            # Test login
            print("🔄 Testing login to test database...")
            common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
            uid = common.authenticate(TEST_DB, USERNAME, USER_PASSWORD, {})
            
            if uid:
                print(f"✅ Login successful! User ID: {uid}")
                
                # Get some basic info
                models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
                
                try:
                    # Count partners
                    partner_count = models.execute_kw(
                        TEST_DB, uid, USER_PASSWORD,
                        'res.partner', 'search_count', [[]]
                    )
                    print(f"📊 Partners in test database: {partner_count}")
                    
                    # Count users
                    user_count = models.execute_kw(
                        TEST_DB, uid, USER_PASSWORD,
                        'res.users', 'search_count', [[]]
                    )
                    print(f"👥 Users in test database: {user_count}")
                    
                except Exception as e:
                    print(f"⚠️  Could not get database stats: {e}")
                
                print(f"\n🎉 TEST DATABASE IS READY!")
                print(f"📋 Access Details:")
                print(f"   🌐 URL: {ODOO_URL}")
                print(f"   🗄️  Database: {TEST_DB}")
                print(f"   👤 Username: {USERNAME}")
                print(f"   🔑 Password: {USER_PASSWORD}")
                
                return True
            else:
                print("❌ Login failed to test database")
                return False
        else:
            print(f"❌ Test database '{TEST_DB}' not found")
            print("\n💡 Next steps:")
            print("1. Go to the web interface and try the Duplicate button")
            print("2. Or ask administrator to create the test database")
            return False
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

if __name__ == "__main__":
    check_test_database()