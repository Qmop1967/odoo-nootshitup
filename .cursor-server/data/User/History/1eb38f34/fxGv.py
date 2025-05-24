#!/usr/bin/env python3

import json
import requests
import xmlrpc.client
import logging
from datetime import datetime
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductMigrator:
    def __init__(self):
        self.load_config()
        self.connect_to_odoo()
        
    def load_config(self):
        """Load configuration"""
        with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
            self.config = json.load(f)
        
        with open('/opt/odoo/migration/config/field_mapping.json', 'r') as f:
            self.field_mapping = json.load(f)
        
        self.zoho_config = self.config['zoho_books']
        self.product_mapping = self.field_mapping['products']
        
    def connect_to_odoo(self):
        """Connect to Odoo"""
        odoo_config = self.config['odoo']['test_db']
        
        url = f"http://{odoo_config['host']}:{odoo_config['port']}"
        
        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.uid = self.common.authenticate(
            odoo_config['database'], 
            odoo_config['username'], 
            odoo_config['password'], 
            {}
        )
        
        if not self.uid:
            raise Exception("Failed to authenticate with Odoo")
            
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        logger.info("✅ Connected to Odoo successfully")
        
    def get_zoho_access_token(self):
        """Get fresh access token from Zoho"""
        token_url = "https://accounts.zoho.com/oauth/v2/token"
        token_params = {
            'refresh_token': self.zoho_config['refresh_token'],
            'client_id': self.zoho_config['client_id'],
            'client_secret': self.zoho_config['client_secret'],
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(token_url, data=token_params)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get access token: {response.text}")
            
        token_data = response.json()
        return token_data['access_token']
        
    def fetch_zoho_products(self):
        """Fetch all products from Zoho Books"""
        access_token = self.get_zoho_access_token()
        
        headers = {
            'Authorization': f'Zoho-oauthtoken {access_token}',
            'Content-Type': 'application/json'
        }
        
        all_products = []
        page = 1
        per_page = 100
        
        while True:
            params = {
                'organization_id': self.zoho_config['organization_id'],
                'page': page,
                'per_page': per_page
            }
            
            url = f"{self.zoho_config['base_url']}/items"
            logger.info(f"Fetching page {page} from Zoho Books...")
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch page {page}: {response.status_code} - {response.text}")
                break
                
            data = response.json()
            items = data.get('items', [])
            
            if not items:
                break
                
            all_products.extend(items)
            logger.info(f"Retrieved {len(items)} products from page {page}")
            
            # Zoho API rate limiting
            time.sleep(0.6)
            
            # Check if we have more pages
            page_context = data.get('page_context', {})
            if not page_context.get('has_more_page', False):
                break
                
            page += 1
            
        logger.info(f"✅ Total products fetched from Zoho: {len(all_products)}")
        return all_products
        
    def transform_product(self, zoho_product):
        """Transform a single Zoho product to Odoo format"""
        odoo_product = {}
        
        # Map fields from Zoho to Odoo
        zoho_mapping = self.product_mapping['zoho_books']
        for zoho_field, odoo_field in zoho_mapping.items():
            if zoho_field in zoho_product and zoho_product[zoho_field]:
                # Handle special field mappings
                if zoho_field == 'rate':
                    # Convert string price to float
                    try:
                        odoo_product[odoo_field] = float(zoho_product[zoho_field])
                    except (ValueError, TypeError):
                        odoo_product[odoo_field] = 0.0
                elif zoho_field == 'purchase_rate':
                    # Convert string price to float
                    try:
                        odoo_product[odoo_field] = float(zoho_product[zoho_field])
                    except (ValueError, TypeError):
                        odoo_product[odoo_field] = 0.0
                else:
                    odoo_product[odoo_field] = zoho_product[zoho_field]
        
        # Apply default values with the CORRECTED product type
        for field, value in self.product_mapping['default_values'].items():
            odoo_product[field] = value
        
        # Ensure required fields
        if 'name' not in odoo_product or not odoo_product['name']:
            odoo_product['name'] = f"Product {zoho_product.get('item_id', 'Unknown')}"
        
        # Clean up the name
        if 'name' in odoo_product:
            odoo_product['name'] = str(odoo_product['name']).strip()
            
        return odoo_product
        
    def migrate_products(self):
        """Main migration function"""
        logger.info("🚀 Starting product migration...")
        
        # Fetch products from Zoho
        zoho_products = self.fetch_zoho_products()
        
        if not zoho_products:
            logger.error("No products to migrate")
            return False
            
        # Transform and import
        success_count = 0
        error_count = 0
        
        odoo_config = self.config['odoo']['test_db']
        
        for i, zoho_product in enumerate(zoho_products, 1):
            try:
                # Transform product
                odoo_product = self.transform_product(zoho_product)
                
                logger.info(f"[{i}/{len(zoho_products)}] Migrating: {odoo_product['name']}")
                logger.info(f"Product data: {odoo_product}")
                
                # Create in Odoo
                product_id = self.models.execute_kw(
                    odoo_config['database'], 
                    self.uid, 
                    odoo_config['password'],
                    'product.template', 
                    'create', 
                    [odoo_product]
                )
                
                if product_id:
                    success_count += 1
                    logger.info(f"✅ Successfully migrated: {odoo_product['name']} (ID: {product_id})")
                else:
                    error_count += 1
                    logger.error(f"❌ Failed to create: {odoo_product['name']}")
                    
            except Exception as e:
                error_count += 1
                product_name = zoho_product.get('name', 'Unknown')
                logger.error(f"❌ Error migrating {product_name}: {e}")
        
        # Summary
        logger.info("\n" + "="*50)
        logger.info("🎉 PRODUCT MIGRATION COMPLETED!")
        logger.info("="*50)
        logger.info(f"✅ Successfully migrated: {success_count}")
        logger.info(f"❌ Errors encountered: {error_count}")
        logger.info(f"📊 Total processed: {len(zoho_products)}")
        logger.info("="*50)
        
        return success_count > 0

if __name__ == "__main__":
    try:
        migrator = ProductMigrator()
        migrator.migrate_products()
    except Exception as e:
        logger.error(f"Critical error: {e}")
        exit(1) 