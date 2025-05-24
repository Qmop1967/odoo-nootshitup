#!/usr/bin/env python3

import json
import requests

def get_zoho_access_token():
    """Get fresh access token from Zoho"""
    try:
        with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
            config = json.load(f)
        
        zoho_config = config['zoho_books']
        
        token_url = "https://accounts.zoho.com/oauth/v2/token"
        token_params = {
            'refresh_token': zoho_config['refresh_token'],
            'client_id': zoho_config['client_id'],
            'client_secret': zoho_config['client_secret'],
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(token_url, data=token_params, timeout=30)
        response.raise_for_status()
        return response.json()['access_token'], zoho_config
    except Exception as e:
        print(f"❌ Error getting Zoho token: {e}")
        return None, None

def main():
    print("📦 Checking Zoho Books products...")
    
    access_token, zoho_config = get_zoho_access_token()
    if not access_token:
        print("❌ Could not get Zoho access token")
        return
        
    headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
    all_products = []
    page = 1
    
    while True:
        try:
            params = {
                'organization_id': zoho_config['organization_id'],
                'page': page,
                'per_page': 200
            }
            
            url = f"{zoho_config['base_url']}/items"
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code != 200:
                break
                
            data = response.json()
            items = data.get('items', [])
            
            if not items:
                break
                
            all_products.extend(items)
            print(f"   📄 Page {page}: {len(items)} products")
            page += 1
            
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break
    
    print(f"\n📊 COMPARISON:")
    print(f"   Zoho Books: {len(all_products)} products")
    
    # Show latest 5 products from Zoho
    print(f"\n✅ Latest 5 Zoho products:")
    for product in all_products[-5:]:
        print(f"   - {product.get('name', 'Unknown')} (ID: {product.get('item_id')})")

if __name__ == "__main__":
    main() 