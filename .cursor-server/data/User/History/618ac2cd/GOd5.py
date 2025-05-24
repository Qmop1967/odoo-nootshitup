#!/usr/bin/env python3

import xmlrpc.client
import logging
from pathlib import Path
import json

def create_zoho_field():
    """Create or verify Zoho ID field in Odoo product template"""
    
    # Setup logging
    log_dir = '/opt/odoo/migration/logs'
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'{log_dir}/create_zoho_field.log'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Load config
        with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
            config = json.load(f)
        
        odoo_config = config['odoo']['test_db']
        
        # Connect to Odoo
        url = f"http://{odoo_config['host']}:{odoo_config['port']}"
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(
            odoo_config['database'],
            odoo_config['username'],
            odoo_config['password'],
            {}
        )
        
        if not uid:
            raise Exception("Failed to authenticate with Odoo")
        
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        # Check if field exists
        fields_data = models.execute_kw(
            odoo_config['database'],
            uid,
            odoo_config['password'],
            'product.template',
            'fields_get',
            [],
            {'attributes': ['string', 'type']}
        )
        
        if 'x_zoho_item_id' not in fields_data:
            # Create the field
            field_data = {
                'name': 'x_zoho_item_id',
                'field_description': 'Zoho Item ID',
                'ttype': 'char',
                'size': 64,
                'required': False,
                'readonly': True,
                'store': True,
                'copy': False,
                'model_id': models.execute_kw(
                    odoo_config['database'],
                    uid,
                    odoo_config['password'],
                    'ir.model',
                    'search',
                    [[('model', '=', 'product.template')]],
                    {'limit': 1}
                )[0]
            }
            
            models.execute_kw(
                odoo_config['database'],
                uid,
                odoo_config['password'],
                'ir.model.fields',
                'create',
                [field_data]
            )
            
            logger.info("✅ Created Zoho Item ID field in product.template")
            
            # Create index for the field
            index_name = 'product_template_zoho_item_id_index'
            query = """
            CREATE INDEX IF NOT EXISTS %s 
            ON product_template (x_zoho_item_id)
            """ % index_name
            
            models.execute_kw(
                odoo_config['database'],
                uid,
                odoo_config['password'],
                'product.template',
                'execute_sql',
                [query]
            )
            
            logger.info("✅ Created index on Zoho Item ID field")
        else:
            logger.info("✅ Zoho Item ID field already exists")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating Zoho field: {e}")
        return False

if __name__ == "__main__":
    create_zoho_field() 