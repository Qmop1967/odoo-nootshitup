#!/usr/bin/env python3

import xmlrpc.client
import json

def create_zoho_field():
    """Create the x_zoho_item_id field in Odoo product.template model"""
    
    # Load config
    with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
        config = json.load(f)

    odoo_config = config['odoo']['test_db']
    url = f'http://{odoo_config["host"]}:{odoo_config["port"]}'

    # Connect to Odoo
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(odoo_config['database'], odoo_config['username'], odoo_config['password'], {})
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    print("🔧 Creating x_zoho_item_id field in Odoo...")

    try:
        # First, check if field already exists
        fields = models.execute_kw(odoo_config['database'], uid, odoo_config['password'], 
                                  'product.template', 'fields_get', [], 
                                  {'attributes': ['string', 'type']})
        
        if 'x_zoho_item_id' in fields:
            print('✅ x_zoho_item_id field already exists!')
            return True

        # Get the product.template model ID
        model_ids = models.execute_kw(odoo_config['database'], uid, odoo_config['password'],
                                     'ir.model', 'search', 
                                     [[('model', '=', 'product.template')]])
        
        if not model_ids:
            print('❌ Could not find product.template model')
            return False
        
        model_id = model_ids[0]
        print(f'📋 Found product.template model ID: {model_id}')

        # Create the custom field
        field_data = {
            'name': 'x_zoho_item_id',
            'field_description': 'Zoho Item ID',
            'model_id': model_id,
            'ttype': 'char',
            'size': 100,
            'index': True,
            'store': True,
            'help': 'Unique identifier from Zoho Books for product synchronization'
        }

        field_id = models.execute_kw(odoo_config['database'], uid, odoo_config['password'],
                                    'ir.model.fields', 'create', [field_data])

        if field_id:
            print(f'✅ Successfully created x_zoho_item_id field (ID: {field_id})')
            
            # Verify field creation
            fields = models.execute_kw(odoo_config['database'], uid, odoo_config['password'], 
                                      'product.template', 'fields_get', [], 
                                      {'attributes': ['string', 'type']})
            
            if 'x_zoho_item_id' in fields:
                print('✅ Field verification successful!')
                print(f'   Type: {fields["x_zoho_item_id"]["type"]}')
                print(f'   Label: {fields["x_zoho_item_id"]["string"]}')
                return True
            else:
                print('❌ Field creation failed - not found after creation')
                return False
        else:
            print('❌ Failed to create field')
            return False

    except Exception as e:
        print(f'❌ Error creating field: {e}')
        print('\n🔧 MANUAL SOLUTION:')
        print('1. Log into Odoo as Administrator')
        print('2. Go to Settings > Technical > Database Structure > Models')
        print('3. Search for "product.template" and click on it')
        print('4. Click "Add a line" in the Fields section')
        print('5. Fill in:')
        print('   - Field Name: x_zoho_item_id')
        print('   - Field Label: Zoho Item ID')
        print('   - Field Type: Char')
        print('   - Size: 100')
        print('6. Check "Indexed" checkbox')
        print('7. Save the field')
        return False

if __name__ == "__main__":
    success = create_zoho_field()
    if success:
        print('\n🎉 Ready to run sync! The field is now available.')
    else:
        print('\n⚠️  Please create the field manually as described above.') 