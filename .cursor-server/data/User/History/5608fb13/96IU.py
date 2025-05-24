#!/usr/bin/env python3

import json
import subprocess
import sys
import time
import os
from datetime import datetime
from zoho_odoo_sync_service_with_images_fixed import ZohoOdooSyncServiceWithImagesFixed

class SyncServiceManagerFixed:
    """Management interface for the Fixed Zoho-Odoo Sync Service with Images"""
    
    def __init__(self):
        self.service_name = "zoho-odoo-sync-fixed"
        self.service_file = "/etc/systemd/system/zoho-odoo-sync-fixed.service"
        self.tracking_file = "/opt/odoo/migration/data/sync_service/sync_tracking_images_fixed.json"
    
    def run_command(self, command):
        """Run a system command and return the result"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def create_service_file(self):
        """Create the systemd service file for the fixed service"""
        service_content = """[Unit]
Description=Fixed Zoho Books to Odoo Sync Service with Images and Unique IDs
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
ExecStart=/usr/bin/python3 /opt/odoo/migration/zoho_odoo_sync_service_with_images_fixed.py
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
SyslogIdentifier=zoho-odoo-sync-fixed

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
        print("🔧 Installing Fixed Zoho-Odoo Sync Service with Images...")
        
        # Stop any conflicting services first
        print("   🛑 Stopping conflicting services...")
        self.run_command("systemctl stop zoho-odoo-sync zoho-odoo-sync-images 2>/dev/null || true")
        self.run_command("systemctl disable zoho-odoo-sync zoho-odoo-sync-images 2>/dev/null || true")
        
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
        
        print("✅ Fixed service installed and enabled successfully")
        return True
    
    def start_service(self):
        """Start the sync service"""
        print("🚀 Starting Fixed Zoho-Odoo Sync Service...")
        
        success, stdout, stderr = self.run_command(f"systemctl start {self.service_name}")
        if not success:
            print(f"❌ Failed to start service: {stderr}")
            return False
        
        print("✅ Fixed service started successfully")
        return True
    
    def stop_service(self):
        """Stop the sync service"""
        print("🛑 Stopping Fixed Zoho-Odoo Sync Service...")
        
        success, stdout, stderr = self.run_command(f"systemctl stop {self.service_name}")
        if not success:
            print(f"❌ Failed to stop service: {stderr}")
            return False
        
        print("✅ Fixed service stopped successfully")
        return True
    
    def restart_service(self):
        """Restart the sync service"""
        print("🔄 Restarting Fixed Zoho-Odoo Sync Service...")
        
        success, stdout, stderr = self.run_command(f"systemctl restart {self.service_name}")
        if not success:
            print(f"❌ Failed to restart service: {stderr}")
            return False
        
        print("✅ Fixed service restarted successfully")
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
        print(f"📋 Recent fixed service logs (last {lines} lines):")
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
            
            print("📊 FIXED SYNC STATISTICS")
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
            
            # Show tracking statistics
            zoho_products = tracking_data.get('zoho_products', {})
            print(f"\n🆔 UNIQUE ID TRACKING:")
            print(f"Products with Zoho IDs: {len(zoho_products)}")
            
            # Show recent image syncs
            recent_images = sorted(
                product_images.items(), 
                key=lambda x: x[1].get('last_sync', ''), 
                reverse=True
            )[:5]
            
            if recent_images:
                print(f"\nRecent Image Syncs:")
                for zoho_id, image_data in recent_images:
                    last_sync = image_data.get('last_sync', 'Unknown')
                    local_path = image_data.get('local_path', 'Unknown')
                    filename = os.path.basename(local_path) if local_path else 'Unknown'
                    print(f"  Product {zoho_id}: {filename} ({last_sync})")
            
        except Exception as e:
            print(f"❌ Error reading statistics: {e}")
    
    def run_one_time_sync(self):
        """Run a one-time synchronization with images"""
        print("🚀 Running one-time synchronization with images and unique IDs...")
        
        try:
            sync_service = ZohoOdooSyncServiceWithImagesFixed()
            success = sync_service.run_sync_cycle()
            
            if success:
                print("✅ One-time sync completed successfully")
                
                # Show results
                status = sync_service.get_service_status()
                stats = status['statistics']
                
                print(f'\n📊 SYNC RESULTS:')
                print(f'   Products Added: {stats["products_added"]}')
                print(f'   Products Updated: {stats["products_updated"]}')
                print(f'   Products Deleted: {stats["products_deleted"]}')
                print(f'   Images Synced: {stats["images_synced"]}')
                print(f'   Images Failed: {stats["images_failed"]}')
                print(f'   Conflicts Resolved: {stats["conflicts_resolved"]}')
                print(f'   Duration: {stats["last_sync_duration"]:.1f}s')
            else:
                print("❌ One-time sync failed")
                
        except Exception as e:
            print(f"❌ One-time sync failed: {e}")
    
    def show_images_log(self, lines=20):
        """Show recent images log"""
        images_log = "/opt/odoo/migration/logs/images_fixed.log"
        
        print(f"🖼️ RECENT IMAGE SYNC LOG (last {lines} lines):")
        print("=" * 80)
        
        success, stdout, stderr = self.run_command(f"tail -n {lines} {images_log}")
        if success and stdout.strip():
            print(stdout)
        else:
            print("ℹ️  No image sync events recorded yet")
    
    def show_conflicts_log(self, lines=20):
        """Show recent conflicts log"""
        conflicts_log = "/opt/odoo/migration/logs/conflicts_fixed.log"
        
        print(f"⚠️  RECENT CONFLICTS (last {lines} lines):")
        print("=" * 80)
        
        success, stdout, stderr = self.run_command(f"tail -n {lines} {conflicts_log}")
        if success and stdout.strip():
            print(stdout)
        else:
            print("✅ No conflicts recorded")
    
    def show_changes_log(self, lines=20):
        """Show recent changes log"""
        changes_log = "/opt/odoo/migration/logs/changes_fixed.log"
        
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
    
    def check_zoho_odoo_counts(self):
        """Check and compare product counts between Zoho and Odoo"""
        print("📊 PRODUCT COUNT COMPARISON")
        print("=" * 50)
        
        try:
            # Use the fixed service to get counts
            sync_service = ZohoOdooSyncServiceWithImagesFixed()
            
            print("🔍 Fetching product counts...")
            
            # Get Zoho products
            zoho_products = sync_service.fetch_all_zoho_products()
            zoho_count = len(zoho_products)
            
            # Get Odoo products
            odoo_products = sync_service.fetch_all_odoo_products()
            odoo_count = len(odoo_products)
            
            # Count Odoo products with Zoho IDs
            odoo_with_zoho_id = sum(1 for p in odoo_products if p.get('x_zoho_item_id'))
            
            print(f"📦 Zoho Books Products: {zoho_count}")
            print(f"📦 Odoo Products (Total): {odoo_count}")
            print(f"🆔 Odoo Products with Zoho ID: {odoo_with_zoho_id}")
            print(f"🎯 Match Status: {'✅ SYNCHRONIZED' if zoho_count == odoo_with_zoho_id else '❌ NOT SYNCHRONIZED'}")
            print(f"📊 Difference: {zoho_count - odoo_with_zoho_id}")
            
            if zoho_count != odoo_with_zoho_id:
                print(f"\n💡 Recommendation: Run sync to synchronize all products")
            
        except Exception as e:
            print(f"❌ Error checking counts: {e}")


def main():
    manager = SyncServiceManagerFixed()
    
    if len(sys.argv) < 2:
        print("🔄 Fixed Zoho-Odoo Sync Service Manager with Images & Unique IDs")
        print("=" * 80)
        print("Usage: python3 sync_service_manager_fixed.py <command>")
        print()
        print("Commands:")
        print("  install     - Install and enable the fixed service")
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
        print("  counts      - Compare Zoho vs Odoo product counts")
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
        
        print("📊 FIXED SERVICE STATUS")
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
    
    elif command == "counts":
        manager.check_zoho_odoo_counts()
    
    elif command == "monitor":
        print("📊 Live Fixed Service Monitoring (Ctrl+C to stop)")
        print("=" * 60)
        
        try:
            while True:
                is_active, is_enabled = manager.get_service_status()
                current_time = datetime.now().strftime("%H:%M:%S")
                
                status = "🟢 RUNNING" if is_active else "🔴 STOPPED"
                print(f"\r[{current_time}] Fixed Service Status: {status}", end="", flush=True)
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print(f"\n👋 Monitoring stopped")
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main() 