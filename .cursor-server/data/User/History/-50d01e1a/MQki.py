#!/usr/bin/env python3

import json
import xmlrpc.client

def check_current_products():
    """Check current products and delivery carriers in Odoo"""
    
    # Load config
    with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
        config = json.load(f)

    odoo_config = config['odoo']['test_db']
    url = f"http://{odoo_config['host']}:{odoo_config['port']}"

    # Connect to Odoo
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(odoo_config['database'], odoo_config['username'], odoo_config['password'], {})
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    print('🔍 CHECKING CURRENT PRODUCTS IN ODOO')
    print('=' * 50)

    # Check all products (including archived)
    all_products = models.execute_kw(
        odoo_config['database'], uid, odoo_config['password'],
        'product.template', 'search_read', [[]],
        {'fields': ['id', 'name', 'active'], 'limit': 10}
    )

    print(f'📦 Total products found: {len(all_products)}')

    if all_products:
        print('Sample products:')
        for product in all_products:
            status = '🟢 Active' if product.get('active', True) else '🔴 Archived'
            print(f'   ID {product["id"]}: {product["name"]} ({status})')
    else:
        print('✅ No products found - database is clean!')

    # Check delivery carriers (shipping methods)
    try:
        carriers = models.execute_kw(
            odoo_config['database'], uid, odoo_config['password'],
            'delivery.carrier', 'search_read', [[]],
            {'fields': ['id', 'name', 'product_id'], 'limit': 10}
        )
        
        print(f'\n🚚 Delivery carriers found: {len(carriers)}')
        if carriers:
            print('Delivery carriers:')
            for carrier in carriers:
                product_id = carrier.get('product_id')
                product_name = product_id[1] if product_id else 'None'
                print(f'   Carrier: {carrier["name"]} -> Product: {product_name} (ID: {product_id[0] if product_id else "None"})')
        
        # If there are carriers with missing products, that could be the issue
        problematic_carriers = []
        for carrier in carriers:
            product_id = carrier.get('product_id')
            if product_id:
                # Check if the product still exists
                try:
                    product_exists = models.execute_kw(
                        odoo_config['database'], uid, odoo_config['password'],
                        'product.template', 'search_count',
                        [[('id', '=', product_id[0])]]
                    )
                    if product_exists == 0:
                        problematic_carriers.append(carrier)
                except:
                    problematic_carriers.append(carrier)
        
        if problematic_carriers:
            print(f'\n⚠️ Found {len(problematic_carriers)} carriers with missing products:')
            for carrier in problematic_carriers:
                print(f'   ❌ {carrier["name"]} references missing product ID {carrier["product_id"][0]}')
            
            print(f'\n💡 SOLUTION: Fix or remove these carriers:')
            choice = input('Do you want to fix these carriers? (y/n): ').strip().lower()
            
            if choice == 'y':
                for carrier in problematic_carriers:
                    try:
                        # Remove the product reference
                        models.execute_kw(
                            odoo_config['database'], uid, odoo_config['password'],
                            'delivery.carrier', 'write',
                            [[carrier['id']], {'product_id': False}]
                        )
                        print(f'   ✅ Fixed carrier: {carrier["name"]}')
                    except Exception as e:
                        print(f'   ❌ Failed to fix carrier {carrier["name"]}: {e}')
                        
                        # Try to delete the carrier instead
                        try:
                            models.execute_kw(
                                odoo_config['database'], uid, odoo_config['password'],
                                'delivery.carrier', 'unlink', [[carrier['id']]]
                            )
                            print(f'   ✅ Deleted carrier: {carrier["name"]}')
                        except Exception as e2:
                            print(f'   ❌ Failed to delete carrier {carrier["name"]}: {e2}')
        
    except Exception as e:
        print(f'\n⚠️ Could not check delivery carriers: {e}')

if __name__ == "__main__":
    check_current_products() 