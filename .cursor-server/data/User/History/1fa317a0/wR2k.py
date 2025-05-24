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

class EnhancedZohoProductSync:
    def __init__(self):
        self.usd_to_iqd_rate = 1500  # 1 USD = 1500 IQD
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
        self.sync_data_file = '/opt/odoo/migration/data/product_sync_data_enhanced.json'
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
                'sync_stats': {'total_synced': 0, 'last_run_added': 0, 'last_run_updated': 0},
                'currency_conversion': {'enabled': True, 'rate': self.usd_to_iqd_rate}
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
                
            all_products.extend(items)
            page += 1
            
            logger.info(f"   📄 Fetched page {page-1}: {len(items)} products")
            
            # Rate limiting
            time.sleep(0.5)
            
        logger.info(f"✅ Total products from Books: {len(all_products)}")
        return all_products
    
    def _fetch_from_zoho_inventory(self, headers):
        """Fetch products from Zoho Inventory (if available)"""
        try:
            if 'inventory_base_url' not in self.zoho_config:
                logger.info("⚠️  Zoho Inventory URL not configured, skipping")
                return []
                
            logger.info("📦 Fetching from Zoho Inventory...")
            
            all_products = []
            page = 1
            per_page = 50
            
            while True:
                params = {
                    'organization_id': self.zoho_config['organization_id'],
                    'page': page,
                    'per_page': per_page
                }
                
                url = f"{self.zoho_config['inventory_base_url']}/items"
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch Inventory page {page}: {response.status_code}")
                    break
                    
                data = response.json()
                items = data.get('items', [])
                
                if not items:
                    break
                    
                all_products.extend(items)
                page += 1
                
                logger.info(f"   📄 Fetched Inventory page {page-1}: {len(items)} products")
                
                # Rate limiting
                time.sleep(0.5)
                
            logger.info(f"✅ Total products from Inventory: {len(all_products)}")
            return all_products
            
        except Exception as e:
            logger.warning(f"⚠️  Error fetching from Zoho Inventory: {e}")
            return []
    
    def download_product_image(self, image_data, product_name, product_id):
        """Download and process product image"""
        if not image_data:
            return None
            
        try:
            access_token = self.get_zoho_access_token()
            headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
            
            image_url = None
            
            # Handle different image data formats
            if isinstance(image_data, str):
                image_url = image_data
            elif isinstance(image_data, list) and len(image_data) > 0:
                image_url = image_data[0].get('image_url') if isinstance(image_data[0], dict) else image_data[0]
            elif isinstance(image_data, dict):
                image_url = image_data.get('image_url') or image_data.get('url')
            
            if not image_url:
                return None
            
            # Download image
            response = requests.get(image_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                image_content = response.content
                
                # Convert to base64
                base64_image = base64.b64encode(image_content).decode('utf-8')
                
                # Save locally for tracking
                safe_name = "".join(c for c in product_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                local_path = os.path.join(self.images_dir, f"{safe_name[:50]}_{product_id}.jpg")
                
                with open(local_path, 'wb') as f:
                    f.write(image_content)
                
                logger.info(f"   📸 Image downloaded for {product_name}")
                
                return {
                    'base64': base64_image,
                    'local_path': local_path,
                    'url': image_url,
                    'hash': hashlib.md5(image_content).hexdigest()
                }
                
        except Exception as e:
            logger.warning(f"⚠️  Error downloading image for {product_name}: {e}")
            
        return None
    
    def convert_currency_usd_to_iqd(self, price):
        """Convert USD price to IQD"""
        if not price or price <= 0:
            return 0.0
            
        # If price looks like USD (under 100), convert it
        if price < 100:
            converted = price * self.usd_to_iqd_rate
            logger.debug(f"   💱 Price conversion: ${price} → {converted:,.0f} IQD")
            return converted
        
        # If price is already high, assume it's already in IQD
        return price
    
    def find_existing_product_enhanced(self, zoho_product):
        """Enhanced product finding with better duplicate detection"""
        zoho_id = zoho_product.get('item_id')
        product_name = zoho_product.get('name', '').strip()
        sku = zoho_product.get('sku', '').strip()
        
        # First check by Zoho ID in our tracking
        if zoho_id and zoho_id in self.sync_data['products']:
            odoo_id = self.sync_data['products'][zoho_id]['odoo_id']
            try:
                existing = self.models.execute_kw(
                    self.odoo_db_config['database'], 
                    self.uid, 
                    self.odoo_db_config['password'],
                    'product.template', 
                    'read', 
                    [odoo_id],
                    {'fields': ['id', 'name', 'default_code']}
                )
                if existing:
                    return existing[0]
            except:
                # Product was deleted, remove from tracking
                del self.sync_data['products'][zoho_id]
        
        # Search by SKU/default_code
        if sku:
            products = self.models.execute_kw(
                self.odoo_db_config['database'], 
                self.uid, 
                self.odoo_db_config['password'],
                'product.template', 
                'search_read', 
                [[('default_code', '=', sku)]],
                {'fields': ['id', 'name', 'default_code'], 'limit': 1}
            )
            if products:
                return products[0]
        
        # Search by exact name match
        if product_name:
            products = self.models.execute_kw(
                self.odoo_db_config['database'], 
                self.uid, 
                self.odoo_db_config['password'],
                'product.template', 
                'search_read', 
                [[('name', '=', product_name)]],
                {'fields': ['id', 'name', 'default_code'], 'limit': 1}
            )
            if products:
                return products[0]
        
        return None
    
    def transform_product_enhanced(self, zoho_product):
        """Transform Zoho product to Odoo format with enhanced currency conversion"""
        odoo_product = {}
        
        # Map basic fields
        zoho_mapping = self.field_mapping['products']['zoho_books']
        for zoho_field, odoo_field in zoho_mapping.items():
            if zoho_field in zoho_product and zoho_product[zoho_field] is not None:
                value = zoho_product[zoho_field]
                
                if zoho_field in ['rate', 'purchase_rate']:
                    try:
                        price_value = float(value) if value else 0.0
                        # Apply currency conversion
                        converted_price = self.convert_currency_usd_to_iqd(price_value)
                        odoo_product[odoo_field] = converted_price
                        
                        if price_value != converted_price:
                            logger.info(f"   💱 {zoho_field}: ${price_value} → {converted_price:,.0f} IQD")
                            
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
    
    def resolve_uom_id(self, uom_string):
        """Resolve UOM string to Odoo UOM ID"""
        if not uom_string:
            return self.default_uom_id
            
        uom_key = str(uom_string).lower().strip()
        return self.uom_mapping.get(uom_key, self.default_uom_id)
    
    def calculate_product_checksum(self, zoho_product):
        """Calculate checksum for product to detect changes"""
        relevant_fields = ['name', 'rate', 'purchase_rate', 'description', 'sku', 'unit']
        data_string = ""
        
        for field in relevant_fields:
            value = zoho_product.get(field, '')
            data_string += str(value)
        
        return hashlib.md5(data_string.encode()).hexdigest()
    
    def sync_products_enhanced(self, force_full_sync=False):
        """Enhanced sync function with better duplicate handling and currency conversion"""
        logger.info("🚀 Starting enhanced product sync from Zoho to Odoo...")
        logger.info(f"💱 Currency conversion enabled: USD → IQD (rate: {self.usd_to_iqd_rate})")
        
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
        currency_conversions = 0
        
        for i, zoho_product in enumerate(zoho_products, 1):
            try:
                zoho_id = zoho_product.get('item_id')
                product_name = zoho_product.get('name', 'Unknown')
                
                logger.info(f"[{i}/{len(zoho_products)}] Processing: {product_name}")
                
                # Calculate checksum for change detection
                current_checksum = self.calculate_product_checksum(zoho_product)
                
                # Check if we need to sync this product
                existing_product = self.find_existing_product_enhanced(zoho_product)
                
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
                    odoo_product = self.transform_product_enhanced(zoho_product)
                    
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
                    
                    # Check if currency conversion was applied
                    rate = zoho_product.get('rate', 0)
                    purchase_rate = zoho_product.get('purchase_rate', 0)
                    if (rate and rate < 100) or (purchase_rate and purchase_rate < 100):
                        currency_conversions += 1
                    
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
                    odoo_product = self.transform_product_enhanced(zoho_product)
                    
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
                        
                        # Check if currency conversion was applied
                        rate = zoho_product.get('rate', 0)
                        purchase_rate = zoho_product.get('purchase_rate', 0)
                        if (rate and rate < 100) or (purchase_rate and purchase_rate < 100):
                            currency_conversions += 1
                        
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
                    logger.info(f"📊 Progress: {added_count} added, {updated_count} updated, {images_synced} with images, {currency_conversions} currency conversions")
                
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
        logger.info("🎉 ENHANCED PRODUCT SYNC COMPLETED!")
        logger.info("="*70)
        logger.info(f"➕ Products added: {added_count}")
        logger.info(f"🔄 Products updated: {updated_count}")
        logger.info(f"⏭️  Products skipped (no changes): {skipped_count}")
        logger.info(f"📷 Products with images synced: {images_synced}")
        logger.info(f"💱 Currency conversions applied: {currency_conversions}")
        logger.info(f"❌ Errors encountered: {error_count}")
        logger.info(f"📊 Total processed: {len(zoho_products)}")
        logger.info(f"💾 Total products tracked: {len(self.sync_data['products'])}")
        logger.info("="*70)
        
        return (added_count + updated_count) > 0

def main():
    print("🔄 Enhanced Zoho to Odoo Product Sync")
    print("="*60)
    print("This enhanced version includes:")
    print("✅ Automatic USD to IQD conversion (×1500)")
    print("✅ Enhanced image handling from Zoho Books/Inventory")
    print("✅ Better duplicate detection and prevention")
    print("✅ Change detection to sync only updated products")
    print("✅ One-way sync (Zoho → Odoo only)")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("1. Smart sync (only changed products)")
        print("2. Force full sync (all products)")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            sync = EnhancedZohoProductSync()
            sync.sync_products_enhanced(force_full_sync=False)
            
        elif choice == '2':
            print("⚠️  WARNING: Full sync will process ALL products!")
            confirm = input("Are you sure? (yes/no): ").lower()
            if confirm == 'yes':
                sync = EnhancedZohoProductSync()
                sync.sync_products_enhanced(force_full_sync=True)
            else:
                print("❌ Cancelled")
                
        elif choice == '3':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main() 