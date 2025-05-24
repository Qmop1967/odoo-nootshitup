#!/usr/bin/env python3

import json
import requests
import sys

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

def list_pricelists():
    """List all price lists and their status"""
    print("💰 ZOHO PRICE LISTS STATUS CHECK")
    print("=" * 50)
    
    access_token, zoho_config = get_zoho_access_token()
    if not access_token:
        return
        
    headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
    
    try:
        params = {
            'organization_id': zoho_config['organization_id']
        }
        
        # Try different endpoints for price books/price lists
        endpoints = [
            f"{zoho_config['base_url']}/pricebooks",
            f"{zoho_config['base_url']}/pricelists"
        ]
        
        all_pricelists = []
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, headers=headers, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    pricelists = data.get('pricebooks', data.get('pricelists', []))
                    if pricelists:
                        all_pricelists = pricelists
                        break
                    
            except Exception as e:
                print(f"Endpoint {endpoint} failed: {e}")
                continue
        
        if not all_pricelists:
            print("❌ No price lists found")
            return
        
        print(f"📋 Found {len(all_pricelists)} total price lists:")
        print("-" * 50)
        
        active_count = 0
        inactive_count = 0
        
        for i, pricelist in enumerate(all_pricelists, 1):
            name = pricelist.get('name', 'Unknown')
            status = pricelist.get('status', '').lower()
            pricebook_id = pricelist.get('pricebook_id', 'N/A')
            
            if status == 'active':
                print(f"{i:2}. ✅ ACTIVE   - {name} (ID: {pricebook_id})")
                active_count += 1
            else:
                print(f"{i:2}. ⏸️  INACTIVE - {name} (ID: {pricebook_id}) [Status: {status}]")
                inactive_count += 1
        
        print("-" * 50)
        print(f"📊 SUMMARY:")
        print(f"   ✅ Active Price Lists: {active_count}")
        print(f"   ⏸️  Inactive Price Lists: {inactive_count}")
        print(f"   📋 Total Price Lists: {len(all_pricelists)}")
        print("-" * 50)
        
        if active_count > 0:
            print(f"🚀 Ready to sync {active_count} active price lists!")
        else:
            print("⚠️  No active price lists found to sync.")
            
    except Exception as e:
        print(f"❌ Error fetching price lists: {e}")

if __name__ == "__main__":
    list_pricelists() 