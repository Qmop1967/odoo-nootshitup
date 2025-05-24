#!/usr/bin/env python3

import xmlrpc.client
import json
import logging
from collections import defaultdict
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductStatusAnalyzer:
    def __init__(self):
        self.load_config()
        self.connect_to_odoo()
        
    def load_config(self):
        """Load configuration"""
        with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
            self.config = json.load(f)
        self.odoo_db_config = self.config['odoo']['test_db']
        
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
        
    def analyze_products(self):
        """Analyze products for duplicates, missing images, and currency issues"""
        logger.info("🔍 Analyzing products...")
        
        # Get all products
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
        
        logger.info(f"📊 Total products found: {len(products)}")
        
        # Analyze duplicates
        name_groups = defaultdict(list)
        code_groups = defaultdict(list)
        
        missing_images = []
        low_prices = []
        
        for product in products:
            # Group by name for duplicate detection
            name = product.get('name', '').strip().lower()
            if name:
                name_groups[name].append(product)
            
            # Group by product code
            code = product.get('default_code', '')
            if code:
                code_groups[code].append(product)
            
            # Check for missing images
            if not product.get('image_1920'):
                missing_images.append(product)
            
            # Check for suspicious prices (USD not converted to IQD)
            list_price = product.get('list_price', 0)
            standard_price = product.get('standard_price', 0)
            
            # Prices under 100 might be in USD (should be 150,000+ in IQD)
            if (list_price > 0 and list_price < 100) or (standard_price > 0 and standard_price < 100):
                low_prices.append(product)
        
        # Find duplicates
        name_duplicates = {name: products for name, products in name_groups.items() if len(products) > 1}
        code_duplicates = {code: products for code, products in code_groups.items() if len(products) > 1}
        
        # Report findings
        self.report_analysis(products, name_duplicates, code_duplicates, missing_images, low_prices)
        
        return {
            'total_products': len(products),
            'name_duplicates': name_duplicates,
            'code_duplicates': code_duplicates,
            'missing_images': missing_images,
            'suspicious_prices': low_prices
        }
    
    def report_analysis(self, products, name_duplicates, code_duplicates, missing_images, low_prices):
        """Report analysis results"""
        logger.info("\n" + "="*80)
        logger.info("📊 PRODUCT STATUS ANALYSIS REPORT")
        logger.info("="*80)
        
        logger.info(f"📦 Total Products: {len(products)}")
        logger.info(f"🔍 Name Duplicates: {len(name_duplicates)} groups")
        logger.info(f"🔗 Code Duplicates: {len(code_duplicates)} groups")
        logger.info(f"🖼️  Missing Images: {len(missing_images)} products")
        logger.info(f"💰 Suspicious Prices (likely USD): {len(low_prices)} products")
        
        # Sample missing images
        if missing_images:
            logger.info(f"\n📸 Sample products missing images:")
            for i, product in enumerate(missing_images[:5]):
                logger.info(f"   {i+1}. ID:{product['id']} - {product['name']}")
        
        # Sample suspicious prices
        if low_prices:
            logger.info(f"\n💸 Sample products with suspicious prices (likely USD):")
            for i, product in enumerate(low_prices[:5]):
                logger.info(f"   {i+1}. ID:{product['id']} - {product['name']} - List: {product.get('list_price', 0)} - Cost: {product.get('standard_price', 0)}")
        
        # Sample name duplicates
        if name_duplicates:
            logger.info(f"\n👥 Sample name duplicates:")
            for name, products in list(name_duplicates.items())[:3]:
                logger.info(f"   '{name}' - {len(products)} products:")
                for product in products:
                    logger.info(f"      ID:{product['id']} - {product['name']}")
        
        logger.info("="*80)

def main():
    analyzer = ProductStatusAnalyzer()
    analysis = analyzer.analyze_products()
    
    print(f"\nQuick Summary:")
    print(f"- Total products: {analysis['total_products']}")
    print(f"- Products missing images: {len(analysis['missing_images'])}")
    print(f"- Products with suspicious prices: {len(analysis['suspicious_prices'])}")
    print(f"- Duplicate groups by name: {len(analysis['name_duplicates'])}")

if __name__ == "__main__":
    main() 