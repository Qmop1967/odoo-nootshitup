#!/usr/bin/env python3

import xmlrpc.client
import json
import logging
from collections import defaultdict
import re
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoDuplicateResolver:
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

    def normalize_string(self, text):
        if not text: return ""
        return re.sub(r'[^\w\s]', '', str(text).lower().strip())

    def normalize_email(self, email):
        if not email: return ""
        return str(email).lower().strip()

    def normalize_phone(self, phone):
        if not phone: return ""
        return re.sub(r'[^\d]', '', str(phone))

    def get_exact_duplicates(self):
        """Find exact duplicates (same name, email, and phone)"""
        logger.info("🔍 Finding exact duplicates...")
        
        contacts = self.models.execute_kw(
            self.odoo_db_config['database'], 
            self.uid, 
            self.odoo_db_config['password'],
            'res.partner', 
            'search_read', 
            [[]],
            {'fields': ['id', 'name', 'email', 'phone', 'mobile', 'create_date', 'customer_rank', 'supplier_rank']}
        )
        
        logger.info(f"📊 Analyzing {len(contacts)} contacts...")
        
        # Group by combination of normalized name + email + phone
        signature_groups = defaultdict(list)
        
        for contact in contacts:
            norm_name = self.normalize_string(contact.get('name', ''))
            norm_email = self.normalize_email(contact.get('email', ''))
            norm_phone = self.normalize_phone(contact.get('phone', '')) or self.normalize_phone(contact.get('mobile', ''))
            
            # Create a signature for exact matching
            signature = f"{norm_name}|{norm_email}|{norm_phone}"
            signature_groups[signature].append(contact)
        
        # Filter to only groups with duplicates
        exact_duplicates = {}
        for signature, contacts_list in signature_groups.items():
            if len(contacts_list) > 1:
                exact_duplicates[signature] = contacts_list
        
        return exact_duplicates

    def show_duplicate_summary(self, exact_duplicates):
        """Show a summary of exact duplicates"""
        if not exact_duplicates:
            logger.info("✅ No exact duplicates found!")
            return 0
        
        total_to_remove = sum(len(contacts) - 1 for contacts in exact_duplicates.values())
        
        logger.info(f"\n🎯 Found {len(exact_duplicates)} groups of EXACT duplicates")
        logger.info(f"📊 Total duplicate contacts to remove: {total_to_remove}")
        
        logger.info("\n📋 Sample duplicate groups:")
        for i, (signature, contacts) in enumerate(list(exact_duplicates.items())[:5], 1):
            logger.info(f"\n   Group {i}: {len(contacts)} exact duplicates")
            for j, contact in enumerate(contacts, 1):
                logger.info(f"      {j}. ID: {contact['id']} | {contact['name'][:40]}{'...' if len(contact['name']) > 40 else ''}")
                logger.info(f"         Email: {contact.get('email', 'N/A')} | Created: {contact.get('create_date', 'N/A')}")
        
        if len(exact_duplicates) > 5:
            logger.info(f"\n   ... and {len(exact_duplicates) - 5} more groups")
        
        return total_to_remove

    def create_backup(self):
        """Create a backup of contacts before making changes"""
        logger.info("💾 Creating backup of all contacts...")
        
        contacts = self.models.execute_kw(
            self.odoo_db_config['database'], 
            self.uid, 
            self.odoo_db_config['password'],
            'res.partner', 
            'search_read', 
            [[]],
            {'fields': ['id', 'name', 'email', 'phone', 'mobile', 'create_date', 'customer_rank', 'supplier_rank']}
        )
        
        backup_file = f'/opt/odoo/migration/backup_contacts_{int(time.time())}.json'
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(contacts, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Backup created: {backup_file}")
        return backup_file

    def remove_exact_duplicates(self, exact_duplicates):
        """Remove exact duplicates, keeping the oldest"""
        logger.info(f"\n🔄 Removing {sum(len(contacts) - 1 for contacts in exact_duplicates.values())} exact duplicates...")
        
        removed_count = 0
        skipped_count = 0
        error_count = 0
        
        for signature, contacts in exact_duplicates.items():
            try:
                # Sort by create_date to keep the oldest
                contacts.sort(key=lambda x: x.get('create_date', ''))
                keeper = contacts[0]
                to_remove = contacts[1:]
                
                logger.info(f"\n✅ Keeping: ID {keeper['id']} - {keeper['name'][:50]}{'...' if len(keeper['name']) > 50 else ''}")
                
                for contact in to_remove:
                    try:
                        # Check for relations before deleting
                        has_relations = self.check_contact_relations(contact['id'])
                        if has_relations:
                            logger.warning(f"   ⚠️  Skipping ID {contact['id']} - has related records")
                            skipped_count += 1
                            continue
                        
                        # Delete the contact
                        self.models.execute_kw(
                            self.odoo_db_config['database'], 
                            self.uid, 
                            self.odoo_db_config['password'],
                            'res.partner', 
                            'unlink', 
                            [[contact['id']]]
                        )
                        logger.info(f"   🗑️  Removed: ID {contact['id']} - {contact['name'][:50]}{'...' if len(contact['name']) > 50 else ''}")
                        removed_count += 1
                        
                    except Exception as e:
                        logger.error(f"   ❌ Error removing contact ID {contact['id']}: {e}")
                        error_count += 1
                    
            except Exception as e:
                error_count += 1
                logger.error(f"❌ Error processing group: {e}")
        
        logger.info(f"\n📊 REMOVAL SUMMARY:")
        logger.info(f"   ✅ Contacts removed: {removed_count}")
        logger.info(f"   ⚠️  Skipped (with relations): {skipped_count}")
        logger.info(f"   ❌ Errors: {error_count}")
        
        return removed_count, skipped_count, error_count

    def check_contact_relations(self, contact_id):
        """Check if contact has related records"""
        try:
            # Check invoices
            invoice_count = self.models.execute_kw(
                self.odoo_db_config['database'], 
                self.uid, 
                self.odoo_db_config['password'],
                'account.move', 
                'search_count', 
                [[('partner_id', '=', contact_id)]]
            )
            
            # Check sales orders
            sale_count = self.models.execute_kw(
                self.odoo_db_config['database'], 
                self.uid, 
                self.odoo_db_config['password'],
                'sale.order', 
                'search_count', 
                [[('partner_id', '=', contact_id)]]
            )
            
            return invoice_count > 0 or sale_count > 0
            
        except Exception:
            return True  # Assume has relations to be safe

def main():
    print("🚀 Automatic Duplicate Contact Resolver")
    print("="*60)
    
    resolver = AutoDuplicateResolver()
    
    # Step 1: Find exact duplicates
    exact_duplicates = resolver.get_exact_duplicates()
    
    # Step 2: Show summary
    total_to_remove = resolver.show_duplicate_summary(exact_duplicates)
    
    if total_to_remove == 0:
        print("✅ No duplicate contacts found to remove!")
        return
    
    # Step 3: Ask for confirmation
    print(f"\n⚠️  Found {total_to_remove} exact duplicate contacts to remove.")
    print("These are contacts with identical name, email, AND phone number.")
    print("The oldest contact in each group will be kept.")
    print("\nOptions:")
    print("1. Create backup and remove duplicates (RECOMMENDED)")
    print("2. Exit without changes")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == "1":
        # Create backup first
        backup_file = resolver.create_backup()
        print(f"✅ Backup created: {backup_file}")
        
        # Remove duplicates
        removed, skipped, errors = resolver.remove_exact_duplicates(exact_duplicates)
        
        print(f"\n🎉 Process completed!")
        print(f"   ✅ Removed: {removed} duplicate contacts")
        print(f"   ⚠️  Skipped: {skipped} (had related records)")
        print(f"   ❌ Errors: {errors}")
        
        if removed > 0:
            print(f"\n📊 Run this to see the updated stats:")
            print(f"   python3 quick_duplicate_check.py")
            
    else:
        print("👋 Exiting without changes.")

if __name__ == "__main__":
    main() 