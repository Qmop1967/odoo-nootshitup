#!/usr/bin/env python3

import xmlrpc.client
import json
import requests
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_migration_status():
    """Check current migration status"""
    
    # Connect to Odoo
    url = 'http://localhost:8069'
    db = 'odtshbrain'
    username = 'khaleel@tsh.sale'
    password = 'Zcbm.97531tsh'
    
    try:
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        logger.info("✅ Connected to Odoo successfully")
        
        # Check product count
        product_count = models.execute_kw(
            db, uid, password,
            'product.template', 'search_count', [[]]
        )
        
        logger.info(f"📊 Total products in Odoo: {product_count}")
        
        # Check recent products
        recent_products = models.execute_kw(
            db, uid, password,
            'product.template', 'search_read', [[]],
            {'fields': ['name', 'create_date', 'image_1920'], 'limit': 10, 'order': 'create_date desc'}
        )
        
        logger.info("📦 Latest products:")
        images_count = 0
        for product in recent_products:
            has_image = "📷" if product.get('image_1920') else "📄"
            if product.get('image_1920'):
                images_count += 1
            logger.info(f"  {has_image} {product['name']} ({product['create_date']})")
        
        logger.info(f"📷 Products with images: {images_count}/{len(recent_products)}")
        
        # Test Zoho connection
        logger.info("\n🔄 Testing Zoho connection...")
        test_zoho_connection()
        
    except Exception as e:
        logger.error(f"❌ Error checking migration status: {e}")

def test_zoho_connection():
    """Test Zoho API connection"""
    
    try:
        # Load config
        with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
            config = json.load(f)
        
        zoho_config = config['zoho_books']
        
        # Get access token
        token_url = "https://accounts.zoho.com/oauth/v2/token"
        token_params = {
            'refresh_token': zoho_config['refresh_token'],
            'client_id': zoho_config['client_id'],
            'client_secret': zoho_config['client_secret'],
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(token_url, data=token_params)
        
        if response.status_code == 200:
            logger.info("✅ Zoho token refresh successful")
            
            # Test items API
            access_token = response.json()['access_token']
            headers = {
                'Authorization': f'Zoho-oauthtoken {access_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'organization_id': zoho_config['organization_id'],
                'page': 1,
                'per_page': 1
            }
            
            items_response = requests.get(
                f"{zoho_config['base_url']}/items",
                headers=headers,
                params=params
            )
            
            if items_response.status_code == 200:
                data = items_response.json()
                total_items = data.get('page_context', {}).get('total', 0)
                logger.info(f"✅ Zoho API working - Total items available: {total_items}")
                
                # Check if there are items with images
                items = data.get('items', [])
                if items:
                    sample_item = items[0]
                    logger.info(f"📦 Sample item: {sample_item.get('name', 'Unknown')}")
                    if 'image_url' in sample_item or 'image' in sample_item:
                        logger.info("📷 Sample item has image URL")
                    else:
                        logger.info("📄 Sample item has no image URL")
                        
            else:
                logger.error(f"❌ Zoho items API failed: {items_response.status_code}")
                
        else:
            logger.error(f"❌ Zoho token refresh failed: {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Error testing Zoho connection: {e}")

if __name__ == "__main__":
    logger.info("🔍 MIGRATION PROGRESS CHECK")
    logger.info("=" * 50)
    check_migration_status()
    logger.info("=" * 50) 