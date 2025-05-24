#!/usr/bin/env python3
"""
Exchange Authorization Codes for Refresh Tokens
==============================================
Convert the authorization codes to proper refresh tokens.
"""

import json
import requests

def exchange_code_for_tokens(auth_code, client_id, client_secret):
    """Exchange authorization code for access and refresh tokens"""
    
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': 'http://localhost:8080/callback',
        'code': auth_code
    }
    
    try:
        response = requests.post('https://accounts.zoho.com/oauth/v2/token', data=token_data)
        print(f"Exchange Status: {response.status_code}")
        print(f"Exchange Response: {response.text}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to exchange code: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception during exchange: {e}")
        return None

def main():
    """Exchange both authorization codes"""
    
    print("🔄 EXCHANGING AUTHORIZATION CODES FOR REFRESH TOKENS")
    print("=" * 60)
    
    # Your credentials
    CLIENT_ID = "1000.GD7654YNI3QGSGCR26VJWN0TXSKGWJ"
    CLIENT_SECRET = "a1cd4bacae541d5266b3e16fb7437442f293159a22"
    
    # The codes you provided (these look like authorization codes)
    books_auth_code = "1000.59b5e2083b6e825f820208af872277.dc6ad9b42a47ba93f886279e3fe042e4"
    inventory_auth_code = "1000.7e0c7f985c7e7c7da6a15efa4012f.1dbcc67811f26b79e0e36978c2d0aaal"
    
    print("📚 EXCHANGING ZOHO BOOKS CODE...")
    books_tokens = exchange_code_for_tokens(books_auth_code, CLIENT_ID, CLIENT_SECRET)
    
    print("\n📦 EXCHANGING ZOHO INVENTORY CODE...")
    inventory_tokens = exchange_code_for_tokens(inventory_auth_code, CLIENT_ID, CLIENT_SECRET)
    
    if books_tokens and inventory_tokens:
        books_refresh = books_tokens.get('refresh_token')
        inventory_refresh = inventory_tokens.get('refresh_token')
        
        print("\n🎉 SUCCESS! TOKENS EXCHANGED:")
        print("=" * 40)
        print(f"📚 Books Refresh Token: {books_refresh}")
        print(f"📦 Inventory Refresh Token: {inventory_refresh}")
        
        # Update configuration
        try:
            with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
                config = json.load(f)
            
            config['zoho_books']['refresh_token'] = books_refresh
            config['zoho_inventory']['refresh_token'] = inventory_refresh
            
            with open('/opt/odoo/migration/config/zoho_config.json', 'w') as f:
                json.dump(config, f, indent=2)
                
            print("\n✅ Configuration updated with proper refresh tokens!")
            print("🚀 Ready to test connections!")
            
        except Exception as e:
            print(f"❌ Error updating config: {e}")
    else:
        print("\n❌ Failed to get proper tokens")

if __name__ == "__main__":
    main() 