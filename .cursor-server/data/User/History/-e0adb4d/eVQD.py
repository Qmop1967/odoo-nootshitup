#!/usr/bin/env python3
"""
Get Fresh Zoho Authorization Codes
=================================
Generate authorization URLs and exchange codes for refresh tokens.
"""

import json
import requests
from urllib.parse import urlencode

def generate_auth_urls():
    """Generate authorization URLs for both Zoho Books and Inventory"""
    
    CLIENT_ID = "1000.GD7654YNI3QGSGCR26VJWN0TXSKGWJ"
    REDIRECT_URI = "http://localhost:8080/callback"
    
    # Zoho Books authorization URL
    books_params = {
        'scope': 'ZohoBooks.fullaccess.all',
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'access_type': 'offline'
    }
    
    books_url = f"https://accounts.zoho.com/oauth/v2/auth?{urlencode(books_params)}"
    
    # Zoho Inventory authorization URL  
    inventory_params = {
        'scope': 'ZohoInventory.fullaccess.all',
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'access_type': 'offline'
    }
    
    inventory_url = f"https://accounts.zoho.com/oauth/v2/auth?{urlencode(inventory_params)}"
    
    print("🔗 FRESH AUTHORIZATION URLS")
    print("=" * 50)
    print("\n📚 ZOHO BOOKS:")
    print(f"   {books_url}")
    print("\n📦 ZOHO INVENTORY:")
    print(f"   {inventory_url}")
    
    print("\n" + "=" * 50)
    print("📋 INSTRUCTIONS:")
    print("1. Open each URL in your browser")
    print("2. Authorize the application")
    print("3. Copy the 'code' parameter from the redirect URL")
    print("4. Run: python exchange_fresh_codes.py <books_code> <inventory_code>")
    print("\nExample redirect URL:")
    print("http://localhost:8080/callback?code=1000.abc123...")
    print("Copy the part after 'code='")

def exchange_codes(books_code, inventory_code):
    """Exchange authorization codes for refresh tokens"""
    
    CLIENT_ID = "1000.GD7654YNI3QGSGCR26VJWN0TXSKGWJ"
    CLIENT_SECRET = "a1cd4bacae541d5266b3e16fb7437442f293159a22"
    REDIRECT_URI = "http://localhost:8080/callback"
    
    print("🔄 EXCHANGING FRESH CODES FOR TOKENS")
    print("=" * 50)
    
    # Exchange Books code
    print("\n📚 EXCHANGING ZOHO BOOKS CODE...")
    books_data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'code': books_code
    }
    
    try:
        books_response = requests.post('https://accounts.zoho.com/oauth/v2/token', data=books_data)
        print(f"Status: {books_response.status_code}")
        
        if books_response.status_code == 200:
            books_tokens = books_response.json()
            books_refresh = books_tokens.get('refresh_token')
            print(f"✅ Books Refresh Token: {books_refresh}")
        else:
            print(f"❌ Books Failed: {books_response.text}")
            books_refresh = None
            
    except Exception as e:
        print(f"❌ Books Exception: {e}")
        books_refresh = None
    
    # Exchange Inventory code
    print("\n📦 EXCHANGING ZOHO INVENTORY CODE...")
    inventory_data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'code': inventory_code
    }
    
    try:
        inventory_response = requests.post('https://accounts.zoho.com/oauth/v2/token', data=inventory_data)
        print(f"Status: {inventory_response.status_code}")
        
        if inventory_response.status_code == 200:
            inventory_tokens = inventory_response.json()
            inventory_refresh = inventory_tokens.get('refresh_token')
            print(f"✅ Inventory Refresh Token: {inventory_refresh}")
        else:
            print(f"❌ Inventory Failed: {inventory_response.text}")
            inventory_refresh = None
            
    except Exception as e:
        print(f"❌ Inventory Exception: {e}")
        inventory_refresh = None
    
    # Update configuration if both successful
    if books_refresh and inventory_refresh:
        try:
            with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
                config = json.load(f)
            
            config['zoho_books']['refresh_token'] = books_refresh
            config['zoho_inventory']['refresh_token'] = inventory_refresh
            
            with open('/opt/odoo/migration/config/zoho_config.json', 'w') as f:
                json.dump(config, f, indent=2)
                
            print("\n🎉 SUCCESS! Configuration updated!")
            print("🚀 Ready to test connections!")
            
        except Exception as e:
            print(f"❌ Error updating config: {e}")
    else:
        print("\n❌ Failed to get valid refresh tokens")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 1:
        # Generate URLs
        generate_auth_urls()
    elif len(sys.argv) == 3:
        # Exchange codes
        books_code = sys.argv[1]
        inventory_code = sys.argv[2]
        exchange_codes(books_code, inventory_code)
    else:
        print("Usage:")
        print("  python get_fresh_tokens.py                    # Generate auth URLs")
        print("  python get_fresh_tokens.py <books> <inventory> # Exchange codes") 