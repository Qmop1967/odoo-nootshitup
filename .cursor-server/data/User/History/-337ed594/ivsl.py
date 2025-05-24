#!/usr/bin/env python3

import os
import sys
import json
import subprocess
import signal
import time
from datetime import datetime
from pathlib import Path

class SyncServiceManager:
    """
    Manager for the Zoho-Odoo Sync Service
    """
    
    def __init__(self):
        self.service_script = '/opt/odoo/migration/zoho_odoo_sync_service_immediate.py'
        self.pid_file = '/opt/odoo/migration/data/sync_service/sync_service.pid'
        self.data_dir = '/opt/odoo/migration/data/sync_service'
        self.logs_dir = '/opt/odoo/migration/logs'
        
        # Ensure directories exist
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        Path(self.logs_dir).mkdir(parents=True, exist_ok=True)
    
    def is_service_running(self):
        """Check if the sync service is currently running"""
        if not os.path.exists(self.pid_file):
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is still running
            try:
                os.kill(pid, 0)  # Send signal 0 to check if process exists
                return True
            except OSError:
                # Process doesn't exist, remove stale PID file
                os.remove(self.pid_file)
                return False
                
        except (ValueError, FileNotFoundError):
            return False
    
    def start_service(self):
        """Start the sync service"""
        if self.is_service_running():
            print("⚠️  Sync service is already running")
            return False
        
        print("🚀 Starting Zoho-Odoo sync service...")
        
        try:
            # Start the service as a background process
            process = subprocess.Popen([
                'python3', self.service_script
            ], cwd='/opt/odoo/migration')
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Give it a moment to start
            time.sleep(2)
            
            if self.is_service_running():
                print("✅ Sync service started successfully")
                print(f"   PID: {process.pid}")
                print(f"   Logs: {self.logs_dir}/sync_service.log")
                return True
            else:
                print("❌ Failed to start sync service")
                return False
                
        except Exception as e:
            print(f"❌ Error starting service: {e}")
            return False
    
    def stop_service(self):
        """Stop the sync service"""
        if not self.is_service_running():
            print("ℹ️  Sync service is not running")
            return True
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            print(f"🛑 Stopping sync service (PID: {pid})...")
            
            # Send SIGTERM to gracefully stop the service
            os.kill(pid, signal.SIGTERM)
            
            # Wait for process to stop
            for i in range(10):
                time.sleep(1)
                if not self.is_service_running():
                    print("✅ Sync service stopped successfully")
                    return True
            
            # If it's still running, force kill
            try:
                os.kill(pid, signal.SIGKILL)
                print("⚠️  Force killed sync service")
            except OSError:
                pass
            
            # Remove PID file
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
            
            return True
            
        except Exception as e:
            print(f"❌ Error stopping service: {e}")
            return False
    
    def restart_service(self):
        """Restart the sync service"""
        print("🔄 Restarting sync service...")
        self.stop_service()
        time.sleep(2)
        return self.start_service()
    
    def get_service_status(self):
        """Get detailed service status"""
        status = {
            'running': self.is_service_running(),
            'pid': None,
            'last_sync': None,
            'stats': {}
        }
        
        # Get PID if running
        if status['running'] and os.path.exists(self.pid_file):
            try:
                with open(self.pid_file, 'r') as f:
                    status['pid'] = int(f.read().strip())
            except (ValueError, FileNotFoundError):
                pass
        
        # Get tracking data
        tracking_file = os.path.join(self.data_dir, 'sync_tracking.json')
        if os.path.exists(tracking_file):
            try:
                with open(tracking_file, 'r') as f:
                    tracking_data = json.load(f)
                
                status['last_sync'] = tracking_data.get('last_sync')
                
                # Get latest sync stats
                sync_history = tracking_data.get('sync_history', [])
                if sync_history:
                    latest_sync = sync_history[-1]
                    status['stats'] = {
                        'products_added': latest_sync.get('products_added', 0),
                        'products_updated': latest_sync.get('products_updated', 0),
                        'products_skipped': latest_sync.get('products_skipped', 0),
                        'products_errors': latest_sync.get('products_errors', 0),
                        'images_synced': latest_sync.get('images_synced', 0),
                        'conflicts_resolved': latest_sync.get('conflicts_resolved', 0),
                        'duration': latest_sync.get('duration', 0),
                        'timestamp': latest_sync.get('timestamp')
                    }
                
            except Exception:
                pass
        
        return status
    
    def show_recent_logs(self, lines=50):
        """Show recent log entries"""
        log_file = os.path.join(self.logs_dir, 'sync_service.log')
        
        if not os.path.exists(log_file):
            print("ℹ️  No log file found")
            return
        
        try:
            # Use tail to get last N lines
            result = subprocess.run(['tail', '-n', str(lines), log_file], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"\n📋 Last {lines} log entries:")
                print("=" * 80)
                print(result.stdout)
                print("=" * 80)
            else:
                print("❌ Failed to read log file")
                
        except Exception as e:
            print(f"❌ Error reading logs: {e}")
    
    def show_sync_history(self, count=10):
        """Show recent sync history"""
        tracking_file = os.path.join(self.data_dir, 'sync_tracking.json')
        
        if not os.path.exists(tracking_file):
            print("ℹ️  No sync history found")
            return
        
        try:
            with open(tracking_file, 'r') as f:
                tracking_data = json.load(f)
            
            sync_history = tracking_data.get('sync_history', [])
            
            if not sync_history:
                print("ℹ️  No sync history available")
                return
            
            print(f"\n📊 Last {min(count, len(sync_history))} sync cycles:")
            print("=" * 120)
            print(f"{'Timestamp':<20} {'Added':<6} {'Updated':<8} {'Skipped':<8} {'Errors':<6} {'Images':<7} {'Conflicts':<9} {'Duration':<8}")
            print("-" * 120)
            
            for sync_record in sync_history[-count:]:
                timestamp = sync_record.get('timestamp', '')[:19]  # Remove microseconds
                added = sync_record.get('products_added', 0)
                updated = sync_record.get('products_updated', 0)
                skipped = sync_record.get('products_skipped', 0)
                errors = sync_record.get('products_errors', 0)
                images = sync_record.get('images_synced', 0)
                conflicts = sync_record.get('conflicts_resolved', 0)
                duration = sync_record.get('duration', 0)
                
                print(f"{timestamp:<20} {added:<6} {updated:<8} {skipped:<8} {errors:<6} {images:<7} {conflicts:<9} {duration:<8.1f}s")
            
            print("=" * 120)
            
        except Exception as e:
            print(f"❌ Error reading sync history: {e}")
    
    def run_manual_sync(self):
        """Run a manual sync cycle"""
        if self.is_service_running():
            print("⚠️  Service is running. Manual sync may conflict with automated sync.")
            response = input("Continue anyway? (y/N): ").strip().lower()
            if response != 'y':
                return
        
        print("🔄 Running manual sync...")
        
        try:
            # Import and run sync directly
            sys.path.insert(0, '/opt/odoo/migration')
            
            # Import the service - handle both file names
            try:
                from zoho_odoo_sync_service_immediate import ZohoOdooSyncService
            except ImportError:
                try:
                    from zoho_odoo_sync_service_with_images import ZohoOdooSyncServiceWithImages as ZohoOdooSyncService
                except ImportError:
                    from zoho_odoo_sync_service import ZohoOdooSyncService
            
            sync_service = ZohoOdooSyncService()
            success = sync_service.run_sync_cycle()
            
            if success:
                print("✅ Manual sync completed successfully")
            else:
                print("❌ Manual sync failed")
                
        except Exception as e:
            print(f"❌ Error running manual sync: {e}")

