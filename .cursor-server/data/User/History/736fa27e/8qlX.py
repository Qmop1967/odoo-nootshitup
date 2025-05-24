#!/usr/bin/env python3

import json
import requests
import xmlrpc.client
import sys
from datetime import datetime

def load_config():
    """Load Zoho configuration"""
    try:
        with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return None

def get_zoho_access_token(config):
    """Get fresh access token from Zoho"""
    try:
        zoho_config = config['zoho_books']
        token_url = "https://accounts.zoho.com/oauth/v2/token"
        token_params = {
            'refresh_token': zoho_config['refresh_token'],
            'client_id': zoho_config['client_id'],
            'client_secret': zoho_config['client_secret'],
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(token_url, data=token_params, timeout=30)
        response.raise_for_status()
        return response.json()['access_token']
    except Exception as e:
        print(f"❌ Error getting Zoho token: {e}")
        return None

def search_zoho_item(config, item_name):
    """Search for specific item in Zoho"""
    access_token = get_zoho_access_token(config)
    if not access_token:
        return None
    
    headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
    
    try:
        # Search for the specific item
        params = {
            'organization_id': config['zoho_books']['organization_id'],
            'search_text': item_name
        }
        
        url = f"{config['zoho_books']['base_url']}/items"
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            
            # Find exact match
            for item in items:
                if item.get('name') == item_name:
                    return item
            
            # If no exact match, return close matches
            return items
        else:
            print(f"❌ Zoho API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error searching Zoho: {e}")
        return None

def search_odoo_item(config, item_name):
    """Search for specific item in Odoo"""
    try:
        odoo_config = config['odoo']['test_db']
        url = f"http://{odoo_config['host']}:{odoo_config['port']}"
        
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(
            odoo_config['database'],
            odoo_config['username'],
            odoo_config['password'],
            {}
        )
        
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
            
            # Search by name
            products = models.execute_kw(
                odoo_config['database'], uid, odoo_config['password'],
                'product.template', 'search_read',
                [[('name', 'ilike', item_name)]],
                {'fields': ['id', 'name', 'list_price', 'standard_price', 'x_zoho_item_id'], 'limit': 10}
            )
            
            return products
        else:
            print("❌ Odoo authentication failed")
            return []
            
    except Exception as e:
        print(f"❌ Error searching Odoo: {e}")
        return []

def check_custom_field_exists(config):
    """Check if custom Zoho field exists in Odoo"""
    try:
        odoo_config = config['odoo']['test_db']
        url = f"http://{odoo_config['host']}:{odoo_config['port']}"
        
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(
            odoo_config['database'],
            odoo_config['username'],
            odoo_config['password'],
            {}
        )
        
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
            
            # Check if custom field exists
            fields = models.execute_kw(
                odoo_config['database'], uid, odoo_config['password'],
                'ir.model.fields', 'search_read',
                [[('model', '=', 'product.template'), ('name', '=', 'x_zoho_item_id')]],
                {'fields': ['id', 'name'], 'limit': 1}
            )
            
            return len(fields) > 0
                
    except Exception as e:
        print(f"❌ Error checking custom field: {e}")
        return False

def get_sync_service_status():
    """Check sync service status"""
    import subprocess
    import os
    
    # Check if any sync process is running
    try:
        result = subprocess.run(['pgrep', '-f', 'zoho.*sync'], capture_output=True, text=True)
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            return f"Running (PIDs: {', '.join(pids)})"
        else:
            return "Not running"
    except:
        return "Unknown"

def main():
    print("🔍 SPECIFIC ITEM SYNC DIAGNOSIS")
    print("="*80)
    
    target_item = "TTTTTTEEEESSSSSSTTTTT"
    print(f"Target Item: {target_item}")
    print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # Load configuration
    config = load_config()
    if not config:
        print("❌ Cannot proceed without configuration")
        return
    
    # 1. Check if sync service is running
    print("1. 🔄 Checking sync service status...")
    service_status = get_sync_service_status()
    print(f"   Sync Service: {service_status}")
    
    # 2. Check custom field
    print("\n2. 🔧 Checking custom field...")
    field_exists = check_custom_field_exists(config)
    print(f"   Custom field 'x_zoho_item_id': {'✅ EXISTS' if field_exists else '❌ MISSING'}")
    
    # 3. Search in Zoho
    print(f"\n3. 📦 Searching for '{target_item}' in Zoho Books...")
    zoho_item = search_zoho_item(config, target_item)
    
    if zoho_item:
        if isinstance(zoho_item, list):
            print(f"   Found {len(zoho_item)} similar items in Zoho:")
            for item in zoho_item:
                print(f"     - {item.get('name', 'Unknown')} (ID: {item.get('item_id', 'N/A')})")
        else:
            print(f"   ✅ Found exact match in Zoho:")
            print(f"     Name: {zoho_item.get('name')}")
            print(f"     ID: {zoho_item.get('item_id')}")
            print(f"     Rate: ${zoho_item.get('rate', 0)}")
            print(f"     Purchase Rate: ${zoho_item.get('purchase_rate', 0)}")
            print(f"     Status: {zoho_item.get('status', 'Unknown')}")
    else:
        print("   ❌ Item not found in Zoho")
    
    # 4. Search in Odoo
    print(f"\n4. 🗃️  Searching for '{target_item}' in Odoo...")
    odoo_items = search_odoo_item(config, target_item)
    
    if odoo_items:
        print(f"   Found {len(odoo_items)} items in Odoo:")
        for item in odoo_items:
            print(f"     - {item.get('name')} (ID: {item.get('id')}) | Zoho ID: {item.get('x_zoho_item_id', 'None')}")
    else:
        print("   ❌ Item not found in Odoo")
    
    # 5. Analysis and recommendations
    print(f"\n5. 📊 ANALYSIS & RECOMMENDATIONS")
    print("-"*60)
    
    if service_status == "Not running":
        print("🔧 CRITICAL ISSUE: No sync service is running!")
        print("   ➡️  SOLUTION: Start the sync service")
        print("      cd /opt/odoo/migration")
        print("      python3 sync_service_manager_images.py start")
        print("      OR")
        print("      systemctl start zoho-odoo-sync-images")
    
    if not field_exists:
        print("🔧 CRITICAL ISSUE: Custom field missing!")
        print("   ➡️  SOLUTION: Add the custom field")
        print("      cd /opt/odoo/migration")
        print("      python3 add_zoho_field.py")
    
    if zoho_item and not odoo_items:
        print("🔧 SYNC ISSUE: Item exists in Zoho but not in Odoo")
        print("   ➡️  SOLUTION: Run manual sync")
        print("      cd /opt/odoo/migration")
        print("      python3 sync_service_manager_images.py manual")
    
    if isinstance(zoho_item, dict) and odoo_items:
        # Check if Zoho ID matches
        zoho_id = str(zoho_item.get('item_id', ''))
        odoo_zoho_ids = [str(item.get('x_zoho_item_id', '')) for item in odoo_items]
        
        if zoho_id in odoo_zoho_ids:
            print("✅ Item is properly synced (Zoho ID matches)")
        else:
            print("🔧 MISMATCH: Item exists in both but Zoho IDs don't match")
            print("   This could indicate duplicate or sync issues")
    
    print(f"\n6. 🚀 IMMEDIATE ACTION PLAN")
    print("-"*60)
    print("Run these commands to fix the sync:")
    print("")
    print("# 1. Navigate to migration directory")
    print("cd /opt/odoo/migration")
    print("")
    print("# 2. Stop any old services")
    print("systemctl stop zoho-odoo-sync 2>/dev/null || true")
    print("")
    print("# 3. Start enhanced service")
    print("systemctl start zoho-odoo-sync-images")
    print("systemctl enable zoho-odoo-sync-images")
    print("")
    print("# 4. Run manual sync to catch up")
    print("python3 sync_service_manager_images.py manual")
    print("")
    print("# 5. Monitor the service")
    print("python3 sync_service_manager_images.py monitor")
    
    print(f"\n✅ This will ensure '{target_item}' and all other items sync properly!")

if __name__ == "__main__":
    main() 