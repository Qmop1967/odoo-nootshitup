#!/usr/bin/env python3

from fix_product_migration_issues import ProductMigrationFixer

def main():
    print("🖼️  Starting image fetch from Zoho...")
    
    fixer = ProductMigrationFixer()
    
    # Start with 50 products to test
    print("Testing with first 50 products...")
    count = fixer.fix_missing_images(dry_run=False, max_requests=50)
    print(f"✅ Fetched {count} images from Zoho")

if __name__ == "__main__":
    main() 