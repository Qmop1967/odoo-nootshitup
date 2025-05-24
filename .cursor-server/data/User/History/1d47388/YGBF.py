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
import schedule
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

class ZohoOdooSyncServiceWithImagesFixed:
    """
    Fixed one-way synchronization service from Zoho Books to Odoo
    Continuously monitors and mirrors all product data including images
    """
    
    def __init__(self, config_path='/opt/odoo/migration/config/zoho_config.json'):
        self.config_path = config_path
        self.running = False
        self.sync_interval = 300  # 5 minutes
        self.last_sync_time = None
        
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
        
        self.logger.info("🚀 Fixed Zoho-Odoo Sync Service with Images initialized successfully")
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = '/opt/odoo/migration/logs'
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # Main service log
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{log_dir}/sync_service_images_fixed.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger('ZohoOdooSyncImagesFixed')
        
        # Conflict resolution log
        self.conflict_logger = logging.getLogger('ConflictResolution')
        conflict_handler = logging.FileHandler(f'{log_dir}/conflicts_fixed.log')
        conflict_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.conflict_logger.addHandler(conflict_handler)
        self.conflict_logger.setLevel(logging.INFO)
        
        # Changes log
        self.changes_logger = logging.getLogger('Changes')
        changes_handler = logging.FileHandler(f'{log_dir}/changes_fixed.log')
        changes_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.changes_logger.addHandler(changes_handler)
        self.changes_logger.setLevel(logging.INFO)
        
        # Images log
        self.images_logger = logging.getLogger('Images')
        images_handler = logging.FileHandler(f'{log_dir}/images_fixed.log')
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
                    'type': 'product',  # Always set as 'product' type for Odoo
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
        self.tracking_file = f'{self.data_dir}/sync_tracking_images_fixed.json'
    
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
            self.logger.error(f"❌ Error getting Zoho access token: {e}")
            return None
    
    def load_sync_tracking(self):
        """Load synchronization tracking data"""
        if os.path.exists(self.tracking_file):
            try:
                with open(self.tracking_file, 'r') as f:
                    self.tracking_data = json.load(f)
                self.logger.info("✅ Sync tracking data loaded")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to load tracking data: {e}")
                self.tracking_data = self.get_empty_tracking_data()
        else:
            self.tracking_data = self.get_empty_tracking_data()
    
    def get_empty_tracking_data(self):
        """Get empty tracking data structure"""
        return {
            'last_full_sync': None,
            'zoho_products': {},  # zoho_id -> {checksum, last_modified, odoo_id, last_sync, image_checksum}
            'odoo_products': {},  # odoo_id -> {zoho_id, last_modified, last_sync}
            'product_images': {},  # zoho_id -> {image_url, local_path, odoo_attachment_id, checksum}
            'deleted_products': [],  # Track products deleted from Zoho
            'sync_history': [],
            'conflicts': [],
            'service_stats': {}
        }
    
    def save_sync_tracking(self):
        """Save synchronization tracking data"""
        try:
            # Create backup
            if os.path.exists(self.tracking_file):
                backup_file = f"{self.tracking_file}.backup_{int(time.time())}"
                os.rename(self.tracking_file, backup_file)
                
                # Keep only last 5 backups
                backup_dir = os.path.dirname(backup_file)
                backups = [f for f in os.listdir(backup_dir) if f.startswith('sync_tracking_images_fixed.json.backup_')]
                if len(backups) > 5:
                    backups.sort()
                    for old_backup in backups[:-5]:
                        os.remove(os.path.join(backup_dir, old_backup))
            
            with open(self.tracking_file, 'w') as f:
                json.dump(self.tracking_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"❌ Failed to save tracking data: {e}")
    
    def sanitize_text(self, text: str) -> str:
        """Sanitize text for Odoo compatibility"""
        if not text:
            return ""
        
        # Convert to string and strip
        text = str(text).strip()
        
        # Replace problematic characters
        replacements = {
            '❌': 'X',
            '✅': 'V',
            '🔥': '',
            '💡': '',
            '⚡': '',
            '🎯': '',
            '📱': '',
            '💻': '',
            '🖥️': '',
            '⌨️': '',
            '🖱️': '',
            '💾': '',
            '💿': '',
            '📀': '',
            '🔌': '',
            '🔋': '',
            '📺': '',
            '📷': '',
            '📹': '',
            '🎥': '',
            '📞': '',
            '☎️': '',
            '📠': '',
            '📡': '',
            '🎧': '',
            '🎤': '',
            '🔊': '',
            '🔇': '',
            '🔈': '',
            '🔉': '',
            '🎵': '',
            '🎶': '',
            '🎼': '',
            '🎹': '',
            '🥁': '',
            '🎸': '',
            '🎺': '',
            '🎷': '',
            '🎻': '',
            '🪕': '',
            '🪗': '',
            '🪘': '',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Remove any remaining non-ASCII characters
        import re
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Ensure it's not empty
        if not text:
            text = "Product"
        
        return text

    def calculate_product_checksum(self, product_data: dict) -> str:
        """Calculate checksum for product data"""
        relevant_fields = ['name', 'rate', 'purchase_rate', 'description', 'sku', 'status']
        data_string = ""
        
        for field in relevant_fields:
            value = product_data.get(field, '')
            data_string += str(value)
        
        return hashlib.md5(data_string.encode()).hexdigest()
    
    def get_image_download_url(self, zoho_product: dict) -> Optional[str]:
        """Extract image download URL from Zoho product data"""
        try:
            # Method 1: Check image_document_id
            image_doc_id = zoho_product.get('image_document_id')
            if image_doc_id:
                # For Zoho Books, we need to construct the download URL
                access_token = self.get_zoho_access_token()
                if access_token:
                    download_url = f"{self.zoho_config['base_url']}/items/{zoho_product.get('item_id')}/documents/{image_doc_id}"
                    self.images_logger.info(f"Found image document ID {image_doc_id} for product {zoho_product.get('item_id')}")
                    return download_url
            
            # Method 2: Check documents array (detailed fetch)
            documents = zoho_product.get('documents', [])
            if documents and isinstance(documents, list):
                for doc in documents:
                    if doc.get('file_type') in ['jpg', 'jpeg', 'png', 'gif']:
                        doc_id = doc.get('document_id')
                        if doc_id:
                            access_token = self.get_zoho_access_token()
                            if access_token:
                                download_url = f"{self.zoho_config['base_url']}/items/{zoho_product.get('item_id')}/documents/{doc_id}"
                                self.images_logger.info(f"Found image in documents array: {doc.get('file_name')} for product {zoho_product.get('item_id')}")
                                return download_url
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting image URL for product {zoho_product.get('item_id')}: {e}")
            return None
    
    def download_product_image(self, image_url: str, zoho_id: str) -> Optional[str]:
        """Download product image from Zoho"""
        try:
            if not image_url:
                return None
            
            # Get access token for image download
            access_token = self.get_zoho_access_token()
            if not access_token:
                return None
            
            headers = {
                'Authorization': f'Zoho-oauthtoken {access_token}',
                'User-Agent': 'ZohoOdooSync/1.0'
            }
            
            # Add organization_id as parameter
            params = {'organization_id': self.zoho_config['organization_id']}
            
            # Download image
            self.images_logger.info(f"Downloading image from: {image_url}")
            response = requests.get(image_url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            # Determine file extension from content type or URL
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            elif 'gif' in content_type:
                ext = '.gif'
            else:
                # Try to get from URL or default to jpg
                if 'png' in image_url.lower():
                    ext = '.png'
                elif 'gif' in image_url.lower():
                    ext = '.gif'
                else:
                    ext = '.jpg'
            
            # Save image locally
            filename = f"product_{zoho_id}_{uuid.uuid4().hex[:8]}{ext}"
            local_path = os.path.join(self.images_dir, filename)
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            self.images_logger.info(f"Downloaded image for product {zoho_id}: {filename} ({len(response.content)} bytes)")
            return local_path
            
        except Exception as e:
            self.images_logger.error(f"❌ Error downloading image for product {zoho_id}: {e}")
            self.sync_stats['images_failed'] += 1
            return None
    
    def upload_image_to_odoo(self, local_path: str, product_id: int, zoho_id: str) -> Optional[int]:
        """Upload image to Odoo and attach to product"""
        try:
            if not os.path.exists(local_path):
                return None
            
            # Read image file
            with open(local_path, 'rb') as f:
                image_data = f.read()
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Create attachment in Odoo
            filename = os.path.basename(local_path)
            
            attachment_data = {
                'name': filename,
                'datas': image_base64,
                'res_model': 'product.template',
                'res_id': product_id,
                'type': 'binary',
                'mimetype': 'image/jpeg',
                'description': f'Product image from Zoho Books (ID: {zoho_id})'
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
                # Set as product image
                self.odoo_models.execute_kw(
                    self.odoo_config['database'],
                    self.odoo_uid,
                    self.odoo_config['password'],
                    'product.template',
                    'write',
                    [[product_id], {'image_1920': image_base64}]
                )
                
                self.images_logger.info(f"Uploaded image to Odoo for product {product_id}: {filename}")
                self.sync_stats['images_synced'] += 1
                return attachment_id
            
        except Exception as e:
            self.images_logger.error(f"❌ Error uploading image to Odoo for product {product_id}: {e}")
            self.sync_stats['images_failed'] += 1
            return None
    
    def sync_product_image(self, zoho_product: dict, odoo_product_id: int) -> bool:
        """Sync product image from Zoho to Odoo"""
        try:
            zoho_id = str(zoho_product.get('item_id', ''))
            
            # Get image URL using improved method
            image_url = self.get_image_download_url(zoho_product)
            
            if not image_url:
                self.images_logger.debug(f"No image found for product {zoho_id}")
                return True  # No image to sync
            
            # Check if image has changed
            current_image_checksum = hashlib.md5(str(image_url).encode()).hexdigest()
            stored_image_data = self.tracking_data['product_images'].get(zoho_id, {})
            stored_checksum = stored_image_data.get('checksum')
            
            if stored_checksum == current_image_checksum:
                self.images_logger.debug(f"Image unchanged for product {zoho_id}")
                return True  # Image hasn't changed
            
            # Download image
            local_path = self.download_product_image(image_url, zoho_id)
            if not local_path:
                return False
            
            # Upload to Odoo
            attachment_id = self.upload_image_to_odoo(local_path, odoo_product_id, zoho_id)
            
            if attachment_id:
                # Update tracking
                self.tracking_data['product_images'][zoho_id] = {
                    'image_url': image_url,
                    'local_path': local_path,
                    'odoo_attachment_id': attachment_id,
                    'checksum': current_image_checksum,
                    'last_sync': datetime.now().isoformat()
                }
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error syncing image for product {zoho_id}: {e}")
            return False
    
    def fetch_all_zoho_products(self) -> List[dict]:
        """Fetch all products from Zoho Books with pagination"""
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
                response.raise_for_status()
                
                data = response.json()
                items = data.get('items', [])
                
                if not items:
                    break
                
                all_products.extend(items)
                self.logger.info(f"   📄 Fetched page {page}: {len(items)} products")
                page += 1
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"❌ Error fetching Zoho page {page}: {e}")
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
                              'description', 'create_date', 'write_date', 'x_zoho_item_id', 'image_1920'],
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
        
        usd_to_iqd_rate = 1500  # Exchange rate
        
        # If price looks like USD (under 100), convert it
        if price < 100:
            return price * usd_to_iqd_rate
        
        return price
    
    def transform_zoho_to_odoo(self, zoho_product: dict) -> dict:
        """Transform Zoho product to Odoo format with robust error handling"""
        try:
            product_mapping = self.field_mapping['products']['zoho_books']
            default_values = self.field_mapping['products']['default_values']
            
            odoo_product = {}
            
            # Map fields with sanitization
            for zoho_field, odoo_field in product_mapping.items():
                if zoho_field in zoho_product and zoho_product[zoho_field] is not None:
                    value = zoho_product[zoho_field]
                    
                    # Special handling for different field types
                    if zoho_field in ['rate', 'purchase_rate']:
                        try:
                            price_value = float(value) if value else 0.0
                            converted_price = self.convert_usd_to_iqd(price_value)
                            odoo_product[odoo_field] = converted_price
                        except (ValueError, TypeError):
                            odoo_product[odoo_field] = 0.0
                    elif zoho_field in ['name', 'description']:
                        # Sanitize text fields
                        odoo_product[odoo_field] = self.sanitize_text(value)
                    else:
                        # For other fields, convert to string and sanitize if needed
                        if isinstance(value, str):
                            odoo_product[odoo_field] = self.sanitize_text(value)
                        else:
                            odoo_product[odoo_field] = value
            
            # Apply default values (always override)
            for field, value in default_values.items():
                odoo_product[field] = value
            
            # Ensure required fields
            if 'name' not in odoo_product or not odoo_product['name']:
                odoo_product['name'] = f"Product {zoho_product.get('item_id', 'Unknown')}"
            
            # Ensure name is not too long (Odoo has limits)
            if len(odoo_product['name']) > 100:
                odoo_product['name'] = odoo_product['name'][:97] + "..."
            
            # Remove problematic fields
            problematic_fields = ['item_type', 'product_type', 'category_id', 'category_name', 'group_id', 'group_name']
            for field in problematic_fields:
                odoo_product.pop(field, None)
            
            return odoo_product
            
        except Exception as e:
            self.logger.error(f"❌ Error transforming product {zoho_product.get('item_id')}: {e}")
            # Return minimal valid product data
            return {
                'name': self.sanitize_text(zoho_product.get('name', f"Product {zoho_product.get('item_id', 'Unknown')}")),
                'type': 'product',
                'sale_ok': True,
                'purchase_ok': True,
                'tracking': 'none',
                'list_price': 0.0,
                'standard_price': 0.0,
                'x_zoho_item_id': str(zoho_product.get('item_id', ''))
            }
    
    def find_odoo_product_by_zoho_id(self, zoho_id: str) -> Optional[dict]:
        """Find Odoo product by Zoho ID"""
        try:
            products = self.odoo_models.execute_kw(
                self.odoo_config['database'],
                self.odoo_uid,
                self.odoo_config['password'],
                'product.template',
                'search_read',
                [[('x_zoho_item_id', '=', zoho_id)]],
                {'fields': ['id', 'name', 'x_zoho_item_id', 'image_1920'], 'limit': 1}
            )
            
            return products[0] if products else None
            
        except Exception as e:
            self.logger.debug(f"Error finding product by Zoho ID {zoho_id}: {e}")
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
                self.changes_logger.info(f"CREATED: Product '{zoho_product.get('name')}' (Zoho ID: {zoho_product.get('item_id')}, Odoo ID: {product_id})")
                self.sync_stats['products_added'] += 1
                
                # Sync product image
                self.sync_product_image(zoho_product, product_id)
            
            return product_id
            
        except Exception as e:
            self.logger.error(f"❌ Error creating product '{zoho_product.get('name')}': {e}")
            return None
    
    def update_product_in_odoo(self, odoo_product_id: int, zoho_product: dict, conflicts: List[str] = None) -> bool:
        """Update existing product in Odoo"""
        try:
            odoo_product_data = self.transform_zoho_to_odoo(zoho_product)
            
            # Remove fields that shouldn't be updated
            update_fields = {k: v for k, v in odoo_product_data.items() 
                           if k not in ['x_zoho_item_id']}
            
            success = self.odoo_models.execute_kw(
                self.odoo_config['database'],
                self.odoo_uid,
                self.odoo_config['password'],
                'product.template',
                'write',
                [[odoo_product_id], update_fields]
            )
            
            if success:
                self.changes_logger.info(f"UPDATED: Product '{zoho_product.get('name')}' (Odoo ID: {odoo_product_id})")
                if conflicts:
                    self.conflict_logger.info(f"CONFLICT RESOLVED: Product ID {odoo_product_id} - Fields: {', '.join(conflicts)} - Overridden with Zoho data")
                    self.sync_stats['conflicts_resolved'] += 1
                self.sync_stats['products_updated'] += 1
                
                # Sync product image
                self.sync_product_image(zoho_product, odoo_product_id)
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error updating product ID {odoo_product_id}: {e}")
            return False
    
    def delete_product_in_odoo(self, odoo_product_id: int, product_name: str) -> bool:
        """Delete product from Odoo"""
        try:
            success = self.odoo_models.execute_kw(
                self.odoo_config['database'],
                self.odoo_uid,
                self.odoo_config['password'],
                'product.template',
                'unlink',
                [[odoo_product_id]]
            )
            
            if success:
                self.changes_logger.info(f"DELETED: Product '{product_name}' (Odoo ID: {odoo_product_id})")
                self.sync_stats['products_deleted'] += 1
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error deleting product ID {odoo_product_id}: {e}")
            return False
    
    def detect_conflicts(self, zoho_product: dict, odoo_product: dict) -> List[str]:
        """Detect conflicts between Zoho and Odoo product data"""
        conflicts = []
        
        # Check name
        if zoho_product.get('name') != odoo_product.get('name'):
            conflicts.append('name')
        
        # Check prices (convert for comparison)
        zoho_price = self.convert_usd_to_iqd(float(zoho_product.get('rate', 0)))
        odoo_price = float(odoo_product.get('list_price', 0))
        if abs(zoho_price - odoo_price) > 0.01:  # Allow small rounding differences
            conflicts.append('list_price')
        
        zoho_cost = self.convert_usd_to_iqd(float(zoho_product.get('purchase_rate', 0)))
        odoo_cost = float(odoo_product.get('standard_price', 0))
        if abs(zoho_cost - odoo_cost) > 0.01:
            conflicts.append('standard_price')
        
        # Check SKU
        if zoho_product.get('sku') != odoo_product.get('default_code'):
            conflicts.append('default_code')
        
        # Check description
        if zoho_product.get('description') != odoo_product.get('description'):
            conflicts.append('description')
        
        return conflicts
    
    def synchronize_products(self) -> Tuple[int, int, int, int]:
        """Main synchronization logic"""
        self.logger.info("🔄 Starting product synchronization with images...")
        
        try:
            # Fetch data from both systems
            zoho_products = self.fetch_all_zoho_products()
            odoo_products = self.fetch_all_odoo_products()
            
            if not zoho_products:
                self.logger.warning("⚠️ No products found in Zoho Books")
                return 0, 0, 0, 0
            
            # Create lookup dictionaries
            zoho_by_id = {str(p.get('item_id')): p for p in zoho_products}
            odoo_by_zoho_id = {}
            
            for odoo_product in odoo_products:
                zoho_id = odoo_product.get('x_zoho_item_id')
                if zoho_id:
                    odoo_by_zoho_id[str(zoho_id)] = odoo_product
            
            self.logger.info(f"📊 Product comparison:")
            self.logger.info(f"   Zoho products: {len(zoho_by_id)}")
            self.logger.info(f"   Odoo products with Zoho ID: {len(odoo_by_zoho_id)}")
            
            added_count = 0
            updated_count = 0
            deleted_count = 0
            error_count = 0
            
            # Process Zoho products (create/update in Odoo)
            for zoho_id, zoho_product in zoho_by_id.items():
                try:
                    product_name = zoho_product.get('name', 'Unknown')
                    current_checksum = self.calculate_product_checksum(zoho_product)
                    
                    # Check if product exists in Odoo
                    odoo_product = odoo_by_zoho_id.get(zoho_id)
                    
                    if odoo_product:
                        # Product exists - check for changes
                        stored_checksum = self.tracking_data['zoho_products'].get(zoho_id, {}).get('checksum')
                        
                        if stored_checksum != current_checksum:
                            # Product has changed - detect conflicts and update
                            conflicts = self.detect_conflicts(zoho_product, odoo_product)
                            
                            if self.update_product_in_odoo(odoo_product['id'], zoho_product, conflicts):
                                updated_count += 1
                            else:
                                error_count += 1
                        
                        # Update tracking
                        self.tracking_data['zoho_products'][zoho_id] = {
                            'checksum': current_checksum,
                            'last_modified': datetime.now().isoformat(),
                            'odoo_id': odoo_product['id'],
                            'last_sync': datetime.now().isoformat()
                        }
                    
                    else:
                        # Product doesn't exist - create it
                        product_id = self.create_product_in_odoo(zoho_product)
                        
                        if product_id:
                            added_count += 1
                            
                            # Update tracking
                            self.tracking_data['zoho_products'][zoho_id] = {
                                'checksum': current_checksum,
                                'last_modified': datetime.now().isoformat(),
                                'odoo_id': product_id,
                                'last_sync': datetime.now().isoformat()
                            }
                        else:
                            error_count += 1
                
                except Exception as e:
                    self.logger.error(f"❌ Error processing product {zoho_id}: {e}")
                    error_count += 1
                    continue
            
            # Handle deleted products (exist in Odoo but not in Zoho)
            for zoho_id, odoo_product in odoo_by_zoho_id.items():
                if zoho_id not in zoho_by_id:
                    # Product was deleted from Zoho
                    product_name = odoo_product.get('name', 'Unknown')
                    
                    if self.delete_product_in_odoo(odoo_product['id'], product_name):
                        deleted_count += 1
                        
                        # Remove from tracking
                        self.tracking_data['zoho_products'].pop(zoho_id, None)
                        self.tracking_data['product_images'].pop(zoho_id, None)
                        
                        # Add to deleted products log
                        self.tracking_data['deleted_products'].append({
                            'zoho_id': zoho_id,
                            'odoo_id': odoo_product['id'],
                            'product_name': product_name,
                            'deleted_at': datetime.now().isoformat()
                        })
                    else:
                        error_count += 1
            
            return added_count, updated_count, deleted_count, error_count
            
        except Exception as e:
            self.logger.error(f"❌ Synchronization failed: {e}")
            return 0, 0, 0, 1
    
    def run_sync_cycle(self):
        """Run a complete synchronization cycle"""
        sync_start_time = datetime.now()
        self.logger.info("🚀 Starting sync cycle with images...")
        
        try:
            # Perform synchronization
            added, updated, deleted, errors = self.synchronize_products()
            
            # Calculate duration
            sync_duration = (datetime.now() - sync_start_time).total_seconds()
            
            # Update statistics
            self.sync_stats.update({
                'total_syncs': self.sync_stats['total_syncs'] + 1,
                'last_sync_duration': sync_duration
            })
            
            if errors == 0:
                self.sync_stats['successful_syncs'] += 1
            else:
                self.sync_stats['failed_syncs'] += 1
            
            # Record sync history
            sync_record = {
                'timestamp': datetime.now().isoformat(),
                'duration': sync_duration,
                'products_added': added,
                'products_updated': updated,
                'products_deleted': deleted,
                'images_synced': self.sync_stats['images_synced'],
                'images_failed': self.sync_stats['images_failed'],
                'errors': errors,
                'conflicts_resolved': self.sync_stats['conflicts_resolved']
            }
            
            self.tracking_data['sync_history'].append(sync_record)
            
            # Keep only last 100 sync records
            if len(self.tracking_data['sync_history']) > 100:
                self.tracking_data['sync_history'] = self.tracking_data['sync_history'][-100:]
            
            # Save tracking data
            self.save_sync_tracking()
            
            # Log results
            self.logger.info(f"✅ Sync cycle completed:")
            self.logger.info(f"   ➕ Added: {added}")
            self.logger.info(f"   🔄 Updated: {updated}")
            self.logger.info(f"   🗑️ Deleted: {deleted}")
            self.logger.info(f"   🖼️ Images Synced: {self.sync_stats['images_synced']}")
            self.logger.info(f"   ❌ Errors: {errors}")
            self.logger.info(f"   ⏱️ Duration: {sync_duration:.1f}s")
            
            self.last_sync_time = datetime.now()
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Sync cycle failed: {e}")
            self.sync_stats['failed_syncs'] += 1
            return False
    
    def start_service(self):
        """Start the synchronization service"""
        if self.running:
            self.logger.warning("⚠️ Service is already running")
            return
        
        self.running = True
        self.logger.info(f"🚀 Starting Fixed Zoho-Odoo Sync Service with Images (interval: {self.sync_interval}s)")
        
        # Schedule synchronization
        schedule.every(self.sync_interval).seconds.do(self.run_sync_cycle)
        
        # Run initial sync
        self.run_sync_cycle()
        
        # Main service loop
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"❌ Error in service loop: {e}")
                time.sleep(10)
        
        self.logger.info("🛑 Sync service stopped")
    
    def stop_service(self):
        """Stop the synchronization service"""
        self.logger.info("🛑 Stopping Fixed Zoho-Odoo Sync Service...")
        self.running = False
    
    def get_service_status(self) -> dict:
        """Get current service status"""
        return {
            'running': self.running,
            'last_sync': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'sync_interval': self.sync_interval,
            'statistics': self.sync_stats.copy(),
            'uptime': (datetime.now() - datetime.fromisoformat(self.sync_stats['service_start_time'])).total_seconds()
        }


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
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
        sync_service = ZohoOdooSyncServiceWithImagesFixed()
        sync_service.start_service()
        
    except Exception as e:
        print(f"❌ Failed to start service: {e}")
        sys.exit(1)


if __name__ == "__main__":
    sync_service = None
    main() 