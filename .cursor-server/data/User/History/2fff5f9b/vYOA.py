#!/usr/bin/env python3

import xmlrpc.client
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutomatedPriceFixer:
    def __init__(self):
        self.load_config()
        self.connect_to_odoo()
        self.usd_to_iqd_rate = 1500  # 1 USD = 1500 IQD
        
    def load_config(self):
        """Load configuration"""
        with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
            self.config = json.load(f)
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
    
    def fix_usd_prices_automated(self):
        """Automatically convert USD prices to IQD"""
        logger.info("💰 Starting automated USD to IQD price conversion...")
        
        # Get products with suspicious prices (likely USD)
        products = self.models.execute_kw(
            self.odoo_db_config['database'], 
            self.uid, 
            self.odoo_db_config['password'],
            'product.template', 
            'search_read', 
            [['|', 
              '&', ('list_price', '>', 0), ('list_price', '<', 100),
              '&', ('standard_price', '>', 0), ('standard_price', '<', 100)
            ]],
            {
                'fields': ['id', 'name', 'list_price', 'standard_price'],
                'order': 'id desc'
            }
        )
        
        logger.info(f"📊 Found {len(products)} products with USD prices")
        
        converted_count = 0
        
        for i, product in enumerate(products, 1):
            list_price = product.get('list_price', 0)
            standard_price = product.get('standard_price', 0)
            
            new_list_price = list_price
            new_standard_price = standard_price
            needs_conversion = False
            
            # Convert list price if it looks like USD
            if list_price > 0 and list_price < 100:
                new_list_price = list_price * self.usd_to_iqd_rate
                needs_conversion = True
                
            # Convert standard price if it looks like USD
            if standard_price > 0 and standard_price < 100:
                new_standard_price = standard_price * self.usd_to_iqd_rate
                needs_conversion = True
            
            if needs_conversion:
                logger.info(f"[{i}/{len(products)}] Converting: {product['name'][:50]}")
                logger.info(f"   List: ${list_price} → {new_list_price:,.0f} IQD")
                logger.info(f"   Cost: ${standard_price} → {new_standard_price:,.0f} IQD")
                
                try:
                    self.models.execute_kw(
                        self.odoo_db_config['database'], 
                        self.uid, 
                        self.odoo_db_config['password'],
                        'product.template', 
                        'write', 
                        [[product['id']], {
                            'list_price': new_list_price,
                            'standard_price': new_standard_price
                        }]
                    )
                    converted_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error updating {product['name']}: {e}")
        
        logger.info(f"✅ Price conversion complete: {converted_count} products converted")
        return converted_count
    
    def create_backup_report(self):
        """Create a backup report of the changes"""
        logger.info("📄 Creating conversion report...")
        
        report_file = f"/opt/odoo/migration/data/price_conversion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Get current product prices
        products = self.models.execute_kw(
            self.odoo_db_config['database'], 
            self.uid, 
            self.odoo_db_config['password'],
            'product.template', 
            'search_read', 
            [[]],
            {
                'fields': ['id', 'name', 'list_price', 'standard_price'],
                'limit': 100  # Sample for report
            }
        )
        
        report_data = {
            'conversion_date': datetime.now().isoformat(),
            'conversion_rate': self.usd_to_iqd_rate,
            'sample_products': products,
            'total_products_in_system': len(products)
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"📄 Report saved to: {report_file}")

def main():
    print("🚀 Automated USD to IQD Price Converter")
    print("=" * 60)
    print("This script will automatically convert all USD prices to IQD")
    print("by multiplying by 1500 (conversion rate: 1 USD = 1500 IQD)")
    print("=" * 60)
    
    try:
        fixer = AutomatedPriceFixer()
        
        # Create backup report before changes
        fixer.create_backup_report()
        
        # Fix prices
        converted = fixer.fix_usd_prices_automated()
        
        print(f"\n✅ Conversion completed!")
        print(f"💰 {converted} products converted from USD to IQD")
        print("📄 Backup report created in data/ directory")
        
    except Exception as e:
        logger.error(f"❌ Error during price conversion: {e}")
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    main() 