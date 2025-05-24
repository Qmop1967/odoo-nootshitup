#!/usr/bin/env python3

import sys
import os
import logging
import json
import requests
import xmlrpc.client
import hashlib
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/odoo/migration/logs/active_pricelist_sync.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ActivePricelistSyncServer:
    def __init__(self):
        self.load_config()
        self.setup_directories()
        self.connect_to_odoo()
        self.usd_to_iqd_rate = 1500
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
        
        for directory in [self.sync_data_dir, self.logs_dir]:
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
                'zoho_products': {},
                'zoho_pricelists': {},
                'odoo_pricelists': {},
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
    
    def fetch_active_zoho_pricelists(self):
        """Fetch only ACTIVE price lists from Zoho Books"""
        logger.info("💰 Fetching ACTIVE price lists from Zoho Books...")
        
        access_token = self.get_zoho_access_token()
        if not access_token:
            return []
            
        headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
        
        try:
            params = {
                'organization_id': self.zoho_config['organization_id']
            }
            
            # Try different endpoints for price books/price lists
            endpoints = [
                f"{self.zoho_config['base_url']}/pricebooks",
                f"{self.zoho_config['base_url']}/pricelists"
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
                            break
                        
                except Exception as e:
                    logger.debug(f"Endpoint {endpoint} failed: {e}")
                    continue
            
            # Filter for ACTIVE price lists only
            active_pricelists = []
            for pricelist in all_pricelists:
                status = pricelist.get('status', '').lower()
                name = pricelist.get('name', 'Unknown')
                
                logger.info(f"📋 Found price list: '{name}' (status: {status})")
                
                # Check if price list is active
                if status == 'active':
                    active_pricelists.append(pricelist)
                    logger.info(f"   ✅ ACTIVE - Will sync")
                else:
                    logger.info(f"   ⏸️  INACTIVE - Skipping")
            
            logger.info(f"✅ Found {len(active_pricelists)} active price lists out of {len(all_pricelists)} total")
            return active_pricelists
            
        except Exception as e:
            logger.error(f"Error fetching Zoho price lists: {e}")
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
                    'applied_on': '1_product',  # Product variant
                    'compute_price': 'fixed',
                    'fixed_price': converted_rate,
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
                    
            except Exception as e:
                logger.error(f"Error creating pricelist item: {e}")
                continue
        
        return created_count
    
    def sync_active_pricelists_only(self):
        """Perform synchronization for ACTIVE price lists only"""
        logger.info("💰 Starting ACTIVE price list synchronization...")
        
        try:
            # Fetch ACTIVE price lists from Zoho and all from Odoo
            zoho_pricelists = self.fetch_active_zoho_pricelists()
            odoo_pricelists = self.fetch_all_odoo_pricelists()
            
            if not zoho_pricelists:
                logger.info("ℹ️  No active price lists found in Zoho - skipping sync")
                return 0, 0, 0
            
            # Count comparison
            zoho_count = len(zoho_pricelists)
            odoo_count = len(odoo_pricelists)
            
            logger.info(f"📊 Price List Count Comparison:")
            logger.info(f"   Zoho (ACTIVE): {zoho_count} price lists")
            logger.info(f"   Odoo: {odoo_count} price lists")
            
            # Track changes
            added_count = 0
            updated_count = 0
            items_added_count = 0
            
            # Process each active Zoho price list
            for i, zoho_pricelist in enumerate(zoho_pricelists, 1):
                try:
                    zoho_pricebook_id = str(zoho_pricelist.get('pricebook_id', ''))
                    pricelist_name = zoho_pricelist.get('name', 'Unknown')
                    
                    logger.info(f"💰 Processing ACTIVE price list: {pricelist_name}")
                    
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
                            logger.info(f"   ⏭️  No changes - skipping")
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
                    
                    # Update tracking for existing price lists
                    if zoho_pricebook_id in self.tracking_data['zoho_pricelists']:
                        self.tracking_data['zoho_pricelists'][zoho_pricebook_id]['checksum'] = current_checksum
                        self.tracking_data['zoho_pricelists'][zoho_pricebook_id]['last_modified'] = datetime.now().isoformat()
                    
                except Exception as e:
                    logger.error(f"❌ Error processing price list {pricelist_name}: {e}")
                    continue
            
            logger.info(f"✅ ACTIVE price list sync completed:")
            logger.info(f"   ➕ Added: {added_count}")
            logger.info(f"   🔄 Updated: {updated_count}")
            logger.info(f"   📝 Items Added: {items_added_count}")
            
            return added_count, updated_count, items_added_count
            
        except Exception as e:
            logger.error(f"❌ ACTIVE price list sync failed: {e}")
            return 0, 0, 0

def main():
    """Run ACTIVE price list sync only"""
    print("💰 ZOHO-ODOO ACTIVE PRICE LIST SYNC")
    print("=" * 55)
    print("This will sync ONLY ACTIVE price lists from Zoho to Odoo")
    print("✅ Filter: Only 'active' status price lists")
    print("✅ Price Lists: Exact copy with all pricing rules")
    print("✅ USD to IQD conversion: Automatic")
    print("=" * 55)
    
    try:
        # Create sync server instance
        sync_server = ActivePricelistSyncServer()
        
        logger.info("🚀 Starting ACTIVE price list synchronization...")
        start_time = datetime.now()
        
        # Run ACTIVE price list sync only
        added, updated, items_added = sync_server.sync_active_pricelists_only()
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        
        # Get final counts for verification
        zoho_pricelists = sync_server.fetch_active_zoho_pricelists()
        odoo_pricelists = sync_server.fetch_all_odoo_pricelists()
        
        zoho_count = len(zoho_pricelists)
        odoo_count = len(odoo_pricelists)
        
        # Save tracking data
        sync_server.save_sync_tracking()
        
        # Print summary
        print("\n" + "="*70)
        print("🎉 ACTIVE PRICE LIST SYNC COMPLETED!")
        print("="*70)
        print(f"💰 ACTIVE PRICE LIST SYNCHRONIZATION RESULTS:")
        print(f"   Zoho Active Price Lists: {zoho_count}")
        print(f"   Odoo Price Lists: {odoo_count}")
        print(f"   ➕ Price Lists Added: {added}")
        print(f"   🔄 Price Lists Updated: {updated}")
        print(f"   📝 Price List Items Added: {items_added}")
        print(f"")
        print(f"⏱️  PERFORMANCE:")
        print(f"   Total Duration: {duration:.1f} seconds")
        print(f"   Average per Price List: {(duration/max(zoho_count, 1)):.2f} seconds")
        print("="*70)
        
        logger.info("✅ ACTIVE price list sync completed successfully!")
        return True
            
    except Exception as e:
        logger.error(f"❌ ACTIVE price list sync failed: {e}")
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 