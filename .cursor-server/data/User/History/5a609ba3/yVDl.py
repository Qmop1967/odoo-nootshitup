#!/usr/bin/env python3

from fix_product_migration_issues import ProductMigrationFixer

def main():
    print("🗑️  Starting duplicate product removal...")
    
    fixer = ProductMigrationFixer()
    
    print("Removing duplicate products (keeping oldest)...")
    count = fixer.remove_duplicates(dry_run=False)
    print(f"✅ Removed {count} duplicate products")

if __name__ == "__main__":
    main() 