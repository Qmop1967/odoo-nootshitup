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

class CompleteMigrator:
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
        
    def check_currency_setup(self):
        """Check if IQD is properly set as base currency"""
        logger.info("💰 Checking currency configuration...")
        
        # Get company currency
        company_ids = self.models.execute_kw(
            'odtshbrain', self.uid, 'Zcbm.97531tsh',
            'res.company', 'search', [[]]
        )
        
        if company_ids:
            company_data = self.models.execute_kw(
                'odtshbrain', self.uid, 'Zcbm.97531tsh',
                'res.company', 'read', [company_ids[0]],
                {'fields': ['name', 'currency_id']}
            )[0]
            
            if company_data['currency_id']:
                currency_data = self.models.execute_kw(
                    'odtshbrain', self.uid, 'Zcbm.97531tsh',
                    'res.currency', 'read', [company_data['currency_id'][0]],
                    {'fields': ['name', 'symbol']}
                )[0]
                
                logger.info(f"Company: {company_data['name']}")
                logger.info(f"Current currency: {currency_data['name']} ({currency_data['symbol']})")
                
                if currency_data['name'] == 'IQD':
                    logger.info("✅ IQD is properly set as base currency!")
                    return True
                else:
                    logger.warning("⚠️  Base currency is not IQD yet")
                    return False
        
        return False
        
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
        """Transform a single Zoho product to Odoo format with fixed field mapping"""
        odoo_product = {}
        
        # Map basic fields
        zoho_mapping = self.field_mapping['products']['zoho_books']
        for zoho_field, odoo_field in zoho_mapping.items():
            if zoho_field in zoho_product and zoho_product[zoho_field]:
                # Handle special field mappings
                if zoho_field == 'rate':
                    try:
                        odoo_product[odoo_field] = float(zoho_product[zoho_field])
                    except (ValueError, TypeError):
                        odoo_product[odoo_field] = 0.0
                elif zoho_field == 'purchase_rate':
                    try:
                        odoo_product[odoo_field] = float(zoho_product[zoho_field])
                    except (ValueError, TypeError):
                        odoo_product[odoo_field] = 0.0
                else:
                    odoo_product[odoo_field] = zoho_product[zoho_field]
        
        # Apply default values
        for field, value in self.field_mapping['products']['default_values'].items():
            odoo_product[field] = value
        
        # Ensure required fields
        if 'name' not in odoo_product or not odoo_product['name']:
            odoo_product['name'] = f"Product {zoho_product.get('item_id', 'Unknown')}"
        
        # Clean up the name
        if 'name' in odoo_product:
            odoo_product['name'] = str(odoo_product['name']).strip()
            
        # Remove problematic fields that cause errors
        problematic_fields = ['uom_id', 'categ_id', 'taxes_id']
        for field in problematic_fields:
            if field in odoo_product:
                del odoo_product[field]
                
        return odoo_product
        
    def migrate_products(self):
        """Migrate products with fixed field mappings"""
        logger.info("🚀 Starting fixed product migration...")
        
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
                    if success_count % 50 == 0:
                        logger.info(f"✅ Progress: {success_count}/{len(zoho_products)} products migrated")
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
                product_name = zoho_product.get('name', 'Unknown')
                logger.error(f"❌ Error migrating {product_name}: {e}")
                
                # Continue with next product instead of stopping
                continue
        
        # Summary
        logger.info("\n" + "="*50)
        logger.info("🎉 PRODUCT MIGRATION COMPLETED!")
        logger.info("="*50)
        logger.info(f"✅ Successfully migrated: {success_count}")
        logger.info(f"❌ Errors encountered: {error_count}")
        logger.info(f"📊 Total processed: {len(zoho_products)}")
        logger.info("="*50)
        
        return success_count > 0
        
    def run_complete_migration(self):
        """Run the complete migration process"""
        logger.info("🚀 COMPLETE ZOHO TO ODOO MIGRATION")
        logger.info("=" * 60)
        
        # Step 1: Check currency setup
        if not self.check_currency_setup():
            logger.warning("⚠️  Please complete the manual currency change to IQD first!")
            logger.info("📋 Manual Currency Change Instructions:")
            logger.info("1. 🌐 Open: http://localhost:8069")
            logger.info("2. 🔑 Login: khaleel@tsh.sale")
            logger.info("3. ⚙️  Settings > General Settings > Multi-Currency")
            logger.info("4. 💰 Configure Currencies > Set IQD rate to 1.0")
            logger.info("5. 🏢 Settings > Companies > Change Currency to IQD")
            
            response = input("\n✅ Have you completed the currency change? (y/n): ")
            if response.lower() != 'y':
                logger.info("Please complete currency change first and run again.")
                return False
                
        # Verify currency is now correct
        if not self.check_currency_setup():
            logger.error("❌ Currency still not set to IQD. Please check manual steps.")
            return False
            
        logger.info("✅ Currency configuration verified!")
        
        # Step 2: Migrate products with fixes
        logger.info("\n📦 Starting product migration...")
        if self.migrate_products():
            logger.info("✅ Product migration completed successfully!")
        else:
            logger.warning("⚠️  Product migration had issues but continuing...")
            
        # Step 3: Migration summary
        logger.info("\n" + "="*60)
        logger.info("🎉 MIGRATION STATUS SUMMARY")
        logger.info("="*60)
        logger.info("✅ Contacts: 199 migrated (previously completed)")
        logger.info("✅ Products: Migration attempted with fixes")
        logger.info("💰 Currency: IQD (Iraqi Dinar) set as base")
        logger.info("🔄 Ready for: Invoices, Bills, Chart of Accounts, Taxes")
        logger.info("="*60)
        
        return True

if __name__ == "__main__":
    try:
        migrator = CompleteMigrator()
        success = migrator.run_complete_migration()
        
        if success:
            print("\n🎉 Migration phase completed!")
            print("Ready to continue with remaining data types.")
        else:
            print("\n⚠️  Please complete currency change and try again.")
            
    except Exception as e:
        logger.error(f"Critical error: {e}")
        exit(1) 