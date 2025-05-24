#!/usr/bin/env python3

import xmlrpc.client
import json

# Connect to Odoo and count products
with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
    config = json.load(f)

odoo_config = config['odoo']['test_db']
url = f"http://{odoo_config['host']}:{odoo_config['port']}"

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(odoo_config['database'], odoo_config['username'], odoo_config['password'], {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
products = models.execute_kw(
    odoo_config['database'], 
    uid, 
    odoo_config['password'], 
    'product.template', 
    'search_read', 
    [[]], 
    {'fields': ['id', 'name', 'create_date'], 'order': 'create_date desc', 'limit': 10}
)

print(f'📦 Current Odoo products: {len(products)} (showing latest 10)')
print('✅ Most recent products:')
for product in products:
    print(f'   - {product["name"]} (Created: {product["create_date"]})') 