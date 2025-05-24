#!/usr/bin/env python3

import json
import requests
import pprint

def test_zoho_api():
    """Test Zoho Books API to see what fields are available"""
    
    # Load config
    with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
        config = json.load(f)
    
    zoho_config = config['zoho_books']
    
    # Get access token
    def get_access_token():
        token_url = "https://accounts.zoho.com/oauth/v2/token"
        token_params = {
            'refresh_token': zoho_config['refresh_token'],
            'client_id': zoho_config['client_id'],
            'client_secret': zoho_config['client_secret'],
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(token_url, data=token_params, timeout=30)
        response.raise_for_status()
        return response.json()['access_token']
    
    access_token = get_access_token()
    headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
    
    print("🔍 Testing Zoho Books API...")
    print("=" * 50)
    
    # Test 1: Get first few items to see structure
    print("📦 Fetching sample products from Zoho Books...")
    
    params = {
        'organization_id': zoho_config['organization_id'],
        'page': 1,
        'per_page': 5
    }
    
    url = f"{zoho_config['base_url']}/items"
    response = requests.get(url, headers=headers, params=params, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])
        
        print(f"✅ Found {len(items)} items")
        
        if items:
            print("\n📋 SAMPLE PRODUCT STRUCTURE:")
            print("=" * 40)
            
            for i, item in enumerate(items[:2], 1):
                print(f"\n🎯 Product {i}: {item.get('name', 'Unknown')}")
                print(f"   Item ID: {item.get('item_id')}")
                print(f"   SKU: {item.get('sku')}")
                print(f"   Rate: {item.get('rate')}")
                print(f"   Status: {item.get('status')}")
                
                # Check for image fields
                image_fields = ['image_url', 'image_document_id', 'image', 'image_name', 'documents']
                found_image_fields = {}
                
                for field in image_fields:
                    if field in item and item[field]:
                        found_image_fields[field] = item[field]
                
                if found_image_fields:
                    print(f"   🖼️ IMAGE FIELDS FOUND:")
                    for field, value in found_image_fields.items():
                        print(f"      {field}: {value}")
                else:
                    print(f"   📷 No image fields found")
                
                print(f"\n   📝 ALL FIELDS:")
                for key, value in item.items():
                    if key not in ['name', 'item_id', 'sku', 'rate', 'status']:
                        print(f"      {key}: {value}")
    else:
        print(f"❌ Failed to fetch items: {response.status_code}")
        print(f"Response: {response.text}")
    
    # Test 2: Try to get detailed item info
    print("\n" + "=" * 50)
    print("🔍 Testing detailed item fetch...")
    
    if items:
        first_item_id = items[0].get('item_id')
        if first_item_id:
            detail_url = f"{zoho_config['base_url']}/items/{first_item_id}"
            detail_params = {'organization_id': zoho_config['organization_id']}
            
            detail_response = requests.get(detail_url, headers=headers, params=detail_params, timeout=30)
            
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                item_detail = detail_data.get('item', {})
                
                print(f"✅ Detailed item info for ID {first_item_id}:")
                print(f"   Name: {item_detail.get('name')}")
                
                # Look for image-related fields in detail
                image_fields = ['image_url', 'image_document_id', 'image', 'image_name', 'documents', 'attachments']
                for field in image_fields:
                    if field in item_detail and item_detail[field]:
                        print(f"   🖼️ {field}: {item_detail[field]}")
                
                print(f"\n   📝 ALL DETAILED FIELDS:")
                pprint.pprint(item_detail, width=80, depth=3)
            else:
                print(f"❌ Failed to fetch item detail: {detail_response.status_code}")
    
    # Test 3: Check what the working sync service sees
    print("\n" + "=" * 50)
    print("🔍 Checking current sync tracking...")
    
    tracking_file = '/opt/odoo/migration/data/sync_service/sync_tracking_images.json'
    try:
        with open(tracking_file, 'r') as f:
            tracking_data = json.load(f)
        
        print(f"✅ Found tracking data")
        print(f"   Tracked products: {len(tracking_data.get('zoho_products', {}))}")
        print(f"   Tracked images: {len(tracking_data.get('product_images', {}))}")
        
        sync_history = tracking_data.get('sync_history', [])
        if sync_history:
            latest = sync_history[-1]
            print(f"   Last sync: {latest.get('timestamp')}")
            print(f"   Products added: {latest.get('products_added', 0)}")
            print(f"   Images synced: {latest.get('images_synced', 0)}")
    except FileNotFoundError:
        print("⚠️  No tracking data found - service hasn't run yet")
    except Exception as e:
        print(f"❌ Error reading tracking data: {e}")

if __name__ == "__main__":
    test_zoho_api() 