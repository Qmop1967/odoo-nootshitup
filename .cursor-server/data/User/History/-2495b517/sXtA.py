#!/usr/bin/env python3

import json
import requests
import xmlrpc.client
import logging
import time
import threading
import signal
import sys
from datetime import datetime, timedelta
import hashlib
import os
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/odoo/migration/logs/sync_server_enhanced.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class EnhancedContinuousSyncServer:
    def __init__(self):
        self.running = False
        self.sync_thread = None
        self.sync_interval = 300  # 5 minutes default
        self.last_sync_time = None
        self.sync_stats = {
            'total_syncs': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'products_added': 0,
            'products_updated': 0,
            'products_deleted': 0,
            'pricelists_added': 0,
            'pricelists_updated': 0,
            'pricelist_items_added': 0,
            'pricelist_items_updated': 0,
            'last_sync_duration': 0
        }
        
        # Load configuration and connect
        self.load_config()
        self.setup_directories()
        self.connect_to_odoo()
        self.usd_to_iqd_rate = 1500
        
        # Tracking data
        self.load_sync_tracking()
        
    def load_config(self):
        """Load configuration"""
        with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
            self.config = json.load(f)
        
        with open('/opt/odoo/migration/config/field_mapping.json', 'r') as f:
            self.field_mapping = json.load(f)
        
        self.zoho_config = self.config['zoho_books']
        self.odoo_db_config = self.config['odoo']['test_db']
        
    def setup_directories(self):
        """Setup required directories"""
        self.sync_data_dir = '/opt/odoo/migration/data/sync_server'
        self.logs_dir = '/opt/odoo/migration/logs'
        self.images_dir = '/opt/odoo/migration/data/product_images'
        
        for directory in [self.sync_data_dir, self.logs_dir, self.images_dir]:
            Path(directory).mkdir(parents=True, exist_ok=True)
            
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
        
    def load_sync_tracking(self):
        """Load sync tracking data"""
        self.tracking_file = os.path.join(self.sync_data_dir, 'sync_tracking_enhanced.json')
        
        if os.path.exists(self.tracking_file):
            with open(self.tracking_file, 'r') as f:
                self.tracking_data = json.load(f)
        else:
            self.tracking_data = {
                'last_full_sync': None,
                'zoho_products': {},  # zoho_id -> {checksum, last_modified, odoo_id}
                'zoho_pricelists': {},  # zoho_pricebook_id -> {checksum, last_modified, odoo_id}
                'zoho_pricelist_items': {},  # zoho_pricebook_item_id -> {checksum, last_modified, odoo_id}
                'odoo_products': {},  # odoo_id -> {zoho_id, last_modified}
                'odoo_pricelists': {},  # odoo_id -> {zoho_id, last_modified}
                'sync_history': [],
                'product_count_history': [],
                'pricelist_count_history': []
            }
    
    def save_sync_tracking(self):
        """Save sync tracking data"""
        with open(self.tracking_file, 'w') as f:
            json.dump(self.tracking_data, f, indent=2)
    
    def get_zoho_access_token(self):
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
            logger.error(f"❌ Error getting Zoho token: {e}")
            return None
    
    def fetch_all_zoho_products(self):
        """Fetch all products from Zoho Books"""
        logger.info("📦 Fetching all products from Zoho Books...")
        
        access_token = self.get_zoho_access_token()
        if not access_token:
            return []
            
        headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
        all_products = []
        page = 1
        per_page = 200  # Max per page
        
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
                    logger.warning(f"Failed to fetch Zoho page {page}: {response.status_code}")
                    break
                    
                data = response.json()
                items = data.get('items', [])
                
                if not items:
                    break
                    
                all_products.extend(items)
                logger.info(f"   📄 Fetched page {page}: {len(items)} products")
                page += 1
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error fetching Zoho page {page}: {e}")
                break
        
        logger.info(f"✅ Total products from Zoho: {len(all_products)}")
        return all_products
    
    def fetch_all_zoho_pricelists(self):
        """Fetch all price lists from Zoho Books"""
        logger.info("💰 Fetching all price lists from Zoho Books...")
        
        access_token = self.get_zoho_access_token()
        if not access_token:
            return []
            
        headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
        
        try:
            params = {
                'organization_id': self.zoho_config['organization_id']
            }
            
            # Note: Zoho Books uses different endpoint structure than Zoho Inventory
            # We'll try both endpoints to be compatible
            endpoints = [
                f"{self.zoho_config['base_url']}/pricebooks",  # Primary endpoint
                f"{self.zoho_config['base_url']}/pricelists"   # Alternative endpoint
            ]
            
            all_pricelists = []
            
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, headers=headers, params=params, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        pricelists = data.get('pricebooks', data.get('pricelists', []))
                        if pricelists:
                            all_pricelists = pricelists
                            logger.info(f"✅ Fetched {len(all_pricelists)} price lists from Zoho")
                            break
                        
                except Exception as e:
                    logger.debug(f"Endpoint {endpoint} failed: {e}")
                    continue
            
            if not all_pricelists:
                logger.warning("⚠️ No price lists found or accessible in Zoho Books")
                
            return all_pricelists
            
        except Exception as e:
            logger.error(f"Error fetching Zoho price lists: {e}")
            return []
    
    def fetch_all_odoo_products(self):
        """Fetch all products from Odoo"""
        logger.info("📦 Fetching all products from Odoo...")
        
        try:
            products = self.models.execute_kw(
                self.odoo_db_config['database'], 
                self.uid, 
                self.odoo_db_config['password'],
                'product.template', 
                'search_read', 
                [[]],
                {
                    'fields': ['id', 'name', 'list_price', 'standard_price', 'default_code', 
                              'create_date', 'write_date'],
                    'order': 'id'
                }
            )
            
            logger.info(f"✅ Total products from Odoo: {len(products)}")
            return products
            
        except Exception as e:
            logger.error(f"❌ Error fetching Odoo products: {e}")
            return []
    
    def fetch_all_odoo_pricelists(self):
        """Fetch all price lists from Odoo"""
        logger.info("💰 Fetching all price lists from Odoo...")
        
        try:
            pricelists = self.models.execute_kw(
                self.odoo_db_config['database'], 
                self.uid, 
                self.odoo_db_config['password'],
                'product.pricelist', 
                'search_read', 
                [[]],
                {
                    'fields': ['id', 'name', 'active', 'currency_id', 'item_ids'],
                    'order': 'id'
                }
            )
            
            logger.info(f"✅ Total price lists from Odoo: {len(pricelists)}")
            return pricelists
            
        except Exception as e:
            logger.error(f"❌ Error fetching Odoo price lists: {e}")
            return []
    
    def calculate_pricelist_checksum(self, zoho_pricelist):
        """Calculate checksum for Zoho price list"""
        relevant_fields = ['name', 'description', 'pricebook_type', 'is_increase', 'percentage', 'status']
        data_string = ""
        
        for field in relevant_fields:
            value = zoho_pricelist.get(field, '')
            data_string += str(value)
        
        # Include pricebook items in checksum
        items = zoho_pricelist.get('pricebook_items', [])
        for item in items:
            data_string += str(item.get('item_id', '')) + str(item.get('pricebook_rate', ''))
        
        return hashlib.md5(data_string.encode()).hexdigest()
    
    def calculate_product_checksum(self, zoho_product):
        """Calculate checksum for Zoho product"""
        relevant_fields = ['name', 'rate', 'purchase_rate', 'description', 'sku', 'unit', 'status']
        data_string = ""
        
        for field in relevant_fields:
            value = zoho_product.get(field, '')
            data_string += str(value)
        
        return hashlib.md5(data_string.encode()).hexdigest()
    
    def convert_usd_to_iqd(self, price):
        """Convert USD price to IQD"""
        if not price or price <= 0:
            return 0.0
        
        # If price looks like USD (under 100), convert it
        if price < 100:
            return price * self.usd_to_iqd_rate
        
        return price
    
    def transform_zoho_pricelist_to_odoo(self, zoho_pricelist):
        """Transform Zoho price list to Odoo format"""
        pricelist_mapping = self.field_mapping['price_lists']['zoho_books']
        default_values = self.field_mapping['price_lists']['default_values']
        
        odoo_pricelist = {}
        
        # Map basic fields
        for zoho_field, odoo_field in pricelist_mapping.items():
            if zoho_field in zoho_pricelist and zoho_pricelist[zoho_field] is not None:
                value = zoho_pricelist[zoho_field]
                
                # Special handling for different field types
                if zoho_field == 'pricebook_id':
                    odoo_pricelist[odoo_field] = str(value)
                elif zoho_field in ['is_increase', 'status']:
                    if zoho_field == 'status':
                        odoo_pricelist['active'] = (value == 'active')
                    else:
                        odoo_pricelist[odoo_field] = value
                else:
                    odoo_pricelist[odoo_field] = value
        
        # Apply default values
        for field, value in default_values.items():
            if field not in odoo_pricelist:
                odoo_pricelist[field] = value
        
        # Ensure required fields
        if 'name' not in odoo_pricelist or not odoo_pricelist['name']:
            pricebook_id = zoho_pricelist.get('pricebook_id', 'Unknown')
            odoo_pricelist['name'] = f"Price List {pricebook_id}"
        
        return odoo_pricelist
    
    def create_pricelist_items(self, odoo_pricelist_id, zoho_pricebook_items):
        """Create price list items in Odoo"""
        items_mapping = self.field_mapping['price_lists']['pricebook_items']
        created_count = 0
        
        for zoho_item in zoho_pricebook_items:
            try:
                # Find corresponding Odoo product
                zoho_item_id = zoho_item.get('item_id')
                if not zoho_item_id:
                    continue
                
                # Look up Odoo product by Zoho item ID
                odoo_product_id = None
                if zoho_item_id in self.tracking_data['zoho_products']:
                    odoo_product_id = self.tracking_data['zoho_products'][zoho_item_id].get('odoo_id')
                
                if not odoo_product_id:
                    logger.warning(f"Could not find Odoo product for Zoho item {zoho_item_id}")
                    continue
                
                # Create pricelist item
                pricebook_rate = float(zoho_item.get('pricebook_rate', 0))
                converted_rate = self.convert_usd_to_iqd(pricebook_rate)
                
                pricelist_item_data = {
                    'pricelist_id': odoo_pricelist_id,
                    'product_tmpl_id': odoo_product_id,
                    'fixed_price': converted_rate,
                    'applied_on': '1_product',  # Apply on product
                    'compute_price': 'fixed',   # Fixed price
                    'min_quantity': 1,
                    'zoho_pricebook_item_id': str(zoho_item.get('pricebook_item_id', ''))
                }
                
                item_id = self.models.execute_kw(
                    self.odoo_db_config['database'], 
                    self.uid, 
                    self.odoo_db_config['password'],
                    'product.pricelist.item', 
                    'create', 
                    [pricelist_item_data]
                )
                
                if item_id:
                    created_count += 1
                    
                    # Track the item
                    zoho_pricebook_item_id = str(zoho_item.get('pricebook_item_id', ''))
                    if zoho_pricebook_item_id:
                        self.tracking_data['zoho_pricelist_items'][zoho_pricebook_item_id] = {
                            'odoo_id': item_id,
                            'checksum': hashlib.md5(str(converted_rate).encode()).hexdigest(),
                            'last_modified': datetime.now().isoformat()
                        }
                
            except Exception as e:
                logger.error(f"Error creating pricelist item: {e}")
                continue
        
        return created_count
    
    def sync_pricelists_exact_copy(self):
        """Perform exact copy synchronization for price lists"""
        logger.info("💰 Starting price list synchronization...")
        
        try:
            # Fetch price lists from both systems
            zoho_pricelists = self.fetch_all_zoho_pricelists()
            odoo_pricelists = self.fetch_all_odoo_pricelists()
            
            if not zoho_pricelists:
                logger.info("ℹ️  No price lists found in Zoho - skipping price list sync")
                return 0, 0, 0
            
            # Count comparison
            zoho_count = len(zoho_pricelists)
            odoo_count = len(odoo_pricelists)
            
            logger.info(f"📊 Price List Count Comparison:")
            logger.info(f"   Zoho: {zoho_count} price lists")
            logger.info(f"   Odoo: {odoo_count} price lists")
            
            # Track changes
            added_count = 0
            updated_count = 0
            items_added_count = 0
            
            # Process each Zoho price list
            for i, zoho_pricelist in enumerate(zoho_pricelists, 1):
                try:
                    zoho_pricebook_id = str(zoho_pricelist.get('pricebook_id', ''))
                    pricelist_name = zoho_pricelist.get('name', 'Unknown')
                    
                    logger.info(f"💰 Processing price list: {pricelist_name}")
                    
                    # Calculate checksum
                    current_checksum = self.calculate_pricelist_checksum(zoho_pricelist)
                    
                    # Check if price list exists in Odoo
                    existing_odoo_pricelist = None
                    if zoho_pricebook_id in self.tracking_data['zoho_pricelists']:
                        odoo_id = self.tracking_data['zoho_pricelists'][zoho_pricebook_id].get('odoo_id')
                        if odoo_id:
                            try:
                                pricelists = self.models.execute_kw(
                                    self.odoo_db_config['database'], 
                                    self.uid, 
                                    self.odoo_db_config['password'],
                                    'product.pricelist', 
                                    'search_read', 
                                    [[('id', '=', odoo_id)]],
                                    {'fields': ['id', 'name'], 'limit': 1}
                                )
                                if pricelists:
                                    existing_odoo_pricelist = pricelists[0]
                            except Exception:
                                pass
                    
                    if existing_odoo_pricelist:
                        # Check if price list has changed
                        stored_checksum = self.tracking_data['zoho_pricelists'].get(zoho_pricebook_id, {}).get('checksum')
                        
                        if stored_checksum == current_checksum:
                            continue
                        
                        # Update existing price list
                        logger.info(f"🔄 Updating price list: {pricelist_name}")
                        odoo_pricelist_data = self.transform_zoho_pricelist_to_odoo(zoho_pricelist)
                        
                        self.models.execute_kw(
                            self.odoo_db_config['database'], 
                            self.uid, 
                            self.odoo_db_config['password'],
                            'product.pricelist', 
                            'write', 
                            [[existing_odoo_pricelist['id']], odoo_pricelist_data]
                        )
                        
                        updated_count += 1
                        
                        # Update pricelist items if needed
                        zoho_items = zoho_pricelist.get('pricebook_items', [])
                        if zoho_items:
                            # Remove existing items
                            existing_items = self.models.execute_kw(
                                self.odoo_db_config['database'], 
                                self.uid, 
                                self.odoo_db_config['password'],
                                'product.pricelist.item', 
                                'search', 
                                [[('pricelist_id', '=', existing_odoo_pricelist['id'])]]
                            )
                            
                            if existing_items:
                                self.models.execute_kw(
                                    self.odoo_db_config['database'], 
                                    self.uid, 
                                    self.odoo_db_config['password'],
                                    'product.pricelist.item', 
                                    'unlink', 
                                    [existing_items]
                                )
                            
                            # Create new items
                            items_count = self.create_pricelist_items(existing_odoo_pricelist['id'], zoho_items)
                            items_added_count += items_count
                        
                    else:
                        # Create new price list
                        logger.info(f"➕ Creating price list: {pricelist_name}")
                        odoo_pricelist_data = self.transform_zoho_pricelist_to_odoo(zoho_pricelist)
                        
                        pricelist_id = self.models.execute_kw(
                            self.odoo_db_config['database'], 
                            self.uid, 
                            self.odoo_db_config['password'],
                            'product.pricelist', 
                            'create', 
                            [odoo_pricelist_data]
                        )
                        
                        if pricelist_id:
                            added_count += 1
                            
                            # Update tracking
                            self.tracking_data['zoho_pricelists'][zoho_pricebook_id] = {
                                'odoo_id': pricelist_id,
                                'checksum': current_checksum,
                                'last_modified': datetime.now().isoformat()
                            }
                            
                            # Create pricelist items
                            zoho_items = zoho_pricelist.get('pricebook_items', [])
                            if zoho_items:
                                items_count = self.create_pricelist_items(pricelist_id, zoho_items)
                                items_added_count += items_count
                    
                    # Update tracking for existing price lists
                    if zoho_pricebook_id in self.tracking_data['zoho_pricelists']:
                        self.tracking_data['zoho_pricelists'][zoho_pricebook_id]['checksum'] = current_checksum
                        self.tracking_data['zoho_pricelists'][zoho_pricebook_id]['last_modified'] = datetime.now().isoformat()
                    
                except Exception as e:
                    logger.error(f"❌ Error processing price list {pricelist_name}: {e}")
                    continue
            
            logger.info(f"✅ Price list sync completed:")
            logger.info(f"   ➕ Added: {added_count}")
            logger.info(f"   🔄 Updated: {updated_count}")
            logger.info(f"   📝 Items Added: {items_added_count}")
            
            return added_count, updated_count, items_added_count
            
        except Exception as e:
            logger.error(f"❌ Price list sync failed: {e}")
            return 0, 0, 0
    
    def transform_zoho_to_odoo(self, zoho_product):
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
        
        # Clean problematic fields
        problematic_fields = ['categ_id', 'taxes_id', 'property_account_expense_id', 'property_account_income_id']
        for field in problematic_fields:
            odoo_product.pop(field, None)
                
        return odoo_product
    
    def find_odoo_product_by_zoho_id(self, zoho_id):
        """Find Odoo product by Zoho ID"""
        if zoho_id in self.tracking_data['zoho_products']:
            odoo_id = self.tracking_data['zoho_products'][zoho_id].get('odoo_id')
            if odoo_id:
                try:
                    products = self.models.execute_kw(
                        self.odoo_db_config['database'], 
                        self.uid, 
                        self.odoo_db_config['password'],
                        'product.template', 
                        'search_read', 
                        [[('id', '=', odoo_id)]],
                        {'fields': ['id', 'name', 'default_code'], 'limit': 1}
                    )
                    if products:
                        return products[0]
                except Exception:
                    pass
        
        return None
    
    def sync_products_exact_copy(self):
        """Perform exact copy synchronization for products"""
        logger.info("🚀 Starting product synchronization...")
        
        try:
            # Fetch products from both systems
            zoho_products = self.fetch_all_zoho_products()
            odoo_products = self.fetch_all_odoo_products()
            
            if not zoho_products:
                logger.error("❌ No products fetched from Zoho - skipping sync")
                return 0, 0, 0
            
            # Count comparison
            zoho_count = len(zoho_products)
            odoo_count = len(odoo_products)
            
            logger.info(f"📊 Product Count Comparison:")
            logger.info(f"   Zoho: {zoho_count} products")
            logger.info(f"   Odoo: {odoo_count} products")
            logger.info(f"   Difference: {zoho_count - odoo_count}")
            
            # Track changes
            added_count = 0
            updated_count = 0
            skipped_count = 0
            error_count = 0
            
            # Process each Zoho product
            for i, zoho_product in enumerate(zoho_products, 1):
                try:
                    zoho_id = zoho_product.get('item_id')
                    product_name = zoho_product.get('name', 'Unknown')
                    
                    if i % 100 == 0:
                        logger.info(f"📊 Progress: {i}/{zoho_count} products processed")
                    
                    # Calculate checksum
                    current_checksum = self.calculate_product_checksum(zoho_product)
                    
                    # Check if product exists in Odoo
                    existing_odoo_product = self.find_odoo_product_by_zoho_id(zoho_id)
                    
                    if existing_odoo_product:
                        # Check if product has changed
                        stored_checksum = self.tracking_data['zoho_products'].get(zoho_id, {}).get('checksum')
                        
                        if stored_checksum == current_checksum:
                            skipped_count += 1
                            continue
                        
                        # Update existing product
                        logger.debug(f"🔄 Updating: {product_name[:50]}")
                        odoo_product_data = self.transform_zoho_to_odoo(zoho_product)
                        
                        # Remove fields that shouldn't be updated
                        update_fields = {k: v for k, v in odoo_product_data.items() 
                                       if k not in ['default_code']}
                        
                        self.models.execute_kw(
                            self.odoo_db_config['database'], 
                            self.uid, 
                            self.odoo_db_config['password'],
                            'product.template', 
                            'write', 
                            [[existing_odoo_product['id']], update_fields]
                        )
                        
                        updated_count += 1
                        
                    else:
                        # Create new product
                        logger.debug(f"➕ Creating: {product_name[:50]}")
                        odoo_product_data = self.transform_zoho_to_odoo(zoho_product)
                        
                        product_id = self.models.execute_kw(
                            self.odoo_db_config['database'], 
                            self.uid, 
                            self.odoo_db_config['password'],
                            'product.template', 
                            'create', 
                            [odoo_product_data]
                        )
                        
                        if product_id:
                            added_count += 1
                            
                            # Update tracking
                            if zoho_id not in self.tracking_data['zoho_products']:
                                self.tracking_data['zoho_products'][zoho_id] = {}
                            
                            self.tracking_data['zoho_products'][zoho_id].update({
                                'odoo_id': product_id,
                                'checksum': current_checksum,
                                'last_modified': datetime.now().isoformat()
                            })
                        else:
                            error_count += 1
                    
                    # Update tracking for existing products
                    if zoho_id in self.tracking_data['zoho_products']:
                        self.tracking_data['zoho_products'][zoho_id]['checksum'] = current_checksum
                        self.tracking_data['zoho_products'][zoho_id]['last_modified'] = datetime.now().isoformat()
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f"❌ Error processing {product_name}: {e}")
                    continue
            
            logger.info(f"✅ Product sync results:")
            logger.info(f"   ➕ Added: {added_count}")
            logger.info(f"   🔄 Updated: {updated_count}")
            logger.info(f"   ⏭️  Skipped: {skipped_count}")
            logger.info(f"   ❌ Errors: {error_count}")
            
            return added_count, updated_count, error_count
            
        except Exception as e:
            logger.error(f"❌ Product sync failed: {e}")
            return 0, 0, 1
    
    def sync_complete_exact_copy(self):
        """Perform complete exact copy synchronization (products + price lists)"""
        sync_start_time = datetime.now()
        logger.info("🚀 Starting COMPLETE EXACT COPY synchronization (Products + Price Lists)...")
        
        try:
            # 1. Sync Products First
            product_added, product_updated, product_errors = self.sync_products_exact_copy()
            
            # 2. Sync Price Lists
            pricelist_added, pricelist_updated, pricelist_items_added = self.sync_pricelists_exact_copy()
            
            # Update sync statistics
            sync_duration = (datetime.now() - sync_start_time).total_seconds()
            
            self.sync_stats.update({
                'total_syncs': self.sync_stats['total_syncs'] + 1,
                'successful_syncs': self.sync_stats['successful_syncs'] + 1,
                'products_added': self.sync_stats['products_added'] + product_added,
                'products_updated': self.sync_stats['products_updated'] + product_updated,
                'pricelists_added': self.sync_stats['pricelists_added'] + pricelist_added,
                'pricelists_updated': self.sync_stats['pricelists_updated'] + pricelist_updated,
                'pricelist_items_added': self.sync_stats['pricelist_items_added'] + pricelist_items_added,
                'last_sync_duration': sync_duration
            })
            
            # Get final counts
            final_zoho_products = self.fetch_all_zoho_products()
            final_odoo_products = self.fetch_all_odoo_products()
            final_zoho_pricelists = self.fetch_all_zoho_pricelists()
            final_odoo_pricelists = self.fetch_all_odoo_pricelists()
            
            zoho_product_count = len(final_zoho_products)
            odoo_product_count = len(final_odoo_products)
            zoho_pricelist_count = len(final_zoho_pricelists)
            odoo_pricelist_count = len(final_odoo_pricelists)
            
            # Record sync history
            sync_record = {
                'timestamp': datetime.now().isoformat(),
                'zoho_product_count': zoho_product_count,
                'odoo_product_count': odoo_product_count,
                'zoho_pricelist_count': zoho_pricelist_count,
                'odoo_pricelist_count': odoo_pricelist_count,
                'products_added': product_added,
                'products_updated': product_updated,
                'products_errors': product_errors,
                'pricelists_added': pricelist_added,
                'pricelists_updated': pricelist_updated,
                'pricelist_items_added': pricelist_items_added,
                'duration': sync_duration
            }
            
            self.tracking_data['sync_history'].append(sync_record)
            self.tracking_data['last_full_sync'] = datetime.now().isoformat()
            
            # Keep only last 50 sync records
            if len(self.tracking_data['sync_history']) > 50:
                self.tracking_data['sync_history'] = self.tracking_data['sync_history'][-50:]
            
            # Save tracking data
            self.save_sync_tracking()
            
            # Log summary
            logger.info("\n" + "="*80)
            logger.info("🎉 COMPLETE EXACT COPY SYNC COMPLETED!")
            logger.info("="*80)
            logger.info(f"📦 PRODUCT SYNCHRONIZATION:")
            logger.info(f"   Zoho Products: {zoho_product_count}")
            logger.info(f"   Odoo Products: {odoo_product_count}")
            logger.info(f"   Products Match: {'✅ YES' if zoho_product_count == odoo_product_count else '❌ NO'}")
            logger.info(f"   ➕ Products Added: {product_added}")
            logger.info(f"   🔄 Products Updated: {product_updated}")
            logger.info(f"   ❌ Product Errors: {product_errors}")
            logger.info(f"")
            logger.info(f"💰 PRICE LIST SYNCHRONIZATION:")
            logger.info(f"   Zoho Price Lists: {zoho_pricelist_count}")
            logger.info(f"   Odoo Price Lists: {odoo_pricelist_count}")
            logger.info(f"   Price Lists Match: {'✅ YES' if zoho_pricelist_count == odoo_pricelist_count else '❌ NO'}")
            logger.info(f"   ➕ Price Lists Added: {pricelist_added}")
            logger.info(f"   🔄 Price Lists Updated: {pricelist_updated}")
            logger.info(f"   📝 Price List Items Added: {pricelist_items_added}")
            logger.info(f"")
            logger.info(f"⏱️  PERFORMANCE:")
            logger.info(f"   Total Duration: {sync_duration:.1f} seconds")
            logger.info(f"   Success Rate: {((product_added + product_updated) / (product_added + product_updated + product_errors) * 100) if (product_added + product_updated + product_errors) > 0 else 100:.1f}%")
            logger.info("="*80)
            
            self.last_sync_time = datetime.now()
            return True
            
        except Exception as e:
            logger.error(f"❌ Complete sync failed: {e}")
            self.sync_stats['failed_syncs'] += 1
            return False
    
    def sync_loop(self):
        """Main sync loop"""
        logger.info(f"🔄 Enhanced sync server started - checking every {self.sync_interval} seconds")
        
        while self.running:
            try:
                # Perform complete sync (products + price lists)
                success = self.sync_complete_exact_copy()
                
                if success:
                    logger.info(f"✅ Complete sync completed successfully")
                else:
                    logger.error(f"❌ Complete sync failed")
                
                # Wait for next sync
                logger.info(f"⏰ Next sync in {self.sync_interval} seconds...")
                
                # Sleep with interrupt check
                sleep_remaining = self.sync_interval
                while sleep_remaining > 0 and self.running:
                    time.sleep(min(30, sleep_remaining))  # Check every 30 seconds
                    sleep_remaining -= 30
                    
            except Exception as e:
                logger.error(f"❌ Error in sync loop: {e}")
                time.sleep(60)  # Wait 1 minute on error
    
    def start_sync_server(self, interval=300):
        """Start the continuous sync server"""
        if self.running:
            logger.warning("⚠️  Sync server is already running")
            return
        
        self.sync_interval = interval
        self.running = True
        
        # Start sync thread
        self.sync_thread = threading.Thread(target=self.sync_loop, daemon=True)
        self.sync_thread.start()
        
        logger.info(f"🚀 Enhanced sync server started with {interval} second interval")
        
    def stop_sync_server(self):
        """Stop the sync server"""
        if not self.running:
            logger.warning("⚠️  Sync server is not running")
            return
        
        logger.info("🛑 Stopping enhanced sync server...")
        self.running = False
        
        if self.sync_thread:
            self.sync_thread.join(timeout=30)
        
        logger.info("✅ Enhanced sync server stopped")
    
    def get_status(self):
        """Get current sync server status"""
        status = {
            'running': self.running,
            'last_sync': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'sync_interval': self.sync_interval,
            'stats': self.sync_stats.copy()
        }
        
        # Get current counts
        try:
            zoho_products = self.fetch_all_zoho_products()
            odoo_products = self.fetch_all_odoo_products()
            zoho_pricelists = self.fetch_all_zoho_pricelists()
            odoo_pricelists = self.fetch_all_odoo_pricelists()
            
            status['current_counts'] = {
                'zoho_products': len(zoho_products),
                'odoo_products': len(odoo_products),
                'zoho_pricelists': len(zoho_pricelists),
                'odoo_pricelists': len(odoo_pricelists),
                'products_match': len(zoho_products) == len(odoo_products),
                'pricelists_match': len(zoho_pricelists) == len(odoo_pricelists)
            }
        except Exception as e:
            status['current_counts'] = {'error': str(e)}
        
        return status

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("🛑 Received shutdown signal")
    global sync_server
    if sync_server:
        sync_server.stop_sync_server()
    sys.exit(0)

