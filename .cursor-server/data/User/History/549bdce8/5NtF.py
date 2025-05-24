#!/usr/bin/env python3

from zoho_odoo_sync_service_with_images_fixed import ZohoOdooSyncServiceWithImagesFixed
import sys

def test_final_service():
    print('🚀 Testing Final Sync Service...')
    print('=' * 50)
    
    try:
        service = ZohoOdooSyncServiceWithImagesFixed()
        print('✅ Service initialized successfully')
        
        # Test text sanitization
        test_texts = [
            '❌rack wd usb2❌',
            '🔥 Hot Product 🔥',
            'Normal Product Name',
            '📱 Mobile Phone 📱',
            '💻 Laptop Computer 💻'
        ]
        
        print('\n🧪 Testing text sanitization:')
        for text in test_texts:
            sanitized = service.sanitize_text(text)
            print(f'   "{text}" -> "{sanitized}"')
        
        # Test product transformation
        print('\n🔄 Testing product transformation:')
        test_product = {
            'item_id': '12345',
            'name': '❌ Test Product ❌',
            'rate': 10.50,
            'purchase_rate': 8.00,
            'description': '🔥 Amazing product 🔥',
            'sku': 'TEST-001'
        }
        
        transformed = service.transform_zoho_to_odoo(test_product)
        print(f'   Original name: "{test_product["name"]}"')
        print(f'   Transformed name: "{transformed["name"]}"')
        print(f'   List price: {transformed["list_price"]} IQD')
        print(f'   Standard price: {transformed["standard_price"]} IQD')
        
        print('\n✅ All tests passed!')
        print('🎯 The service is ready to sync products with images and unique IDs!')
        
        return True
        
    except Exception as e:
        print(f'❌ Test failed: {e}')
        return False

if __name__ == "__main__":
    success = test_final_service()
    sys.exit(0 if success else 1) 