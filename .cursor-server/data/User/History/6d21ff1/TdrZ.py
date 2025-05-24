#!/usr/bin/env python3

import json
import logging
from fix_product_migration_issues import ProductMigrationFixer
from check_product_status import ProductStatusAnalyzer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_small_batch():
    """Test fixes on a small batch of products"""
    print("🧪 Testing Product Migration Fixes on Small Batch")
    print("=" * 60)
    
    # Initialize components
    fixer = ProductMigrationFixer()
    analyzer = ProductStatusAnalyzer()
    
    # Get all products for analysis
    products = fixer.get_all_products()
    
    # Test on first 10 products only
    test_products = products[:10]
    
    print(f"📊 Testing on {len(test_products)} products")
    print("\n1. Current status of test products:")
    
    for i, product in enumerate(test_products, 1):
        list_price = product.get('list_price', 0)
        standard_price = product.get('standard_price', 0)
        has_image = 'Yes' if product.get('image_1920') else 'No'
        
        price_status = "USD" if (list_price > 0 and list_price < 100) or (standard_price > 0 and standard_price < 100) else "IQD"
        
        print(f"   {i}. {product['name'][:50]}")
        print(f"      Price: {list_price}/{standard_price} ({price_status}) | Image: {has_image}")
    
    print("\n2. Testing price conversion (dry run)...")
    price_count = fixer.fix_price_currency(products=test_products, dry_run=True)
    print(f"   ✅ Would convert {price_count} products")
    
    print("\n3. Testing image fetching (dry run, 3 products)...")
    image_count = fixer.fix_missing_images(products=test_products, dry_run=True, max_requests=3)
    print(f"   ✅ Would fetch {image_count} images")
    
    print("\n4. Testing duplicate detection (dry run)...")
    duplicate_count = fixer.remove_duplicates(products=test_products, dry_run=True)
    print(f"   ✅ Would remove {duplicate_count} duplicates")
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print(f"   💰 Price conversions needed: {price_count}")
    print(f"   🖼️  Images that could be fetched: {image_count}")
    print(f"   🗑️  Duplicates that would be removed: {duplicate_count}")
    print("=" * 60)
    
    # Ask if user wants to apply fixes to test batch
    if price_count > 0 or image_count > 0 or duplicate_count > 0:
        print("\n❓ Do you want to apply these fixes to the test batch? (y/n): ", end="")
        apply = input().lower().startswith('y')
        
        if apply:
            print("\n🚀 Applying fixes to test batch...")
            
            if price_count > 0:
                actual_price = fixer.fix_price_currency(products=test_products, dry_run=False)
                print(f"   💰 Converted {actual_price} product prices")
            
            if image_count > 0:
                actual_images = fixer.fix_missing_images(products=test_products, dry_run=False, max_requests=3)
                print(f"   🖼️  Fetched {actual_images} images")
            
            if duplicate_count > 0:
                actual_duplicates = fixer.remove_duplicates(products=test_products, dry_run=False)
                print(f"   🗑️  Removed {actual_duplicates} duplicates")
            
            print("✅ Test batch fixes completed!")
            
            # Show results
            print("\n📊 Verifying results...")
            updated_products = fixer.get_all_products()[:10]
            
            for i, product in enumerate(updated_products, 1):
                list_price = product.get('list_price', 0)
                standard_price = product.get('standard_price', 0)
                has_image = 'Yes' if product.get('image_1920') else 'No'
                
                price_status = "USD" if (list_price > 0 and list_price < 100) or (standard_price > 0 and standard_price < 100) else "IQD"
                
                print(f"   {i}. {product['name'][:50]}")
                print(f"      Price: {list_price:,.0f}/{standard_price:,.0f} ({price_status}) | Image: {has_image}")
        
        else:
            print("❌ Test fixes cancelled")
    
    else:
        print("✅ No fixes needed for test batch")

def main():
    try:
        test_small_batch()
    except Exception as e:
        logger.error(f"❌ Error during testing: {e}")
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main() 