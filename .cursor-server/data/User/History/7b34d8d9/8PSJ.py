#!/usr/bin/env python3
"""
Simple Test Migration
===================
Simplified test to verify all connections work before running full migration.
"""

import json
import requests
import odoorpc

def test_zoho_books():
    """Test Zoho Books API connection"""
    print("📚 Testing Zoho Books API...")
    
    with open('config/zoho_config.json', 'r') as f:
        config = json.load(f)
    
    books_config = config['zoho_books']
    
    # Get access token
    token_data = {
        'grant_type': 'refresh_token',
        'client_id': books_config['client_id'],
        'client_secret': books_config['client_secret'],
        'refresh_token': books_config['refresh_token']
    }
    
    response = requests.post('https://accounts.zoho.com/oauth/v2/token', data=token_data)
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        print(f"✅ Zoho Books: Access token obtained")
        
        # Test API call
        headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
        test_url = f'{books_config["base_url"]}/organizations/{books_config["organization_id"]}'
        test_response = requests.get(test_url, headers=headers)
        
        if test_response.status_code == 200:
            org_data = test_response.json()
            org_name = org_data.get('organization', {}).get('name', 'Unknown')
            print(f"✅ Zoho Books: Organization '{org_name}' accessible")
            return True
        else:
            print(f"❌ Zoho Books: API test failed - {test_response.status_code}")
            return False
    else:
        print(f"❌ Zoho Books: Token exchange failed - {response.status_code}")
        return False

def test_zoho_inventory():
    """Test Zoho Inventory API connection"""
    print("\n📦 Testing Zoho Inventory API...")
    
    with open('config/zoho_config.json', 'r') as f:
        config = json.load(f)
    
    inventory_config = config['zoho_inventory']
    
    # Get access token
    token_data = {
        'grant_type': 'refresh_token',
        'client_id': inventory_config['client_id'],
        'client_secret': inventory_config['client_secret'],
        'refresh_token': inventory_config['refresh_token']
    }
    
    response = requests.post('https://accounts.zoho.com/oauth/v2/token', data=token_data)
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        print(f"✅ Zoho Inventory: Access token obtained")
        
        # Test API call
        headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
        test_url = f'{inventory_config["base_url"]}/items?organization_id={inventory_config["organization_id"]}&per_page=1'
        test_response = requests.get(test_url, headers=headers)
        
        if test_response.status_code == 200:
            items_data = test_response.json()
            item_count = items_data.get('page_context', {}).get('total', 0)
            print(f"✅ Zoho Inventory: {item_count} items found")
            return True
        else:
            print(f"❌ Zoho Inventory: API test failed - {test_response.status_code}")
            return False
    else:
        print(f"❌ Zoho Inventory: Token exchange failed - {response.status_code}")
        return False

def test_odoo_connection():
    """Test Odoo test database connection"""
    print("\n🔗 Testing Odoo Test Database...")
    
    with open('config/zoho_config.json', 'r') as f:
        config = json.load(f)
    
    odoo_config = config['odoo']['test_db']
    
    try:
        # Connect to Odoo
        odoo = odoorpc.ODOO(odoo_config['host'], port=odoo_config['port'])
        print(f"✅ Connected to Odoo at {odoo_config['host']}:{odoo_config['port']}")
        
        # List databases
        databases = odoo.db.list()
        print(f"📊 Available databases: {databases}")
        
        if odoo_config['database'] in databases:
            print(f"✅ Target database '{odoo_config['database']}' found")
            
            # Try to login
            try:
                odoo.login(odoo_config['database'], odoo_config['username'], odoo_config['password'])
                print(f"✅ Successfully logged in as '{odoo_config['username']}'")
                
                # Test basic operations
                user_name = odoo.env.user.name
                company_name = odoo.env.user.company_id.name
                print(f"👤 User: {user_name}")
                print(f"🏢 Company: {company_name}")
                
                return True
                
            except Exception as e:
                print(f"❌ Login failed: {e}")
                return False
        else:
            print(f"❌ Database '{odoo_config['database']}' not found")
            return False
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def main():
    """Run all connection tests"""
    print("🧪 SIMPLE MIGRATION CONNECTION TEST")
    print("=" * 50)
    
    tests = [
        ("Zoho Books API", test_zoho_books),
        ("Zoho Inventory API", test_zoho_inventory),
        ("Odoo Test Database", test_odoo_connection)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: Exception - {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("🎯 TEST RESULTS:")
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Ready for migration!")
        return True
    else:
        print("\n❌ Some tests failed. Please fix issues before migration.")
        return False

if __name__ == "__main__":
    main() 