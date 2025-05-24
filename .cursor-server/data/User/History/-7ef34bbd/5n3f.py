#!/usr/bin/env python3

import xmlrpc.client
import json

def check_status():
    with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
        config = json.load(f)

    odoo_config = config['odoo']['test_db']
    url = f"http://{odoo_config['host']}:{odoo_config['port']}"
    
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(odoo_config['database'], odoo_config['username'], odoo_config['password'], {})
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    # Quick count of products
    total = len(models.execute_kw(odoo_config['database'], uid, odoo_config['password'], 'product.template', 'search', [[]]))

    # Count with images
    with_images = len(models.execute_kw(odoo_config['database'], uid, odoo_config['password'], 'product.template', 'search', [[('image_1920', '!=', False)]]))

    # Count with USD prices
    usd_prices = len(models.execute_kw(odoo_config['database'], uid, odoo_config['password'], 'product.template', 'search', [['|', '&', ('list_price', '>', 0), ('list_price', '<', 100), '&', ('standard_price', '>', 0), ('standard_price', '<', 100)]]))

    print(f'📊 Current Status:')
    print(f'   Total products: {total}')
    print(f'   Products with images: {with_images}')
    print(f'   Products missing images: {total - with_images}')
    print(f'   Products with USD prices: {usd_prices}')

if __name__ == "__main__":
    check_status() 