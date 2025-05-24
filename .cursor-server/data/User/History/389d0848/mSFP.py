#!/usr/bin/env python3

import json
import requests
import xmlrpc.client
import re

def main():
    print("🔧 FIXING ZOHO-ODOO SYNC ISSUE")
    print("=" * 50)
    
    # Load config
    with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
        config = json.load(f)
    
    zoho_config = config['zoho_books']
    odoo_config = config['odoo']['test_db']
    
    # Connect to Odoo
    url = f"http://{odoo_config['host']}:{odoo_config['port']}"
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(odoo_config['database'], odoo_config['username'], odoo_config['password'], {})
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    print("✅ Connected to Odoo")
    
    # Check current status
    odoo_total = len(models.execute_kw(
        odoo_config['database'], uid, odoo_config['password'],
        'product.template', 'search', [[]]
    ))
    
    odoo_with_zoho_id = len(models.execute_kw(
        odoo_config['database'], uid, odoo_config['password'],
        'product.template', 'search', [[('x_zoho_item_id', '!=', False)]]
    ))
    
    print(f"📊 Current Status:")
    print(f"   Total Odoo products: {odoo_total}")
    print(f"   Products with Zoho ID: {odoo_with_zoho_id}")
    print(f"   Products without Zoho ID: {odoo_total - odoo_with_zoho_id}")
    
    # Get Zoho products count
    token_url = "https://accounts.zoho.com/oauth/v2/token"
    token_params = {
        'refresh_token': zoho_config['refresh_token'],
        'client_id': zoho_config['client_id'],
        'client_secret': zoho_config['client_secret'],
        'grant_type': 'refresh_token'
    }
    
    response = requests.post(token_url, data=token_params, timeout=30)
    access_token = response.json()['access_token']
    headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
    
    # Get total Zoho count
    params = {
        'organization_id': zoho_config['organization_id'],
        'page': 1,
        'per_page': 1
    }
    
    zoho_url = f"{zoho_config['base_url']}/items"
    response = requests.get(zoho_url, headers=headers, params=params, timeout=30)
    page_context = response.json().get('page_context', {})
    zoho_total = page_context.get('total', 0)
    
    print(f"   Total Zoho products: {zoho_total}")
    print(f"   Expected sync difference: {zoho_total - odoo_with_zoho_id}")
    
    print(f"\n💡 SOLUTION OPTIONS:")
    print(f"1. 🗑️  DELETE all existing Odoo products and do clean import")
    print(f"2. 🔗 MATCH existing Odoo products with Zoho products by name")
    print(f"3. 🆕 CREATE only new products (skip existing ones)")
    
    choice = input(f"\nSelect option (1, 2, or 3): ").strip()
    
    if choice == "1":
        print(f"\n⚠️  WARNING: This will DELETE all {odoo_total} existing products!")
        confirm = input("Type 'DELETE' to confirm: ").strip()
        
        if confirm == "DELETE":
            # Delete all products
            all_products = models.execute_kw(
                odoo_config['database'], uid, odoo_config['password'],
                'product.template', 'search', [[]]
            )
            
            models.execute_kw(
                odoo_config['database'], uid, odoo_config['password'],
                'product.template', 'unlink', [all_products]
            )
            
            print(f"✅ Deleted all {len(all_products)} products")
            print(f"🚀 Now run: python3 sync_service_manager_fixed.py sync-once")
        else:
            print("❌ Operation cancelled")
    
    elif choice == "2":
        print(f"\n🔗 Matching products by name similarity...")
        print("This will take a few minutes...")
        
        # This would be complex - matching by name similarity
        print("⚠️  This option requires custom implementation")
        print("🔧 For now, use option 1 or 3")
    
    elif choice == "3":
        print(f"\n🆕 Setting up for incremental sync...")
        print("This will modify the sync service to skip duplicates")
        
        # Create a marker file to tell sync service to skip existing products
        marker_file = "/opt/odoo/migration/data/sync_service/skip_existing_products.flag"
        with open(marker_file, 'w') as f:
            f.write("true")
        
        print("✅ Created skip-existing-products flag")
        print("🚀 Now run: python3 sync_service_manager_fixed.py sync-once")
    
    else:
        print("❌ Invalid option")

if __name__ == "__main__":
    main() 