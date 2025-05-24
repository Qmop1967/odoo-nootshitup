#!/usr/bin/env python3

import json
import requests
import xmlrpc.client
from difflib import SequenceMatcher
import re

def sanitize_for_comparison(text):
    """Sanitize text for comparison"""
    if not text:
        return ""
    
    text = str(text).lower().strip()
    
    # Remove special characters and emojis
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def main():
    print('🔗 MATCHING EXISTING PRODUCTS WITH ZOHO IDs')
    print('This will add Zoho IDs to existing Odoo products')
    print('=' * 60)

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

    print('✅ Connected to Odoo')

    # Get Zoho access token
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

    print('✅ Got Zoho access token')

    # Get first 50 Zoho products for testing
    params = {
        'organization_id': zoho_config['organization_id'],
        'page': 1,
        'per_page': 50
    }

    zoho_url = f"{zoho_config['base_url']}/items"
    response = requests.get(zoho_url, headers=headers, params=params, timeout=30)
    zoho_products = response.json().get('items', [])

    print(f'📦 Got {len(zoho_products)} Zoho products for testing')

    # Get Odoo products without Zoho ID
    odoo_products = models.execute_kw(
        odoo_config['database'], uid, odoo_config['password'],
        'product.template', 'search_read',
        [[('x_zoho_item_id', '=', False)]],
        {'fields': ['id', 'name'], 'limit': 100}
    )

    print(f'📦 Got {len(odoo_products)} Odoo products without Zoho ID')

    # Try to match by name similarity
    matches = 0
    for i, zoho_product in enumerate(zoho_products):
        zoho_name = sanitize_for_comparison(zoho_product.get('name', ''))
        zoho_display_name = zoho_product.get('name', 'Unknown')
        
        if not zoho_name:
            continue
            
        best_match = None
        best_score = 0
        
        for odoo_product in odoo_products:
            odoo_name = sanitize_for_comparison(odoo_product['name'])
            score = SequenceMatcher(None, zoho_name, odoo_name).ratio()
            
            if score > best_score and score > 0.85:  # 85% similarity
                best_score = score
                best_match = odoo_product
        
        if best_match:
            print(f'✅ MATCH {i+1} ({best_score:.2f}): {zoho_display_name[:50]}... -> {best_match["name"][:50]}...')
            
            # Update Odoo product with Zoho ID
            try:
                models.execute_kw(
                    odoo_config['database'], uid, odoo_config['password'],
                    'product.template', 'write',
                    [[best_match['id']], {'x_zoho_item_id': str(zoho_product.get('item_id'))}]
                )
                matches += 1
                print(f'   ✅ Added Zoho ID {zoho_product.get("item_id")} to Odoo product {best_match["id"]}')
                
                # Remove from list to avoid duplicate matches
                odoo_products.remove(best_match)
                
            except Exception as e:
                print(f'   ❌ Failed to update: {e}')
        else:
            print(f'❌ NO MATCH {i+1}: {zoho_display_name[:50]}...')

    print(f'\n📊 RESULTS: {matches} products matched and updated')
    
    # Check final status
    final_with_zoho_id = len(models.execute_kw(
        odoo_config['database'], uid, odoo_config['password'],
        'product.template', 'search', [[('x_zoho_item_id', '!=', False)]]
    ))
    
    print(f'📊 Final Status: {final_with_zoho_id} Odoo products now have Zoho IDs')

if __name__ == "__main__":
    main() 