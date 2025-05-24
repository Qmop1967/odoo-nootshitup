#!/usr/bin/env python3
"""
Extract Zoho Data
================
Extract data from Zoho Books and Inventory APIs and save to files for analysis.
"""

import json
import requests
from datetime import datetime
import os

def get_zoho_access_token(config):
    """Get access token from refresh token"""
    token_data = {
        'grant_type': 'refresh_token',
        'client_id': config['client_id'],
        'client_secret': config['client_secret'],
        'refresh_token': config['refresh_token']
    }
    
    response = requests.post('https://accounts.zoho.com/oauth/v2/token', data=token_data)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print(f"❌ Token exchange failed: {response.text}")
        return None

def extract_zoho_books_data():
    """Extract data from Zoho Books"""
    print("📚 EXTRACTING ZOHO BOOKS DATA")
    print("=" * 40)
    
    with open('config/zoho_config.json', 'r') as f:
        config = json.load(f)
    
    books_config = config['zoho_books']
    access_token = get_zoho_access_token(books_config)
    
    if not access_token:
        return False
    
    headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
    base_url = books_config['base_url']
    org_id = books_config['organization_id']
    
    # Create data directory
    os.makedirs('data/extracted', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Extract different data types
    data_types = {
        'organization': f'{base_url}/organizations/{org_id}',
        'contacts': f'{base_url}/contacts?organization_id={org_id}',
        'items': f'{base_url}/items?organization_id={org_id}',
        'invoices': f'{base_url}/invoices?organization_id={org_id}',
        'bills': f'{base_url}/bills?organization_id={org_id}',
        'chartofaccounts': f'{base_url}/chartofaccounts?organization_id={org_id}',
        'taxes': f'{base_url}/settings/taxes?organization_id={org_id}'
    }
    
    extracted_data = {}
    
    for data_type, url in data_types.items():
        try:
            print(f"📥 Extracting {data_type}...")
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                extracted_data[data_type] = data
                
                # Count records
                if data_type == 'organization':
                    count = 1
                else:
                    count = len(data.get(data_type, []))
                
                print(f"✅ {data_type}: {count} records")
                
                # Save individual file
                filename = f'data/extracted/books_{data_type}_{timestamp}.json'
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                    
            else:
                print(f"❌ {data_type}: Failed - {response.status_code}")
                extracted_data[data_type] = None
                
        except Exception as e:
            print(f"❌ {data_type}: Exception - {e}")
            extracted_data[data_type] = None
    
    # Save combined file
    combined_file = f'data/extracted/books_all_data_{timestamp}.json'
    with open(combined_file, 'w') as f:
        json.dump(extracted_data, f, indent=2)
    
    print(f"💾 All Books data saved to: {combined_file}")
    return True

def extract_zoho_inventory_data():
    """Extract data from Zoho Inventory"""
    print("\n📦 EXTRACTING ZOHO INVENTORY DATA")
    print("=" * 40)
    
    with open('config/zoho_config.json', 'r') as f:
        config = json.load(f)
    
    inventory_config = config['zoho_inventory']
    access_token = get_zoho_access_token(inventory_config)
    
    if not access_token:
        return False
    
    headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
    base_url = inventory_config['base_url']
    org_id = inventory_config['organization_id']
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Extract different data types
    data_types = {
        'items': f'{base_url}/items?organization_id={org_id}',
        'warehouses': f'{base_url}/settings/warehouses?organization_id={org_id}',
        'salesorders': f'{base_url}/salesorders?organization_id={org_id}',
        'purchaseorders': f'{base_url}/purchaseorders?organization_id={org_id}',
        'inventoryadjustments': f'{base_url}/inventoryadjustments?organization_id={org_id}'
    }
    
    extracted_data = {}
    
    for data_type, url in data_types.items():
        try:
            print(f"📥 Extracting {data_type}...")
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                extracted_data[data_type] = data
                
                # Count records
                count = len(data.get(data_type, []))
                print(f"✅ {data_type}: {count} records")
                
                # Save individual file
                filename = f'data/extracted/inventory_{data_type}_{timestamp}.json'
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                    
            else:
                print(f"❌ {data_type}: Failed - {response.status_code}")
                extracted_data[data_type] = None
                
        except Exception as e:
            print(f"❌ {data_type}: Exception - {e}")
            extracted_data[data_type] = None
    
    # Save combined file
    combined_file = f'data/extracted/inventory_all_data_{timestamp}.json'
    with open(combined_file, 'w') as f:
        json.dump(extracted_data, f, indent=2)
    
    print(f"💾 All Inventory data saved to: {combined_file}")
    return True

def main():
    """Main extraction function"""
    print("🔄 ZOHO DATA EXTRACTION")
    print("=" * 50)
    
    # Extract from both systems
    books_success = extract_zoho_books_data()
    inventory_success = extract_zoho_inventory_data()
    
    print("\n" + "=" * 50)
    print("🎯 EXTRACTION SUMMARY:")
    print(f"   Zoho Books: {'✅ Success' if books_success else '❌ Failed'}")
    print(f"   Zoho Inventory: {'✅ Success' if inventory_success else '❌ Failed'}")
    
    if books_success and inventory_success:
        print("\n🎉 DATA EXTRACTION COMPLETED!")
        print("📁 Check the 'data/extracted/' directory for all files")
        print("🔍 Review the data before proceeding with Odoo import")
        return True
    else:
        print("\n❌ Some extractions failed.")
        return False

if __name__ == "__main__":
    main() 