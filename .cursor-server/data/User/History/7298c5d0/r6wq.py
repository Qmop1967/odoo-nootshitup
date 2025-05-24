#!/usr/bin/env python3

import subprocess
import json
import os
import time
from datetime import datetime, timedelta

def check_service_health():
    """Check if sync service is healthy"""
    try:
        # Check if systemd service is active
        result = subprocess.run(['systemctl', 'is-active', 'zoho-odoo-sync-images'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0 and 'active' in result.stdout:
            return True, "Service is active"
        else:
            return False, "Service is not active"
            
    except Exception as e:
        return False, f"Error checking service: {e}"

def check_recent_sync():
    """Check if sync happened recently"""
    tracking_file = '/opt/odoo/migration/data/sync_service/sync_tracking_images.json'
    
    if not os.path.exists(tracking_file):
        return False, "No sync tracking file found"
    
    try:
        with open(tracking_file, 'r') as f:
            tracking_data = json.load(f)
        
        last_sync = tracking_data.get('last_sync')
        if not last_sync:
            return False, "No sync history found"
        
        # Parse last sync time
        last_sync_time = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
        time_diff = datetime.now() - last_sync_time
        
        if time_diff > timedelta(minutes=10):  # If more than 10 minutes
            return False, f"Last sync was {time_diff.total_seconds()/60:.1f} minutes ago"
        else:
            return True, f"Last sync was {time_diff.total_seconds()/60:.1f} minutes ago"
            
    except Exception as e:
        return False, f"Error reading sync data: {e}"

def restart_service():
    """Restart the sync service"""
    try:
        # Stop service
        subprocess.run(['systemctl', 'stop', 'zoho-odoo-sync-images'], 
                      capture_output=True)
        time.sleep(2)
        
        # Start service
        result = subprocess.run(['systemctl', 'start', 'zoho-odoo-sync-images'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, "Service restarted successfully"
        else:
            return False, f"Failed to restart: {result.stderr}"
            
    except Exception as e:
        return False, f"Error restarting service: {e}"

def send_alert(message):
    """Log alert message"""
    log_file = '/opt/odoo/migration/logs/sync_monitoring.log'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - ALERT: {message}\n")
    
    print(f"🚨 ALERT: {message}")

def main():
    """Main monitoring function"""
    print("🔍 Sync Service Health Check")
    print("="*50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check service status
    service_ok, service_msg = check_service_health()
    print(f"Service Status: {'✅' if service_ok else '❌'} {service_msg}")
    
    # Check recent sync
    sync_ok, sync_msg = check_recent_sync()
    print(f"Recent Sync: {'✅' if sync_ok else '❌'} {sync_msg}")
    
    # Take action if needed
    if not service_ok:
        send_alert("Sync service is not running - attempting restart")
        restart_ok, restart_msg = restart_service()
        print(f"Restart Attempt: {'✅' if restart_ok else '❌'} {restart_msg}")
        
        if restart_ok:
            print("✅ Service restored successfully")
        else:
            send_alert(f"Failed to restart service: {restart_msg}")
            print("❌ Manual intervention required")
    
    elif not sync_ok:
        send_alert(f"Sync appears stalled: {sync_msg}")
        print("⚠️  Consider manual sync or restart")
    
    else:
        print("✅ All systems healthy")

if __name__ == "__main__":
    main() 