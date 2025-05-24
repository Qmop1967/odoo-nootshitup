#!/usr/bin/env python3
"""
Simple Zoho Token Generator
===========================
This script generates the authorization URLs and handles token exchange.
"""

import json
import requests

# Your credentials
CLIENT_ID = "1000.GD7654YNI3QGSGCR26VJWN0TXSKGWJ"
CLIENT_SECRET = "a1cd4bacae541d5266b3e16fb7437442f293159a22"
ORGANIZATION_ID = "748369814"
REDIRECT_URI = "http://localhost:8080/callback"

def generate_auth_urls():
    """Generate authorization URLs"""
    
    books_scopes = "ZohoBooks.fullaccess.all"
    inventory_scopes = "ZohoInventory.fullaccess.all"
    
    books_url = (
        f"https://accounts.zoho.com/oauth/v2/auth"
        f"?scope={books_scopes}"
        f"&client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&access_type=offline"
    )
    
    inventory_url = (
        f"https://accounts.zoho.com/oauth/v2/auth"
        f"?scope={inventory_scopes}"
        f"&client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&access_type=offline"
    )
    
    return books_url, inventory_url

def get_access_token(auth_code):
    """Exchange authorization code for access token"""
    
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'code': auth_code
    }
    
    try:
        response = requests.post('https://accounts.zoho.com/oauth/v2/token', data=token_data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None

def update_config(books_refresh_token, inventory_refresh_token):
    """Update configuration file with tokens"""
    
    config_path = '/opt/odoo/migration/config/zoho_config.json'
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        config['zoho_books']['refresh_token'] = books_refresh_token
        config['zoho_inventory']['refresh_token'] = inventory_refresh_token
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        print("✅ Configuration updated successfully!")
        
    except Exception as e:
        print(f"❌ Error updating configuration: {e}")

def main():
    """Main authorization process"""
    
    print("🔐 ZOHO API AUTHORIZATION")
    print("=" * 40)
    
    # Generate URLs
    books_url, inventory_url = generate_auth_urls()
    
    print("\n📚 STEP 1: ZOHO BOOKS AUTHORIZATION")
    print("-" * 40)
    print("1. Click this link (or copy to browser):")
    print(f"\n{books_url}\n")
    print("2. Click 'Accept' to authorize")
    print("3. Copy the 'code' from the redirect URL")
    print("   (It will look like: http://localhost:8080/callback?code=XXXXXXXXX)")
    
    books_code = input("\nEnter Zoho Books authorization code: ").strip()
    
    print("\n📦 STEP 2: ZOHO INVENTORY AUTHORIZATION")
    print("-" * 40)
    print("1. Click this link (or copy to browser):")
    print(f"\n{inventory_url}\n")
    print("2. Click 'Accept' to authorize")
    print("3. Copy the 'code' from the redirect URL")
    
    inventory_code = input("\nEnter Zoho Inventory authorization code: ").strip()
    
    # Exchange codes for tokens
    print("\n🔄 GETTING ACCESS TOKENS...")
    
    books_token_data = get_access_token(books_code)
    if not books_token_data:
        print("❌ Failed to get Zoho Books token")
        return False
        
    inventory_token_data = get_access_token(inventory_code)
    if not inventory_token_data:
        print("❌ Failed to get Zoho Inventory token")
        return False
    
    # Update configuration
    books_refresh_token = books_token_data.get('refresh_token')
    inventory_refresh_token = inventory_token_data.get('refresh_token')
    
    if books_refresh_token and inventory_refresh_token:
        update_config(books_refresh_token, inventory_refresh_token)
        
        print("\n🎉 AUTHORIZATION COMPLETE!")
        print("=" * 30)
        print("✅ Zoho Books: Authorized")
        print("✅ Zoho Inventory: Authorized")
        print("✅ Configuration: Updated")
        print("\n🚀 Ready for migration!")
        return True
    else:
        print("❌ Failed to get refresh tokens")
        return False

if __name__ == "__main__":
    main() 