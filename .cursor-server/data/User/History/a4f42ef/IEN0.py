#!/usr/bin/env python3

import json
import subprocess
import sys
import time
import os
from datetime import datetime
from zoho_odoo_sync_service_with_images import ZohoOdooSyncServiceWithImages

class SyncServiceManagerWithImages:
    """Management interface for the Enhanced Zoho-Odoo Sync Service with Images"""
    
    def __init__(self):
        self.service_name = "zoho-odoo-sync-images"
        self.service_file = "/etc/systemd/system/zoho-odoo-sync-images.service"
        self.tracking_file = "/opt/odoo/migration/data/sync_service/sync_tracking_images.json"
    
    def run_command(self, command):
        """Run a system command and return the result"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def create_service_file(self):
        """Create the systemd service file for the enhanced service"""
        service_content = """[Unit]
Description=Zoho Books to Odoo One-Way Synchronization Service with Images
Documentation=https://github.com/your-repo/zoho-odoo-sync
Wants=network-online.target
After=network-online.target
StartLimitIntervalSec=30
StartLimitBurst=3

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/odoo/migration
ExecStart=/usr/bin/python3 /opt/odoo/migration/zoho_odoo_sync_service_with_images.py
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10
TimeoutStartSec=30
TimeoutStopSec=30

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/opt/odoo/migration

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=zoho-odoo-sync-images

