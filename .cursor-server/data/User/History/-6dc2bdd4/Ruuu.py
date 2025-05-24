#!/usr/bin/env python3
"""
Test Odoo Connection
==================
Test connection to Odoo test instance and find admin credentials.
"""

import odoorpc

def test_odoo_connection():
    """Test connection to Odoo test instance"""
    
    try:
        # Connect to test instance
        print("🔗 Connecting to Odoo test instance...")
        odoo = odoorpc.ODOO('localhost', port=8070)
        print("✅ Connected to Odoo test instance")
        
        # List databases
        databases = odoo.db.list()
        print(f"📊 Available databases: {databases}")
        
        if 'odtshbrain_test' in databases:
            print("✅ Test database 'odtshbrain_test' found")
            
            # Try common admin credentials
            credentials_to_try = [
                ('admin', 'admin'),
                ('admin', 'admin123'),
                ('admin', ''),
                ('admin', 'password'),
            ]
            
            for username, password in credentials_to_try:
                try:
                    print(f"🔐 Trying login: {username} / {'*' * len(password) if password else '(empty)'}")
                    odoo.login('odtshbrain_test', username, password)
                    print(f"✅ SUCCESS! Login credentials: {username} / {password}")
                    
                    # Test basic operations
                    user_id = odoo.env.user.id
                    user_name = odoo.env.user.name
                    print(f"👤 Logged in as: {user_name} (ID: {user_id})")
                    
                    return username, password
                    
                except Exception as e:
                    print(f"❌ Failed: {e}")
                    continue
            
            print("❌ No valid credentials found")
            return None, None
        else:
            print("❌ Test database 'odtshbrain_test' not found")
            return None, None
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None, None

if __name__ == "__main__":
    test_odoo_connection() 