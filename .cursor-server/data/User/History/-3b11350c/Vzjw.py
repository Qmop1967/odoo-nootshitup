#!/usr/bin/env python3

from zoho_odoo_sync_service_with_images_fixed import ZohoOdooSyncServiceWithImagesFixed

def test_fixed_sync():
    print('🚀 Testing Fixed Sync Service...')
    print('=' * 50)
    
    try:
        service = ZohoOdooSyncServiceWithImagesFixed()
        print('✅ Service initialized successfully')
        
        # Run one sync cycle
        success = service.run_sync_cycle()
        
        if success:
            print('✅ Sync cycle completed successfully')
            
            # Show results
            status = service.get_service_status()
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
            print('❌ Sync cycle failed')
            
    except Exception as e:
        print(f'❌ Test failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_sync() 