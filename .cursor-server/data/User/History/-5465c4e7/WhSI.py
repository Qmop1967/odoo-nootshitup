#!/usr/bin/env python3

import json
import requests
import xmlrpc.client
import logging
from datetime import datetime
import time
import base64
import os
import hashlib
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ZohoProductSync:
    def __init__(self):
        self.load_config()
        self.connect_to_odoo()
        self.setup_uom_mapping()
        self.setup_sync_tracking()
        
    def load_config(self):
        """Load configuration"""
        with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
            self.config = json.load(f)
        
        with open('/opt/odoo/migration/config/field_mapping.json', 'r') as f:
            self.field_mapping = json.load(f)
        
        self.zoho_config = self.config['zoho_books']
        self.odoo_db_config = self.config['odoo']['test_db']
        
    def connect_to_odoo(self):
        """Connect to Odoo"""
        url = f"http://{self.odoo_db_config['host']}:{self.odoo_db_config['port']}"
        
        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.uid = self.common.authenticate(
            self.odoo_db_config['database'], 
            self.odoo_db_config['username'], 
            self.odoo_db_config['password'], 
            {}
        )
        
        if not self.uid:
            raise Exception("Failed to authenticate with Odoo")
            
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        logger.info("✅ Connected to Odoo successfully")
        
    def setup_uom_mapping(self):
        """Setup UOM (Unit of Measure) mapping"""
        logger.info("🔄 Setting up UOM mapping...")
        
        try:
            uoms = self.models.execute_kw(
                self.odoo_db_config['database'], 
                self.uid, 
                self.odoo_db_config['password'],
                'uom.uom', 'search_read', [[]],
                {'fields': ['id', 'name', 'category_id']}
            )
            
            self.uom_mapping = {}
            self.default_uom_id = None
            
            for uom in uoms:
                name = uom['name'].lower()
                uom_id = uom['id']
                
                # Map common UOM names
                if name in ['unit', 'units', 'pcs', 'pieces', 'piece', 'each']:
                    self.uom_mapping.update({
                        'pcs': uom_id, 'pieces': uom_id, 'piece': uom_id,
                        'unit': uom_id, 'units': uom_id, 'each': uom_id
                    })
                    self.default_uom_id = uom_id
                elif name in ['kg', 'kilogram', 'kilograms']:
                    self.uom_mapping['kg'] = uom_id
                elif name in ['meter', 'metres', 'm']:
                    self.uom_mapping['m'] = uom_id
                elif name in ['liter', 'litre', 'l']:
                    self.uom_mapping['l'] = uom_id
                    
            if not self.default_uom_id:
                self.default_uom_id = uoms[0]['id'] if uoms else 1
                
            logger.info(f"✅ UOM mapping created with default ID: {self.default_uom_id}")
            
        except Exception as e:
            logger.error(f"❌ Error setting up UOM mapping: {e}")
            self.default_uom_id = 1
            self.uom_mapping = {}

    def setup_sync_tracking(self):
        """Setup sync tracking to detect changes"""
        self.sync_data_file = '/opt/odoo/migration/data/product_sync_data.json'
        self.images_dir = '/opt/odoo/migration/data/product_images'
        
        # Create directories if they don't exist
        Path(self.sync_data_file).parent.mkdir(parents=True, exist_ok=True)
        Path(self.images_dir).mkdir(parents=True, exist_ok=True)
        
        # Load existing sync data
        if os.path.exists(self.sync_data_file):
            with open(self.sync_data_file, 'r') as f:
                self.sync_data = json.load(f)
        else:
            self.sync_data = {
                'last_sync': None,
                'products': {},  # zoho_id -> {odoo_id, last_modified, checksum}
                'sync_stats': {'total_synced': 0, 'last_run_added': 0, 'last_run_updated': 0}
            }
    
    def save_sync_data(self):
        """Save sync tracking data"""
        with open(self.sync_data_file, 'w') as f:
            json.dump(self.sync_data, f, indent=2)
    
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
        response.raise_for_status()
        return response.json()['access_token']
    
    def fetch_zoho_products_with_images(self):
        """Fetch products from both Zoho Books and Zoho Inventory for complete data including images"""
        logger.info("📦 Fetching products from Zoho with enhanced image support...")
        
        access_token = self.get_zoho_access_token()
        headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
        
        all_products = []
        
        # Fetch from Zoho Books (main product data)
        books_products = self._fetch_from_zoho_books(headers)
        
        # Try to fetch from Zoho Inventory (for better image support)
        inventory_products = self._fetch_from_zoho_inventory(headers)
        
        # Merge data prioritizing inventory images
        products_map = {p['item_id']: p for p in books_products}
        
        for inv_product in inventory_products:
            item_id = inv_product.get('item_id') or inv_product.get('product_id')
            if item_id in products_map:
                # Merge inventory data (especially images) with books data
                books_product = products_map[item_id]
                
                # Prioritize inventory images
                if inv_product.get('image_url') or inv_product.get('images'):
                    books_product['image_url'] = inv_product.get('image_url')
                    books_product['images'] = inv_product.get('images', [])
                    books_product['has_inventory_image'] = True
                
                # Add any additional inventory fields
                books_product.update({k: v for k, v in inv_product.items() 
                                    if k not in books_product or not books_product[k]})
        
        return list(products_map.values())
    
    def _fetch_from_zoho_books(self, headers):
        """Fetch products from Zoho Books"""
        logger.info("📚 Fetching from Zoho Books...")
        
        all_products = []
        page = 1
        per_page = 50
        
        while True:
            params = {
                'organization_id': self.zoho_config['organization_id'],
                'page': page,
                'per_page': per_page
            }
            
            url = f"{self.zoho_config['base_url']}/items"
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch Books page {page}: {response.status_code}")
                break
                
            data = response.json()
            items = data.get('items', [])
            
            if not items:
                break
            
            # Get detailed info for each item
            for item in items:
                try:
                    item_url = f"{self.zoho_config['base_url']}/items/{item['item_id']}"
                    item_response = requests.get(item_url, headers=headers, 
                                               params={'organization_id': self.zoho_config['organization_id']})
                    
                    if item_response.status_code == 200:
                        detailed_item = item_response.json().get('item', {})
                        item.update(detailed_item)
                        
                    time.sleep(0.2)  # Rate limiting
                except Exception as e:
                    logger.warning(f"Could not get detailed info for item {item.get('name', 'Unknown')}: {e}")
                    
            all_products.extend(items)
            logger.info(f"Retrieved {len(items)} products from Books page {page}")
            
            time.sleep(0.6)  # Rate limiting
            
            page_context = data.get('page_context', {})
            if not page_context.get('has_more_page', False):
                break
                
            page += 1
        
        logger.info(f"✅ Fetched {len(all_products)} products from Zoho Books")
        return all_products
    
    def _fetch_from_zoho_inventory(self, headers):
        """Fetch products from Zoho Inventory for better image support"""
        logger.info("🏪 Attempting to fetch from Zoho Inventory for enhanced images...")
        
        try:
            # Try Zoho Inventory API (if available)
            inventory_base_url = self.zoho_config.get('inventory_base_url', 
                                                    'https://www.zohoapis.com/inventory/v1')
            
            all_products = []
            page = 1
            per_page = 50
            
            while True:
                params = {
                    'organization_id': self.zoho_config['organization_id'],
                    'page': page,
                    'per_page': per_page
                }
                
                url = f"{inventory_base_url}/items"
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code != 200:
                    if page == 1:
                        logger.info("📝 Zoho Inventory not available, using Books images only")
                    break
                    
                data = response.json()
                items = data.get('items', [])
                
                if not items:
                    break
                
                all_products.extend(items)
                logger.info(f"Retrieved {len(items)} products from Inventory page {page}")
                
                time.sleep(0.6)  # Rate limiting
                
                page_context = data.get('page_context', {})
                if not page_context.get('has_more_page', False):
                    break
                    
                page += 1
            
            if all_products:
                logger.info(f"✅ Fetched {len(all_products)} products from Zoho Inventory")
            
            return all_products
            
        except Exception as e:
            logger.info(f"📝 Zoho Inventory fetch failed (using Books only): {e}")
            return []
    
    def download_product_image(self, image_data, product_name, product_id):
        """Enhanced image download with multiple source support"""
        if not image_data:
            return None
            
        try:
            access_token = self.get_zoho_access_token()
            headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
            
            image_url = None
            
            # Handle different image data formats
            if isinstance(image_data, str):
                image_url = image_data
            elif isinstance(image_data, dict):
                image_url = image_data.get('url') or image_data.get('image_url')
            elif isinstance(image_data, list) and image_data:
                # Multiple images, take the first one
                first_image = image_data[0]
                if isinstance(first_image, dict):
                    image_url = first_image.get('url') or first_image.get('image_url')
                else:
                    image_url = str(first_image)
            
            if not image_url:
                return None
                
            logger.info(f"📷 Downloading image for: {product_name}")
            
            # Add organization_id if not in URL
            if 'organization_id' not in image_url and '?' not in image_url:
                image_url += f"?organization_id={self.zoho_config['organization_id']}"
            elif 'organization_id' not in image_url:
                image_url += f"&organization_id={self.zoho_config['organization_id']}"
            
            response = requests.get(image_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                # Save image locally for tracking
                image_hash = hashlib.md5(response.content).hexdigest()
                image_filename = f"{product_id}_{image_hash}.jpg"
                image_path = os.path.join(self.images_dir, image_filename)
                
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                
                # Convert to base64 for Odoo
                image_base64 = base64.b64encode(response.content).decode('utf-8')
                logger.info(f"✅ Image downloaded and saved: {product_name}")
                
                return {
                    'base64': image_base64,
                    'hash': image_hash,
                    'path': image_path,
                    'url': image_url
                }
            else:
                logger.warning(f"⚠️  Failed to download image for {product_name}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.warning(f"⚠️  Error downloading image for {product_name}: {e}")
            return None
    
    def calculate_product_checksum(self, zoho_product):
        """Calculate checksum to detect changes"""
        # Include key fields that would indicate a product change
        key_fields = ['name', 'description', 'rate', 'purchase_rate', 'unit', 'category_name', 'last_modified_time']
        
        checksum_data = {}
        for field in key_fields:
            checksum_data[field] = zoho_product.get(field, '')
        
        # Include image URL/hash if available
        image_data = (zoho_product.get('image_url') or 
                     zoho_product.get('images') or 
                     zoho_product.get('image'))
        if image_data:
            checksum_data['image'] = str(image_data)
        
        checksum_string = json.dumps(checksum_data, sort_keys=True)
        return hashlib.md5(checksum_string.encode()).hexdigest()
    
    def find_existing_product(self, zoho_product):
        """Find existing product in Odoo by external ID or name matching"""
        zoho_id = zoho_product.get('item_id')
        
        # Check our sync tracking first
        if zoho_id in self.sync_data['products']:
            odoo_id = self.sync_data['products'][zoho_id]['odoo_id']
            try:
                # Verify product still exists in Odoo
                existing = self.models.execute_kw(
                    self.odoo_db_config['database'], 
                    self.uid, 
                    self.odoo_db_config['password'],
                    'product.template', 
                    'search_read', 
                    [[('id', '=', odoo_id)]],
                    {'fields': ['id', 'name']}
                )
                if existing:
                    return existing[0]
            except:
                # Product was deleted, remove from tracking
                del self.sync_data['products'][zoho_id]
        
        # Search by name as fallback
        product_name = zoho_product.get('name', '')
        if product_name:
            try:
                existing = self.models.execute_kw(
                    self.odoo_db_config['database'], 
                    self.uid, 
                    self.odoo_db_config['password'],
                    'product.template', 
                    'search_read', 
                    [[('name', '=', product_name)]],
                    {'fields': ['id', 'name'], 'limit': 1}
                )
                if existing:
                    return existing[0]
            except:
                pass
        
        return None
    
    def resolve_uom_id(self, uom_string):
        """Convert UOM string to Odoo UOM ID"""
        if not uom_string:
            return self.default_uom_id
            
        uom_lower = str(uom_string).lower().strip()
        return self.uom_mapping.get(uom_lower, self.default_uom_id)
    
    def transform_product(self, zoho_product):
        """Transform Zoho product to Odoo format with enhanced image handling"""
        odoo_product = {}
        
        # Map basic fields
        zoho_mapping = self.field_mapping['products']['zoho_books']
        for zoho_field, odoo_field in zoho_mapping.items():
            if zoho_field in zoho_product and zoho_product[zoho_field] is not None:
                value = zoho_product[zoho_field]
                
                if zoho_field in ['rate', 'purchase_rate']:
                    try:
                        odoo_product[odoo_field] = float(value) if value else 0.0
                    except (ValueError, TypeError):
                        odoo_product[odoo_field] = 0.0
                elif zoho_field == 'unit':
                    odoo_product['uom_id'] = self.resolve_uom_id(value)
                    odoo_product['uom_po_id'] = self.resolve_uom_id(value)
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
        
        odoo_product['name'] = str(odoo_product['name']).strip()
        
        # Enhanced image handling
        zoho_id = zoho_product.get('item_id')
        image_sources = [
            zoho_product.get('image_url'),
            zoho_product.get('images'),
            zoho_product.get('image')
        ]
        
        for image_source in image_sources:
            if image_source:
                image_data = self.download_product_image(image_source, odoo_product['name'], zoho_id)
                if image_data:
                    odoo_product['image_1920'] = image_data['base64']
                    break
        
        # Remove problematic fields
        problematic_fields = ['categ_id', 'taxes_id', 'property_account_expense_id', 'property_account_income_id']
        for field in problematic_fields:
            odoo_product.pop(field, None)
                
        return odoo_product
    
    def sync_products(self, force_full_sync=False):
        """Main sync function - one-way from Zoho to Odoo"""
        logger.info("🚀 Starting one-way product sync from Zoho to Odoo...")
        
        # Fetch products from Zoho
        zoho_products = self.fetch_zoho_products_with_images()
        
        if not zoho_products:
            logger.error("No products fetched from Zoho")
            return False
        
        added_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        images_synced = 0
        
        for i, zoho_product in enumerate(zoho_products, 1):
            try:
                zoho_id = zoho_product.get('item_id')
                product_name = zoho_product.get('name', 'Unknown')
                
                logger.info(f"[{i}/{len(zoho_products)}] Processing: {product_name}")
                
                # Calculate checksum for change detection
                current_checksum = self.calculate_product_checksum(zoho_product)
                
                # Check if we need to sync this product
                existing_product = self.find_existing_product(zoho_product)
                
                if existing_product and not force_full_sync:
                    # Check if product has changed
                    if zoho_id in self.sync_data['products']:
                        stored_checksum = self.sync_data['products'][zoho_id].get('checksum')
                        if stored_checksum == current_checksum:
                            skipped_count += 1
                            logger.info(f"   ⏭️  No changes detected, skipping")
                            continue
                    
                    # Product exists and has changes - update it
                    logger.info(f"   🔄 Updating existing product...")
                    odoo_product = self.transform_product(zoho_product)
                    
                    # Remove fields that shouldn't be updated
                    update_fields = {k: v for k, v in odoo_product.items() 
                                   if k not in ['default_code']}  # Preserve internal reference
                    
                    self.models.execute_kw(
                        self.odoo_db_config['database'], 
                        self.uid, 
                        self.odoo_db_config['password'],
                        'product.template', 
                        'write', 
                        [[existing_product['id']], update_fields]
                    )
                    
                    updated_count += 1
                    if 'image_1920' in odoo_product:
                        images_synced += 1
                    
                    # Update tracking
                    self.sync_data['products'][zoho_id] = {
                        'odoo_id': existing_product['id'],
                        'last_modified': datetime.now().isoformat(),
                        'checksum': current_checksum
                    }
                    
                    logger.info(f"   ✅ Updated: {product_name}")
                    
                else:
                    # New product - create it
                    logger.info(f"   ➕ Creating new product...")
                    odoo_product = self.transform_product(zoho_product)
                    
                    product_id = self.models.execute_kw(
                        self.odoo_db_config['database'], 
                        self.uid, 
                        self.odoo_db_config['password'],
                        'product.template', 
                        'create', 
                        [odoo_product]
                    )
                    
                    if product_id:
                        added_count += 1
                        if 'image_1920' in odoo_product:
                            images_synced += 1
                        
                        # Add to tracking
                        self.sync_data['products'][zoho_id] = {
                            'odoo_id': product_id,
                            'last_modified': datetime.now().isoformat(),
                            'checksum': current_checksum
                        }
                        
                        logger.info(f"   ✅ Created: {product_name}")
                    else:
                        error_count += 1
                        logger.error(f"   ❌ Failed to create: {product_name}")
                
                # Progress update
                if (added_count + updated_count) % 25 == 0 and (added_count + updated_count) > 0:
                    logger.info(f"📊 Progress: {added_count} added, {updated_count} updated, {images_synced} with images")
                
            except Exception as e:
                error_count += 1
                logger.error(f"❌ Error processing {product_name}: {e}")
                continue
        
        # Update sync stats
        self.sync_data['last_sync'] = datetime.now().isoformat()
        self.sync_data['sync_stats'].update({
            'total_synced': len(self.sync_data['products']),
            'last_run_added': added_count,
            'last_run_updated': updated_count
        })
        
        # Save tracking data
        self.save_sync_data()
        
        # Summary
        logger.info("\n" + "="*70)
        logger.info("🎉 ONE-WAY PRODUCT SYNC COMPLETED!")
        logger.info("="*70)
        logger.info(f"➕ Products added: {added_count}")
        logger.info(f"🔄 Products updated: {updated_count}")
        logger.info(f"⏭️  Products skipped (no changes): {skipped_count}")
        logger.info(f"📷 Products with images synced: {images_synced}")
        logger.info(f"❌ Errors encountered: {error_count}")
        logger.info(f"📊 Total processed: {len(zoho_products)}")
        logger.info(f"💾 Total products tracked: {len(self.sync_data['products'])}")
        logger.info("="*70)
        
        return (added_count + updated_count) > 0

def main():
    print("🔄 Zoho to Odoo One-Way Product Sync")
    print("="*60)
    print("This will sync products from Zoho to Odoo with:")
    print("✅ Enhanced image handling from Zoho Books/Inventory")
    print("✅ Change detection to sync only updated products")
    print("✅ One-way sync (Zoho → Odoo only)")
    print("✅ Complete duplicate prevention")
    print("="*60)
    
    sync_type = input("\nChoose sync type:\n1. Smart sync (only changed products)\n2. Force full sync (all products)\nEnter choice (1 or 2): ").strip()
    
    try:
        syncer = ZohoProductSync()
        
        if sync_type == "2":
            success = syncer.sync_products(force_full_sync=True)
        else:
            success = syncer.sync_products(force_full_sync=False)
        
        if success:
            print("\n🎉 Product sync completed successfully!")
            print("📊 Run this to verify the results:")
            print("   python3 check_migration_progress.py")
        else:
            print("\n⚠️  Product sync completed with issues. Check logs above.")
            
    except Exception as e:
        logger.error(f"❌ Sync failed: {e}")
        print(f"\n❌ Sync failed: {e}")

if __name__ == "__main__":
    main() 