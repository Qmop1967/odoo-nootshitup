#!/usr/bin/env python3
"""
Quick Migration Test
===================
Test Odoo connection with new credentials and start migration.
"""

import odoorpc
import json

def test_odoo_connection():
    """Test connection to Odoo with new credentials"""
    
    try:
        print("🔗 Testing Odoo connection...")
        
        # Connect to Odoo
        odoo = odoorpc.ODOO('localhost', port=8069)
        odoo.login('odtshbrain', 'khaleel@tsh.sale', 'Zcbm.97531tsh')
        
        print("✅ Successfully connected to Odoo!")
        print(f"👤 User: {odoo.env.user.name}")
        print(f"🏢 Company: {odoo.env.user.company_id.name}")
        print(f"🗄️ Database: odtshbrain")
        
        # Test access to key models
        models_to_test = [
            'res.partner',     # Contacts
            'product.product', # Products  
            'account.move',    # Invoices/Bills
            'sale.order',      # Sales Orders
            'purchase.order'   # Purchase Orders
        ]
        
        print("\n🔍 Testing model access...")
        for model in models_to_test:
            try:
                count = odoo.env[model].search_count([])
                print(f"✅ {model}: {count} records accessible")
            except Exception as e:
                print(f"❌ {model}: Access denied - {str(e)[:50]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def main():
    """Main function"""
    
    print("🚀 QUICK MIGRATION TEST")
    print("=" * 50)
    
    if test_odoo_connection():
        print("\n✅ CONNECTION TEST PASSED!")
        print("🎯 Ready to proceed with full migration")
        return True
    else:
        print("\n❌ CONNECTION TEST FAILED!")
        print("⚠️ Please check credentials and Odoo service")
        return False

if __name__ == "__main__":
    main() 