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
    
    books_config = config['zoho_books']
    
    print("🔍 DEBUGGING TOKEN EXCHANGE")
    print("=" * 40)
    print(f"Client ID: {books_config['client_id']}")
    print(f"Organization ID: {books_config['organization_id']}")
    print(f"Refresh Token: {books_config['refresh_token'][:20]}...")
    
    # Try to exchange refresh token for access token
    token_data = {
        'grant_type': 'refresh_token',
        'client_id': books_config['client_id'],
        'client_secret': books_config['client_secret'],
        'refresh_token': books_config['refresh_token']
    }
    
    print("\n🔄 ATTEMPTING TOKEN EXCHANGE...")
    
    try:
        response = requests.post('https://accounts.zoho.com/oauth/v2/token', data=token_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            token_info = response.json()
            print(f"✅ Success! Access Token: {token_info.get('access_token', 'None')[:20]}...")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    debug_token_exchange() 