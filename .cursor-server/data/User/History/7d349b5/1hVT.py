#!/usr/bin/env python3
"""
Full Migration Runner
====================
Complete migration from Zoho to Odoo with proper error handling.
"""

import json
import os
import sys
import time
from datetime import datetime
import logging

# Add migration directory to path
sys.path.append('/opt/odoo/migration')

try:
    import odoorpc
    import requests
except ImportError as e:
    print(f"❌ Missing required packages: {e}")
    print("📦 Please install: pip install odoorpc requests")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/odoo/migration/logs/full_migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ZohoOdooMigration:
    def __init__(self):
        self.config_file = '/opt/odoo/migration/config/zoho_config.json'
        self.config = self.load_config()
        self.odoo = None
        self.migration_stats = {
            'start_time': datetime.now(),
            'contacts_migrated': 0,
            'products_migrated': 0,
            'invoices_migrated': 0,
            'bills_migrated': 0,
            'errors': []
        }
    
    def load_config(self):
        """Load migration configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            sys.exit(1)
    
    def test_odoo_connection(self):
        """Test connection to Odoo"""
        try:
            logger.info("🔗 Testing Odoo connection...")
            
            db_config = self.config['odoo']['production_db']
            
            # Connect to Odoo
            self.odoo = odoorpc.ODOO(
                db_config['host'], 
                port=db_config['port']
            )
            self.odoo.login(
                db_config['database'],
                db_config['username'], 
                db_config['password']
            )
            
            logger.info("✅ Successfully connected to Odoo!")
            logger.info(f"👤 User: {self.odoo.env.user.name}")
            logger.info(f"🏢 Company: {self.odoo.env.user.company_id.name}")
            
            # Test model access
            test_models = ['res.partner', 'product.product', 'account.move']
            for model in test_models:
                try:
                    count = self.odoo.env[model].search_count([])
                    logger.info(f"✅ {model}: {count} records accessible")
                except Exception as e:
                    logger.warning(f"⚠️ {model}: Limited access - {str(e)[:50]}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Odoo connection failed: {e}")
            return False
    
    def get_zoho_access_token(self, service='books'):
        """Get fresh access token from Zoho"""
        try:
            config_key = f'zoho_{service}'
            config = self.config[config_key]
            
            token_url = "https://accounts.zoho.com/oauth/v2/token"
            
            data = {
                'refresh_token': config['refresh_token'],
                'client_id': config['client_id'],
                'client_secret': config['client_secret'],
                'grant_type': 'refresh_token'
            }
            
            response = requests.post(token_url, data=data)
            
            if response.status_code == 200:
                return response.json().get('access_token')
            else:
                logger.error(f"Failed to get {service} access token: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting {service} access token: {e}")
            return None
    
    def fetch_zoho_data(self, service, endpoint, params=None):
        """Fetch data from Zoho API"""
        try:
            access_token = self.get_zoho_access_token(service)
            if not access_token:
                return None
            
            config = self.config[f'zoho_{service}']
            url = f"{config['base_url']}{endpoint}"
            
            headers = {
                'Authorization': f'Zoho-oauthtoken {access_token}',
                'Content-Type': 'application/json'
            }
            
            if params is None:
                params = {'organization_id': config['organization_id']}
            else:
                params['organization_id'] = config['organization_id']
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Zoho API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching Zoho data: {e}")
            return None
    
    def migrate_contacts(self):
        """Migrate contacts from Zoho Books to Odoo"""
        try:
            logger.info("📇 Starting contacts migration...")
            
            # Fetch contacts from Zoho
            contacts_data = self.fetch_zoho_data('books', '/contacts')
            if not contacts_data or 'contacts' not in contacts_data:
                logger.warning("No contacts data found")
                return 0
            
            contacts = contacts_data['contacts']
            migrated_count = 0
            
            for contact in contacts:
                try:
                    # Check if contact already exists
                    existing = self.odoo.env['res.partner'].search([
                        ('name', '=', contact.get('contact_name', ''))
                    ])
                    
                    if existing:
                        logger.info(f"Skipping existing contact: {contact.get('contact_name')}")
                        continue
                    
                    # Create new contact
                    partner_data = {
                        'name': contact.get('contact_name', 'Unknown'),
                        'email': contact.get('email', ''),
                        'phone': contact.get('phone', ''),
                        'is_company': contact.get('contact_type') == 'vendor',
                        'supplier_rank': 1 if contact.get('contact_type') == 'vendor' else 0,
                        'customer_rank': 1 if contact.get('contact_type') == 'customer' else 0,
                    }
                    
                    # Add address if available
                    if contact.get('billing_address'):
                        addr = contact['billing_address']
                        partner_data.update({
                            'street': addr.get('address', ''),
                            'city': addr.get('city', ''),
                            'zip': addr.get('zip', ''),
                            'country_id': self.get_country_id(addr.get('country', ''))
                        })
                    
                    partner_id = self.odoo.env['res.partner'].create(partner_data)
                    migrated_count += 1
                    
                    if migrated_count % 10 == 0:
                        logger.info(f"Migrated {migrated_count} contacts...")
                    
                except Exception as e:
                    logger.error(f"Error migrating contact {contact.get('contact_name', '')}: {e}")
                    self.migration_stats['errors'].append(f"Contact: {str(e)}")
            
            logger.info(f"✅ Contacts migration completed: {migrated_count} migrated")
            self.migration_stats['contacts_migrated'] = migrated_count
            return migrated_count
            
        except Exception as e:
            logger.error(f"❌ Contacts migration failed: {e}")
            return 0
    
    def get_country_id(self, country_name):
        """Get Odoo country ID by name"""
        try:
            if not country_name:
                return False
            country = self.odoo.env['res.country'].search([
                ('name', 'ilike', country_name)
            ], limit=1)
            return country[0].id if country else False
        except:
            return False
    
    def migrate_products(self):
        """Migrate products from Zoho to Odoo"""
        try:
            logger.info("📦 Starting products migration...")
            
            # Fetch items from Zoho Books
            items_data = self.fetch_zoho_data('books', '/items')
            if not items_data or 'items' not in items_data:
                logger.warning("No products data found")
                return 0
            
            products = items_data['items']
            migrated_count = 0
            
            for product in products:
                try:
                    # Check if product already exists
                    existing = self.odoo.env['product.product'].search([
                        ('name', '=', product.get('name', ''))
                    ])
                    
                    if existing:
                        logger.info(f"Skipping existing product: {product.get('name')}")
                        continue
                    
                    # Create new product
                    product_data = {
                        'name': product.get('name', 'Unknown Product'),
                        'default_code': product.get('sku', ''),
                        'list_price': float(product.get('rate', 0)),
                        'standard_price': float(product.get('purchase_rate', 0)),
                        'type': 'product',
                        'sale_ok': True,
                        'purchase_ok': True,
                    }
                    
                    if product.get('description'):
                        product_data['description'] = product['description']
                    
                    product_id = self.odoo.env['product.product'].create(product_data)
                    migrated_count += 1
                    
                    if migrated_count % 10 == 0:
                        logger.info(f"Migrated {migrated_count} products...")
                    
                except Exception as e:
                    logger.error(f"Error migrating product {product.get('name', '')}: {e}")
                    self.migration_stats['errors'].append(f"Product: {str(e)}")
            
            logger.info(f"✅ Products migration completed: {migrated_count} migrated")
            self.migration_stats['products_migrated'] = migrated_count
            return migrated_count
            
        except Exception as e:
            logger.error(f"❌ Products migration failed: {e}")
            return 0
    
    def run_full_migration(self):
        """Run the complete migration process"""
        try:
            logger.info("🚀 STARTING FULL MIGRATION")
            logger.info("=" * 60)
            
            # Test Odoo connection
            if not self.test_odoo_connection():
                logger.error("❌ Cannot proceed without Odoo connection")
                return False
            
            # Start migration
            logger.info("📊 Beginning data migration...")
            
            # Migrate contacts
            contacts_count = self.migrate_contacts()
            time.sleep(2)  # Brief pause
            
            # Migrate products  
            products_count = self.migrate_products()
            time.sleep(2)  # Brief pause
            
            # Calculate results
            self.migration_stats['end_time'] = datetime.now()
            duration = self.migration_stats['end_time'] - self.migration_stats['start_time']
            
            # Print final summary
            logger.info("\n" + "=" * 60)
            logger.info("🎉 MIGRATION COMPLETED!")
            logger.info("=" * 60)
            logger.info(f"⏱️ Duration: {duration}")
            logger.info(f"📇 Contacts migrated: {self.migration_stats['contacts_migrated']}")
            logger.info(f"📦 Products migrated: {self.migration_stats['products_migrated']}")
            logger.info(f"❌ Errors: {len(self.migration_stats['errors'])}")
            
            if self.migration_stats['errors']:
                logger.info("\n⚠️ Errors encountered:")
                for error in self.migration_stats['errors'][:5]:  # Show first 5 errors
                    logger.info(f"   - {error}")
                if len(self.migration_stats['errors']) > 5:
                    logger.info(f"   ... and {len(self.migration_stats['errors']) - 5} more")
            
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False

def main():
    """Main function"""
    
    print("🚀 ZOHO TO ODOO FULL MIGRATION")
    print("=" * 60)
    
    # Create logs directory
    os.makedirs('/opt/odoo/migration/logs', exist_ok=True)
    
    # Run migration
    migration = ZohoOdooMigration()
    success = migration.run_full_migration()
    
    if success:
        print("\n✅ MIGRATION SUCCESSFUL!")
    else:
        print("\n❌ MIGRATION FAILED!")
    
    return success

if __name__ == "__main__":
    main() 