def main():
    global sync_server
    
    print("🔄 Enhanced Continuous Zoho-Odoo Sync Server")
    print("="*70)
    print("This server synchronizes PRODUCTS + PRICE LISTS:")
    print("✅ Products: Same number in Zoho and Odoo")
    print("✅ Price Lists: Exact copy with all pricing rules")
    print("✅ Price List Items: Individual product pricing")
    print("✅ USD to IQD conversion: Automatic")
    print("✅ Real-time sync until you stop it")
    print("="*70)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        sync_server = EnhancedContinuousSyncServer()
        
        while True:
            print("\nOptions:")
            print("1. Start enhanced sync server (5 minute interval)")
            print("2. Start enhanced sync server (custom interval)")
            print("3. Stop sync server")
            print("4. Check status")
            print("5. Run one-time complete sync")
            print("6. Run products only sync")
            print("7. Run price lists only sync")
            print("8. Exit")
            
            choice = input("\nSelect option (1-8): ").strip()
            
            if choice == '1':
                sync_server.start_sync_server(300)  # 5 minutes
                
            elif choice == '2':
                try:
                    interval = int(input("Enter interval in seconds (min 60): "))
                    if interval < 60:
                        print("❌ Minimum interval is 60 seconds")
                        continue
                    sync_server.start_sync_server(interval)
                except ValueError:
                    print("❌ Invalid interval")
                    
            elif choice == '3':
                sync_server.stop_sync_server()
                
            elif choice == '4':
                status = sync_server.get_status()
                print(f"\n📊 ENHANCED SYNC SERVER STATUS:")
                print(f"   Running: {'✅ YES' if status['running'] else '❌ NO'}")
                print(f"   Last Sync: {status['last_sync'] or 'Never'}")
                print(f"   Interval: {status['sync_interval']} seconds")
                print(f"\n📈 SYNC STATISTICS:")
                print(f"   Total Syncs: {status['stats']['total_syncs']}")
                print(f"   Successful: {status['stats']['successful_syncs']}")
                print(f"   Failed: {status['stats']['failed_syncs']}")
                print(f"   Products Added: {status['stats']['products_added']}")
                print(f"   Products Updated: {status['stats']['products_updated']}")
                print(f"   Price Lists Added: {status['stats']['pricelists_added']}")
                print(f"   Price Lists Updated: {status['stats']['pricelists_updated']}")
                print(f"   Price List Items Added: {status['stats']['pricelist_items_added']}")
                
                if 'current_counts' in status and 'error' not in status['current_counts']:
                    counts = status['current_counts']
                    print(f"\n📦 CURRENT COUNTS:")
                    print(f"   Zoho Products: {counts['zoho_products']}")
                    print(f"   Odoo Products: {counts['odoo_products']}")
                    print(f"   Products Match: {'✅ YES' if counts['products_match'] else '❌ NO'}")
                    print(f"   Zoho Price Lists: {counts['zoho_pricelists']}")
                    print(f"   Odoo Price Lists: {counts['odoo_pricelists']}")
                    print(f"   Price Lists Match: {'✅ YES' if counts['pricelists_match'] else '❌ NO'}")
                
            elif choice == '5':
                print("🚀 Running one-time complete sync (products + price lists)...")
                success = sync_server.sync_complete_exact_copy()
                if success:
                    print("✅ One-time complete sync completed successfully")
                else:
                    print("❌ One-time complete sync failed")
                    
            elif choice == '6':
                print("📦 Running products only sync...")
                added, updated, errors = sync_server.sync_products_exact_copy()
                print(f"✅ Products sync completed: {added} added, {updated} updated, {errors} errors")
                
            elif choice == '7':
                print("💰 Running price lists only sync...")
                added, updated, items = sync_server.sync_pricelists_exact_copy()
                print(f"✅ Price lists sync completed: {added} added, {updated} updated, {items} items")
                    
            elif choice == '8':
                sync_server.stop_sync_server()
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid option")
                
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    sync_server = None
    main() 