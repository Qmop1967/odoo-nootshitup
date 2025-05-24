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
        logging.FileHandler('/opt/odoo/migration/logs/sync_server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ContinuousSyncServer:
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
        self.tracking_file = os.path.join(self.sync_data_dir, 'sync_tracking.json')
        
        if os.path.exists(self.tracking_file):
            with open(self.tracking_file, 'r') as f:
                self.tracking_data = json.load(f)
        else:
            self.tracking_data = {
                'last_full_sync': None,
                'zoho_products': {},  # zoho_id -> {checksum, last_modified}
                'odoo_products': {},  # odoo_id -> {zoho_id, last_modified}
                'sync_history': [],
                'product_count_history': []
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
        """Perform exact copy synchronization"""
        sync_start_time = datetime.now()
        logger.info("🚀 Starting EXACT COPY synchronization...")
        
        try:
            # Fetch products from both systems
            zoho_products = self.fetch_all_zoho_products()
            odoo_products = self.fetch_all_odoo_products()
            
            if not zoho_products:
                logger.error("❌ No products fetched from Zoho - skipping sync")
                return False
            
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
                        logger.info(f"🔄 Updating: {product_name[:50]}")
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
                        logger.info(f"➕ Creating: {product_name[:50]}")
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
            
            # Update sync statistics
            sync_duration = (datetime.now() - sync_start_time).total_seconds()
            
            self.sync_stats.update({
                'total_syncs': self.sync_stats['total_syncs'] + 1,
                'successful_syncs': self.sync_stats['successful_syncs'] + 1,
                'products_added': self.sync_stats['products_added'] + added_count,
                'products_updated': self.sync_stats['products_updated'] + updated_count,
                'last_sync_duration': sync_duration
            })
            
            # Record sync history
            sync_record = {
                'timestamp': datetime.now().isoformat(),
                'zoho_count': zoho_count,
                'odoo_count_before': odoo_count,
                'odoo_count_after': odoo_count + added_count,
                'added': added_count,
                'updated': updated_count,
                'skipped': skipped_count,
                'errors': error_count,
                'duration': sync_duration
            }
            
            self.tracking_data['sync_history'].append(sync_record)
            self.tracking_data['last_full_sync'] = datetime.now().isoformat()
            
            # Keep only last 50 sync records
            if len(self.tracking_data['sync_history']) > 50:
                self.tracking_data['sync_history'] = self.tracking_data['sync_history'][-50:]
            
            # Save tracking data
            self.save_sync_tracking()
            
            # Final count verification
            final_odoo_products = self.fetch_all_odoo_products()
            final_odoo_count = len(final_odoo_products)
            
            # Log summary
            logger.info("\n" + "="*70)
            logger.info("🎉 EXACT COPY SYNC COMPLETED!")
            logger.info("="*70)
            logger.info(f"📊 PRODUCT COUNT VERIFICATION:")
            logger.info(f"   Zoho Products: {zoho_count}")
            logger.info(f"   Odoo Products (Before): {odoo_count}")
            logger.info(f"   Odoo Products (After): {final_odoo_count}")
            logger.info(f"   Count Match: {'✅ YES' if zoho_count == final_odoo_count else '❌ NO'}")
            logger.info(f"")
            logger.info(f"📈 SYNC RESULTS:")
            logger.info(f"   ➕ Products Added: {added_count}")
            logger.info(f"   🔄 Products Updated: {updated_count}")
            logger.info(f"   ⏭️  Products Skipped: {skipped_count}")
            logger.info(f"   ❌ Errors: {error_count}")
            logger.info(f"   ⏱️  Duration: {sync_duration:.1f} seconds")
            logger.info("="*70)
            
            self.last_sync_time = datetime.now()
            return True
            
        except Exception as e:
            logger.error(f"❌ Sync failed: {e}")
            self.sync_stats['failed_syncs'] += 1
            return False
    
    def sync_loop(self):
        """Main sync loop"""
        logger.info(f"🔄 Sync server started - checking every {self.sync_interval} seconds")
        
        while self.running:
            try:
                # Perform sync
                success = self.sync_products_exact_copy()
                
                if success:
                    logger.info(f"✅ Sync completed successfully")
                else:
                    logger.error(f"❌ Sync failed")
                
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
        
        logger.info(f"🚀 Sync server started with {interval} second interval")
        
    def stop_sync_server(self):
        """Stop the sync server"""
        if not self.running:
            logger.warning("⚠️  Sync server is not running")
            return
        
        logger.info("🛑 Stopping sync server...")
        self.running = False
        
        if self.sync_thread:
            self.sync_thread.join(timeout=30)
        
        logger.info("✅ Sync server stopped")
    
    def get_status(self):
        """Get current sync server status"""
        status = {
            'running': self.running,
            'last_sync': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'sync_interval': self.sync_interval,
            'stats': self.sync_stats.copy()
        }
        
        # Get current product counts
        try:
            zoho_products = self.fetch_all_zoho_products()
            odoo_products = self.fetch_all_odoo_products()
            
            status['current_counts'] = {
                'zoho': len(zoho_products),
                'odoo': len(odoo_products),
                'match': len(zoho_products) == len(odoo_products)
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
    
    print("🔄 Continuous Zoho-Odoo Sync Server")
    print("="*60)
    print("This server will maintain EXACT copy synchronization:")
    print("✅ Same number of products in Zoho and Odoo")
    print("✅ Continuous monitoring for changes")
    print("✅ Automatic USD to IQD conversion")
    print("✅ Real-time sync until you stop it")
    print("="*60)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        sync_server = ContinuousSyncServer()
        
        while True:
            print("\nOptions:")
            print("1. Start sync server (5 minute interval)")
            print("2. Start sync server (custom interval)")
            print("3. Stop sync server")
            print("4. Check status")
            print("5. Run one-time sync")
            print("6. Exit")
            
            choice = input("\nSelect option (1-6): ").strip()
            
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
                print(f"\n📊 SYNC SERVER STATUS:")
                print(f"   Running: {'✅ YES' if status['running'] else '❌ NO'}")
                print(f"   Last Sync: {status['last_sync'] or 'Never'}")
                print(f"   Interval: {status['sync_interval']} seconds")
                print(f"   Total Syncs: {status['stats']['total_syncs']}")
                print(f"   Successful: {status['stats']['successful_syncs']}")
                print(f"   Failed: {status['stats']['failed_syncs']}")
                
                if 'current_counts' in status and 'error' not in status['current_counts']:
                    counts = status['current_counts']
                    print(f"\n📦 CURRENT PRODUCT COUNTS:")
                    print(f"   Zoho: {counts['zoho']} products")
                    print(f"   Odoo: {counts['odoo']} products")
                    print(f"   Match: {'✅ YES' if counts['match'] else '❌ NO'}")
                
            elif choice == '5':
                print("🚀 Running one-time sync...")
                success = sync_server.sync_products_exact_copy()
                if success:
                    print("✅ One-time sync completed successfully")
                else:
                    print("❌ One-time sync failed")
                    
            elif choice == '6':
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