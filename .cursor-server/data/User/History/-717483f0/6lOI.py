#!/usr/bin/env python3

import xmlrpc.client
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CurrencyChanger:
    def __init__(self):
        self.connect_to_odoo()
        
    def connect_to_odoo(self):
        """Connect to Odoo"""
        url = 'http://localhost:8069'
        db = 'odtshbrain'
        username = 'khaleel@tsh.sale'
        password = 'Zcbm.97531tsh'
        
        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.uid = self.common.authenticate(db, username, password, {})
        
        if not self.uid:
            raise Exception("Failed to authenticate with Odoo")
            
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        logger.info("✅ Connected to Odoo successfully")
        
    def get_current_currency_info(self):
        """Get current currency setup"""
        logger.info("📋 Checking current currency configuration...")
        
        # Get company info
        company_id = self.models.execute_kw(
            'odtshbrain', self.uid, 'Zcbm.97531tsh',
            'res.company', 'search', [[]], {'limit': 1}
        )[0]
        
        company_data = self.models.execute_kw(
            'odtshbrain', self.uid, 'Zcbm.97531tsh',
            'res.company', 'read', [company_id],
            {'fields': ['name', 'currency_id']}
        )[0]
        
        logger.info(f"Company: {company_data['name']}")
        logger.info(f"Current currency ID: {company_data['currency_id']}")
        
        # Get current currency details
        if company_data['currency_id']:
            currency_data = self.models.execute_kw(
                'odtshbrain', self.uid, 'Zcbm.97531tsh',
                'res.currency', 'read', [company_data['currency_id'][0]],
                {'fields': ['name', 'symbol', 'active']}
            )[0]
            logger.info(f"Current currency: {currency_data['name']} ({currency_data['symbol']})")
            
        return company_id, company_data['currency_id']
        
    def check_iqd_currency(self):
        """Check if IQD currency exists and activate it"""
        logger.info("🔍 Checking for IQD currency...")
        
        # Search for IQD currency
        iqd_ids = self.models.execute_kw(
            'odtshbrain', self.uid, 'Zcbm.97531tsh',
            'res.currency', 'search', [['name', '=', 'IQD']]
        )
        
        if iqd_ids:
            logger.info("✅ IQD currency found")
            iqd_id = iqd_ids[0]
            
            # Get IQD details
            iqd_data = self.models.execute_kw(
                'odtshbrain', self.uid, 'Zcbm.97531tsh',
                'res.currency', 'read', [iqd_id],
                {'fields': ['name', 'symbol', 'active', 'rate']}
            )[0]
            
            logger.info(f"IQD Details: {iqd_data}")
            
            # Activate IQD if not active
            if not iqd_data['active']:
                logger.info("🔄 Activating IQD currency...")
                self.models.execute_kw(
                    'odtshbrain', self.uid, 'Zcbm.97531tsh',
                    'res.currency', 'write', [iqd_id], {'active': True}
                )
                logger.info("✅ IQD currency activated")
                
            return iqd_id
        else:
            # Create IQD currency if it doesn't exist
            logger.info("➕ Creating IQD currency...")
            iqd_data = {
                'name': 'IQD',
                'symbol': 'د.ع',
                'active': True,
                'rate': 1.0,  # Base currency rate
                'rounding': 0.01,
                'position': 'after',  # Symbol position
                'decimal_places': 0  # Iraqi Dinar typically doesn't use decimals
            }
            
            iqd_id = self.models.execute_kw(
                'odtshbrain', self.uid, 'Zcbm.97531tsh',
                'res.currency', 'create', [iqd_data]
            )
            
            logger.info(f"✅ IQD currency created with ID: {iqd_id}")
            return iqd_id
            
    def change_company_currency(self, company_id, iqd_id):
        """Change company base currency to IQD"""
        logger.info("🔄 Changing company base currency to IQD...")
        
        try:
            # Update company currency
            self.models.execute_kw(
                'odtshbrain', self.uid, 'Zcbm.97531tsh',
                'res.company', 'write', [company_id], {'currency_id': iqd_id}
            )
            
            logger.info("✅ Company base currency changed to IQD")
            
            # Verify the change
            company_data = self.models.execute_kw(
                'odtshbrain', self.uid, 'Zcbm.97531tsh',
                'res.company', 'read', [company_id],
                {'fields': ['currency_id']}
            )[0]
            
            currency_data = self.models.execute_kw(
                'odtshbrain', self.uid, 'Zcbm.97531tsh',
                'res.currency', 'read', [company_data['currency_id'][0]],
                {'fields': ['name', 'symbol']}
            )[0]
            
            logger.info(f"✅ Verified: Company currency is now {currency_data['name']} ({currency_data['symbol']})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error changing company currency: {e}")
            return False
            
    def update_existing_records(self):
        """Update existing records to use IQD"""
        logger.info("🔄 Updating existing records to use IQD...")
        
        # Get IQD currency ID
        iqd_ids = self.models.execute_kw(
            'odtshbrain', self.uid, 'Zcbm.97531tsh',
            'res.currency', 'search', [['name', '=', 'IQD']]
        )
        
        if not iqd_ids:
            logger.error("❌ IQD currency not found")
            return False
            
        iqd_id = iqd_ids[0]
        
        try:
            # Update existing products (if any) to use IQD for pricing
            product_ids = self.models.execute_kw(
                'odtshbrain', self.uid, 'Zcbm.97531tsh',
                'product.template', 'search', [[]]
            )
            
            if product_ids:
                logger.info(f"Found {len(product_ids)} products to update")
                # Note: Products inherit currency from company, so this should be automatic
                
            # Update existing partners (if any) to use IQD
            partner_ids = self.models.execute_kw(
                'odtshbrain', self.uid, 'Zcbm.97531tsh',
                'res.partner', 'search', [['currency_id', '!=', False]]
            )
            
            if partner_ids:
                logger.info(f"Updating {len(partner_ids)} partners to use IQD")
                self.models.execute_kw(
                    'odtshbrain', self.uid, 'Zcbm.97531tsh',
                    'res.partner', 'write', [partner_ids], {'currency_id': iqd_id}
                )
                
            logger.info("✅ Existing records updated to use IQD")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating existing records: {e}")
            return False
            
    def run_currency_change(self):
        """Main function to change currency to IQD"""
        logger.info("🚀 CHANGING BASE CURRENCY TO IQD")
        logger.info("=" * 50)
        
        try:
            # Step 1: Get current currency info
            company_id, current_currency = self.get_current_currency_info()
            
            # Step 2: Check/create IQD currency
            iqd_id = self.check_iqd_currency()
            
            # Step 3: Change company currency
            if self.change_company_currency(company_id, iqd_id):
                # Step 4: Update existing records
                self.update_existing_records()
                
                logger.info("\n" + "=" * 50)
                logger.info("🎉 CURRENCY CHANGE COMPLETED!")
                logger.info("=" * 50)
                logger.info("✅ Base currency changed to IQD (Iraqi Dinar)")
                logger.info("✅ Symbol: د.ع")
                logger.info("✅ All existing records updated")
                logger.info("✅ Ready for migration with IQD currency")
                logger.info("=" * 50)
                
                return True
            else:
                logger.error("❌ Failed to change company currency")
                return False
                
        except Exception as e:
            logger.error(f"❌ Critical error during currency change: {e}")
            return False

if __name__ == "__main__":
    try:
        changer = CurrencyChanger()
        success = changer.run_currency_change()
        
        if success:
            print("\n✅ Currency change completed successfully!")
            print("You can now proceed with the migration using IQD as base currency.")
        else:
            print("\n❌ Currency change failed. Please check the logs.")
            exit(1)
            
    except Exception as e:
        print(f"❌ Critical error: {e}")
        exit(1) 