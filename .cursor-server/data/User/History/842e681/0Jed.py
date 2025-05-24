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
    with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
        config = json.load(f)
    
    print("🔍 DEBUGGING TOKEN EXCHANGE")
    print("=" * 50)
    
    # Test Books
    print("\n📚 TESTING ZOHO BOOKS:")
    books_config = config['zoho_books']
    print(f"Client ID: {books_config['client_id']}")
    print(f"Organization ID: {books_config['organization_id']}")
    print(f"Refresh Token: {books_config['refresh_token'][:30]}...")
    
    # Try to exchange refresh token for access token
    token_data = {
        'grant_type': 'refresh_token',
        'client_id': books_config['client_id'],
        'client_secret': books_config['client_secret'],
        'refresh_token': books_config['refresh_token']
    }
    
    print("🔄 Attempting Books token exchange...")
    try:
        response = requests.post('https://accounts.zoho.com/oauth/v2/token', data=token_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test Inventory
    print("\n📦 TESTING ZOHO INVENTORY:")
    inventory_config = config['zoho_inventory']
    print(f"Client ID: {inventory_config['client_id']}")
    print(f"Organization ID: {inventory_config['organization_id']}")
    print(f"Refresh Token: {inventory_config['refresh_token'][:30]}...")
    
    # Try to exchange refresh token for access token
    token_data = {
        'grant_type': 'refresh_token',
        'client_id': inventory_config['client_id'],
        'client_secret': inventory_config['client_secret'],
        'refresh_token': inventory_config['refresh_token']
    }
    
    print("🔄 Attempting Inventory token exchange...")
    try:
        response = requests.post('https://accounts.zoho.com/oauth/v2/token', data=token_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    debug_token_exchange() 