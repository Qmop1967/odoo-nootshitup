#!/usr/bin/env python3

import time
from fix_product_migration_issues import ProductMigrationFixer
from quick_status import check_status

def run_image_batches():
    print("🖼️  Starting batch image fetching from Zoho...")
    print("=" * 60)
    
    fixer = ProductMigrationFixer()
    
    # Run multiple batches
    batch_size = 100  # Increased batch size
    total_batches = 5  # Run 5 batches
    
    total_fetched = 0
    
    for batch_num in range(1, total_batches + 1):
        print(f"\n🔄 Batch {batch_num}/{total_batches} - Fetching {batch_size} images...")
        
        try:
            count = fixer.fix_missing_images(dry_run=False, max_requests=batch_size)
            total_fetched += count
            
            print(f"✅ Batch {batch_num} completed: {count} images fetched")
            
            # Quick status check
            print(f"\n📊 Quick status after batch {batch_num}:")
            check_status()
            
            # Brief pause between batches to avoid overwhelming the API
            if batch_num < total_batches:
                print(f"⏸️  Pausing 30 seconds before next batch...")
                time.sleep(30)
                
        except Exception as e:
            print(f"❌ Error in batch {batch_num}: {e}")
            continue
    
    print(f"\n🎉 All batches completed!")
    print(f"📊 Total images fetched across all batches: {total_fetched}")
    
    # Final status
    print(f"\n📊 Final status:")
    check_status()

if __name__ == "__main__":
    run_image_batches() 