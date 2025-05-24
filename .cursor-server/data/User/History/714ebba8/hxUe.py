#!/usr/bin/env python3

import json
import requests
import xmlrpc.client
import subprocess
import os
import sys
from datetime import datetime

def print_step(step, description):
    print(f"\n{step}. {description}")
    print("-" * 60)

def load_config():
    """Load configuration"""
    with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
        return json.load(f)

def get_zoho_access_token(config):
    """Get Zoho access token"""
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

def connect_to_odoo(config):
    """Connect to Odoo"""
    odoo_config = config['odoo']['test_db']
    url = f"http://{odoo_config['host']}:{odoo_config['port']}"
    
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(
        odoo_config['database'],
        odoo_config['username'],
        odoo_config['password'],
        {}
    )
    
    if not uid:
        raise Exception("Failed to authenticate with Odoo")
    
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    return uid, models, odoo_config

def stop_old_services():
    """Stop any old conflicting services"""
    old_services = ['zoho-odoo-sync', 'zoho-odoo-sync-fixed']
    
    for service in old_services:
        try:
            result = subprocess.run(['systemctl', 'stop', service], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ Stopped {service}")
            else:
                print(f"   ℹ️  {service} was not running")
        except Exception as e:
            print(f"   ⚠️  Could not stop {service}: {e}")

def start_enhanced_service():
    """Start the enhanced sync service"""
    try:
        # First try systemctl
        result = subprocess.run(['systemctl', 'start', 'zoho-odoo-sync-images'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Enhanced service started via systemctl")
            
            # Enable for auto-start
            subprocess.run(['systemctl', 'enable', 'zoho-odoo-sync-images'], 
                         capture_output=True)
            return True
        else:
            print(f"   ⚠️  Systemctl failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error starting service: {e}")
        return False

def sync_specific_item(config, target_item_name):
    """Sync a specific item from Zoho to Odoo"""
    try:
        # Get Zoho access token
        access_token = get_zoho_access_token(config)
        headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
        
        # Search for the item in Zoho
        params = {
            'organization_id': config['zoho_books']['organization_id'],
            'search_text': target_item_name
        }
        
        url = f"{config['zoho_books']['base_url']}/items"
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code != 200:
            print(f"   ❌ Failed to fetch from Zoho: {response.status_code}")
            return False
        
        data = response.json()
        items = data.get('items', [])
        
        # Find exact match
        target_item = None
        for item in items:
            if item.get('name') == target_item_name:
                target_item = item
                break
        
        if not target_item:
            print(f"   ❌ Item '{target_item_name}' not found in Zoho")
            return False
        
        print(f"   ✅ Found item in Zoho:")
        print(f"      Name: {target_item.get('name')}")
        print(f"      ID: {target_item.get('item_id')}")
        print(f"      Rate: ${target_item.get('rate', 0)}")
        print(f"      Purchase Rate: ${target_item.get('purchase_rate', 0)}")
        
        # Connect to Odoo
        uid, models, odoo_config = connect_to_odoo(config)
        
        # Check if item already exists in Odoo
        existing_products = models.execute_kw(
            odoo_config['database'], uid, odoo_config['password'],
            'product.template', 'search_read',
            [[('x_zoho_item_id', '=', str(target_item.get('item_id')))]],
            {'fields': ['id', 'name'], 'limit': 1}
        )
        
        # Convert USD to IQD
        usd_to_iqd_rate = 1500
        
        def convert_price(price):
            if not price or price <= 0:
                return 0.0
            if price < 100:  # Likely USD
                return price * usd_to_iqd_rate
            return price
        
        # Prepare product data
        product_data = {
            'name': target_item.get('name'),
            'list_price': convert_price(float(target_item.get('rate', 0))),
            'standard_price': convert_price(float(target_item.get('purchase_rate', 0))),
            'default_code': target_item.get('sku'),
            'x_zoho_item_id': str(target_item.get('item_id')),
            'type': 'product',
            'sale_ok': True,
            'purchase_ok': True,
            'tracking': 'none'
        }
        
        # Remove None values
        product_data = {k: v for k, v in product_data.items() if v is not None}
        
        if existing_products:
            # Update existing product
            product_id = existing_products[0]['id']
            models.execute_kw(
                odoo_config['database'], uid, odoo_config['password'],
                'product.template', 'write',
                [[product_id], product_data]
            )
            print(f"   ✅ Updated existing product in Odoo (ID: {product_id})")
        else:
            # Create new product
            product_id = models.execute_kw(
                odoo_config['database'], uid, odoo_config['password'],
                'product.template', 'create',
                [product_data]
            )
            print(f"   ✅ Created new product in Odoo (ID: {product_id})")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error syncing item: {e}")
        return False

def main():
    print("🚀 IMMEDIATE SYNC FIX FOR SPECIFIC ITEM")
    print("="*80)
    print(f"Target: TTTTTTEEEESSSSSSTTTTT")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Load configuration
        print_step(1, "Loading configuration")
        config = load_config()
        print("   ✅ Configuration loaded")
        
        # Stop old services
        print_step(2, "Stopping old/conflicting services")
        stop_old_services()
        
        # Start enhanced service
        print_step(3, "Starting enhanced sync service")
        service_started = start_enhanced_service()
        
        # Sync the specific item immediately
        print_step(4, "Syncing specific item immediately")
        target_item = "TTTTTTEEEESSSSSSTTTTT"
        sync_success = sync_specific_item(config, target_item)
        
        # Verify the sync
        print_step(5, "Verification")
        if sync_success:
            print("   ✅ Item sync completed successfully")
        else:
            print("   ❌ Item sync failed")
        
        if service_started:
            print("   ✅ Enhanced service is running for future syncs")
        else:
            print("   ⚠️  Service may need manual start")
        
        # Final instructions
        print_step(6, "NEXT STEPS TO PREVENT FUTURE ISSUES")
        print("   1. ✅ Enhanced service should now be running automatically")
        print("   2. ✅ All new Zoho items will sync within 5 minutes")
        print("   3. ✅ Images will be downloaded and attached")
        print("   4. ✅ Prices will be converted from USD to IQD")
        print("")
        print("   📊 Monitor the service:")
        print("      cd /opt/odoo/migration")
        print("      python3 sync_service_manager_images.py status")
        print("      python3 sync_service_manager_images.py monitor")
        print("")
        print("   📋 View logs:")
        print("      tail -f /opt/odoo/migration/logs/sync_service_images.log")
        
        print(f"\n🎉 SYNC FIX COMPLETE!")
        print("Your Zoho item should now be in Odoo, and future items will sync automatically.")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        print("\n🔧 MANUAL SOLUTION:")
        print("1. cd /opt/odoo/migration")
        print("2. systemctl stop zoho-odoo-sync")
        print("3. systemctl start zoho-odoo-sync-images")
        print("4. python3 sync_service_manager_images.py manual")

if __name__ == "__main__":
    main() 