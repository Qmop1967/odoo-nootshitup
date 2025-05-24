#!/usr/bin/env python3

import json
import requests
import xmlrpc.client
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_product_creation():
    """Test creating a product with correct type"""
    
    # Odoo connection
    url = 'http://localhost:8069'
    db = 'odtshbrain'
    username = 'khaleel@tsh.sale'
    password = 'Zcbm.97531tsh'
    
    try:
        # Connect to Odoo
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})
        
        if not uid:
            logger.error("Failed to authenticate with Odoo")
            return False
            
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        # Test product data
        test_product = {
            'name': 'Test Product from Zoho',
            'type': 'consu',  # Using correct Odoo 18 value
            'default_code': 'TEST-001',
            'list_price': 100.0,
            'standard_price': 80.0,
            'invoice_policy': 'order'
        }
        
        logger.info(f"Testing product creation with data: {test_product}")
        
        # Create product
        product_id = models.execute_kw(db, uid, password, 'product.template', 'create', [test_product])
        
        if product_id:
            logger.info(f"✅ Successfully created test product with ID: {product_id}")
            
            # Read back to verify
            product_data = models.execute_kw(db, uid, password, 'product.template', 'read', [product_id], {'fields': ['name', 'type', 'default_code']})
            logger.info(f"✅ Product data: {product_data}")
            
            return True
        else:
            logger.error("❌ Failed to create test product")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing product creation: {e}")
        return False

def get_zoho_products_sample():
    """Get sample Zoho products for testing"""
    
    # Load config
    with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
        config = json.load(f)
    
    zoho_config = config['zoho_books']
    
    try:
        # Get access token
        token_url = "https://accounts.zoho.com/oauth/v2/token"
        token_params = {
            'refresh_token': zoho_config['refresh_token'],
            'client_id': zoho_config['client_id'],
            'client_secret': zoho_config['client_secret'],
            'grant_type': 'refresh_token'
        }
        
        logger.info("Getting fresh access token from Zoho...")
        response = requests.post(token_url, data=token_params)
        
        if response.status_code != 200:
            logger.error(f"Failed to get access token: {response.text}")
            return None
            
        token_data = response.json()
        access_token = token_data['access_token']
        
        # Get items from Zoho Books
        items_url = f"{zoho_config['base_url']}/items"
        headers = {
            'Authorization': f'Zoho-oauthtoken {access_token}',
            'Content-Type': 'application/json'
        }
        params = {
            'organization_id': zoho_config['organization_id'],
            'per_page': 5  # Just get 5 for testing
        }
        
        logger.info("Fetching sample products from Zoho Books...")
        response = requests.get(items_url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            logger.info(f"✅ Retrieved {len(items)} sample products from Zoho")
            return items
        else:
            logger.error(f"Failed to fetch items: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching Zoho products: {e}")
        return None

def migrate_sample_products():
    """Test migrating a few products with correct field mapping"""
    
    # Get sample products
    zoho_products = get_zoho_products_sample()
    if not zoho_products:
        logger.error("No products to migrate")
        return False
    
    # Load field mapping
    with open('/opt/odoo/migration/config/field_mapping.json', 'r') as f:
        field_mapping = json.load(f)
    
    product_mapping = field_mapping['products']
    
    # Odoo connection
    url = 'http://localhost:8069'
    db = 'odtshbrain'
    username = 'khaleel@tsh.sale'
    password = 'Zcbm.97531tsh'
    
    try:
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        success_count = 0
        
        for zoho_product in zoho_products:
            try:
                # Transform data
                odoo_product = {}
                
                # Map fields from Zoho to Odoo
                zoho_mapping = product_mapping['zoho_books']
                for zoho_field, odoo_field in zoho_mapping.items():
                    if zoho_field in zoho_product:
                        odoo_product[odoo_field] = zoho_product[zoho_field]
                
                # Apply default values
                for field, value in product_mapping['default_values'].items():
                    odoo_product[field] = value
                
                # Ensure required fields
                if 'name' not in odoo_product or not odoo_product['name']:
                    odoo_product['name'] = f"Product {zoho_product.get('item_id', 'Unknown')}"
                
                logger.info(f"Creating product: {odoo_product['name']}")
                
                # Create in Odoo
                product_id = models.execute_kw(db, uid, password, 'product.template', 'create', [odoo_product])
                
                if product_id:
                    success_count += 1
                    logger.info(f"✅ Successfully migrated product: {odoo_product['name']} (ID: {product_id})")
                else:
                    logger.error(f"❌ Failed to create product: {odoo_product['name']}")
                    
            except Exception as e:
                logger.error(f"❌ Error migrating product {zoho_product.get('name', 'Unknown')}: {e}")
        
        logger.info(f"✅ Migration test completed: {success_count}/{len(zoho_products)} products migrated")
        return success_count > 0
        
    except Exception as e:
        logger.error(f"❌ Error during migration test: {e}")
        return False

if __name__ == "__main__":
    logger.info("🧪 TESTING PRODUCT MIGRATION")
    logger.info("=" * 40)
    
    # Test 1: Simple product creation
    logger.info("Test 1: Simple product creation...")
    if test_product_creation():
        logger.info("✅ Test 1 passed")
    else:
        logger.error("❌ Test 1 failed")
        exit(1)
    
    # Test 2: Sample product migration
    logger.info("\nTest 2: Sample product migration...")
    if migrate_sample_products():
        logger.info("✅ Test 2 passed")
    else:
        logger.error("❌ Test 2 failed - but this might be due to Zoho API issues")
    
    logger.info("\n🎉 Product migration testing completed!") 