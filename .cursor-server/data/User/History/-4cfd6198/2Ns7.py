#!/usr/bin/env python3

import json
import subprocess
import sys
import time
from datetime import datetime
from zoho_odoo_sync_service import ZohoOdooSyncService

class SyncServiceManager:
    """Management interface for the Zoho-Odoo Sync Service"""
    
    def __init__(self):
        self.service_name = "zoho-odoo-sync"
        self.service_file = "/etc/systemd/system/zoho-odoo-sync.service"
        self.tracking_file = "/opt/odoo/migration/data/sync_service/sync_tracking.json"
    
    def run_command(self, command):
        """Run a system command and return the result"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def install_service(self):
        """Install and enable the systemd service"""
        print("🔧 Installing Zoho-Odoo Sync Service...")
        
        # Reload systemd
        success, stdout, stderr = self.run_command("systemctl daemon-reload")
        if not success:
            print(f"❌ Failed to reload systemd: {stderr}")
            return False
        
        # Enable service
        success, stdout, stderr = self.run_command(f"systemctl enable {self.service_name}")
        if not success:
            print(f"❌ Failed to enable service: {stderr}")
            return False
        
        print("✅ Service installed and enabled successfully")
        return True
    
    def start_service(self):
        """Start the sync service"""
        print("🚀 Starting Zoho-Odoo Sync Service...")
        
        success, stdout, stderr = self.run_command(f"systemctl start {self.service_name}")
        if not success:
            print(f"❌ Failed to start service: {stderr}")
            return False
        
        print("✅ Service started successfully")
        return True
    
    def stop_service(self):
        """Stop the sync service"""
        print("🛑 Stopping Zoho-Odoo Sync Service...")
        
        success, stdout, stderr = self.run_command(f"systemctl stop {self.service_name}")
        if not success:
            print(f"❌ Failed to stop service: {stderr}")
            return False
        
        print("✅ Service stopped successfully")
        return True
    
    def restart_service(self):
        """Restart the sync service"""
        print("🔄 Restarting Zoho-Odoo Sync Service...")
        
        success, stdout, stderr = self.run_command(f"systemctl restart {self.service_name}")
        if not success:
            print(f"❌ Failed to restart service: {stderr}")
            return False
        
        print("✅ Service restarted successfully")
        return True
    
    def get_service_status(self):
        """Get the current service status"""
        success, stdout, stderr = self.run_command(f"systemctl is-active {self.service_name}")
        is_active = success and stdout.strip() == "active"
        
        success, stdout, stderr = self.run_command(f"systemctl is-enabled {self.service_name}")
        is_enabled = success and stdout.strip() == "enabled"
        
        return is_active, is_enabled
    
    def show_service_logs(self, lines=50):
        """Show recent service logs"""
        print(f"📋 Recent service logs (last {lines} lines):")
        print("=" * 80)
        
        success, stdout, stderr = self.run_command(f"journalctl -u {self.service_name} -n {lines} --no-pager")
        if success:
            print(stdout)
        else:
            print(f"❌ Failed to get logs: {stderr}")
    
    def show_sync_statistics(self):
        """Show synchronization statistics"""
        try:
            if not os.path.exists(self.tracking_file):
                print("⚠️  No sync statistics available yet")
                return
            
            with open(self.tracking_file, 'r') as f:
                tracking_data = json.load(f)
            
            sync_history = tracking_data.get('sync_history', [])
            if not sync_history:
                print("⚠️  No sync history available yet")
                return
            
            latest_sync = sync_history[-1]
            
            print("📊 SYNC STATISTICS")
            print("=" * 50)
            print(f"Total Syncs: {len(sync_history)}")
            
            if latest_sync:
                print(f"Last Sync: {latest_sync.get('timestamp', 'Unknown')}")
                print(f"Duration: {latest_sync.get('duration', 0):.1f} seconds")
                print(f"Products Added: {latest_sync.get('products_added', 0)}")
                print(f"Products Updated: {latest_sync.get('products_updated', 0)}")
                print(f"Products Deleted: {latest_sync.get('products_deleted', 0)}")
                print(f"Errors: {latest_sync.get('errors', 0)}")
                print(f"Conflicts Resolved: {latest_sync.get('conflicts_resolved', 0)}")
            
            # Show recent sync history
            print(f"\n📈 RECENT SYNC HISTORY (last 10):")
            for sync in sync_history[-10:]:
                timestamp = sync.get('timestamp', 'Unknown')
                added = sync.get('products_added', 0)
                updated = sync.get('products_updated', 0)
                deleted = sync.get('products_deleted', 0)
                errors = sync.get('errors', 0)
                print(f"  {timestamp}: +{added} ~{updated} -{deleted} ❌{errors}")
            
        except Exception as e:
            print(f"❌ Error reading statistics: {e}")
    
    def run_one_time_sync(self):
        """Run a one-time synchronization"""
        print("🚀 Running one-time synchronization...")
        
        try:
            sync_service = ZohoOdooSyncService()
            success = sync_service.run_sync_cycle()
            
            if success:
                print("✅ One-time sync completed successfully")
            else:
                print("❌ One-time sync failed")
                
        except Exception as e:
            print(f"❌ One-time sync failed: {e}")
    
    def show_conflicts_log(self, lines=20):
        """Show recent conflicts log"""
        conflicts_log = "/opt/odoo/migration/logs/conflicts.log"
        
        print(f"⚠️  RECENT CONFLICTS (last {lines} lines):")
        print("=" * 80)
        
        success, stdout, stderr = self.run_command(f"tail -n {lines} {conflicts_log}")
        if success and stdout.strip():
            print(stdout)
        else:
            print("✅ No conflicts recorded")
    
    def show_changes_log(self, lines=20):
        """Show recent changes log"""
        changes_log = "/opt/odoo/migration/logs/changes.log"
        
        print(f"📝 RECENT CHANGES (last {lines} lines):")
        print("=" * 80)
        
        success, stdout, stderr = self.run_command(f"tail -n {lines} {changes_log}")
        if success and stdout.strip():
            print(stdout)
        else:
            print("ℹ️  No changes recorded yet")


def main():
    manager = SyncServiceManager()
    
    if len(sys.argv) < 2:
        print("🔄 Zoho-Odoo Sync Service Manager")
        print("=" * 50)
        print("Usage: python3 sync_service_manager.py <command>")
        print()
        print("Commands:")
        print("  install     - Install and enable the service")
        print("  start       - Start the service")
        print("  stop        - Stop the service")
        print("  restart     - Restart the service")
        print("  status      - Show service status")
        print("  logs        - Show recent logs")
        print("  stats       - Show sync statistics")
        print("  conflicts   - Show recent conflicts")
        print("  changes     - Show recent changes")
        print("  sync-once   - Run one-time sync")
        print("  monitor     - Live monitoring")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "install":
        manager.install_service()
    
    elif command == "start":
        manager.start_service()
    
    elif command == "stop":
        manager.stop_service()
    
    elif command == "restart":
        manager.restart_service()
    
    elif command == "status":
        is_active, is_enabled = manager.get_service_status()
        
        print("📊 SERVICE STATUS")
        print("=" * 30)
        print(f"Active: {'✅ YES' if is_active else '❌ NO'}")
        print(f"Enabled: {'✅ YES' if is_enabled else '❌ NO'}")
        
        if is_active:
            print("\n📈 SYNC STATISTICS:")
            manager.show_sync_statistics()
    
    elif command == "logs":
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        manager.show_service_logs(lines)
    
    elif command == "stats":
        manager.show_sync_statistics()
    
    elif command == "conflicts":
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        manager.show_conflicts_log(lines)
    
    elif command == "changes":
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        manager.show_changes_log(lines)
    
    elif command == "sync-once":
        manager.run_one_time_sync()
    
    elif command == "monitor":
        print("📊 Live Service Monitoring (Ctrl+C to stop)")
        print("=" * 50)
        
        try:
            while True:
                is_active, is_enabled = manager.get_service_status()
                current_time = datetime.now().strftime("%H:%M:%S")
                
                status = "🟢 RUNNING" if is_active else "🔴 STOPPED"
                print(f"\r[{current_time}] Service Status: {status}", end="", flush=True)
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print(f"\n👋 Monitoring stopped")
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    import os
    main() 