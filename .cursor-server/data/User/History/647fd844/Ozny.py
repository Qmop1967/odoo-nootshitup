#!/usr/bin/env python3

import xmlrpc.client
import json

# Load config
with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
    config = json.load(f)

odoo_config = config['odoo']['test_db']
url = f'http://{odoo_config["host"]}:{odoo_config["port"]}'

# Connect to Odoo
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(odoo_config['database'], odoo_config['username'], odoo_config['password'], {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("🔍 Checking Odoo product.template fields...")

# Check if x_zoho_item_id field exists
try:
    fields = models.execute_kw(odoo_config['database'], uid, odoo_config['password'], 
                              'product.template', 'fields_get', [], 
                              {'attributes': ['string', 'type']})
    
    if 'x_zoho_item_id' in fields:
        print('✅ x_zoho_item_id field EXISTS')
        print(f'   Type: {fields["x_zoho_item_id"]["type"]}')
        print(f'   Label: {fields["x_zoho_item_id"]["string"]}')
    else:
        print('❌ x_zoho_item_id field MISSING')
        print('🔧 This field needs to be created in Odoo first!')
        print('')
        print('SOLUTION: Create the field manually in Odoo:')
        print('1. Go to Settings > Technical > Database Structure > Models')
        print('2. Search for "product.template"')
        print('3. Add a new field:')
        print('   - Field Name: x_zoho_item_id')
        print('   - Field Label: Zoho Item ID')
        print('   - Field Type: Char')
        
    # Also check existing products
    products = models.execute_kw(odoo_config['database'], uid, odoo_config['password'],
                                'product.template', 'search_read', [[]],
                                {'fields': ['id', 'name'], 'limit': 5})
    
    print(f'\n📦 Sample Odoo products ({len(products)} shown):')
    for product in products:
        print(f'   ID {product["id"]}: {product["name"]}')
        
except Exception as e:
    print(f'❌ Error checking field: {e}') 