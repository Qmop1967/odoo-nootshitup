#!/usr/bin/env python3

import json
import requests
import xmlrpc.client
import re

def sanitize_text(text):
    """Sanitize text for Odoo compatibility"""
    if not text:
        return ""
    
    text = str(text).strip()
    
    # Replace problematic characters
    replacements = {
        '❌': 'X', '✅': 'V', '🔥': '', '💡': '', '⚡': '', '🎯': '',
        '📱': '', '💻': '', '🖥️': '', '⌨️': '', '🖱️': '', '💾': '',
        '💿': '', '📀': '', '🔌': '', '🔋': '', '📺': '', '📷': '',
        '📹': '', '🎥': '', '📞': '', '☎️': '', '📠': '', '📡': '',
        '🎧': '', '🎤': '', '🔊': '', '🔇': '', '🔈': '', '🔉': ''
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Remove any remaining non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    if not text:
        text = "Product"
    
    return text

def test_sync():
    print("🧪 Testing Simple Sync...")
    
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
    
    print("✅ Got Zoho access token")
    
    # Get first 5 products from Zoho
    headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
    params = {
        'organization_id': zoho_config['organization_id'],
        'page': 1,
        'per_page': 5
    }
    
    zoho_url = f"{zoho_config['base_url']}/items"
    response = requests.get(zoho_url, headers=headers, params=params, timeout=30)
    zoho_products = response.json().get('items', [])
    
    print(f"✅ Got {len(zoho_products)} test products from Zoho")
    
    # Try to create one product in Odoo
    for i, zoho_product in enumerate(zoho_products):
        print(f"\n🔍 Testing product {i+1}: {zoho_product.get('name', 'Unknown')}")
        
        # Check if already exists
        existing = models.execute_kw(
            odoo_config['database'], uid, odoo_config['password'],
            'product.template', 'search_read',
            [[('x_zoho_item_id', '=', str(zoho_product.get('item_id')))]],
            {'fields': ['id', 'name'], 'limit': 1}
        )
        
        if existing:
            print(f"   ✅ Already exists in Odoo (ID: {existing[0]['id']})")
            continue
        
        # Transform product data
        name = sanitize_text(zoho_product.get('name', f"Product {zoho_product.get('item_id')}"))
        
        # Convert prices
        rate = float(zoho_product.get('rate', 0))
        purchase_rate = float(zoho_product.get('purchase_rate', 0))
        
        # Convert USD to IQD if needed
        if rate < 100:
            rate = rate * 1500
        if purchase_rate < 100:
            purchase_rate = purchase_rate * 1500
        
        product_data = {
            'name': name,
            'list_price': rate,
            'standard_price': purchase_rate,
            'default_code': sanitize_text(zoho_product.get('sku', '')),
            'description': sanitize_text(zoho_product.get('description', '')),
            'x_zoho_item_id': str(zoho_product.get('item_id')),
            'type': 'product',
            'sale_ok': True,
            'purchase_ok': True,
            'tracking': 'none'
        }
        
        print(f"   📝 Sanitized name: '{name}'")
        print(f"   💰 Prices: List={rate} IQD, Cost={purchase_rate} IQD")
        
        try:
            # Try to create the product
            product_id = models.execute_kw(
                odoo_config['database'], uid, odoo_config['password'],
                'product.template', 'create', [product_data]
            )
            
            if product_id:
                print(f"   ✅ SUCCESS! Created product ID: {product_id}")
            else:
                print(f"   ❌ FAILED: Product creation returned None")
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            
            # If it's a field error, try with minimal data
            try:
                minimal_data = {
                    'name': name,
                    'x_zoho_item_id': str(zoho_product.get('item_id')),
                    'type': 'product'
                }
                print(f"   🔄 Trying with minimal data...")
                
                product_id = models.execute_kw(
                    odoo_config['database'], uid, odoo_config['password'],
                    'product.template', 'create', [minimal_data]
                )
                
                if product_id:
                    print(f"   ✅ SUCCESS with minimal data! Product ID: {product_id}")
                else:
                    print(f"   ❌ FAILED even with minimal data")
                    
            except Exception as e2:
                print(f"   ❌ MINIMAL DATA ALSO FAILED: {str(e2)}")
        
        break  # Test only first product
    
    print(f"\n📊 Final count check:")
    
    # Check final counts
    zoho_count = len(models.execute_kw(
        odoo_config['database'], uid, odoo_config['password'],
        'product.template', 'search', [[('x_zoho_item_id', '!=', False)]]
    ))
    
    odoo_total = len(models.execute_kw(
        odoo_config['database'], uid, odoo_config['password'],
        'product.template', 'search', [[]]
    ))
    
    print(f"   Odoo products with Zoho ID: {zoho_count}")
    print(f"   Odoo products total: {odoo_total}")

if __name__ == "__main__":
    test_sync() 