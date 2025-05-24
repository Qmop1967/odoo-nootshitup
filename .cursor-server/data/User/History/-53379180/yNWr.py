#!/usr/bin/env python3

import json
import time
import logging
import schedule
import threading
from datetime import datetime, timedelta
import os
import sys

# Add the migration directory to path
sys.path.insert(0, '/opt/odoo/migration')

from zoho_product_sync import ZohoProductSync

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/odoo/migration/logs/product_sync_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductSyncScheduler:
    def __init__(self):
        self.config_file = '/opt/odoo/migration/config/sync_schedule.json'
        self.load_schedule_config()
        self.is_running = False
        
    def load_schedule_config(self):
        """Load or create schedule configuration"""
        default_config = {
            'enabled': True,
            'sync_interval_hours': 4,  # Sync every 4 hours
            'force_full_sync_days': 7,  # Force full sync weekly
            'last_full_sync': None,
            'max_consecutive_errors': 5,
            'consecutive_errors': 0,
            'notifications': {
                'log_file': '/opt/odoo/migration/logs/sync_notifications.log',
                'email_on_error': False,
                'email_address': None
            }
        }
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            # Merge with defaults for any missing keys
            for key, value in default_config.items():
                if key not in self.config:
                    self.config[key] = value
        else:
            self.config = default_config
            
        self.save_config()
        
    def save_config(self):
        """Save schedule configuration"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def should_force_full_sync(self):
        """Check if we should do a full sync"""
        if not self.config.get('last_full_sync'):
            return True
            
        last_full_sync = datetime.fromisoformat(self.config['last_full_sync'])
        days_since_full_sync = (datetime.now() - last_full_sync).days
        
        return days_since_full_sync >= self.config['force_full_sync_days']
    
    def run_sync(self):
        """Run the product sync"""
        if self.is_running:
            logger.warning("⚠️  Sync already running, skipping this cycle")
            return
            
        self.is_running = True
        start_time = datetime.now()
        
        try:
            logger.info("🚀 Starting scheduled product sync...")
            
            # Check if we should do full sync
            force_full_sync = self.should_force_full_sync()
            if force_full_sync:
                logger.info("📅 Performing weekly full sync")
            
            # Create syncer and run
            syncer = ZohoProductSync()
            success = syncer.sync_products(force_full_sync=force_full_sync)
            
            if success:
                logger.info("✅ Scheduled sync completed successfully")
                self.config['consecutive_errors'] = 0
                
                if force_full_sync:
                    self.config['last_full_sync'] = datetime.now().isoformat()
                    
                self.log_notification(f"Product sync completed successfully at {datetime.now()}")
            else:
                self.handle_sync_error("Sync completed with issues")
                
        except Exception as e:
            self.handle_sync_error(f"Sync failed with error: {e}")
            
        finally:
            self.is_running = False
            duration = datetime.now() - start_time
            logger.info(f"⏱️  Sync duration: {duration}")
            self.save_config()
    
    def handle_sync_error(self, error_message):
        """Handle sync errors with escalation"""
        self.config['consecutive_errors'] += 1
        error_count = self.config['consecutive_errors']
        
        logger.error(f"❌ {error_message} (Error #{error_count})")
        
        if error_count >= self.config['max_consecutive_errors']:
            critical_message = f"CRITICAL: {error_count} consecutive sync failures. Manual intervention required."
            logger.critical(critical_message)
            self.log_notification(critical_message, level='CRITICAL')
            
            # Disable automatic sync to prevent spam
            self.config['enabled'] = False
            logger.critical("🔴 Automatic sync disabled due to consecutive failures")
        
        self.log_notification(error_message, level='ERROR')
    
    def log_notification(self, message, level='INFO'):
        """Log notification to separate file"""
        notification_file = self.config['notifications']['log_file']
        os.makedirs(os.path.dirname(notification_file), exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        with open(notification_file, 'a') as f:
            f.write(f"{timestamp} - {level} - {message}\n")
    
    def start_scheduler(self):
        """Start the sync scheduler"""
        if not self.config['enabled']:
            logger.warning("⚠️  Scheduler is disabled. Enable in config to start automatic sync.")
            return
            
        interval_hours = self.config['sync_interval_hours']
        logger.info(f"🕐 Starting product sync scheduler (every {interval_hours} hours)")
        
        # Schedule the sync
        schedule.every(interval_hours).hours.do(self.run_sync)
        
        # Also schedule immediate sync if more than interval has passed
        syncer = ZohoProductSync()
        sync_data = syncer.sync_data
        
        if sync_data.get('last_sync'):
            last_sync = datetime.fromisoformat(sync_data['last_sync'])
            hours_since_sync = (datetime.now() - last_sync).total_seconds() / 3600
            
            if hours_since_sync >= interval_hours:
                logger.info("⏰ Running immediate sync (interval exceeded)")
                threading.Thread(target=self.run_sync).start()
        else:
            logger.info("🆕 Running initial sync")
            threading.Thread(target=self.run_sync).start()
        
        # Keep the scheduler running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("👋 Scheduler stopped by user")
    
    def show_status(self):
        """Show current scheduler status"""
        print("📊 Product Sync Scheduler Status")
        print("="*50)
        print(f"Enabled: {self.config['enabled']}")
        print(f"Sync interval: Every {self.config['sync_interval_hours']} hours")
        print(f"Full sync interval: Every {self.config['force_full_sync_days']} days")
        print(f"Consecutive errors: {self.config['consecutive_errors']}")
        
        if self.config.get('last_full_sync'):
            last_full = datetime.fromisoformat(self.config['last_full_sync'])
            print(f"Last full sync: {last_full.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("Last full sync: Never")
        
        # Check sync data
        try:
            syncer = ZohoProductSync()
            sync_data = syncer.sync_data
            
            if sync_data.get('last_sync'):
                last_sync = datetime.fromisoformat(sync_data['last_sync'])
                print(f"Last sync: {last_sync.strftime('%Y-%m-%d %H:%M:%S')}")
                
                hours_since = (datetime.now() - last_sync).total_seconds() / 3600
                print(f"Hours since last sync: {hours_since:.1f}")
            else:
                print("Last sync: Never")
                
            stats = sync_data.get('sync_stats', {})
            print(f"Total products tracked: {stats.get('total_synced', 0)}")
            print(f"Last run - Added: {stats.get('last_run_added', 0)}, Updated: {stats.get('last_run_updated', 0)}")
            
        except Exception as e:
            print(f"Could not load sync data: {e}")
        
        print("="*50)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Product Sync Scheduler')
    parser.add_argument('action', choices=['start', 'status', 'config', 'run-now'], 
                       help='Action to perform')
    parser.add_argument('--enable', action='store_true', help='Enable scheduler')
    parser.add_argument('--disable', action='store_true', help='Disable scheduler')
    parser.add_argument('--interval', type=int, help='Set sync interval in hours')
    parser.add_argument('--full-sync-days', type=int, help='Set full sync interval in days')
    
    args = parser.parse_args()
    
    scheduler = ProductSyncScheduler()
    
    if args.action == 'status':
        scheduler.show_status()
        
    elif args.action == 'config':
        if args.enable:
            scheduler.config['enabled'] = True
            scheduler.config['consecutive_errors'] = 0  # Reset error count
            print("✅ Scheduler enabled")
            
        if args.disable:
            scheduler.config['enabled'] = False
            print("🔴 Scheduler disabled")
            
        if args.interval:
            scheduler.config['sync_interval_hours'] = args.interval
            print(f"⏰ Sync interval set to {args.interval} hours")
            
        if args.full_sync_days:
            scheduler.config['force_full_sync_days'] = args.full_sync_days
            print(f"📅 Full sync interval set to {args.full_sync_days} days")
            
        scheduler.save_config()
        scheduler.show_status()
        
    elif args.action == 'run-now':
        print("🚀 Running manual sync...")
        scheduler.run_sync()
        
    elif args.action == 'start':
        scheduler.start_scheduler()

if __name__ == "__main__":
    main() 