def main():
    manager = SyncServiceManager()
    
    if len(sys.argv) < 2:
        print("Zoho-Odoo Sync Service Manager")
        print("=" * 50)
        print("Usage: python3 sync_manager_immediate.py <command>")
        print("")
        print("Commands:")
        print("  start     - Start the sync service")
        print("  stop      - Stop the sync service")
        print("  restart   - Restart the sync service")
        print("  status    - Show service status")
        print("  logs      - Show recent log entries")
        print("  history   - Show sync history")
        print("  manual    - Run manual sync")
        print("  monitor   - Show live status updates")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        manager.start_service()
        
    elif command == 'stop':
        manager.stop_service()
        
    elif command == 'restart':
        manager.restart_service()
        
    elif command == 'status':
        status = manager.get_service_status()
        
        print("📊 Zoho-Odoo Sync Service Status")
        print("=" * 50)
        print(f"Running: {'✅ YES' if status['running'] else '❌ NO'}")
        
        if status['pid']:
            print(f"PID: {status['pid']}")
        
        if status['last_sync']:
            last_sync = datetime.fromisoformat(status['last_sync'].replace('Z', '+00:00'))
            print(f"Last Sync: {last_sync.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("Last Sync: Never")
        
        if status['stats']:
            stats = status['stats']
            print("\n📈 Latest Sync Results:")
            print(f"  ➕ Added: {stats['products_added']}")
            print(f"  🔄 Updated: {stats['products_updated']}")
            print(f"  ⏭️  Skipped: {stats['products_skipped']}")
            print(f"  ❌ Errors: {stats['products_errors']}")
            print(f"  🖼️  Images: {stats['images_synced']}")
            print(f"  ⚡ Conflicts: {stats['conflicts_resolved']}")
            print(f"  ⏱️  Duration: {stats['duration']:.1f}s")
        
    elif command == 'logs':
        lines = 50
        if len(sys.argv) > 2:
            try:
                lines = int(sys.argv[2])
            except ValueError:
                pass
        manager.show_recent_logs(lines)
        
    elif command == 'history':
        count = 10
        if len(sys.argv) > 2:
            try:
                count = int(sys.argv[2])
            except ValueError:
                pass
        manager.show_sync_history(count)
        
    elif command == 'manual':
        manager.run_manual_sync()
        
    elif command == 'monitor':
        print("📊 Live Service Monitor (Press Ctrl+C to exit)")
        print("=" * 60)
        
        try:
            while True:
                status = manager.get_service_status()
                
                # Clear screen
                os.system('clear' if os.name == 'posix' else 'cls')
                
                print("📊 Zoho-Odoo Sync Service - Live Monitor")
                print("=" * 60)
                print(f"Status: {'🟢 RUNNING' if status['running'] else '🔴 STOPPED'}")
                print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                if status['last_sync']:
                    last_sync = datetime.fromisoformat(status['last_sync'].replace('Z', '+00:00'))
                    time_diff = datetime.now() - last_sync
                    print(f"Last Sync: {last_sync.strftime('%H:%M:%S')} ({time_diff.total_seconds():.0f}s ago)")
                
                if status['stats']:
                    stats = status['stats']
                    print(f"\nLatest Results:")
                    print(f"  Added: {stats['products_added']:<4} Updated: {stats['products_updated']:<4}")
                    print(f"  Images: {stats['images_synced']:<3} Conflicts: {stats['conflicts_resolved']:<3}")
                
                print("\nPress Ctrl+C to exit...")
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n👋 Monitor stopped")
        
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python3 sync_manager_immediate.py' to see available commands")

if __name__ == "__main__":
    main() 