# Environment
Environment=PYTHONPATH=/opt/odoo/migration
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
"""
        
        try:
            with open(self.service_file, 'w') as f:
                f.write(service_content)
            return True
        except Exception as e:
            print(f"❌ Error creating service file: {e}")
            return False
    
    def install_service(self):
        """Install and enable the systemd service"""
        print("🔧 Installing Enhanced Zoho-Odoo Sync Service with Images...")
        
        # Create service file
        if not self.create_service_file():
            return False
        
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
        
        print("✅ Enhanced service installed and enabled successfully")
        return True
    
    def start_service(self):
        """Start the sync service"""
        print("🚀 Starting Enhanced Zoho-Odoo Sync Service with Images...")
        
        success, stdout, stderr = self.run_command(f"systemctl start {self.service_name}")
        if not success:
            print(f"❌ Failed to start service: {stderr}")
            return False
        
        print("✅ Enhanced service started successfully")
        return True
    
    def stop_service(self):
        """Stop the sync service"""
        print("🛑 Stopping Enhanced Zoho-Odoo Sync Service...")
        
        success, stdout, stderr = self.run_command(f"systemctl stop {self.service_name}")
        if not success:
            print(f"❌ Failed to stop service: {stderr}")
            return False
        
        print("✅ Enhanced service stopped successfully")
        return True
    
    def restart_service(self):
        """Restart the sync service"""
        print("🔄 Restarting Enhanced Zoho-Odoo Sync Service...")
        
        success, stdout, stderr = self.run_command(f"systemctl restart {self.service_name}")
        if not success:
            print(f"❌ Failed to restart service: {stderr}")
            return False
        
        print("✅ Enhanced service restarted successfully")
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
        print(f"📋 Recent enhanced service logs (last {lines} lines):")
        print("=" * 80)
        
        success, stdout, stderr = self.run_command(f"journalctl -u {self.service_name} -n {lines} --no-pager")
        if success:
            print(stdout)
        else:
            print(f"❌ Failed to get logs: {stderr}")
    
    def show_sync_statistics(self):
        """Show synchronization statistics including image sync"""
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
            
            print("📊 ENHANCED SYNC STATISTICS")
            print("=" * 60)
            print(f"Total Syncs: {len(sync_history)}")
            
            if latest_sync:
                print(f"Last Sync: {latest_sync.get('timestamp', 'Unknown')}")
                print(f"Duration: {latest_sync.get('duration', 0):.1f} seconds")
                print(f"Products Added: {latest_sync.get('products_added', 0)}")
                print(f"Products Updated: {latest_sync.get('products_updated', 0)}")
                print(f"Products Deleted: {latest_sync.get('products_deleted', 0)}")
                print(f"🖼️ Images Synced: {latest_sync.get('images_synced', 0)}")
                print(f"❌ Image Failures: {latest_sync.get('images_failed', 0)}")
                print(f"Errors: {latest_sync.get('errors', 0)}")
                print(f"Conflicts Resolved: {latest_sync.get('conflicts_resolved', 0)}")
            
            # Show recent sync history
            print(f"\n📈 RECENT SYNC HISTORY (last 10):")
            for sync in sync_history[-10:]:
                timestamp = sync.get('timestamp', 'Unknown')
                added = sync.get('products_added', 0)
                updated = sync.get('products_updated', 0)
                deleted = sync.get('products_deleted', 0)
                images = sync.get('images_synced', 0)
                errors = sync.get('errors', 0)
                print(f"  {timestamp}: +{added} ~{updated} -{deleted} 🖼️{images} ❌{errors}")
            
            # Show image statistics
            product_images = tracking_data.get('product_images', {})
            print(f"\n🖼️ IMAGE STATISTICS:")
            print(f"Total Products with Images: {len(product_images)}")
            
            # Show recent image syncs
            recent_images = sorted(
                product_images.items(), 
                key=lambda x: x[1].get('last_sync', ''), 
                reverse=True
            )[:5]
            
            if recent_images:
                print(f"Recent Image Syncs:")
                for zoho_id, image_data in recent_images:
                    last_sync = image_data.get('last_sync', 'Unknown')
                    local_path = image_data.get('local_path', 'Unknown')
                    filename = os.path.basename(local_path) if local_path else 'Unknown'
                    print(f"  Product {zoho_id}: {filename} ({last_sync})")
            
        except Exception as e:
            print(f"❌ Error reading statistics: {e}")
    
    def run_one_time_sync(self):
        """Run a one-time synchronization with images"""
        print("🚀 Running one-time synchronization with images...")
        
        try:
            sync_service = ZohoOdooSyncServiceWithImages()
            success = sync_service.run_sync_cycle()
            
            if success:
                print("✅ One-time sync with images completed successfully")
            else:
                print("❌ One-time sync with images failed")
                
        except Exception as e:
            print(f"❌ One-time sync failed: {e}")
    
    def show_images_log(self, lines=20):
        """Show recent images log"""
        images_log = "/opt/odoo/migration/logs/images.log"
        
        print(f"🖼️ RECENT IMAGE SYNC LOG (last {lines} lines):")
        print("=" * 80)
        
        success, stdout, stderr = self.run_command(f"tail -n {lines} {images_log}")
        if success and stdout.strip():
            print(stdout)
        else:
            print("ℹ️  No image sync events recorded yet")
    
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
    
    def show_image_directory(self):
        """Show contents of image directory"""
        images_dir = "/opt/odoo/migration/data/product_images"
        
        print(f"🖼️ DOWNLOADED PRODUCT IMAGES:")
        print("=" * 50)
        
        if not os.path.exists(images_dir):
            print("📁 Image directory doesn't exist yet")
            return
        
        try:
            files = os.listdir(images_dir)
            if not files:
                print("📁 No images downloaded yet")
                return
            
            # Sort by modification time (newest first)
            files_with_time = []
            for filename in files:
                filepath = os.path.join(images_dir, filename)
                if os.path.isfile(filepath):
                    mtime = os.path.getmtime(filepath)
                    size = os.path.getsize(filepath)
                    files_with_time.append((filename, mtime, size))
            
            files_with_time.sort(key=lambda x: x[1], reverse=True)
            
            print(f"Total Images: {len(files_with_time)}")
            print(f"Recent Images (last 10):")
            
            for filename, mtime, size in files_with_time[:10]:
                mod_time = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                size_kb = size / 1024
                print(f"  📸 {filename} ({size_kb:.1f} KB) - {mod_time}")
                
        except Exception as e:
            print(f"❌ Error reading image directory: {e}")


def main():
    manager = SyncServiceManagerWithImages()
    
    if len(sys.argv) < 2:
        print("🔄 Enhanced Zoho-Odoo Sync Service Manager with Images")
        print("=" * 70)
        print("Usage: python3 sync_service_manager_images.py <command>")
        print()
        print("Commands:")
        print("  install     - Install and enable the enhanced service")
        print("  start       - Start the service")
        print("  stop        - Stop the service")
        print("  restart     - Restart the service")
        print("  status      - Show service status")
        print("  logs        - Show recent logs")
        print("  stats       - Show sync statistics")
        print("  conflicts   - Show recent conflicts")
        print("  changes     - Show recent changes")
        print("  images      - Show image sync log")
        print("  image-dir   - Show downloaded images")
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
        
        print("📊 ENHANCED SERVICE STATUS")
        print("=" * 40)
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
    
    elif command == "images":
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        manager.show_images_log(lines)
    
    elif command == "image-dir":
        manager.show_image_directory()
    
    elif command == "sync-once":
        manager.run_one_time_sync()
    
    elif command == "monitor":
        print("📊 Live Enhanced Service Monitoring (Ctrl+C to stop)")
        print("=" * 60)
        
        try:
            while True:
                is_active, is_enabled = manager.get_service_status()
                current_time = datetime.now().strftime("%H:%M:%S")
                
                status = "🟢 RUNNING" if is_active else "🔴 STOPPED"
                print(f"\r[{current_time}] Enhanced Service Status: {status}", end="", flush=True)
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print(f"\n👋 Monitoring stopped")
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main() 