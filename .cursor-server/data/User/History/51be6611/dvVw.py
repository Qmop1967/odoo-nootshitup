#!/usr/bin/env python3

import json
import requests
import xmlrpc.client
import logging
from datetime import datetime
import time
import base64
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedProductMigrator:
    def __init__(self):
        self.load_config()
        self.connect_to_odoo()
        self.setup_uom_mapping()
        
    def load_config(self):
        """Load configuration"""
        with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
            self.config = json.load(f)
        
        with open('/opt/odoo/migration/config/field_mapping.json', 'r') as f:
            self.field_mapping = json.load(f)
        
        self.zoho_config = self.config['zoho_books']
        
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
        
    def setup_uom_mapping(self):
        """Setup UOM (Unit of Measure) mapping from strings to Odoo IDs"""
        logger.info("🔄 Setting up UOM mapping...")
        
        try:
            # Get all UOMs from Odoo
            uoms = self.models.execute_kw(
                'odtshbrain', self.uid, 'Zcbm.97531tsh',
                'uom.uom', 'search_read', [[]],
                {'fields': ['id', 'name', 'category_id']}
            )
            
            # Create mapping from common names to IDs
            self.uom_mapping = {}
            default_uom_id = None
            
            for uom in uoms:
                name = uom['name'].lower()
                uom_id = uom['id']
                
                # Map common UOM names
                if name in ['unit', 'units', 'pcs', 'pieces', 'piece', 'each']:
                    self.uom_mapping['pcs'] = uom_id
                    self.uom_mapping['pieces'] = uom_id
                    self.uom_mapping['piece'] = uom_id
                    self.uom_mapping['unit'] = uom_id
                    self.uom_mapping['units'] = uom_id
                    default_uom_id = uom_id
                elif name in ['kg', 'kilogram', 'kilograms']:
                    self.uom_mapping['kg'] = uom_id
                elif name in ['meter', 'metres', 'm']:
                    self.uom_mapping['m'] = uom_id
                elif name in ['liter', 'litre', 'l']:
                    self.uom_mapping['l'] = uom_id
                    
            # Set default UOM if we found 'Units'
            if default_uom_id:
                self.default_uom_id = default_uom_id
                logger.info(f"✅ Default UOM ID set to: {default_uom_id}")
            else:
                # Fallback: use first UOM found
                self.default_uom_id = uoms[0]['id'] if uoms else 1
                logger.warning(f"⚠️  Using fallback UOM ID: {self.default_uom_id}")
                
            logger.info(f"✅ UOM mapping created with {len(self.uom_mapping)} mappings")
            
        except Exception as e:
            logger.error(f"❌ Error setting up UOM mapping: {e}")
            # Fallback: use ID 1 (usually 'Units')
            self.default_uom_id = 1
            self.uom_mapping = {}
            
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
        """Fetch all products from Zoho Books with images"""
        access_token = self.get_zoho_access_token()
        
        headers = {
            'Authorization': f'Zoho-oauthtoken {access_token}',
            'Content-Type': 'application/json'
        }
        
        all_products = []
        page = 1
        per_page = 50  # Reduced to handle images better
        
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
                
            # Get detailed info for each item (including images)
            for item in items:
                try:
                    # Get detailed item info
                    item_url = f"{self.zoho_config['base_url']}/items/{item['item_id']}"
                    item_response = requests.get(item_url, headers=headers, params={'organization_id': self.zoho_config['organization_id']})
                    
                    if item_response.status_code == 200:
                        detailed_item = item_response.json().get('item', {})
                        # Merge basic and detailed info
                        item.update(detailed_item)
                        
                    time.sleep(0.2)  # Rate limiting for detailed requests
                except Exception as e:
                    logger.warning(f"Could not get detailed info for item {item.get('name', 'Unknown')}: {e}")
                    
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
        
    def download_product_image(self, image_url, product_name):
        """Download product image from Zoho"""
        if not image_url:
            return None
            
        try:
            logger.info(f"📷 Downloading image for: {product_name}")
            
            # Get access token for image download
            access_token = self.get_zoho_access_token()
            headers = {
                'Authorization': f'Zoho-oauthtoken {access_token}'
            }
            
            response = requests.get(image_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                # Convert to base64 for Odoo
                image_base64 = base64.b64encode(response.content).decode('utf-8')
                logger.info(f"✅ Image downloaded successfully for: {product_name}")
                return image_base64
            else:
                logger.warning(f"⚠️  Failed to download image for {product_name}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.warning(f"⚠️  Error downloading image for {product_name}: {e}")
            return None
            
    def resolve_uom_id(self, uom_string):
        """Convert UOM string to Odoo UOM ID"""
        if not uom_string:
            return self.default_uom_id
            
        uom_lower = str(uom_string).lower().strip()
        
        # Check our mapping
        if uom_lower in self.uom_mapping:
            return self.uom_mapping[uom_lower]
        else:
            logger.warning(f"⚠️  Unknown UOM '{uom_string}', using default")
            return self.default_uom_id
            
    def transform_product(self, zoho_product):
        """Transform a single Zoho product to Odoo format with all fixes"""
        odoo_product = {}
        
        # Map basic fields with proper handling
        zoho_mapping = self.field_mapping['products']['zoho_books']
        for zoho_field, odoo_field in zoho_mapping.items():
            if zoho_field in zoho_product and zoho_product[zoho_field] is not None:
                value = zoho_product[zoho_field]
                
                # Handle special field mappings
                if zoho_field == 'rate':
                    try:
                        odoo_product[odoo_field] = float(value) if value else 0.0
                    except (ValueError, TypeError):
                        odoo_product[odoo_field] = 0.0
                elif zoho_field == 'purchase_rate':
                    try:
                        odoo_product[odoo_field] = float(value) if value else 0.0
                    except (ValueError, TypeError):
                        odoo_product[odoo_field] = 0.0
                elif zoho_field == 'unit':
                    # Handle UOM properly
                    odoo_product['uom_id'] = self.resolve_uom_id(value)
                    odoo_product['uom_po_id'] = self.resolve_uom_id(value)  # Purchase UOM
                else:
                    odoo_product[odoo_field] = value
        
        # Apply default values
        for field, value in self.field_mapping['products']['default_values'].items():
            odoo_product[field] = value
        
        # Set default UOM if not set
        if 'uom_id' not in odoo_product:
            odoo_product['uom_id'] = self.default_uom_id
            odoo_product['uom_po_id'] = self.default_uom_id
        
        # Ensure required fields
        if 'name' not in odoo_product or not odoo_product['name']:
            odoo_product['name'] = f"Product {zoho_product.get('item_id', 'Unknown')}"
        
        # Clean up the name
        if 'name' in odoo_product:
            odoo_product['name'] = str(odoo_product['name']).strip()
            
        # Handle product image
        image_url = zoho_product.get('image_url') or zoho_product.get('image')
        if image_url:
            image_data = self.download_product_image(image_url, odoo_product['name'])
            if image_data:
                odoo_product['image_1920'] = image_data  # Main product image in Odoo
                
        # Remove problematic fields that might cause issues
        problematic_fields = ['categ_id', 'taxes_id', 'property_account_expense_id', 'property_account_income_id']
        for field in problematic_fields:
            if field in odoo_product:
                del odoo_product[field]
                
        return odoo_product
        
    def migrate_products(self):
        """Migrate products with all fixes applied"""
        logger.info("🚀 Starting ENHANCED product migration with images...")
        
        # Fetch products from Zoho
        zoho_products = self.fetch_zoho_products()
        
        if not zoho_products:
            logger.error("No products to migrate")
            return False
            
        # Transform and import
        success_count = 0
        error_count = 0
        image_count = 0
        
        odoo_config = self.config['odoo']['test_db']
        
        for i, zoho_product in enumerate(zoho_products, 1):
            try:
                # Transform product
                odoo_product = self.transform_product(zoho_product)
                
                logger.info(f"[{i}/{len(zoho_products)}] Migrating: {odoo_product['name']}")
                
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
                    if 'image_1920' in odoo_product:
                        image_count += 1
                        logger.info(f"✅ Migrated with image: {odoo_product['name']}")
                    
                    if success_count % 25 == 0:
                        logger.info(f"📊 Progress: {success_count}/{len(zoho_products)} products migrated ({image_count} with images)")
                else:
                    error_count += 1
                    logger.error(f"❌ Failed to create: {odoo_product['name']}")
                    
            except Exception as e:
                error_count += 1
                product_name = zoho_product.get('name', zoho_product.get('item_name', 'Unknown'))
                logger.error(f"❌ Error migrating {product_name}: {e}")
                
                # Log detailed error for debugging
                if "invalid input syntax" in str(e):
                    logger.error(f"🔍 Data causing error: {odoo_product}")
                
                # Continue with next product
                continue
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("🎉 ENHANCED PRODUCT MIGRATION COMPLETED!")
        logger.info("="*60)
        logger.info(f"✅ Successfully migrated: {success_count}")
        logger.info(f"📷 Products with images: {image_count}")
        logger.info(f"❌ Errors encountered: {error_count}")
        logger.info(f"📊 Total processed: {len(zoho_products)}")
        logger.info(f"🎯 Success rate: {(success_count/len(zoho_products)*100):.1f}%")
        logger.info("="*60)
        
        return success_count > 0

if __name__ == "__main__":
    try:
        migrator = EnhancedProductMigrator()
        success = migrator.migrate_products()
        
        if success:
            print("\n🎉 Enhanced product migration completed!")
            print("Products with images have been successfully migrated.")
        else:
            print("\n❌ Product migration failed.")
            exit(1)
            
    except Exception as e:
        logger.error(f"Critical error: {e}")
        exit(1) 