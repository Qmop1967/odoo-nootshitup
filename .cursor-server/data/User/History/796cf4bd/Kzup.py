#!/usr/bin/env python3

import json
import requests
import xmlrpc.client
import logging
import time
import threading
import signal
import sys
import os
import hashlib
import base64
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

class ZohoOdooSyncService:
    """
    One-way synchronization service from Zoho Books to Odoo with images
    Enhanced version with conflict resolution and comprehensive logging
    """
    
    def __init__(self, config_path='/opt/odoo/migration/config/zoho_config.json'):
        self.config_path = config_path
        self.running = False
        self.sync_interval = 300  # 5 minutes
        self.last_sync_time = None
        self.usd_to_iqd_rate = 1500  # USD to IQD conversion rate
        
        # Setup logging
        self.setup_logging()
        
        # Load configuration
        self.load_config()
        self.setup_directories()
        
        # Connect to systems
        self.connect_to_odoo()
        self.test_zoho_connection()
        
        # Load tracking data
        self.load_sync_tracking()
        
        # Sync statistics
        self.sync_stats = {
            'total_syncs': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'products_added': 0,
            'products_updated': 0,
            'products_deleted': 0,
            'images_synced': 0,
            'images_failed': 0,
            'conflicts_resolved': 0,
            'last_sync_duration': 0,
            'errors': [],
            'service_start_time': datetime.now().isoformat()
        }
        
        self.logger.info("🚀 Zoho-Odoo Sync Service initialized successfully")
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = '/opt/odoo/migration/logs'
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # Main service log
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{log_dir}/sync_service.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger('ZohoOdooSync')
        
        # Conflict resolution log
        self.conflict_logger = logging.getLogger('ConflictResolution')
        conflict_handler = logging.FileHandler(f'{log_dir}/conflicts.log')
        conflict_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.conflict_logger.addHandler(conflict_handler)
        self.conflict_logger.setLevel(logging.INFO)
        
        # Changes log
        self.changes_logger = logging.getLogger('Changes')
        changes_handler = logging.FileHandler(f'{log_dir}/changes.log')
        changes_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.changes_logger.addHandler(changes_handler)
        self.changes_logger.setLevel(logging.INFO)
        
        # Images log
        self.images_logger = logging.getLogger('Images')
        images_handler = logging.FileHandler(f'{log_dir}/images.log')
        images_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.images_logger.addHandler(images_handler)
        self.images_logger.setLevel(logging.INFO)
    
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            
            self.zoho_config = self.config['zoho_books']
            self.odoo_config = self.config['odoo']['test_db']
            
            # Load field mapping if exists
            mapping_path = '/opt/odoo/migration/config/field_mapping.json'
            if os.path.exists(mapping_path):
                with open(mapping_path, 'r') as f:
                    self.field_mapping = json.load(f)
            else:
                self.field_mapping = self.get_default_field_mapping()
            
            self.logger.info("✅ Configuration loaded successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load configuration: {e}")
            raise
    
    def get_default_field_mapping(self):
        """Default field mapping for Zoho to Odoo"""
        return {
            'products': {
                'zoho_books': {
                    'name': 'name',
                    'rate': 'list_price',
                    'purchase_rate': 'standard_price',
                    'description': 'description',
                    'sku': 'default_code',
                    'item_id': 'x_zoho_item_id'
                },
                'default_values': {
                    'type': 'product',
                    'sale_ok': True,
                    'purchase_ok': True,
                    'tracking': 'none'
                }
            }
        }
    
    def setup_directories(self):
        """Setup required directories"""
        directories = [
            '/opt/odoo/migration/data/sync_service',
            '/opt/odoo/migration/logs',
            '/opt/odoo/migration/backups',
            '/opt/odoo/migration/data/product_images'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        self.data_dir = '/opt/odoo/migration/data/sync_service'
        self.images_dir = '/opt/odoo/migration/data/product_images'
        self.tracking_file = f'{self.data_dir}/sync_tracking.json'
    
    def connect_to_odoo(self):
        """Establish connection to Odoo"""
        try:
            url = f"http://{self.odoo_config['host']}:{self.odoo_config['port']}"
            
            self.odoo_common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
            self.odoo_uid = self.odoo_common.authenticate(
                self.odoo_config['database'],
                self.odoo_config['username'],
                self.odoo_config['password'],
                {}
            )
            
            if not self.odoo_uid:
                raise Exception("Failed to authenticate with Odoo")
            
            self.odoo_models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
            self.logger.info("✅ Connected to Odoo successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to Odoo: {e}")
            raise
    
    def test_zoho_connection(self):
        """Test Zoho API connection"""
        try:
            access_token = self.get_zoho_access_token()
            if access_token:
                self.logger.info("✅ Zoho API connection verified")
            else:
                raise Exception("Failed to get Zoho access token")
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to Zoho: {e}")
            raise
    
    def get_zoho_access_token(self) -> Optional[str]:
        """Get fresh access token from Zoho"""
        try:
            token_url = "https://accounts.zoho.com/oauth/v2/token"
            token_params = {
                'refresh_token': self.zoho_config['refresh_token'],
                'client_id': self.zoho_config['client_id'],
                'client_secret': self.zoho_config['client_secret'],
                'grant_type': 'refresh_token'
            }
            
            response = requests.post(token_url, data=token_params, timeout=30)
            response.raise_for_status()
            return response.json()['access_token']
        except Exception as e:
            self.logger.error(f"❌ Error getting Zoho token: {e}")
            return None
    
    def load_sync_tracking(self):
        """Load sync tracking data"""
        if os.path.exists(self.tracking_file):
            try:
                with open(self.tracking_file, 'r') as f:
                    self.tracking_data = json.load(f)
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to load tracking data: {e}")
                self.tracking_data = self.get_empty_tracking_data()
        else:
            self.tracking_data = self.get_empty_tracking_data()
    
    def get_empty_tracking_data(self):
        """Get empty tracking data structure"""
        return {
            'last_sync': None,
            'zoho_products': {},  # zoho_id -> {checksum, last_modified, odoo_id, image_url, image_checksum}
            'sync_history': [],
            'service_stats': {
                'uptime_start': datetime.now().isoformat(),
                'total_products_synced': 0,
                'total_images_synced': 0
            }
        }
    
    def save_sync_tracking(self):
        """Save sync tracking data"""
        try:
            # Create backup
            if os.path.exists(self.tracking_file):
                backup_file = f"{self.tracking_file}.backup.{int(time.time())}"
                os.rename(self.tracking_file, backup_file)
                
                # Keep only last 5 backups
                backup_files = sorted([f for f in os.listdir(self.data_dir) if f.startswith('sync_tracking.json.backup.')])
                if len(backup_files) > 5:
                    for old_backup in backup_files[:-5]:
                        os.remove(os.path.join(self.data_dir, old_backup))
            
            with open(self.tracking_file, 'w') as f:
                json.dump(self.tracking_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"❌ Failed to save tracking data: {e}")
    
    def calculate_product_checksum(self, product_data: dict) -> str:
        """Calculate checksum for product data"""
        relevant_fields = ['name', 'rate', 'purchase_rate', 'description', 'sku', 'status', 'image_url']
        data_string = ""
        
        for field in relevant_fields:
            value = product_data.get(field, '')
            data_string += str(value)
        
        return hashlib.md5(data_string.encode()).hexdigest()
    
    def download_product_image(self, image_url: str, zoho_id: str) -> Optional[str]:
        """Download product image from Zoho and save locally"""
        if not image_url:
            return None
            
        try:
            # Create filename
            file_extension = 'jpg'  # Default
            if '.' in image_url:
                file_extension = image_url.split('.')[-1].lower()
                if file_extension not in ['jpg', 'jpeg', 'png', 'gif']:
                    file_extension = 'jpg'
            
            filename = f"product_{zoho_id}.{file_extension}"
            local_path = os.path.join(self.images_dir, filename)
            
            # Check if file already exists and is recent
            if os.path.exists(local_path):
                file_age = time.time() - os.path.getmtime(local_path)
                if file_age < 86400:  # Less than 24 hours old
                    return local_path
            
            # Download image
            access_token = self.get_zoho_access_token()
            if not access_token:
                return None
                
            headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
            response = requests.get(image_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                
                self.images_logger.info(f"✅ Downloaded image for product {zoho_id}: {filename}")
                return local_path
            else:
                self.images_logger.warning(f"⚠️ Failed to download image for product {zoho_id}: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            self.images_logger.error(f"❌ Error downloading image for product {zoho_id}: {e}")
            return None
    
    def upload_image_to_odoo(self, local_path: str, product_id: int, zoho_id: str) -> Optional[int]:
        """Upload image to Odoo product"""
        try:
            if not os.path.exists(local_path):
                return None
            
            # Read image file
            with open(local_path, 'rb') as f:
                image_data = f.read()
            
            # Encode to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Get filename
            filename = os.path.basename(local_path)
            
            # Check if product already has an image
            existing_attachments = self.odoo_models.execute_kw(
                self.odoo_config['database'], 
                self.odoo_uid, 
                self.odoo_config['password'],
                'ir.attachment', 
                'search_read', 
                [[
                    ('res_model', '=', 'product.template'),
                    ('res_id', '=', product_id),
                    ('res_field', '=', 'image_1920')
                ]],
                {'fields': ['id'], 'limit': 1}
            )
            
            if existing_attachments:
                # Update existing attachment
                attachment_id = existing_attachments[0]['id']
                self.odoo_models.execute_kw(
                    self.odoo_config['database'], 
                    self.odoo_uid, 
                    self.odoo_config['password'],
                    'ir.attachment', 
                    'write', 
                    [[attachment_id], {
                        'datas': image_base64,
                        'name': filename
                    }]
                )
                self.images_logger.info(f"🔄 Updated image for product {product_id} (Zoho ID: {zoho_id})")
                return attachment_id
            else:
                # Create new attachment
                attachment_data = {
                    'name': filename,
                    'type': 'binary',
                    'datas': image_base64,
                    'res_model': 'product.template',
                    'res_id': product_id,
                    'res_field': 'image_1920',
                    'public': False,
                    'store_fname': filename
                }
                
                attachment_id = self.odoo_models.execute_kw(
                    self.odoo_config['database'], 
                    self.odoo_uid, 
                    self.odoo_config['password'],
                    'ir.attachment', 
                    'create', 
                    [attachment_data]
                )
                
                if attachment_id:
                    self.images_logger.info(f"✅ Added new image for product {product_id} (Zoho ID: {zoho_id})")
                    return attachment_id
                
            return None
            
        except Exception as e:
            self.images_logger.error(f"❌ Error uploading image to Odoo for product {product_id}: {e}")
            return None
    
    def sync_product_image(self, zoho_product: dict, odoo_product_id: int) -> bool:
        """Sync product image from Zoho to Odoo"""
        zoho_id = str(zoho_product.get('item_id', ''))
        image_url = zoho_product.get('image_url')
        
        if not image_url:
            return True  # No image to sync
        
        try:
            # Check if image has changed
            current_image_checksum = hashlib.md5(image_url.encode()).hexdigest()
            stored_data = self.tracking_data['zoho_products'].get(zoho_id, {})
            stored_image_checksum = stored_data.get('image_checksum')
            
            if stored_image_checksum == current_image_checksum:
                return True  # Image hasn't changed
            
            # Download image
            local_path = self.download_product_image(image_url, zoho_id)
            if not local_path:
                return False
            
            # Upload to Odoo
            attachment_id = self.upload_image_to_odoo(local_path, odoo_product_id, zoho_id)
            if attachment_id:
                # Update tracking
                if zoho_id not in self.tracking_data['zoho_products']:
                    self.tracking_data['zoho_products'][zoho_id] = {}
                
                self.tracking_data['zoho_products'][zoho_id]['image_checksum'] = current_image_checksum
                self.tracking_data['zoho_products'][zoho_id]['image_url'] = image_url
                self.sync_stats['images_synced'] += 1
                return True
            else:
                self.sync_stats['images_failed'] += 1
                return False
                
        except Exception as e:
            self.images_logger.error(f"❌ Error syncing image for product {zoho_id}: {e}")
            self.sync_stats['images_failed'] += 1
            return False
    
    def fetch_all_zoho_products(self) -> List[dict]:
        """Fetch all products from Zoho Books"""
        self.logger.info("📦 Fetching all products from Zoho Books...")
        
        access_token = self.get_zoho_access_token()
        if not access_token:
            return []
            
        headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
        all_products = []
        page = 1
        per_page = 200
        
        while True:
            try:
                params = {
                    'organization_id': self.zoho_config['organization_id'],
                    'page': page,
                    'per_page': per_page
                }
                
                url = f"{self.zoho_config['base_url']}/items"
                response = requests.get(url, headers=headers, params=params, timeout=30)
                
                if response.status_code != 200:
                    self.logger.warning(f"Failed to fetch Zoho page {page}: {response.status_code}")
                    break
                    
                data = response.json()
                items = data.get('items', [])
                
                if not items:
                    break
                    
                all_products.extend(items)
                self.logger.info(f"   📄 Fetched page {page}: {len(items)} products")
                page += 1
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                self.logger.error(f"Error fetching Zoho page {page}: {e}")
                break
        
        self.logger.info(f"✅ Total products from Zoho: {len(all_products)}")
        return all_products
    
    def fetch_all_odoo_products(self) -> List[dict]:
        """Fetch all products from Odoo"""
        self.logger.info("📦 Fetching all products from Odoo...")
        
        try:
            products = self.odoo_models.execute_kw(
                self.odoo_config['database'], 
                self.odoo_uid, 
                self.odoo_config['password'],
                'product.template', 
                'search_read', 
                [[]],
                {
                    'fields': ['id', 'name', 'list_price', 'standard_price', 'default_code', 
                              'x_zoho_item_id', 'create_date', 'write_date'],
                    'order': 'id'
                }
            )
            
            self.logger.info(f"✅ Total products from Odoo: {len(products)}")
            return products
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching Odoo products: {e}")
            return []
    
    def convert_usd_to_iqd(self, price: float) -> float:
        """Convert USD price to IQD"""
        if not price or price <= 0:
            return 0.0
        
        # If price looks like USD (under 100), convert it
        if price < 100:
            return price * self.usd_to_iqd_rate
        
        return price
    
    def transform_zoho_to_odoo(self, zoho_product: dict) -> dict:
        """Transform Zoho product to Odoo format"""
        odoo_product = {}
        
        # Map basic fields
        zoho_mapping = self.field_mapping['products']['zoho_books']
        for zoho_field, odoo_field in zoho_mapping.items():
            if zoho_field in zoho_product and zoho_product[zoho_field] is not None:
                value = zoho_product[zoho_field]
                
                if zoho_field in ['rate', 'purchase_rate']:
                    try:
                        price_value = float(value) if value else 0.0
                        converted_price = self.convert_usd_to_iqd(price_value)
                        odoo_product[odoo_field] = converted_price
                    except (ValueError, TypeError):
                        odoo_product[odoo_field] = 0.0
                else:
                    odoo_product[odoo_field] = value
        
        # Apply default values
        for field, value in self.field_mapping['products']['default_values'].items():
            odoo_product[field] = value
        
        # Ensure required fields
        if 'name' not in odoo_product or not odoo_product['name']:
            odoo_product['name'] = f"Product {zoho_product.get('item_id', 'Unknown')}"
        
        return odoo_product
    
    def find_odoo_product_by_zoho_id(self, zoho_id: str) -> Optional[dict]:
        """Find Odoo product by Zoho ID using the custom field"""
        try:
            products = self.odoo_models.execute_kw(
                self.odoo_config['database'], 
                self.odoo_uid, 
                self.odoo_config['password'],
                'product.template', 
                'search_read', 
                [[('x_zoho_item_id', '=', zoho_id)]],
                {'fields': ['id', 'name', 'list_price', 'standard_price', 'x_zoho_item_id'], 'limit': 1}
            )
            
            if products:
                return products[0]
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error finding Odoo product by Zoho ID {zoho_id}: {e}")
            return None
    
    def create_product_in_odoo(self, zoho_product: dict) -> Optional[int]:
        """Create new product in Odoo"""
        try:
            odoo_product_data = self.transform_zoho_to_odoo(zoho_product)
            
            product_id = self.odoo_models.execute_kw(
                self.odoo_config['database'], 
                self.odoo_uid, 
                self.odoo_config['password'],
                'product.template', 
                'create', 
                [odoo_product_data]
            )
            
            if product_id:
                product_name = zoho_product.get('name', 'Unknown')
                self.changes_logger.info(f"✅ CREATED: {product_name} (ID: {product_id})")
                return product_id
            
            return None
            
        except Exception as e:
            product_name = zoho_product.get('name', 'Unknown')
            self.logger.error(f"❌ Error creating product '{product_name}': {e}")
            return None
    
    def update_product_in_odoo(self, odoo_product_id: int, zoho_product: dict, conflicts: List[str] = None) -> bool:
        """Update existing product in Odoo"""
        try:
            odoo_product_data = self.transform_zoho_to_odoo(zoho_product)
            
            # Remove fields that shouldn't be updated
            update_fields = {k: v for k, v in odoo_product_data.items() 
                           if k not in ['default_code']}
            
            self.odoo_models.execute_kw(
                self.odoo_config['database'], 
                self.odoo_uid, 
                self.odoo_config['password'],
                'product.template', 
                'write', 
                [[odoo_product_id], update_fields]
            )
            
            product_name = zoho_product.get('name', 'Unknown')
            if conflicts:
                self.conflict_logger.info(f"🔄 CONFLICT RESOLVED: {product_name} (ID: {odoo_product_id}) - Zoho data wins")
                self.changes_logger.info(f"🔄 UPDATED (conflict): {product_name} (ID: {odoo_product_id})")
                self.sync_stats['conflicts_resolved'] += 1
            else:
                self.changes_logger.info(f"🔄 UPDATED: {product_name} (ID: {odoo_product_id})")
            
            return True
            
        except Exception as e:
            product_name = zoho_product.get('name', 'Unknown')
            self.logger.error(f"❌ Error updating product '{product_name}' (ID: {odoo_product_id}): {e}")
            return False
    
    def delete_product_in_odoo(self, odoo_product_id: int, product_name: str) -> bool:
        """Delete product from Odoo (if needed)"""
        try:
            self.odoo_models.execute_kw(
                self.odoo_config['database'], 
                self.odoo_uid, 
                self.odoo_config['password'],
                'product.template', 
                'unlink', 
                [[odoo_product_id]]
            )
            
            self.changes_logger.info(f"🗑️ DELETED: {product_name} (ID: {odoo_product_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error deleting product '{product_name}' (ID: {odoo_product_id}): {e}")
            return False
    
    def detect_conflicts(self, zoho_product: dict, odoo_product: dict) -> List[str]:
        """Detect conflicts between Zoho and Odoo data"""
        conflicts = []
        
        # Convert prices for comparison
        zoho_list_price = self.convert_usd_to_iqd(float(zoho_product.get('rate', 0)))
        zoho_cost_price = self.convert_usd_to_iqd(float(zoho_product.get('purchase_rate', 0)))
        
        odoo_list_price = float(odoo_product.get('list_price', 0))
        odoo_cost_price = float(odoo_product.get('standard_price', 0))
        
        # Check for significant price differences (more than 1% difference)
        if abs(zoho_list_price - odoo_list_price) > (odoo_list_price * 0.01):
            conflicts.append(f"List price differs: Zoho={zoho_list_price:.2f} vs Odoo={odoo_list_price:.2f}")
        
        if abs(zoho_cost_price - odoo_cost_price) > (odoo_cost_price * 0.01):
            conflicts.append(f"Cost price differs: Zoho={zoho_cost_price:.2f} vs Odoo={odoo_cost_price:.2f}")
        
        # Check name differences
        zoho_name = zoho_product.get('name', '').strip()
        odoo_name = odoo_product.get('name', '').strip()
        if zoho_name != odoo_name:
            conflicts.append(f"Name differs: Zoho='{zoho_name}' vs Odoo='{odoo_name}'")
        
        return conflicts
    
    def synchronize_products(self) -> Tuple[int, int, int, int]:
        """Synchronize products from Zoho to Odoo"""
        self.logger.info("🚀 Starting product synchronization...")
        
        # Fetch products from both systems
        zoho_products = self.fetch_all_zoho_products()
        odoo_products = self.fetch_all_odoo_products()
        
        if not zoho_products:
            self.logger.error("❌ No products fetched from Zoho - skipping sync")
            return 0, 0, 0, 0
        
        # Create lookup for Odoo products by Zoho ID
        odoo_by_zoho_id = {}
        for odoo_product in odoo_products:
            zoho_id = odoo_product.get('x_zoho_item_id')
            if zoho_id:
                odoo_by_zoho_id[str(zoho_id)] = odoo_product
        
        # Count comparison
        zoho_count = len(zoho_products)
        odoo_count = len(odoo_products)
        
        self.logger.info(f"📊 Product Count Comparison:")
        self.logger.info(f"   Zoho: {zoho_count} products")
        self.logger.info(f"   Odoo: {odoo_count} products")
        self.logger.info(f"   Difference: {zoho_count - odoo_count}")
        
        # Track changes
        added_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        # Process each Zoho product
        for i, zoho_product in enumerate(zoho_products, 1):
            try:
                zoho_id = str(zoho_product.get('item_id', ''))
                product_name = zoho_product.get('name', 'Unknown')
                
                if i % 100 == 0 or i == len(zoho_products):
                    self.logger.info(f"📊 Progress: {i}/{zoho_count} products processed")
                
                # Calculate checksum
                current_checksum = self.calculate_product_checksum(zoho_product)
                
                # Check if product has changed
                stored_data = self.tracking_data['zoho_products'].get(zoho_id, {})
                stored_checksum = stored_data.get('checksum')
                
                if stored_checksum == current_checksum:
                    skipped_count += 1
                    continue
                
                # Find corresponding Odoo product
                odoo_product = odoo_by_zoho_id.get(zoho_id)
                
                if odoo_product:
                    # Detect conflicts
                    conflicts = self.detect_conflicts(zoho_product, odoo_product)
                    
                    # Update existing product (Zoho data wins)
                    if self.update_product_in_odoo(odoo_product['id'], zoho_product, conflicts):
                        updated_count += 1
                        
                        # Sync image
                        self.sync_product_image(zoho_product, odoo_product['id'])
                        
                        # Update tracking
                        self.tracking_data['zoho_products'][zoho_id] = {
                            'checksum': current_checksum,
                            'last_modified': datetime.now().isoformat(),
                            'odoo_id': odoo_product['id']
                        }
                    else:
                        error_count += 1
                
                else:
                    # Create new product
                    product_id = self.create_product_in_odoo(zoho_product)
                    if product_id:
                        added_count += 1
                        
                        # Sync image
                        self.sync_product_image(zoho_product, product_id)
                        
                        # Update tracking
                        self.tracking_data['zoho_products'][zoho_id] = {
                            'checksum': current_checksum,
                            'last_modified': datetime.now().isoformat(),
                            'odoo_id': product_id
                        }
                    else:
                        error_count += 1
                
            except Exception as e:
                error_count += 1
                self.logger.error(f"❌ Error processing product {product_name}: {e}")
                continue
        
        self.logger.info(f"✅ Product sync results:")
        self.logger.info(f"   ➕ Added: {added_count}")
        self.logger.info(f"   🔄 Updated: {updated_count}")
        self.logger.info(f"   ⏭️  Skipped: {skipped_count}")
        self.logger.info(f"   ❌ Errors: {error_count}")
        
        return added_count, updated_count, skipped_count, error_count
    
    def run_sync_cycle(self):
        """Run one complete sync cycle"""
        sync_start_time = datetime.now()
        self.logger.info("🔄 Starting sync cycle...")
        
        try:
            # Synchronize products
            added, updated, skipped, errors = self.synchronize_products()
            
            # Update statistics
            sync_duration = (datetime.now() - sync_start_time).total_seconds()
            
            self.sync_stats.update({
                'total_syncs': self.sync_stats['total_syncs'] + 1,
                'successful_syncs': self.sync_stats['successful_syncs'] + 1,
                'products_added': self.sync_stats['products_added'] + added,
                'products_updated': self.sync_stats['products_updated'] + updated,
                'last_sync_duration': sync_duration
            })
            
            # Record sync history
            sync_record = {
                'timestamp': datetime.now().isoformat(),
                'products_added': added,
                'products_updated': updated,
                'products_skipped': skipped,
                'products_errors': errors,
                'images_synced': self.sync_stats['images_synced'],
                'conflicts_resolved': self.sync_stats['conflicts_resolved'],
                'duration': sync_duration
            }
            
            self.tracking_data['sync_history'].append(sync_record)
            self.tracking_data['last_sync'] = datetime.now().isoformat()
            
            # Keep only last 50 sync records
            if len(self.tracking_data['sync_history']) > 50:
                self.tracking_data['sync_history'] = self.tracking_data['sync_history'][-50:]
            
            # Save tracking data
            self.save_sync_tracking()
            
            self.last_sync_time = datetime.now()
            
            # Log summary
            self.logger.info("\n" + "="*80)
            self.logger.info("🎉 SYNC CYCLE COMPLETED!")
            self.logger.info("="*80)
            self.logger.info(f"⏱️  Duration: {sync_duration:.1f} seconds")
            self.logger.info(f"➕ Added: {added}")
            self.logger.info(f"🔄 Updated: {updated}")
            self.logger.info(f"⏭️  Skipped: {skipped}")
            self.logger.info(f"❌ Errors: {errors}")
            self.logger.info(f"🖼️  Images Synced: {self.sync_stats['images_synced']}")
            self.logger.info(f"⚡ Conflicts Resolved: {self.sync_stats['conflicts_resolved']}")
            self.logger.info("="*80)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Sync cycle failed: {e}")
            self.sync_stats['failed_syncs'] += 1
            return False
    
    def start_service(self):
        """Start the continuous sync service"""
        if self.running:
            self.logger.warning("⚠️ Service is already running")
            return
        
        self.running = True
        self.logger.info(f"🚀 Starting Zoho-Odoo sync service (interval: {self.sync_interval}s)")
        
        # Run initial sync
        self.run_sync_cycle()
        
        # Start continuous sync loop
        while self.running:
            try:
                # Wait for next sync
                sleep_remaining = self.sync_interval
                while sleep_remaining > 0 and self.running:
                    time.sleep(min(30, sleep_remaining))
                    sleep_remaining -= 30
                
                if self.running:
                    self.run_sync_cycle()
                    
            except Exception as e:
                self.logger.error(f"❌ Error in sync loop: {e}")
                time.sleep(60)  # Wait 1 minute on error
    
    def stop_service(self):
        """Stop the sync service"""
        self.logger.info("🛑 Stopping sync service...")
        self.running = False
    
    def get_service_status(self) -> dict:
        """Get current service status"""
        return {
            'running': self.running,
            'last_sync': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'sync_interval': self.sync_interval,
            'stats': self.sync_stats.copy()
        }

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger = logging.getLogger('ZohoOdooSync')
    logger.info("🛑 Received shutdown signal")
    global sync_service
    if sync_service:
        sync_service.stop_service()
    sys.exit(0)

def main():
    """Main service entry point"""
    global sync_service
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        sync_service = ZohoOdooSyncService()
        sync_service.start_service()
        
    except Exception as e:
        logger = logging.getLogger('ZohoOdooSync')
        logger.error(f"❌ Service failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    sync_service = None
    main() 