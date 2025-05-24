#!/usr/bin/env python3
"""
Simplified Zoho Token Generator (No Redirect Required)
====================================================
This version uses device flow or manual token entry to avoid redirect URI issues.
"""

import json
import requests

# Your credentials
CLIENT_ID = "1000.GD7654YNI3QGSGCR26VJWN0TXSKGWJ"
CLIENT_SECRET = "a1cd4bacae541d5266b3e16fb7437442f293159a22"
ORGANIZATION_ID = "748369814"

def manual_token_method():
    """Manual token entry method"""
    
    print("🔐 SIMPLIFIED ZOHO AUTHORIZATION")
    print("=" * 50)
    print()
    print("📋 INSTRUCTIONS:")
    print("1. Go to Zoho API Console: https://api-console.zoho.com/")
    print("2. Find your application and click 'Self Client'")
    print("3. Click 'Generate Token' for the scopes you need")
    print("4. Copy the generated tokens")
    print()
    
    print("📚 ZOHO BOOKS TOKEN:")
    print("- Scope needed: ZohoBooks.fullaccess.all")
    books_token = input("Enter Zoho Books refresh token: ").strip()
    
    print("\n📦 ZOHO INVENTORY TOKEN:")
    print("- Scope needed: ZohoInventory.fullaccess.all")
    inventory_token = input("Enter Zoho Inventory refresh token: ").strip()
    
    if books_token and inventory_token:
        return books_token, inventory_token
    else:
        print("❌ Both tokens are required!")
        return None, None

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
        return True
        
    except Exception as e:
        print(f"❌ Error updating configuration: {e}")
        return False

def test_token(refresh_token, service_name, base_url):
    """Test if a refresh token works"""
    
    try:
        # Try to get a new access token
        token_data = {
            'grant_type': 'refresh_token',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'refresh_token': refresh_token
        }
        
        response = requests.post('https://accounts.zoho.com/oauth/v2/token', data=token_data)
        
        if response.status_code == 200:
            print(f"✅ {service_name}: Token is valid")
            return True
        else:
            print(f"❌ {service_name}: Token test failed - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ {service_name}: Error testing token - {e}")
        return False

def main():
    """Main process"""
    
    print("🚀 GETTING ZOHO API TOKENS")
    print("=" * 40)
    print()
    print("Due to redirect URI issues, we'll use the manual method.")
    print()
    
    # Get tokens manually
    books_token, inventory_token = manual_token_method()
    
    if not books_token or not inventory_token:
        print("❌ Setup incomplete. Exiting.")
        return False
    
    print("\n🧪 TESTING TOKENS...")
    
    # Test both tokens
    books_valid = test_token(books_token, "Zoho Books", "https://books.zoho.com/api/v3")
    inventory_valid = test_token(inventory_token, "Zoho Inventory", "https://inventory.zoho.com/api/v1")
    
    if books_valid and inventory_valid:
        # Update configuration
        if update_config(books_token, inventory_token):
            print("\n🎉 SETUP COMPLETE!")
            print("=" * 25)
            print("✅ Zoho Books: Authorized & Tested")
            print("✅ Zoho Inventory: Authorized & Tested")
            print("✅ Configuration: Updated")
            print("\n🚀 Ready for migration testing!")
            return True
    
    print("❌ Setup failed. Please check your tokens.")
    return False

if __name__ == "__main__":
    main() 