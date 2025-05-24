#!/usr/bin/env python3
"""
Direct Migration Script
======================
Migrate data directly using extracted Zoho data without Odoo connection issues.
"""

import json
import os
from datetime import datetime

def load_extracted_data():
    """Load the extracted Zoho data"""
    
    data_files = {
        'contacts': '/opt/odoo/migration/data/zoho_books_contacts.json',
        'items': '/opt/odoo/migration/data/zoho_books_items.json', 
        'invoices': '/opt/odoo/migration/data/zoho_books_invoices.json',
        'bills': '/opt/odoo/migration/data/zoho_books_bills.json',
        'accounts': '/opt/odoo/migration/data/zoho_books_chartofaccounts.json',
        'inventory_items': '/opt/odoo/migration/data/zoho_inventory_items.json',
        'warehouses': '/opt/odoo/migration/data/zoho_inventory_warehouses.json',
        'sales_orders': '/opt/odoo/migration/data/zoho_inventory_salesorders.json',
        'purchase_orders': '/opt/odoo/migration/data/zoho_inventory_purchaseorders.json'
    }
    
    extracted_data = {}
    total_records = 0
    
    print("📊 LOADING EXTRACTED ZOHO DATA")
    print("=" * 50)
    
    for data_type, file_path in data_files.items():
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                extracted_data[data_type] = data
                count = len(data) if isinstance(data, list) else 1
                total_records += count
                print(f"✅ {data_type.title()}: {count} records")
        else:
            print(f"⚠️ {data_type.title()}: File not found")
            extracted_data[data_type] = []
    
    print(f"\n📈 TOTAL RECORDS: {total_records}")
    return extracted_data

def generate_migration_report(data):
    """Generate a comprehensive migration report"""
    
    report = {
        'migration_date': datetime.now().isoformat(),
        'source_system': 'Zoho (Books + Inventory)',
        'target_system': 'Odoo 18 Enterprise',
        'company_info': {
            'name': 'Tech Spider Hand Company For General Trading Ltd',
            'currency': 'USD',
            'country': 'Iraq (Baghdad)',
            'industry': 'Retail (E-Commerce and Offline)'
        },
        'data_summary': {},
        'migration_plan': []
    }
    
    # Analyze data
    for data_type, records in data.items():
        if records:
            count = len(records) if isinstance(records, list) else 1
            report['data_summary'][data_type] = {
                'count': count,
                'status': 'ready_for_import'
            }
            
            # Add to migration plan
            if data_type == 'contacts':
                report['migration_plan'].append({
                    'step': 1,
                    'action': 'Import Customers & Vendors',
                    'records': count,
                    'target_model': 'res.partner'
                })
            elif data_type == 'items':
                report['migration_plan'].append({
                    'step': 2, 
                    'action': 'Import Products',
                    'records': count,
                    'target_model': 'product.product'
                })
            elif data_type == 'accounts':
                report['migration_plan'].append({
                    'step': 3,
                    'action': 'Import Chart of Accounts', 
                    'records': count,
                    'target_model': 'account.account'
                })
            elif data_type == 'invoices':
                report['migration_plan'].append({
                    'step': 4,
                    'action': 'Import Customer Invoices',
                    'records': count, 
                    'target_model': 'account.move'
                })
            elif data_type == 'bills':
                report['migration_plan'].append({
                    'step': 5,
                    'action': 'Import Vendor Bills',
                    'records': count,
                    'target_model': 'account.move'
                })
            elif data_type == 'sales_orders':
                report['migration_plan'].append({
                    'step': 6,
                    'action': 'Import Sales Orders',
                    'records': count,
                    'target_model': 'sale.order'
                })
            elif data_type == 'purchase_orders':
                report['migration_plan'].append({
                    'step': 7,
                    'action': 'Import Purchase Orders', 
                    'records': count,
                    'target_model': 'purchase.order'
                })
    
    return report

def save_migration_report(report):
    """Save the migration report"""
    
    report_file = f"/opt/odoo/migration/reports/migration_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📋 Migration report saved: {report_file}")
    return report_file

def print_migration_summary(report):
    """Print a summary of the migration plan"""
    
    print("\n" + "=" * 60)
    print("🚀 MIGRATION PLAN SUMMARY")
    print("=" * 60)
    
    print(f"📅 Date: {report['migration_date']}")
    print(f"🏢 Company: {report['company_info']['name']}")
    print(f"💰 Currency: {report['company_info']['currency']}")
    print(f"🌍 Location: {report['company_info']['country']}")
    
    print(f"\n📊 DATA OVERVIEW:")
    total_records = sum(item['count'] for item in report['data_summary'].values())
    print(f"   Total Records: {total_records}")
    
    for data_type, info in report['data_summary'].items():
        print(f"   {data_type.title()}: {info['count']} records")
    
    print(f"\n📋 MIGRATION STEPS:")
    for step in sorted(report['migration_plan'], key=lambda x: x['step']):
        print(f"   {step['step']}. {step['action']}: {step['records']} records → {step['target_model']}")
    
    print(f"\n✅ STATUS: Ready for Odoo import")
    print(f"📁 Data files available in: /opt/odoo/migration/data/")
    print("=" * 60)

def main():
    """Main migration function"""
    
    print("🔄 STARTING DIRECT MIGRATION")
    print("=" * 50)
    
    # Load extracted data
    data = load_extracted_data()
    
    if not data:
        print("❌ No data found. Please run data extraction first.")
        return False
    
    # Generate migration report
    report = generate_migration_report(data)
    
    # Save report
    report_file = save_migration_report(report)
    
    # Print summary
    print_migration_summary(report)
    
    print(f"\n🎉 MIGRATION PREPARATION COMPLETE!")
    print(f"📋 Next steps:")
    print(f"   1. Review migration plan: {report_file}")
    print(f"   2. Fix Odoo connection issues")
    print(f"   3. Run actual data import to Odoo")
    
    return True

if __name__ == "__main__":
    main() 