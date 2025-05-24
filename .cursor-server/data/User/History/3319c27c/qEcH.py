#!/usr/bin/env python3

import os
import sys
import json
import subprocess
import time
import requests
import xmlrpc.client
from datetime import datetime

def print_header(title):
    print("\n" + "="*80)
    print(f"🔧 {title}")
    print("="*80)

def print_step(step, description):
    print(f"\n{step}. {description}")
    print("-" * 60)

def run_command(cmd, description=""):
    """Run a system command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_service_status(service_name):
    """Check systemd service status"""
    success, stdout, stderr = run_command(f"systemctl is-active {service_name}")
    if success and "active" in stdout:
        return "active"
    elif "inactive" in stdout or "failed" in stdout:
        return "inactive"
    else:
        return "unknown"

def load_config():
    """Load Zoho configuration"""
    try:
        with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return None

def test_zoho_connection(config):
    """Test Zoho API connection"""
    try:
        zoho_config = config['zoho_books']
        
        token_url = "https://accounts.zoho.com/oauth/v2/token"
        token_params = {
            'refresh_token': zoho_config['refresh_token'],
            'client_id': zoho_config['client_id'],
            'client_secret': zoho_config['client_secret'],
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(token_url, data=token_params, timeout=10)
        if response.status_code == 200:
            access_token = response.json()['access_token']
            
            # Test API call
            headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
            params = {
                'organization_id': zoho_config['organization_id'],
                'page': 1,
                'per_page': 5
            }
            
            api_response = requests.get(f"{zoho_config['base_url']}/items", 
                                      headers=headers, params=params, timeout=10)
            
            if api_response.status_code == 200:
                data = api_response.json()
                items = data.get('items', [])
                print(f"✅ Zoho API working - found {len(items)} items in test call")
                return True, len(data.get('items', []))
            else:
                print(f"❌ Zoho API error: {api_response.status_code}")
                return False, 0
        else:
            print(f"❌ Token refresh failed: {response.status_code}")
            return False, 0
            
    except Exception as e:
        print(f"❌ Zoho connection error: {e}")
        return False, 0

def test_odoo_connection(config):
    """Test Odoo connection"""
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
            
            # Test query
            products = models.execute_kw(
                odoo_config['database'], uid, odoo_config['password'],
                'product.template', 'search_count', [[]]
            )
            
            print(f"✅ Odoo connection working - found {products} products")
            return True, products
        else:
            print("❌ Odoo authentication failed")
            return False, 0
            
    except Exception as e:
        print(f"❌ Odoo connection error: {e}")
        return False, 0

def check_custom_field(config):
    """Check if custom Zoho field exists"""
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
            
            if fields:
                print(f"✅ Custom field 'x_zoho_item_id' exists (ID: {fields[0]['id']})")
                return True
            else:
                print("❌ Custom field 'x_zoho_item_id' not found")
                return False
                
    except Exception as e:
        print(f"❌ Error checking custom field: {e}")
        return False

def main():
    print_header("ZOHO-ODOO SYNC ISSUE DIAGNOSIS AND FIX")
    
    # Step 1: Check current service status
    print_step(1, "Checking current sync service status")
    
    services = ['zoho-odoo-sync', 'zoho-odoo-sync-images', 'zoho-odoo-sync-immediate']
    active_services = []
    
    for service in services:
        status = check_service_status(service)
        print(f"   {service}: {status}")
        if status == "active":
            active_services.append(service)
    
    if len(active_services) > 1:
        print(f"⚠️  Multiple services running: {active_services}")
        print("   This can cause conflicts!")
    elif len(active_services) == 0:
        print("ℹ️  No sync services currently running")
    else:
        print(f"ℹ️  Active service: {active_services[0]}")
    
    # Step 2: Load and test configuration
    print_step(2, "Testing system connections")
    
    config = load_config()
    if not config:
        print("❌ Cannot proceed without configuration")
        return
    
    # Test Zoho
    print("Testing Zoho Books API...")
    zoho_ok, zoho_items = test_zoho_connection(config)
    
    # Test Odoo  
    print("Testing Odoo connection...")
    odoo_ok, odoo_products = test_odoo_connection(config)
    
    # Test custom field
    print("Checking custom field...")
    field_ok = check_custom_field(config)
    
    # Step 3: Check sync data disparity
    print_step(3, "Checking data synchronization status")
    
    print(f"📊 Current Status:")
    print(f"   Zoho Items: {zoho_items}")
    print(f"   Odoo Products: {odoo_products}")
    print(f"   Difference: {zoho_items - odoo_products}")
    print(f"   Custom Field: {'✅ OK' if field_ok else '❌ Missing'}")
    
    # Step 4: Stop conflicting services
    print_step(4, "Stopping old/conflicting services")
    
    old_services = ['zoho-odoo-sync', 'zoho-odoo-sync-images']
    for service in old_services:
        if check_service_status(service) == "active":
            print(f"🛑 Stopping {service}...")
            success, stdout, stderr = run_command(f"systemctl stop {service}")
            if success:
                print(f"   ✅ {service} stopped")
            else:
                print(f"   ❌ Failed to stop {service}: {stderr}")
    
    # Step 5: Check if enhanced service exists and is configured
    print_step(5, "Checking enhanced sync service")
    
    enhanced_script = '/opt/odoo/migration/zoho_odoo_sync_service_with_images.py'
    immediate_script = '/opt/odoo/migration/zoho_odoo_sync_service_immediate.py'
    
    if os.path.exists(enhanced_script):
        print(f"✅ Enhanced script exists: {enhanced_script}")
        enhanced_available = True
    else:
        print(f"❌ Enhanced script missing: {enhanced_script}")
        enhanced_available = False
    
    if os.path.exists(immediate_script):
        print(f"✅ Immediate script exists: {immediate_script}")
        immediate_available = True
    else:
        print(f"❌ Immediate script missing: {immediate_script}")
        immediate_available = False
    
    # Step 6: Recommend solution
    print_step(6, "Recommended solution")
    
    if not field_ok:
        print("🔧 CRITICAL: Custom field missing!")
        print("   Run: cd /opt/odoo/migration && python3 add_zoho_field.py")
        print("   This is required for sync to work properly")
        return
    
    if zoho_items - odoo_products > 10:
        print(f"🔧 SYNC NEEDED: {zoho_items - odoo_products} items missing from Odoo")
        
        if immediate_available:
            print("\n📋 RECOMMENDED ACTIONS:")
            print("1. Use the immediate sync service:")
            print("   cd /opt/odoo/migration")
            print("   python3 sync_manager_immediate.py manual")
            print("")
            print("2. If successful, start the service:")
            print("   python3 sync_manager_immediate.py start")
            print("")
            print("3. Monitor the service:")
            print("   python3 sync_manager_immediate.py status")
            
        elif enhanced_available:
            print("\n📋 RECOMMENDED ACTIONS:")
            print("1. Install missing dependencies:")
            print("   pip3 install schedule")
            print("")
            print("2. Start enhanced service:")
            print("   systemctl enable zoho-odoo-sync-images")
            print("   systemctl start zoho-odoo-sync-images")
            
        else:
            print("❌ No working sync scripts found!")
            print("   Need to recreate sync service")
    
    else:
        print("✅ Data counts look synchronized")
        print("   The issue might be with new items not syncing")
        
        if not active_services:
            print("\n🔧 NO SERVICE RUNNING - This explains missing new items!")
            print("📋 RECOMMENDED ACTION:")
            if immediate_available:
                print("   python3 sync_manager_immediate.py start")
            else:
                print("   systemctl start zoho-odoo-sync-images")
    
    # Step 7: Show next steps
    print_step(7, "Next steps summary")
    
    print("🎯 TO FIX SYNC ISSUES:")
    
    if not field_ok:
        print("   1. ❗ Add custom field first (CRITICAL)")
        print("      cd /opt/odoo/migration && python3 add_zoho_field.py")
    
    if zoho_items - odoo_products > 10:
        print("   2. 🔄 Run manual sync to catch up")
        print("      python3 sync_manager_immediate.py manual")
    
    if not active_services:
        print("   3. 🚀 Start sync service for ongoing sync")
        print("      python3 sync_manager_immediate.py start")
    
    print("   4. 📊 Monitor sync service")
    print("      python3 sync_manager_immediate.py monitor")
    
    print("\n🎉 This should resolve:")
    print("   ✅ New Zoho items appearing in Odoo")
    print("   ✅ Product image synchronization")
    print("   ✅ Continuous monitoring")
    
    print(f"\n⏰ Diagnosis completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 