#!/usr/bin/env python3
"""
Debug Zoho Token Exchange
========================
Debug script to see what's happening with token exchange.
"""

import json
import requests

def debug_token_exchange():
    """Debug the token exchange process"""
    
    # Load configuration
    config_path = '/opt/odoo/migration/config/zoho_config.json'
    print(f"Loading config from: {config_path}")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print("🔍 DEBUGGING TOKEN EXCHANGE")
    print("=" * 50)
    
    # Test Books
    print("\n📚 TESTING ZOHO BOOKS:")
    books_config = config['zoho_books']
    print(f"Client ID: {books_config['client_id']}")
    print(f"Organization ID: {books_config['organization_id']}")
    books_refresh = books_config.get('refresh_token')
    if books_refresh:
        print(f"Refresh Token: {books_refresh[:30]}...")
    else:
        print("❌ No refresh token found!")
        return
    
    # Try to exchange refresh token for access token
    token_data = {
        'grant_type': 'refresh_token',
        'client_id': books_config['client_id'],
        'client_secret': books_config['client_secret'],
        'refresh_token': books_refresh
    }
    
    print("🔄 Attempting Books token exchange...")
    try:
        response = requests.post('https://accounts.zoho.com/oauth/v2/token', data=token_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            token_info = response.json()
            access_token = token_info.get('access_token')
            if access_token:
                print(f"✅ Books Access Token obtained: {access_token[:20]}...")
                
                # Test API call
                headers = {
                    'Authorization': f'Zoho-oauthtoken {access_token}',
                    'Content-Type': 'application/json'
                }
                
                test_url = f'https://books.zoho.com/api/v3/organizations/{books_config["organization_id"]}'
                test_response = requests.get(test_url, headers=headers)
                print(f"API Test Status: {test_response.status_code}")
                if test_response.status_code == 200:
                    org_data = test_response.json()
                    org_name = org_data.get('organization', {}).get('name', 'Unknown')
                    print(f"✅ Organization: {org_name}")
                else:
                    print(f"❌ API Test Failed: {test_response.text}")
        
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test Inventory
    print("\n📦 TESTING ZOHO INVENTORY:")
    inventory_config = config['zoho_inventory']
    print(f"Client ID: {inventory_config['client_id']}")
    print(f"Organization ID: {inventory_config['organization_id']}")
    inventory_refresh = inventory_config.get('refresh_token')
    if inventory_refresh:
        print(f"Refresh Token: {inventory_refresh[:30]}...")
    else:
        print("❌ No refresh token found!")
        return
    
    # Try to exchange refresh token for access token
    token_data = {
        'grant_type': 'refresh_token',
        'client_id': inventory_config['client_id'],
        'client_secret': inventory_config['client_secret'],
        'refresh_token': inventory_refresh
    }
    
    print("🔄 Attempting Inventory token exchange...")
    try:
        response = requests.post('https://accounts.zoho.com/oauth/v2/token', data=token_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            token_info = response.json()
            access_token = token_info.get('access_token')
            if access_token:
                print(f"✅ Inventory Access Token obtained: {access_token[:20]}...")
                
                # Test API call
                headers = {
                    'Authorization': f'Zoho-oauthtoken {access_token}',
                    'Content-Type': 'application/json'
                }
                
                test_url = f'https://inventory.zoho.com/api/v1/items?organization_id={inventory_config["organization_id"]}&per_page=1'
                test_response = requests.get(test_url, headers=headers)
                print(f"API Test Status: {test_response.status_code}")
                if test_response.status_code == 200:
                    items_data = test_response.json()
                    item_count = items_data.get('page_context', {}).get('total', 0)
                    print(f"✅ Total Items: {item_count}")
                else:
                    print(f"❌ API Test Failed: {test_response.text}")
        
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    debug_token_exchange() 