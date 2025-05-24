#!/usr/bin/env python3

import xmlrpc.client
import json
import time

def get_odoo_product_count():
    """Get current product count in Odoo"""
    try:
        with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
            config = json.load(f)

        odoo_config = config['odoo']['test_db']
        url = f"http://{odoo_config['host']}:{odoo_config['port']}"

        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(odoo_config['database'], odoo_config['username'], odoo_config['password'], {})

        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        count = models.execute_kw(
            odoo_config['database'], 
            uid, 
            odoo_config['password'], 
            'product.template', 
            'search_count', 
            [[]]
        )
        return count
    except Exception as e:
        print(f"Error getting count: {e}")
        return 0

def main():
    print("📊 Monitoring sync progress...")
    print("Target: 2154 products from Zoho Books")
    print("Press Ctrl+C to stop monitoring\n")
    
    previous_count = 0
    
    while True:
        try:
            current_count = get_odoo_product_count()
            
            if current_count != previous_count:
                progress = (current_count / 2154) * 100
                print(f"📦 Odoo products: {current_count}/2154 ({progress:.1f}%) - Added: {current_count - previous_count}")
                previous_count = current_count
            
            if current_count >= 2154:
                print("🎉 Sync completed! All products synced.")
                break
                
            time.sleep(10)  # Check every 10 seconds
            
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main() 