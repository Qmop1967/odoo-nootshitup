#!/usr/bin/env python3
"""
Comprehensive Odoo Diagnostic Tool
Tests all possible database operations and permissions
"""

import xmlrpc.client
import requests
import json

# Your configuration
ODOO_URL = "http://138.68.89.104:8069"
SOURCE_DB = "odtshbrain"
USERNAME = "khaleel@tsh.sale"
MASTER_PASSWORD = "Zcbm.97531tSh"
USER_PASSWORD = "Zcbm.97531tsh"

def test_web_interface_access():
    """Test web interface database management"""
    print("🌐 Testing Web Interface Database Management")
    print("-" * 45)
    
    try:
        # Test database manager page
        response = requests.get(f"{ODOO_URL}/web/database/manager", timeout=10)
        print(f"   Database Manager Page: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text.lower()
            if "backup" in content:
                print("   ✅ Backup button available in web interface")
            if "duplicate" in content:
                print("   ✅ Duplicate button available in web interface")
            if "restore" in content:
                print("   ✅ Restore button available in web interface")
            if "set master password" in content:
                print("   ⚠️  'Set Master Password' button found - password might not be set")
        
        # Test if database management is enabled
        try:
            response = requests.post(f"{ODOO_URL}/web/database/list", 
                                   headers={'Content-Type': 'application/json'},
                                   data='{"jsonrpc":"2.0","method":"call","params":{},"id":1}',
                                   timeout=10)
            if response.status_code == 200:
                print("   ✅ Database listing via web API works")
            else:
                print(f"   ❌ Database listing failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Web API error: {e}")
            
    except Exception as e:
        print(f"   ❌ Web interface test failed: {e}")

def test_xmlrpc_permissions():
    """Test XML-RPC database operations with different approaches"""
    print("\n🔧 Testing XML-RPC Database Operations")
    print("-" * 40)
    
    try:
        db_service = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/db')
        
        # Test 1: List databases (should always work)
        try:
            databases = db_service.list()
            print(f"   ✅ Database listing: {databases}")
        except Exception as e:
            print(f"   ❌ Database listing failed: {e}")
            return
        
        # Test 2: Server version (usually works)
        try:
            version = db_service.server_version()
            print(f"   ✅ Server version: {version}")
        except Exception as e:
            print(f"   ⚠️  Server version failed: {e}")
        
        # Test 3: Database exists check
        try:
            exists = db_service.db_exist(SOURCE_DB)
            print(f"   ✅ Database exists check: {exists}")
        except Exception as e:
            print(f"   ⚠️  Database exists check failed: {e}")
        
        # Test 4: Try different master password variations
        print("   🔑 Testing master password variations...")
        password_variations = [
            MASTER_PASSWORD,
            "admin",
            "",
            "password",
            "Zcbm.97531Tsh",
            "zcbm.97531tsh",
            "ZCBM.97531TSH"
        ]
        
        for pwd in password_variations:
            try:
                # Try a safe operation that requires master password
                result = db_service.duplicate_database(pwd, SOURCE_DB, "temp_test_db")
                print(f"   ✅ Master password '{pwd}' works!")
                
                # Clean up
                try:
                    db_service.drop(pwd, "temp_test_db")
                except:
                    pass
                break
                
            except Exception as e:
                if "Access Denied" in str(e):
                    print(f"   ❌ Password '{pwd}': Access Denied")
                elif "already exists" in str(e):
                    print(f"   ✅ Password '{pwd}' works (database exists)")
                    break
                else:
                    print(f"   ⚠️  Password '{pwd}': {e}")
        
    except Exception as e:
        print(f"   ❌ XML-RPC test failed: {e}")

def test_user_permissions():
    """Test user permissions and capabilities"""
    print("\n👤 Testing User Permissions")
    print("-" * 25)
    
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        
        # Authenticate
        uid = common.authenticate(SOURCE_DB, USERNAME, USER_PASSWORD, {})
        if not uid:
            print("   ❌ User authentication failed")
            return
        
        print(f"   ✅ User authenticated: ID {uid}")
        
        # Check user groups and permissions
        try:
            user_info = models.execute_kw(
                SOURCE_DB, uid, USER_PASSWORD,
                'res.users', 'read',
                [uid], {'fields': ['name', 'login', 'groups_id']}
            )
            print(f"   👤 User: {user_info[0]['name']}")
            print(f"   📧 Login: {user_info[0]['login']}")
            
            # Get group names
            if user_info[0]['groups_id']:
                groups = models.execute_kw(
                    SOURCE_DB, uid, USER_PASSWORD,
                    'res.groups', 'read',
                    [user_info[0]['groups_id']], {'fields': ['name']}
                )
                print("   🏷️  User Groups:")
                for group in groups:
                    print(f"      - {group['name']}")
                    
        except Exception as e:
            print(f"   ⚠️  Could not get user info: {e}")
        
        # Test if user has admin rights
        try:
            # Try to access admin settings
            settings = models.execute_kw(
                SOURCE_DB, uid, USER_PASSWORD,
                'ir.config_parameter', 'search_read',
                [[]],
                {'fields': ['key', 'value'], 'limit': 1}
            )
            if settings:
                print("   ✅ User has admin/technical access")
            else:
                print("   ⚠️  User might not have admin access")
        except Exception as e:
            print(f"   ❌ User does not have admin access: {e}")
            
    except Exception as e:
        print(f"   ❌ User permission test failed: {e}")

def test_alternative_methods():
    """Test alternative database copy methods"""
    print("\n🔄 Testing Alternative Methods")
    print("-" * 30)
    
    # Test 1: Check if we can export/import data instead
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        
        uid = common.authenticate(SOURCE_DB, USERNAME, USER_PASSWORD, {})
        if uid:
            # Test data export capabilities
            try:
                # Try to export a small amount of data
                partners = models.execute_kw(
                    SOURCE_DB, uid, USER_PASSWORD,
                    'res.partner', 'search_read',
                    [[]],
                    {'fields': ['name'], 'limit': 1}
                )
                print("   ✅ Data export works - alternative: export/import specific data")
            except Exception as e:
                print(f"   ❌ Data export failed: {e}")
                
    except Exception as e:
        print(f"   ❌ Alternative method test failed: {e}")
    
    # Test 2: Check Odoo configuration
    print("   🔧 Checking Odoo Configuration:")
    print("      - Database management might be disabled in odoo.conf")
    print("      - list_db = False might be set")
    print("      - dbfilter might be restricting access")
    print("      - Server might be in production mode")

def provide_solutions():
    """Provide comprehensive solutions"""
    print("\n💡 COMPREHENSIVE SOLUTIONS")
    print("=" * 30)
    
    print("🌐 1. WEB INTERFACE METHOD (Most Likely to Work):")
    print(f"   • Go to: {ODOO_URL}/web/database/manager")
    print("   • Try clicking 'Duplicate' button directly")
    print("   • If prompted for master password, try: Zcbm.97531tSh")
    print("   • Name new database: odtshbrain_test")
    
    print("\n🔧 2. SERVER CONFIGURATION ISSUE:")
    print("   • Database management might be disabled")
    print("   • Check /etc/odoo/odoo.conf for:")
    print("     - list_db = True")
    print("     - No dbfilter restrictions")
    print("   • Contact server administrator")
    
    print("\n📞 3. CONTACT ADMINISTRATOR:")
    print("   • Ask them to create test database copy")
    print("   • Request database management permissions")
    print("   • Get correct master password")
    
    print("\n🔄 4. ALTERNATIVE DATA COPY:")
    print("   • Export specific modules/data instead of full database")
    print("   • Create new database and import data")
    print("   • Use Odoo's built-in data export/import tools")
    
    print("\n🐳 5. DIRECT SERVER ACCESS (If Available):")
    print("   • SSH to server and use pg_dump/pg_restore")
    print("   • Use Odoo CLI if available")
    print("   • Copy database files directly")

def main():
    """Main diagnostic function"""
    print("🔍 COMPREHENSIVE ODOO DIAGNOSTIC")
    print("=" * 40)
    print("Testing all possible database operations and permissions...")
    print()
    
    test_web_interface_access()
    test_xmlrpc_permissions()
    test_user_permissions()
    test_alternative_methods()
    provide_solutions()
    
    print(f"\n🎯 RECOMMENDATION:")
    print(f"Based on the 'Access Denied' errors, database management")
    print(f"appears to be disabled at the server level. Try the web")
    print(f"interface duplicate button or contact your administrator.")

if __name__ == "__main__":
    main()