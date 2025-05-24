#!/usr/bin/env python3

import json
import xmlrpc.client

def safe_clean_import():
    """Safely archive existing products and prepare for clean Zoho import"""
    
    print("🧹 SAFE CLEAN IMPORT - Archive & Fresh Sync")
    print("=" * 60)
    print("This will:")
    print("✅ Archive all existing Odoo products (safe)")
    print("✅ Keep them for reference but hide from views")
    print("✅ Allow fresh import of all Zoho products")
    print("✅ Avoid foreign key constraint issues")
    print()
    
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

    # Check current status
    all_products = models.execute_kw(
        odoo_config['database'], uid, odoo_config['password'],
        'product.template', 'search_read', [[]],
        {'fields': ['id', 'name', 'active'], 'limit': 5}
    )
    
    total_products = len(models.execute_kw(
        odoo_config['database'], uid, odoo_config['password'],
        'product.template', 'search', [[]]
    ))
    
    active_products = len(models.execute_kw(
        odoo_config['database'], uid, odoo_config['password'],
        'product.template', 'search', [['&', ('active', '=', True), ('active', '!=', False)]]
    ))
    
    print(f"📊 Current Status:")
    print(f"   Total products: {total_products}")
    print(f"   Active products: {active_products}")
    print(f"   Sample products:")
    for product in all_products:
        status = "🟢 Active" if product.get('active', True) else "🔴 Archived"
        print(f"     ID {product['id']}: {product['name'][:50]}... ({status})")

    print(f"\n⚠️  WARNING: This will archive ALL {active_products} active products!")
    print("📝 Archived products will still exist but won't appear in normal views")
    print("🔄 You can reactivate them later if needed")
    
    confirm = input(f"\nType 'ARCHIVE' to confirm archiving {active_products} products: ").strip()
    
    if confirm != "ARCHIVE":
        print("❌ Operation cancelled")
        return False

    try:
        print(f"\n🗃️  Archiving all active products...")
        
        # Get all active product IDs
        active_product_ids = models.execute_kw(
            odoo_config['database'], uid, odoo_config['password'],
            'product.template', 'search', 
            [['&', ('active', '=', True), ('active', '!=', False)]]
        )
        
        if not active_product_ids:
            print("ℹ️  No active products found to archive")
            return True
        
        # Archive products in batches to avoid timeout
        batch_size = 100
        archived_count = 0
        
        for i in range(0, len(active_product_ids), batch_size):
            batch = active_product_ids[i:i+batch_size]
            
            try:
                models.execute_kw(
                    odoo_config['database'], uid, odoo_config['password'],
                    'product.template', 'write',
                    [batch, {'active': False}]
                )
                archived_count += len(batch)
                print(f"   📦 Archived batch {i//batch_size + 1}: {len(batch)} products (Total: {archived_count})")
                
            except Exception as e:
                print(f"   ❌ Error archiving batch {i//batch_size + 1}: {e}")
                continue
        
        # Verify archiving
        remaining_active = len(models.execute_kw(
            odoo_config['database'], uid, odoo_config['password'],
            'product.template', 'search', 
            [['&', ('active', '=', True), ('active', '!=', False)]]
        ))
        
        print(f"\n✅ Archiving completed!")
        print(f"   📦 Products archived: {archived_count}")
        print(f"   🟢 Active products remaining: {remaining_active}")
        
        if remaining_active == 0:
            print(f"\n🎉 SUCCESS! All products archived safely")
            print(f"📋 Next steps:")
            print(f"   1. Run: python3 sync_service_manager_fixed.py sync-once")
            print(f"   2. This will import all 2154 Zoho products fresh")
            print(f"   3. Each will get a unique Zoho ID")
            print(f"   4. You'll have exactly 2154 products matching Zoho")
            return True
        else:
            print(f"⚠️  Warning: {remaining_active} products couldn't be archived")
            print(f"💡 You can still proceed with sync - it will skip existing active products")
            return True
            
    except Exception as e:
        print(f"❌ Error during archiving: {e}")
        return False

if __name__ == "__main__":
    success = safe_clean_import()
    
    if success:
        print(f"\n🚀 Ready for clean import!")
        print(f"Run the sync command when ready:")
        print(f"   python3 sync_service_manager_fixed.py sync-once")
    else:
        print(f"\n❌ Clean import preparation failed")
        print(f"💡 You can try the product matching approach instead:") 