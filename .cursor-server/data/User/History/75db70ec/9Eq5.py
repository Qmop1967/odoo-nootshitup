#!/usr/bin/env python3

import sys
import os
import logging
from datetime import datetime
from continuous_sync_server_enhanced import EnhancedContinuousSyncServer

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/odoo/migration/logs/pricelist_sync.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Run price list sync only"""
    print("💰 ZOHO-ODOO PRICE LIST SYNC")
    print("=" * 50)
    print("This will sync ONLY price lists from Zoho to Odoo")
    print("✅ Price Lists: Exact copy with all pricing rules")
    print("✅ Price List Items: Individual product pricing")
    print("✅ USD to IQD conversion: Automatic")
    print("=" * 50)
    
    try:
        # Create sync server instance
        sync_server = EnhancedContinuousSyncServer()
        
        logger.info("🚀 Starting price list synchronization...")
        start_time = datetime.now()
        
        # Run price list sync only
        added, updated, items_added = sync_server.sync_pricelists_exact_copy()
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        
        # Get final counts for verification
        zoho_pricelists = sync_server.fetch_all_zoho_pricelists()
        odoo_pricelists = sync_server.fetch_all_odoo_pricelists()
        
        zoho_count = len(zoho_pricelists)
        odoo_count = len(odoo_pricelists)
        
        # Save tracking data
        sync_server.save_sync_tracking()
        
        # Print summary
        print("\n" + "="*60)
        print("🎉 PRICE LIST SYNC COMPLETED!")
        print("="*60)
        print(f"💰 PRICE LIST SYNCHRONIZATION RESULTS:")
        print(f"   Zoho Price Lists: {zoho_count}")
        print(f"   Odoo Price Lists: {odoo_count}")
        print(f"   Price Lists Match: {'✅ YES' if zoho_count == odoo_count else '❌ NO'}")
        print(f"   ➕ Price Lists Added: {added}")
        print(f"   🔄 Price Lists Updated: {updated}")
        print(f"   📝 Price List Items Added: {items_added}")
        print(f"")
        print(f"⏱️  PERFORMANCE:")
        print(f"   Total Duration: {duration:.1f} seconds")
        print(f"   Average per Price List: {(duration/max(zoho_count, 1)):.2f} seconds")
        print("="*60)
        
        if zoho_count == odoo_count:
            logger.info("✅ Price list sync completed successfully - counts match!")
            return True
        else:
            logger.warning(f"⚠️  Price list counts don't match - Zoho: {zoho_count}, Odoo: {odoo_count}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Price list sync failed: {e}")
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 