#!/usr/bin/env python3

import json
import xmlrpc.client

def delete_standard_delivery_product():
    """Delete the Standard delivery product that's causing validation errors"""
    
    print("🗑️ DELETING STANDARD DELIVERY PRODUCT")
    print("=" * 50)
    
    # Load config
    with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
        config = json.load(f)

    odoo_config = config['odoo']['test_db']
    url = f"http://{odoo_config['host']}:{odoo_config['port']}"

    # Connect to Odoo
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(odoo_config['database'], odoo_config['username'], odoo_config['password'], {})
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    print("✅ Connected to Odoo")

    try:
        # Search for "Standard delivery" products
        delivery_products = models.execute_kw(
            odoo_config['database'], uid, odoo_config['password'],
            'product.template', 'search_read',
            [[('name', 'ilike', 'Standard delivery')]],
            {'fields': ['id', 'name', 'active', 'default_code']}
        )
        
        print(f"🔍 Found {len(delivery_products)} 'Standard delivery' products:")
        
        for product in delivery_products:
            status = "🟢 Active" if product.get('active', True) else "🔴 Archived"
            print(f"   ID {product['id']}: {product['name']} ({status})")
            print(f"      Reference: {product.get('default_code', 'None')}")
        
        if not delivery_products:
            print("ℹ️  No 'Standard delivery' products found")
            return True
        
        # Also check for any products with reference "Delivery_007"
        delivery_007_products = models.execute_kw(
            odoo_config['database'], uid, odoo_config['password'],
            'product.template', 'search_read',
            [[('default_code', '=', 'Delivery_007')]],
            {'fields': ['id', 'name', 'active', 'default_code']}
        )
        
        if delivery_007_products:
            print(f"\n🔍 Found {len(delivery_007_products)} products with reference 'Delivery_007':")
            for product in delivery_007_products:
                status = "🟢 Active" if product.get('active', True) else "🔴 Archived"
                print(f"   ID {product['id']}: {product['name']} ({status})")
                delivery_products.extend(delivery_007_products)
        
        # Remove duplicates
        unique_products = {}
        for product in delivery_products:
            unique_products[product['id']] = product
        delivery_products = list(unique_products.values())
        
        print(f"\n⚠️  Found {len(delivery_products)} delivery products to handle")
        print("Options:")
        print("1. 🗑️  DELETE all delivery products (risky)")
        print("2. 🗃️  ARCHIVE all delivery products (safe)")
        print("3. ❌ Cancel")
        
        choice = input("\nSelect option (1, 2, or 3): ").strip()
        
        if choice == "1":
            print(f"\n⚠️  WARNING: This will DELETE {len(delivery_products)} delivery products!")
            confirm = input("Type 'DELETE' to confirm: ").strip()
            
            if confirm == "DELETE":
                deleted_count = 0
                failed_count = 0
                
                for product in delivery_products:
                    try:
                        models.execute_kw(
                            odoo_config['database'], uid, odoo_config['password'],
                            'product.template', 'unlink', [[product['id']]]
                        )
                        print(f"   ✅ Deleted: {product['name']} (ID: {product['id']})")
                        deleted_count += 1
                        
                    except Exception as e:
                        print(f"   ❌ Failed to delete {product['name']} (ID: {product['id']}): {e}")
                        failed_count += 1
                
                print(f"\n📊 Results:")
                print(f"   ✅ Deleted: {deleted_count}")
                print(f"   ❌ Failed: {failed_count}")
                
                if failed_count > 0:
                    print(f"\n💡 Some products couldn't be deleted due to constraints.")
                    print(f"   Try archiving them instead (option 2)")
                
            else:
                print("❌ Delete operation cancelled")
                
        elif choice == "2":
            print(f"\n🗃️  Archiving {len(delivery_products)} delivery products...")
            
            archived_count = 0
            failed_count = 0
            
            for product in delivery_products:
                try:
                    models.execute_kw(
                        odoo_config['database'], uid, odoo_config['password'],
                        'product.template', 'write',
                        [[product['id']], {'active': False}]
                    )
                    print(f"   ✅ Archived: {product['name']} (ID: {product['id']})")
                    archived_count += 1
                    
                except Exception as e:
                    print(f"   ❌ Failed to archive {product['name']} (ID: {product['id']}): {e}")
                    failed_count += 1
            
            print(f"\n📊 Results:")
            print(f"   ✅ Archived: {archived_count}")
            print(f"   ❌ Failed: {failed_count}")
            
        else:
            print("❌ Operation cancelled")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = delete_standard_delivery_product()
    
    if success:
        print(f"\n✅ Operation completed!")
        print(f"💡 You can now try running the sync again:")
        print(f"   python3 sync_service_manager_fixed.py sync-once")
    else:
        print(f"\n❌ Operation failed") 