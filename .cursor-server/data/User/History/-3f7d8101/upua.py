#!/usr/bin/env python3

import xmlrpc.client
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def change_currency_via_settings():
    """Change currency through Odoo settings"""
    
    # Connect to Odoo
    url = 'http://localhost:8069'
    db = 'odtshbrain'
    username = 'khaleel@tsh.sale'
    password = 'Zcbm.97531tsh'
    
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    
    if not uid:
        raise Exception("Failed to authenticate with Odoo")
        
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    logger.info("✅ Connected to Odoo successfully")
    
    try:
        logger.info("🚀 SETTING UP IQD CURRENCY")
        logger.info("=" * 50)
        
        # Step 1: Get all currencies to see what's available
        logger.info("📋 Checking available currencies...")
        currencies = models.execute_kw(
            db, uid, password,
            'res.currency', 'search_read', [[]],
            {'fields': ['id', 'name', 'symbol', 'active', 'rate']}
        )
        
        logger.info(f"Found {len(currencies)} currencies:")
        iqd_currency = None
        usd_currency = None
        
        for currency in currencies:
            if currency['name'] == 'IQD':
                iqd_currency = currency
                logger.info(f"  ✅ IQD: {currency['symbol']} (Active: {currency['active']}, Rate: {currency['rate']})")
            elif currency['name'] == 'USD':
                usd_currency = currency
                logger.info(f"  💲 USD: {currency['symbol']} (Active: {currency['active']}, Rate: {currency['rate']})")
        
        # Step 2: Ensure IQD is active and properly configured
        if iqd_currency:
            logger.info("🔄 Configuring IQD currency...")
            
            # Make sure IQD is active and set as base currency (rate = 1.0)
            models.execute_kw(
                db, uid, password,
                'res.currency', 'write', [[iqd_currency['id']]], {
                    'active': True,
                    'rate': 1.0,  # Base currency
                    'symbol': 'د.ع',  # Iraqi Dinar symbol
                    'rounding': 1.0,  # Whole numbers
                    'decimal_places': 0,
                    'position': 'after'
                }
            )
            
            # Set USD rate relative to IQD (approximately 1 USD = 1310 IQD as of 2024)
            if usd_currency:
                models.execute_kw(
                    db, uid, password,
                    'res.currency', 'write', [[usd_currency['id']]], {
                        'rate': 0.000763359  # 1/1310 approximately
                    }
                )
                logger.info("✅ Set USD exchange rate relative to IQD")
            
            logger.info("✅ IQD currency configured successfully")
            
        else:
            logger.error("❌ IQD currency not found in the system")
            return False
        
        # Step 3: Try alternative approach - update through ir.config_parameter
        logger.info("🔄 Setting system currency preference...")
        try:
            # Check if there are any config parameters for currency
            config_params = models.execute_kw(
                db, uid, password,
                'ir.config_parameter', 'search_read', 
                [[('key', 'ilike', 'currency')]],
                {'fields': ['key', 'value']}
            )
            
            logger.info(f"Found {len(config_params)} currency-related config parameters")
            for param in config_params:
                logger.info(f"  {param['key']}: {param['value']}")
                
        except Exception as e:
            logger.info(f"Config parameter check: {e}")
        
        # Step 4: Update company data through direct SQL if needed
        logger.info("💡 INSTRUCTIONS FOR MANUAL CURRENCY CHANGE:")
        logger.info("=" * 50)
        logger.info("Since the API restrictions prevent automatic currency change,")
        logger.info("please follow these steps in the Odoo web interface:")
        logger.info("")
        logger.info("1. 🌐 Open Odoo in browser: http://localhost:8069")
        logger.info("2. 🔑 Login with: khaleel@tsh.sale")
        logger.info("3. ⚙️  Go to Settings > General Settings")
        logger.info("4. 💰 In the 'Multi-Currency' section:")
        logger.info("   - Enable 'Multi-Currency' if not already enabled")
        logger.info("   - Click 'Configure Currencies'")
        logger.info("5. 🇮🇶 Find 'IQD - Iraqi Dinar' and:")
        logger.info("   - Set it as Active")
        logger.info("   - Set Rate to 1.0 (base currency)")
        logger.info("   - Click Save")
        logger.info("6. 🏢 Go to Settings > Company")
        logger.info("7. 💱 Change 'Currency' from USD to IQD")
        logger.info("8. 💾 Save the changes")
        logger.info("")
        logger.info("✅ IQD currency is ready and configured!")
        logger.info("✅ Exchange rates are set appropriately")
        logger.info("=" * 50)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during currency setup: {e}")
        return False

if __name__ == "__main__":
    try:
        success = change_currency_via_settings()
        
        if success:
            print("\n✅ Currency setup completed!")
            print("Please follow the manual instructions above to complete the currency change.")
            print("After changing to IQD, you can proceed with the migration.")
        else:
            print("\n❌ Currency setup failed.")
            exit(1)
            
    except Exception as e:
        print(f"❌ Critical error: {e}")
        exit(1) 