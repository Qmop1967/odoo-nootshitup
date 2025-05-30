#!/usr/bin/env python3
"""
Quick Odoo Test Database Creator
Uses your known configuration, just asks for passwords
"""

import xmlrpc.client
import getpass
import time

# Your known Odoo configuration
ODOO_URL = "http://138.68.89.104:8069"
SOURCE_DB = "odtshbrain"
USERNAME = "khaleel@tsh.sale"
TEST_DB = "odtshbrain_test"

def create_test_database():
    """Create test database with known configuration"""
    print("🚀 Quick Odoo Test Database Creator")
    print("=" * 40)
    print(f"📋 Configuration:")
    print(f"   Odoo URL: {ODOO_URL}")
    print(f"   Source DB: {SOURCE_DB}")
    print(f"   Test DB: {TEST_DB}")
    print(f"   Username: {USERNAME}")
    print()
    
    # Get passwords
    print("🔑 Please provide passwords:")
    master_password = getpass.getpass("Master/Admin Password: ")
    user_password = getpass.getpass(f"Password for {USERNAME}: ")
    
    if not master_password or not user_password:
        print("❌ Both passwords are required!")
        return False
    
    try:
        print("\n🔄 Connecting to Odoo...")
        
        # Initialize XML-RPC connections
        db_service = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/db')
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        
        # Test connection
        print("🔄 Testing connection...")
        databases = db_service.list()
        print(f"✅ Connected! Found databases: {databases}")
        
        if SOURCE_DB not in databases:
            print(f"❌ Source database '{SOURCE_DB}' not found!")
            print(f"Available databases: {databases}")
            return False
        
        # Check if test database already exists
        if TEST_DB in databases:
            print(f"⚠️  Test database '{TEST_DB}' already exists!")
            response = input("Drop it and recreate? (y/N): ").strip().lower()
            if response == 'y':
                print(f"🗑️  Dropping existing database '{TEST_DB}'...")
                result = db_service.drop(master_password, TEST_DB)
                if result:
                    print("✅ Existing database dropped")
                else:
                    print("❌ Failed to drop existing database")
                    return False
            else:
                print("❌ Cannot proceed with existing database")
                return False
        
        # Create backup
        print(f"📦 Creating backup of '{SOURCE_DB}'...")
        backup_data = db_service.dump(master_password, SOURCE_DB, 'zip')
        
        if not backup_data:
            print("❌ Failed to create backup")
            return False
        
        print("✅ Backup created successfully!")
        
        # Save backup to file
        timestamp = int(time.time())
        backup_filename = f"odoo_backups/{SOURCE_DB}_backup_{timestamp}.zip"
        
        try:
            import os
            os.makedirs("odoo_backups", exist_ok=True)
            with open(backup_filename, 'wb') as f:
                f.write(backup_data)
            print(f"💾 Backup saved to: {backup_filename}")
        except Exception as e:
            print(f"⚠️  Could not save backup file: {e}")
        
        # Restore as test database
        print(f"🔄 Restoring as test database '{TEST_DB}'...")
        result = db_service.restore(master_password, TEST_DB, backup_data, True)
        
        if result:
            print(f"✅ Test database '{TEST_DB}' created successfully!")
            
            # Test authentication with the new database
            print("🔄 Testing authentication with test database...")
            uid = common.authenticate(TEST_DB, USERNAME, user_password, {})
            
            if uid:
                print(f"✅ Authentication successful! User ID: {uid}")
                
                # Ask about data anonymization
                print("\n🔒 Data Anonymization")
                anonymize = input("Anonymize sensitive data in test database? (y/N): ").strip().lower()
                
                if anonymize == 'y':
                    print("🔄 Starting data anonymization...")
                    
                    # Simple anonymization
                    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
                    
                    try:
                        # Anonymize partner emails
                        partners = models.execute_kw(
                            TEST_DB, uid, user_password,
                            'res.partner', 'search_read',
                            [[]],
                            {'fields': ['id', 'email'], 'limit': 50}
                        )
                        
                        anonymized_count = 0
                        for partner in partners:
                            if partner.get('email'):
                                test_email = f"test_user_{partner['id']}@example.com"
                                models.execute_kw(
                                    TEST_DB, uid, user_password,
                                    'res.partner', 'write',
                                    [[partner['id']], {'email': test_email}]
                                )
                                anonymized_count += 1
                        
                        print(f"✅ Anonymized {anonymized_count} email addresses")
                        
                    except Exception as e:
                        print(f"⚠️  Error during anonymization: {e}")
                
                print(f"\n🎉 Test database setup complete!")
                print(f"📋 Summary:")
                print(f"   ✅ Test Database: {TEST_DB}")
                print(f"   🌐 Access URL: {ODOO_URL}")
                print(f"   🔑 Username: {USERNAME}")
                print(f"   💾 Backup: {backup_filename}")
                print(f"   💡 Use your regular password to access the test database")
                
                return True
            else:
                print("❌ Authentication failed with test database")
                print("💡 The database was created but login verification failed")
                return False
        else:
            print("❌ Failed to restore test database")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = create_test_database()
    
    if success:
        print("\n🚀 Ready to test!")
        print(f"Access your test database at: {ODOO_URL}")
        print(f"Login with: {USERNAME} and your regular password")
    else:
        print("\n❌ Test database creation failed")
        print("💡 You can try the manual method or check your credentials")