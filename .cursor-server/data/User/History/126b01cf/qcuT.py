#!/usr/bin/env python3

import json
import requests
import xmlrpc.client
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_zoho_access_token():
    """Get fresh access token from Zoho"""
    try:
        with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
            config = json.load(f)
        
        zoho_config = config['zoho_books']
        
        token_url = "https://accounts.zoho.com/oauth/v2/token"
        token_params = {
            'refresh_token': zoho_config['refresh_token'],
            'client_id': zoho_config['client_id'],
            'client_secret': zoho_config['client_secret'],
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(token_url, data=token_params, timeout=30)
        response.raise_for_status()
        return response.json()['access_token'], zoho_config
    except Exception as e:
        logger.error(f"❌ Error getting Zoho token: {e}")
        return None, None

def fetch_zoho_products():
    """Fetch products from Zoho Books"""
    logger.info("📦 Fetching products from Zoho Books...")
    
    access_token, zoho_config = get_zoho_access_token()
    if not access_token:
        return []
        
    headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
    all_products = []
    page = 1
    
    while True:
        try:
            params = {
                'organization_id': zoho_config['organization_id'],
                'page': page,
                'per_page': 200
            }
            
            url = f"{zoho_config['base_url']}/items"
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code != 200:
                break
                
            data = response.json()
            items = data.get('items', [])
            
            if not items:
                break
                
            all_products.extend(items)
            logger.info(f"   📄 Fetched page {page}: {len(items)} products")
            page += 1
            
        except Exception as e:
            logger.error(f"Error fetching page {page}: {e}")
            break
    
    logger.info(f"✅ Total products from Zoho: {len(all_products)}")
    return all_products

def connect_to_odoo():
    """Connect to Odoo"""
    with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
        config = json.load(f)
    
    odoo_config = config['odoo']['test_db']
    url = f"http://{odoo_config['host']}:{odoo_config['port']}"
    
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(
        odoo_config['database'], 
        odoo_config['username'], 
        odoo_config['password'], 
        {}
    )
    
    if not uid:
        raise Exception("Failed to authenticate with Odoo")
        
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    logger.info("✅ Connected to Odoo successfully")
    
    return models, uid, odoo_config

def create_simple_product(models, uid, odoo_config, zoho_product):
    """Create a simple product in Odoo"""
    try:
        # Simple product data - only essential fields
        product_data = {
            'name': zoho_product.get('name', f"Product {zoho_product.get('item_id')}"),
            'list_price': float(zoho_product.get('rate', 0)) * 1500,  # USD to IQD
            'standard_price': float(zoho_product.get('purchase_rate', 0)) * 1500,
            'type': 'product',
            'sale_ok': True,
            'purchase_ok': True,
        }
        
        # Add SKU if available
        if zoho_product.get('sku'):
            product_data['default_code'] = zoho_product['sku']
        
        # Add description if available
        if zoho_product.get('description'):
            product_data['description'] = zoho_product['description']
        
        product_id = models.execute_kw(
            odoo_config['database'], 
            uid, 
            odoo_config['password'],
            'product.template', 
            'create', 
            [product_data]
        )
        
        return product_id
        
    except Exception as e:
        logger.error(f"❌ Error creating product {zoho_product.get('name')}: {e}")
        return None

def main():
    print("🚀 Simple Product Sync - Getting your new Zoho products...")
    
    try:
        # Connect to systems
        models, uid, odoo_config = connect_to_odoo()
        zoho_products = fetch_zoho_products()
        
        if not zoho_products:
            print("❌ No products found in Zoho")
            return
        
        # Get existing Odoo products
        odoo_products = models.execute_kw(
            odoo_config['database'], 
            uid, 
            odoo_config['password'],
            'product.template', 
            'search_read', 
            [[]],
            {'fields': ['id', 'name', 'default_code']}
        )
        
        # Find existing product names/SKUs
        existing_names = {p['name'] for p in odoo_products}
        existing_skus = {p.get('default_code') for p in odoo_products if p.get('default_code')}
        
        print(f"📊 Found {len(zoho_products)} products in Zoho, {len(odoo_products)} in Odoo")
        
        # Sync new products
        new_products = 0
        for zoho_product in zoho_products:
            product_name = zoho_product.get('name', '')
            product_sku = zoho_product.get('sku', '')
            
            # Check if product already exists
            if product_name in existing_names or (product_sku and product_sku in existing_skus):
                continue
            
            # Create new product
            print(f"➕ Creating new product: {product_name}")
            product_id = create_simple_product(models, uid, odoo_config, zoho_product)
            
            if product_id:
                new_products += 1
                print(f"   ✅ Created product ID: {product_id}")
            else:
                print(f"   ❌ Failed to create product")
        
        print(f"\n🎉 Sync completed!")
        print(f"   ➕ New products added: {new_products}")
        print(f"   📦 Total Zoho products: {len(zoho_products)}")
        print(f"   📦 Total Odoo products: {len(odoo_products) + new_products}")
        
    except Exception as e:
        print(f"❌ Sync failed: {e}")

if __name__ == "__main__":
    main() 