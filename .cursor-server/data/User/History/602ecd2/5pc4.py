#!/usr/bin/env python3

import xmlrpc.client
import json

def add_zoho_field_to_odoo():
    """Add zoho_item_id field to product.template in Odoo"""
    
    # Load configuration
    with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
        config = json.load(f)
    
    odoo_config = config['odoo']['test_db']
    url = f"http://{odoo_config['host']}:{odoo_config['port']}"
    
    # Connect to Odoo
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(
        odoo_config['database'],
        odoo_config['username'],
        odoo_config['password'],
        {}
    )
    
    if not uid:
        print("❌ Failed to authenticate with Odoo")
        return False
    
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    try:
        # Check if field already exists
        print("🔍 Checking if zoho_item_id field exists...")
        
        field_exists = models.execute_kw(
            odoo_config['database'],
            uid,
            odoo_config['password'],
            'ir.model.fields',
            'search_count',
            [[('model', '=', 'product.template'), ('name', '=', 'zoho_item_id')]]
        )
        
        if field_exists:
            print("✅ Field zoho_item_id already exists in product.template")
            return True
        
        # Add the field
        print("➕ Adding zoho_item_id field to product.template...")
        
        field_data = {
            'name': 'x_zoho_item_id',
            'field_description': 'Zoho Item ID',
            'model': 'product.template',
            'model_id': models.execute_kw(
                odoo_config['database'],
                uid,
                odoo_config['password'],
                'ir.model',
                'search',
                [[('model', '=', 'product.template')]],
                {'limit': 1}
            )[0],
            'ttype': 'char',
            'size': 50,
            'readonly': True,
            'help': 'Unique identifier from Zoho Books/Inventory'
        }
        
        field_id = models.execute_kw(
            odoo_config['database'],
            uid,
            odoo_config['password'],
            'ir.model.fields',
            'create',
            [field_data]
        )
        
        if field_id:
            print(f"✅ Field zoho_item_id created successfully (ID: {field_id})")
            return True
        else:
            print("❌ Failed to create zoho_item_id field")
            return False
            
    except Exception as e:
        print(f"❌ Error adding field: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Adding Zoho Item ID field to Odoo...")
    success = add_zoho_field_to_odoo()
    
    if success:
        print("🎉 Field addition completed successfully!")
    else:
        print("💥 Field addition failed!") 