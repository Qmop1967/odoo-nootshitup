#!/usr/bin/env python3
import subprocess
import os

def check_status():
    print("QUICK SYNC DIAGNOSIS")
    print("="*50)
    
    # Check services
    services = ['zoho-odoo-sync', 'zoho-odoo-sync-images']
    for service in services:
        try:
            result = subprocess.run(['systemctl', 'is-active', service], 
                                  capture_output=True, text=True)
            status = result.stdout.strip()
            print(f"{service}: {status}")
        except:
            print(f"{service}: unknown")
    
    # Check files
    files = [
        '/opt/odoo/migration/zoho_odoo_sync_service_with_images.py',
        '/opt/odoo/migration/zoho_odoo_sync_service_immediate.py',
        '/opt/odoo/migration/config/zoho_config.json'
    ]
    
    print("\nFiles:")
    for file in files:
        exists = "✅" if os.path.exists(file) else "❌"
        print(f"{exists} {file}")
    
    print("\nRECOMMENDED ACTION:")
    print("1. Stop all old services:")
    print("   systemctl stop zoho-odoo-sync")
    print("   systemctl stop zoho-odoo-sync-images")
    print("")
    print("2. Start enhanced service:")
    print("   systemctl start zoho-odoo-sync-images")
    print("   systemctl enable zoho-odoo-sync-images")

if __name__ == "__main__":
    check_status() 