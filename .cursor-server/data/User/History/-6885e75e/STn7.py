#!/usr/bin/env python3

import xmlrpc.client
import json
import logging
import requests
import base64
import time
from collections import defaultdict
from datetime import datetime
import hashlib
import os
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductMigrationFixer:
    def __init__(self):
        self.load_config()
        self.connect_to_odoo()
        self.setup_directories()
        self.usd_to_iqd_rate = 1500  # 1 USD = 1500 IQD
        
    def load_config(self):
        """Load configuration"""
        with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
            self.config = json.load(f)
        self.odoo_db_config = self.config['odoo']['test_db']
        self.zoho_config = self.config['zoho_books']
        
    def connect_to_odoo(self):
        """Connect to Odoo"""
        url = f"http://{self.odoo_db_config['host']}:{self.odoo_db_config['port']}"
        
        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.uid = self.common.authenticate(
            self.odoo_db_config['database'], 
            self.odoo_db_config['username'], 
            self.odoo_db_config['password'], 
            {}
        )
        
        if not self.uid:
            raise Exception("Failed to authenticate with Odoo")
            
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        logger.info("✅ Connected to Odoo successfully")
        
    def setup_directories(self):
        """Setup directories for data and images"""
        self.images_dir = '/opt/odoo/migration/data/product_images'
        self.backup_dir = '/opt/odoo/migration/data/backups'
        
        Path(self.images_dir).mkdir(parents=True, exist_ok=True)
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)
        
    def get_zoho_access_token(self):
        """Get fresh access token from Zoho"""
        token_url = "https://accounts.zoho.com/oauth/v2/token"
        token_params = {
            'refresh_token': self.zoho_config['refresh_token'],
            'client_id': self.zoho_config['client_id'],
            'client_secret': self.zoho_config['client_secret'],
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(token_url, data=token_params)
        response.raise_for_status()
        return response.json()['access_token']
    
    def get_all_products(self):
        """Get all products from Odoo"""
        logger.info("🔍 Fetching all products from Odoo...")
        
        products = self.models.execute_kw(
            self.odoo_db_config['database'], 
            self.uid, 
            self.odoo_db_config['password'],
            'product.template', 
            'search_read', 
            [[]],
            {
                'fields': ['id', 'name', 'list_price', 'standard_price', 'image_1920', 
                          'default_code', 'create_date'],
                'order': 'create_date desc'
            }
        )
        
        logger.info(f"📊 Found {len(products)} products total")
        return products
    
    def fix_price_currency(self, products=None, dry_run=True):
        """Convert USD prices to IQD by multiplying by 1500"""
        logger.info("💰 Starting USD to IQD price conversion...")
        
        if products is None:
            products = self.get_all_products()
        
        if dry_run:
            logger.info("🚨 DRY RUN MODE - No actual changes will be made")
        
        converted_count = 0
        
        for product in products:
            list_price = product.get('list_price', 0)
            standard_price = product.get('standard_price', 0)
            
            # Check if prices look like USD (under 100)
            needs_conversion = False
            new_list_price = list_price
            new_standard_price = standard_price
            
            if list_price > 0 and list_price < 100:
                new_list_price = list_price * self.usd_to_iqd_rate
                needs_conversion = True
                
            if standard_price > 0 and standard_price < 100:
                new_standard_price = standard_price * self.usd_to_iqd_rate
                needs_conversion = True
            
            if needs_conversion:
                logger.info(f"💱 Converting: {product['name']}")
                logger.info(f"   List: ${list_price} → {new_list_price:,.0f} IQD")
                logger.info(f"   Cost: ${standard_price} → {new_standard_price:,.0f} IQD")
                
                if not dry_run:
                    try:
                        self.models.execute_kw(
                            self.odoo_db_config['database'], 
                            self.uid, 
                            self.odoo_db_config['password'],
                            'product.template', 
                            'write', 
                            [[product['id']], {
                                'list_price': new_list_price,
                                'standard_price': new_standard_price
                            }]
                        )
                        converted_count += 1
                        
                    except Exception as e:
                        logger.error(f"❌ Error updating {product['name']}: {e}")
                else:
                    converted_count += 1
        
        logger.info(f"✅ Price conversion complete: {converted_count} products converted")
        return converted_count
    
    def fetch_zoho_product_image(self, product_name, default_code=None):
        """Fetch product image from Zoho"""
        try:
            access_token = self.get_zoho_access_token()
            headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
            
            # Search for product in Zoho Books
            params = {
                'organization_id': self.zoho_config['organization_id'],
                'search_text': product_name[:50]  # Limit search text length
            }
            
            url = f"{self.zoho_config['base_url']}/items"
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                for item in items:
                    # Check if this is the right product
                    if (item.get('name', '').strip().lower() == product_name.strip().lower() or
                        (default_code and item.get('sku', '') == default_code)):
                        
                        # Try to get image URL
                        image_url = item.get('image_url') or item.get('image')
                        if image_url:
                            return self.download_image_from_url(image_url, product_name)
            
            # Try Zoho Inventory if available
            if hasattr(self.zoho_config, 'inventory_base_url'):
                inventory_url = f"{self.zoho_config['inventory_base_url']}/items"
                response = requests.get(inventory_url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items', [])
                    
                    for item in items:
                        if (item.get('name', '').strip().lower() == product_name.strip().lower() or
                            (default_code and item.get('sku', '') == default_code)):
                            
                            images = item.get('images', [])
                            if images and len(images) > 0:
                                image_url = images[0].get('image_url')
                                if image_url:
                                    return self.download_image_from_url(image_url, product_name)
                            
                            image_url = item.get('image_url')
                            if image_url:
                                return self.download_image_from_url(image_url, product_name)
            
        except Exception as e:
            logger.warning(f"⚠️  Error fetching image for {product_name}: {e}")
            
        return None
    
    def download_image_from_url(self, image_url, product_name):
        """Download image from URL and convert to base64"""
        try:
            # Use Zoho authentication if needed
            access_token = self.get_zoho_access_token()
            headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
            
            response = requests.get(image_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                image_data = response.content
                
                # Convert to base64
                base64_image = base64.b64encode(image_data).decode('utf-8')
                
                # Save locally for tracking
                safe_name = "".join(c for c in product_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                local_path = os.path.join(self.images_dir, f"{safe_name[:50]}.jpg")
                
                with open(local_path, 'wb') as f:
                    f.write(image_data)
                
                logger.info(f"   📸 Image downloaded: {safe_name}")
                return base64_image
                
        except Exception as e:
            logger.warning(f"⚠️  Error downloading image from {image_url}: {e}")
            
        return None
    
    def fix_missing_images(self, products=None, dry_run=True, max_requests=100):
        """Fetch missing images from Zoho"""
        logger.info("🖼️  Starting image recovery from Zoho...")
        
        if products is None:
            products = self.get_all_products()
        
        if dry_run:
            logger.info("🚨 DRY RUN MODE - No actual changes will be made")
        
        # Filter products without images
        products_without_images = [p for p in products if not p.get('image_1920')]
        logger.info(f"📊 Found {len(products_without_images)} products without images")
        
        if len(products_without_images) > max_requests:
            logger.info(f"⚠️  Limiting to first {max_requests} products to avoid API limits")
            products_without_images = products_without_images[:max_requests]
        
        images_found = 0
        
        for i, product in enumerate(products_without_images, 1):
            logger.info(f"[{i}/{len(products_without_images)}] Searching image for: {product['name']}")
            
            image_data = self.fetch_zoho_product_image(
                product['name'], 
                product.get('default_code')
            )
            
            if image_data:
                if not dry_run:
                    try:
                        self.models.execute_kw(
                            self.odoo_db_config['database'], 
                            self.uid, 
                            self.odoo_db_config['password'],
                            'product.template', 
                            'write', 
                            [[product['id']], {'image_1920': image_data}]
                        )
                        images_found += 1
                        logger.info(f"   ✅ Image updated in Odoo")
                        
                    except Exception as e:
                        logger.error(f"   ❌ Error updating image: {e}")
                else:
                    images_found += 1
                    logger.info(f"   ✅ Image would be updated (dry run)")
            else:
                logger.info(f"   ⚠️  No image found in Zoho")
            
            # Rate limiting
            time.sleep(1)  # 1 second between requests
        
        logger.info(f"✅ Image recovery complete: {images_found} images found")
        return images_found
    
    def remove_duplicates(self, products=None, dry_run=True):
        """Remove duplicate products keeping the oldest one"""
        logger.info("🔍 Starting duplicate removal...")
        
        if products is None:
            products = self.get_all_products()
        
        if dry_run:
            logger.info("🚨 DRY RUN MODE - No actual changes will be made")
        
        # Group by name
        name_groups = defaultdict(list)
        
        for product in products:
            name = product.get('name', '').strip().lower()
            if name:
                name_groups[name].append(product)
        
        # Find duplicates
        duplicates = {name: products for name, products in name_groups.items() if len(products) > 1}
        
        removed_count = 0
        
        for name, duplicate_products in duplicates.items():
            # Sort by create_date to keep the oldest
            duplicate_products.sort(key=lambda x: x.get('create_date', ''))
            
            keeper = duplicate_products[0]  # Keep the oldest
            to_remove = duplicate_products[1:]  # Remove the rest
            
            logger.info(f"🔧 Processing duplicates for: {name}")
            logger.info(f"   ✅ Keeping: ID {keeper['id']} (Created: {keeper.get('create_date', 'N/A')})")
            
            for duplicate in to_remove:
                logger.info(f"   🗑️  Removing: ID {duplicate['id']} (Created: {duplicate.get('create_date', 'N/A')})")
                
                if not dry_run:
                    try:
                        # Check if product has any dependencies (sales orders, etc.)
                        # For now, just delete - in production you might want more checks
                        self.models.execute_kw(
                            self.odoo_db_config['database'], 
                            self.uid, 
                            self.odoo_db_config['password'],
                            'product.template', 
                            'unlink', 
                            [[duplicate['id']]]
                        )
                        removed_count += 1
                        
                    except Exception as e:
                        logger.error(f"   ❌ Error removing duplicate {duplicate['id']}: {e}")
                else:
                    removed_count += 1
        
        logger.info(f"✅ Duplicate removal complete: {removed_count} duplicates removed")
        return removed_count

def main():
    fixer = ProductMigrationFixer()
    
    print("🔧 Product Migration Issues Fixer")
    print("=" * 60)
    print("This script will:")
    print("1. Convert USD prices to IQD (×1500)")
    print("2. Fetch missing images from Zoho")
    print("3. Remove duplicate products")
    print("=" * 60)
    
    while True:
        print("\nOptions:")
        print("1. Run full analysis (dry run)")
        print("2. Fix price currency (USD → IQD)")
        print("3. Fetch missing images from Zoho")
        print("4. Remove duplicate products")
        print("5. Run all fixes")
        print("6. Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            # Analysis
            from check_product_status import ProductStatusAnalyzer
            analyzer = ProductStatusAnalyzer()
            analyzer.analyze_products()
            
        elif choice == '2':
            # Price conversion
            dry_run = input("Dry run? (y/n): ").lower().startswith('y')
            count = fixer.fix_price_currency(dry_run=dry_run)
            print(f"✅ {count} products processed")
            
        elif choice == '3':
            # Image fetching
            dry_run = input("Dry run? (y/n): ").lower().startswith('y')
            max_requests = int(input("Max requests (default 100): ") or 100)
            count = fixer.fix_missing_images(dry_run=dry_run, max_requests=max_requests)
            print(f"✅ {count} images processed")
            
        elif choice == '4':
            # Duplicate removal
            dry_run = input("Dry run? (y/n): ").lower().startswith('y')
            count = fixer.remove_duplicates(dry_run=dry_run)
            print(f"✅ {count} duplicates processed")
            
        elif choice == '5':
            # Run all fixes
            dry_run = input("Dry run for all operations? (y/n): ").lower().startswith('y')
            max_images = int(input("Max image requests (default 50): ") or 50)
            
            print("\n🚀 Running all fixes...")
            
            price_count = fixer.fix_price_currency(dry_run=dry_run)
            print(f"   💰 Prices: {price_count} converted")
            
            image_count = fixer.fix_missing_images(dry_run=dry_run, max_requests=max_images)
            print(f"   🖼️  Images: {image_count} fetched")
            
            duplicate_count = fixer.remove_duplicates(dry_run=dry_run)
            print(f"   🗑️  Duplicates: {duplicate_count} removed")
            
            print("✅ All fixes completed!")
            
        elif choice == '6':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main() 