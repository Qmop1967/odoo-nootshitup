#!/usr/bin/env python3
"""
Test Zoho API Connections
========================
Test both Zoho Books and Inventory API connections with the configured tokens.
"""

import json
import requests

def get_access_token(refresh_token, client_id, client_secret):
    """Get access token from refresh token"""
    
    token_data = {
        'grant_type': 'refresh_token',
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token
    }
    
    try:
        response = requests.post('https://accounts.zoho.com/oauth/v2/token', data=token_data)
        response.raise_for_status()
        return response.json().get('access_token')
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None

def test_zoho_books(access_token, organization_id):
    """Test Zoho Books API"""
    
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test basic connection with organization info
        url = f'https://books.zoho.com/api/v3/organizations/{organization_id}'
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            org_name = data.get('organization', {}).get('name', 'Unknown')
            print(f"✅ Zoho Books: Connected successfully")
            print(f"   Organization: {org_name}")
            
            # Test contacts endpoint
            contacts_url = f'https://books.zoho.com/api/v3/contacts?organization_id={organization_id}&per_page=1'
            contacts_response = requests.get(contacts_url, headers=headers)
            if contacts_response.status_code == 200:
                contacts_data = contacts_response.json()
                contact_count = contacts_data.get('page_context', {}).get('total', 0)
                print(f"   Total Contacts: {contact_count}")
            
            return True
        else:
            print(f"❌ Zoho Books: API test failed - {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Zoho Books: Connection error - {e}")
        return False

def test_zoho_inventory(access_token, organization_id):
    """Test Zoho Inventory API"""
    
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test items endpoint
        url = f'https://inventory.zoho.com/api/v1/items?organization_id={organization_id}&per_page=1'
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Zoho Inventory: Connected successfully")
            
            # Get item count
            page_context = data.get('page_context', {})
            item_count = page_context.get('total', 0)
            print(f"   Total Items: {item_count}")
            
            return True
        else:
            print(f"❌ Zoho Inventory: API test failed - {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Zoho Inventory: Connection error - {e}")
        return False

def main():
    """Test all connections"""
    
    print("🧪 TESTING ZOHO API CONNECTIONS")
    print("=" * 40)
    
    # Load configuration
    try:
        with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return False
    
    # Test Zoho Books
    print("\n📚 TESTING ZOHO BOOKS...")
    books_config = config['zoho_books']
    books_access_token = get_access_token(
        books_config['refresh_token'],
        books_config['client_id'], 
        books_config['client_secret']
    )
    
    if books_access_token:
        books_success = test_zoho_books(books_access_token, books_config['organization_id'])
    else:
        print("❌ Zoho Books: Failed to get access token")
        books_success = False
    
    # Test Zoho Inventory
    print("\n📦 TESTING ZOHO INVENTORY...")
    inventory_config = config['zoho_inventory']
    inventory_access_token = get_access_token(
        inventory_config['refresh_token'],
        inventory_config['client_id'],
        inventory_config['client_secret']
    )
    
    if inventory_access_token:
        inventory_success = test_zoho_inventory(inventory_access_token, inventory_config['organization_id'])
    else:
        print("❌ Zoho Inventory: Failed to get access token")
        inventory_success = False
    
    # Summary
    print("\n" + "=" * 40)
    print("🎯 CONNECTION TEST SUMMARY:")
    print(f"   Zoho Books: {'✅ Success' if books_success else '❌ Failed'}")
    print(f"   Zoho Inventory: {'✅ Success' if inventory_success else '❌ Failed'}")
    
    if books_success and inventory_success:
        print("\n🎉 ALL CONNECTIONS SUCCESSFUL!")
        print("🚀 Ready to start migration!")
        return True
    else:
        print("\n❌ Some connections failed. Please check your tokens.")
        return False

if __name__ == "__main__":
    main() 