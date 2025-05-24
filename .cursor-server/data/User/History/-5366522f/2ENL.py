#!/usr/bin/env python3

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

class SyncMonitor:
    def __init__(self):
        self.tracking_file = '/opt/odoo/migration/data/sync_server/sync_tracking.json'
        self.log_file = '/opt/odoo/migration/logs/sync_server.log'
        
    def load_tracking_data(self):
        """Load sync tracking data"""
        if os.path.exists(self.tracking_file):
            with open(self.tracking_file, 'r') as f:
                return json.load(f)
        return None
    
    def get_last_log_entries(self, lines=20):
        """Get last log entries"""
        if not os.path.exists(self.log_file):
            return []
            
        try:
            with open(self.log_file, 'r') as f:
                all_lines = f.readlines()
                return all_lines[-lines:]
        except:
            return []
    
    def display_status(self):
        """Display comprehensive sync status"""
        print("🔄 CONTINUOUS SYNC SERVER MONITOR")
        print("=" * 60)
        
        # Load tracking data
        tracking_data = self.load_tracking_data()
        
        if not tracking_data:
            print("❌ No sync tracking data found")
            print("   The sync server has not been started yet.")
            return
        
        # Current timestamp
        now = datetime.now()
        print(f"📅 Current Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Last sync info
        last_sync = tracking_data.get('last_full_sync')
        if last_sync:
            last_sync_dt = datetime.fromisoformat(last_sync.replace('Z', '+00:00').replace('+00:00', ''))
            time_since = now - last_sync_dt
            print(f"🕐 Last Sync: {last_sync_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏰ Time Since: {time_since}")
        else:
            print("🕐 Last Sync: Never")
        
        # Sync history (last few syncs)
        sync_history = tracking_data.get('sync_history', [])
        if sync_history:
            print(f"\n📊 RECENT SYNC HISTORY (Last {min(5, len(sync_history))} syncs):")
            print("-" * 60)
            print(f"{'Time':<20} {'Zoho':<6} {'Odoo':<6} {'Added':<6} {'Updated':<8} {'Duration':<10}")
            print("-" * 60)
            
            for sync_record in sync_history[-5:]:
                sync_time = datetime.fromisoformat(sync_record['timestamp']).strftime('%m-%d %H:%M')
                zoho_count = sync_record.get('zoho_count', 0)
                odoo_after = sync_record.get('odoo_count_after', 0)
                added = sync_record.get('added', 0)
                updated = sync_record.get('updated', 0)
                duration = sync_record.get('duration', 0)
                
                print(f"{sync_time:<20} {zoho_count:<6} {odoo_after:<6} {added:<6} {updated:<8} {duration:<10.1f}s")
        
        # Current product tracking
        zoho_products = tracking_data.get('zoho_products', {})
        print(f"\n📦 PRODUCT TRACKING:")
        print(f"   Products being tracked: {len(zoho_products)}")
        
        # Count history
        if sync_history:
            latest_sync = sync_history[-1]
            zoho_count = latest_sync.get('zoho_count', 0)
            odoo_count = latest_sync.get('odoo_count_after', 0)
            match = zoho_count == odoo_count
            
            print(f"\n🎯 LATEST PRODUCT COUNTS:")
            print(f"   Zoho Products: {zoho_count}")
            print(f"   Odoo Products: {odoo_count}")
            print(f"   Count Match: {'✅ YES' if match else f'❌ NO (Difference: {zoho_count - odoo_count})'}")
        
        # Overall statistics
        total_syncs = len(sync_history)
        if total_syncs > 0:
            successful_syncs = sum(1 for s in sync_history if s.get('errors', 0) == 0)
            total_added = sum(s.get('added', 0) for s in sync_history)
            total_updated = sum(s.get('updated', 0) for s in sync_history)
            avg_duration = sum(s.get('duration', 0) for s in sync_history) / len(sync_history)
            
            print(f"\n📈 OVERALL STATISTICS:")
            print(f"   Total Syncs: {total_syncs}")
            print(f"   Successful: {successful_syncs} ({(successful_syncs/total_syncs)*100:.1f}%)")
            print(f"   Products Added: {total_added}")
            print(f"   Products Updated: {total_updated}")
            print(f"   Average Duration: {avg_duration:.1f} seconds")
        
        # Recent log entries
        print(f"\n📝 RECENT LOG ENTRIES:")
        print("-" * 60)
        log_entries = self.get_last_log_entries(10)
        for entry in log_entries:
            entry = entry.strip()
            if entry:
                # Colorize log levels
                if "ERROR" in entry:
                    print(f"❌ {entry}")
                elif "WARNING" in entry:
                    print(f"⚠️  {entry}")
                elif "INFO" in entry and ("✅" in entry or "completed" in entry):
                    print(f"✅ {entry}")
                else:
                    print(f"   {entry}")
        
        print("=" * 60)
    
    def watch_mode(self, interval=30):
        """Watch mode - refresh status every interval seconds"""
        print("👁️  WATCH MODE - Press Ctrl+C to exit")
        print(f"🔄 Refreshing every {interval} seconds...")
        
        try:
            while True:
                os.system('clear')  # Clear screen
                self.display_status()
                print(f"\n⏰ Refreshing in {interval} seconds... (Ctrl+C to exit)")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n👋 Exiting watch mode...")

def main():
    monitor = SyncMonitor()
    
    print("📊 Sync Server Monitor")
    print("=" * 40)
    print("1. Show current status")
    print("2. Watch mode (auto-refresh)")
    print("3. Exit")
    
    while True:
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            monitor.display_status()
            
        elif choice == '2':
            try:
                interval = int(input("Refresh interval in seconds (default 30): ") or "30")
                monitor.watch_mode(interval)
            except ValueError:
                print("❌ Invalid interval")
                
        elif choice == '3':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    main() 