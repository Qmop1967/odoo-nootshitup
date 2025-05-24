#!/usr/bin/env python3

import xmlrpc.client
import json
import logging
from collections import defaultdict
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InteractiveDuplicateResolver:
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

    def show_exact_duplicates(self, exact_duplicates):
        """Show exact duplicates"""
        logger.info(f"\n🎯 Found {len(exact_duplicates)} groups of EXACT duplicates")
        
        total_to_remove = 0
        for i, (signature, contacts) in enumerate(exact_duplicates.items(), 1):
            total_to_remove += len(contacts) - 1
            logger.info(f"\n📋 Group {i}: {len(contacts)} exact duplicates")
            for j, contact in enumerate(contacts, 1):
                logger.info(f"   {j}. ID: {contact['id']} | Name: {contact['name'][:50]}{'...' if len(contact['name']) > 50 else ''}")
                logger.info(f"      Email: {contact.get('email', 'N/A')} | Phone: {contact.get('phone', 'N/A')} | Created: {contact.get('create_date', 'N/A')}")
        
        logger.info(f"\n📊 Summary: {total_to_remove} exact duplicate contacts can be safely removed")
        return total_to_remove

    def auto_remove_exact_duplicates(self, exact_duplicates, dry_run=True):
        """Automatically remove exact duplicates, keeping the oldest"""
        logger.info(f"\n🔄 {'DRY RUN: ' if dry_run else ''}Removing exact duplicates...")
        
        removed_count = 0
        error_count = 0
        
        for signature, contacts in exact_duplicates.items():
            try:
                # Sort by create_date to keep the oldest
                contacts.sort(key=lambda x: x.get('create_date', ''))
                keeper = contacts[0]
                to_remove = contacts[1:]
                
                logger.info(f"\n✅ Keeping: ID {keeper['id']} - {keeper['name'][:50]}{'...' if len(keeper['name']) > 50 else ''}")
                
                for contact in to_remove:
                    if not dry_run:
                        # Check for relations before deleting
                        has_relations = self.check_contact_relations(contact['id'])
                        if has_relations:
                            logger.warning(f"   ⚠️  Skipping ID {contact['id']} - has related records")
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
                        logger.info(f"   🗑️  Removed: ID {contact['id']}")
                    else:
                        logger.info(f"   🗑️  Would remove: ID {contact['id']} - {contact['name'][:50]}{'...' if len(contact['name']) > 50 else ''}")
                    
                    removed_count += 1
                    
            except Exception as e:
                error_count += 1
                logger.error(f"❌ Error processing group: {e}")
        
        logger.info(f"\n📊 {'DRY RUN ' if dry_run else ''}Results:")
        logger.info(f"   ✅ Contacts {'would be ' if dry_run else ''}removed: {removed_count}")
        logger.info(f"   ❌ Errors: {error_count}")

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

def main():
    print("🚀 Interactive Duplicate Contact Resolver")
    print("="*60)
    
    resolver = InteractiveDuplicateResolver()
    
    # Get exact duplicates
    exact_duplicates = resolver.get_exact_duplicates()
    
    if not exact_duplicates:
        print("✅ No exact duplicates found!")
        return
    
    # Show duplicates
    total_to_remove = resolver.show_exact_duplicates(exact_duplicates)
    
    print("\n" + "="*60)
    print("🤔 What would you like to do?")
    print("1. DRY RUN - Show what would be removed (recommended first)")
    print("2. CREATE BACKUP and remove exact duplicates")
    print("3. Remove exact duplicates WITHOUT backup (not recommended)")
    print("4. Exit without changes")
    print("="*60)
    
    while True:
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == "1":
            resolver.auto_remove_exact_duplicates(exact_duplicates, dry_run=True)
            break
            
        elif choice == "2":
            confirm = input(f"⚠️  This will remove {total_to_remove} contacts after creating backup. Type 'YES' to confirm: ")
            if confirm == "YES":
                import time
                backup_file = resolver.create_backup()
                print(f"✅ Backup created: {backup_file}")
                resolver.auto_remove_exact_duplicates(exact_duplicates, dry_run=False)
                print("🎉 Exact duplicates removed successfully!")
            else:
                print("❌ Operation cancelled.")
            break
            
        elif choice == "3":
            confirm = input(f"⚠️  This will PERMANENTLY remove {total_to_remove} contacts WITHOUT backup. Type 'YES I UNDERSTAND' to confirm: ")
            if confirm == "YES I UNDERSTAND":
                resolver.auto_remove_exact_duplicates(exact_duplicates, dry_run=False)
                print("🎉 Exact duplicates removed!")
            else:
                print("❌ Operation cancelled.")
            break
            
        elif choice == "4":
            print("👋 Exiting without changes.")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    import time
    main() 