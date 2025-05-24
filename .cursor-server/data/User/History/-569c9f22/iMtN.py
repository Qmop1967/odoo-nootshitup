#!/usr/bin/env python3

import xmlrpc.client
import json
import requests
import base64
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleImageFetcher:
    def __init__(self):
        self.load_config()
        self.connect_to_odoo()
        
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
    
    def get_zoho_access_token(self):
        """Get fresh access token from Zoho"""
        try:
            token_url = "https://accounts.zoho.com/oauth/v2/token"
            token_params = {
                'refresh_token': self.zoho_config['refresh_token'],
                'client_id': self.zoho_config['client_id'],
                'client_secret': self.zoho_config['client_secret'],
                'grant_type': 'refresh_token'
            }
            
            response = requests.post(token_url, data=token_params, timeout=30)
            response.raise_for_status()
            return response.json()['access_token']
        except Exception as e:
            logger.error(f"❌ Error getting Zoho token: {e}")
            return None
    
    def get_products_without_images(self, limit=20):
        """Get products that don't have images"""
        products = self.models.execute_kw(
            self.odoo_db_config['database'], 
            self.uid, 
            self.odoo_db_config['password'],
            'product.template', 
            'search_read', 
            [[('image_1920', '=', False)]],
            {
                'fields': ['id', 'name', 'default_code'],
                'limit': limit,
                'order': 'id desc'
            }
        )
        return products
    
    def search_product_in_zoho(self, product_name, access_token):
        """Search for product in Zoho and get image URL"""
        try:
            headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
            
            # Clean product name for search
            clean_name = product_name.replace('❌', '').strip()
            if len(clean_name) < 3:
                return None
                
            params = {
                'organization_id': self.zoho_config['organization_id'],
                'search_text': clean_name[:30]  # Shorter search text
            }
            
            url = f"{self.zoho_config['base_url']}/items"
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                for item in items:
                    item_name = item.get('name', '').lower()
                    search_name = clean_name.lower()
                    
                    # Simple name matching
                    if search_name in item_name or item_name in search_name:
                        # Look for image URL
                        image_url = item.get('image_url')
                        if image_url:
                            return image_url
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️  Error searching Zoho for {product_name}: {e}")
            return None
    
    def download_and_convert_image(self, image_url, access_token):
        """Download image and convert to base64"""
        try:
            headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
            response = requests.get(image_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                image_data = response.content
                base64_image = base64.b64encode(image_data).decode('utf-8')
                return base64_image
            else:
                # Try without auth headers (in case image is public)
                response = requests.get(image_url, timeout=30)
                if response.status_code == 200:
                    image_data = response.content
                    base64_image = base64.b64encode(image_data).decode('utf-8')
                    return base64_image
                    
        except Exception as e:
            logger.warning(f"⚠️  Error downloading image: {e}")
            
        return None
    
    def update_product_image(self, product_id, image_base64):
        """Update product with new image"""
        try:
            self.models.execute_kw(
                self.odoo_db_config['database'], 
                self.uid, 
                self.odoo_db_config['password'],
                'product.template', 
                'write', 
                [[product_id], {'image_1920': image_base64}]
            )
            return True
        except Exception as e:
            logger.error(f"❌ Error updating product {product_id}: {e}")
            return False
    
    def fetch_images_batch(self, batch_size=20):
        """Fetch images for a batch of products"""
        logger.info(f"🖼️  Starting image fetch for {batch_size} products...")
        
        # Get access token
        access_token = self.get_zoho_access_token()
        if not access_token:
            logger.error("❌ Could not get Zoho access token")
            return 0
        
        # Get products without images
        products = self.get_products_without_images(batch_size)
        logger.info(f"📊 Found {len(products)} products without images")
        
        if not products:
            logger.info("✅ No products need images!")
            return 0
        
        images_fetched = 0
        
        for i, product in enumerate(products, 1):
            product_name = product['name']
            product_id = product['id']
            
            logger.info(f"[{i}/{len(products)}] Processing: {product_name[:50]}")
            
            # Search for image in Zoho
            image_url = self.search_product_in_zoho(product_name, access_token)
            
            if image_url:
                logger.info(f"   📸 Found image URL: {image_url[:50]}...")
                
                # Download and convert image
                image_base64 = self.download_and_convert_image(image_url, access_token)
                
                if image_base64:
                    # Update product
                    if self.update_product_image(product_id, image_base64):
                        images_fetched += 1
                        logger.info(f"   ✅ Image updated for {product_name[:30]}")
                    else:
                        logger.error(f"   ❌ Failed to update image for {product_name[:30]}")
                else:
                    logger.warning(f"   ⚠️  Could not download image for {product_name[:30]}")
            else:
                logger.info(f"   ⚠️  No image found in Zoho for {product_name[:30]}")
            
            # Rate limiting - wait between requests
            time.sleep(2)
        
        logger.info(f"✅ Batch complete: {images_fetched} images fetched")
        return images_fetched

def main():
    print("🖼️  Simple Image Fetcher for Zoho Products")
    print("=" * 50)
    
    try:
        fetcher = SimpleImageFetcher()
        
        # Run 3 small batches
        total_fetched = 0
        
        for batch_num in range(1, 4):
            print(f"\n🔄 Running batch {batch_num}/3...")
            count = fetcher.fetch_images_batch(20)  # Small batches
            total_fetched += count
            
            print(f"📊 Batch {batch_num} result: {count} images fetched")
            
            if batch_num < 3:
                print("⏸️  Waiting 30 seconds before next batch...")
                time.sleep(30)
        
        print(f"\n🎉 All batches completed!")
        print(f"📊 Total images fetched: {total_fetched}")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    main() 