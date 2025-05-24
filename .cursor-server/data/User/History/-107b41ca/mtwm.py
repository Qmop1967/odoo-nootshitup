#!/usr/bin/env python3

import xmlrpc.client
import json
import logging
from collections import defaultdict
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DuplicateContactFixer:
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
        """Normalize string for comparison"""
        if not text:
            return ""
        # Remove extra spaces, convert to lowercase, remove special chars
        return re.sub(r'[^\w\s]', '', str(text).lower().strip())

    def normalize_email(self, email):
        """Normalize email for comparison"""
        if not email:
            return ""
        return str(email).lower().strip()

    def normalize_phone(self, phone):
        """Normalize phone for comparison"""
        if not phone:
            return ""
        # Remove all non-digit characters
        return re.sub(r'[^\d]', '', str(phone))

    def find_duplicates(self):
        """Find duplicate contacts based on name, email, and phone"""
        logger.info("🔍 Fetching all contacts from Odoo...")
        
        # Fetch all contacts with relevant fields
        contacts = self.models.execute_kw(
            self.odoo_db_config['database'], 
            self.uid, 
            self.odoo_db_config['password'],
            'res.partner', 
            'search_read', 
            [[]],
            {
                'fields': ['id', 'name', 'email', 'phone', 'mobile', 'vat', 'is_company', 
                          'customer_rank', 'supplier_rank', 'create_date', 'street', 'city'],
                'order': 'create_date desc'
            }
        )
        
        logger.info(f"📊 Total contacts found: {len(contacts)}")
        
        # Group contacts by normalized identifiers
        name_groups = defaultdict(list)
        email_groups = defaultdict(list)
        phone_groups = defaultdict(list)
        
        for contact in contacts:
            # Group by name
            normalized_name = self.normalize_string(contact.get('name', ''))
            if normalized_name:
                name_groups[normalized_name].append(contact)
            
            # Group by email
            normalized_email = self.normalize_email(contact.get('email', ''))
            if normalized_email:
                email_groups[normalized_email].append(contact)
            
            # Group by phone (check both phone and mobile)
            for phone_field in ['phone', 'mobile']:
                normalized_phone = self.normalize_phone(contact.get(phone_field, ''))
                if normalized_phone and len(normalized_phone) >= 7:  # Minimum phone length
                    phone_groups[normalized_phone].append(contact)
        
        # Find duplicates
        duplicates = {}
        
        # Name-based duplicates
        for name, contacts_list in name_groups.items():
            if len(contacts_list) > 1:
                duplicates[f"name:{name}"] = {
                    'type': 'name',
                    'identifier': name,
                    'contacts': contacts_list,
                    'count': len(contacts_list)
                }
        
        # Email-based duplicates
        for email, contacts_list in email_groups.items():
            if len(contacts_list) > 1:
                duplicates[f"email:{email}"] = {
                    'type': 'email',
                    'identifier': email,
                    'contacts': contacts_list,
                    'count': len(contacts_list)
                }
        
        # Phone-based duplicates
        for phone, contacts_list in phone_groups.items():
            if len(contacts_list) > 1:
                duplicates[f"phone:{phone}"] = {
                    'type': 'phone',
                    'identifier': phone,
                    'contacts': contacts_list,
                    'count': len(contacts_list)
                }
        
        return duplicates

    def analyze_duplicates(self, duplicates):
        """Analyze and report on duplicates"""
        logger.info("\n" + "="*80)
        logger.info("📊 DUPLICATE ANALYSIS REPORT")
        logger.info("="*80)
        
        if not duplicates:
            logger.info("✅ No duplicates found!")
            return
        
        total_duplicate_contacts = 0
        
        for duplicate_key, duplicate_info in duplicates.items():
            duplicate_type = duplicate_info['type']
            identifier = duplicate_info['identifier']
            contacts = duplicate_info['contacts']
            count = duplicate_info['count']
            
            logger.info(f"\n🔍 Duplicate group by {duplicate_type.upper()}: '{identifier}'")
            logger.info(f"   📈 Number of duplicates: {count}")
            
            total_duplicate_contacts += count - 1  # -1 because one is the original
            
            for i, contact in enumerate(contacts, 1):
                logger.info(f"   {i}. ID: {contact['id']} | Name: {contact['name']} | "
                          f"Email: {contact.get('email', 'N/A')} | Phone: {contact.get('phone', 'N/A')} | "
                          f"Created: {contact.get('create_date', 'N/A')}")
        
        logger.info(f"\n📊 SUMMARY:")
        logger.info(f"   🔢 Total duplicate groups: {len(duplicates)}")
        logger.info(f"   👥 Total duplicate contacts (excluding originals): {total_duplicate_contacts}")
        logger.info("="*80)

    def merge_contacts(self, duplicates, dry_run=True):
        """Merge duplicate contacts - keeping the oldest one"""
        logger.info("\n🔄 Starting contact merge process...")
        
        if dry_run:
            logger.info("🚨 DRY RUN MODE - No actual changes will be made")
        
        merged_count = 0
        error_count = 0
        
        for duplicate_key, duplicate_info in duplicates.items():
            try:
                contacts = duplicate_info['contacts']
                
                # Sort by create_date to keep the oldest
                contacts.sort(key=lambda x: x.get('create_date', ''))
                keeper = contacts[0]  # Keep the oldest
                duplicates_to_remove = contacts[1:]  # Remove the rest
                
                logger.info(f"\n🔧 Merging {duplicate_info['type']} duplicates for: {duplicate_info['identifier']}")
                logger.info(f"   ✅ Keeping: ID {keeper['id']} - {keeper['name']} (Created: {keeper.get('create_date', 'N/A')})")
                
                if not dry_run:
                    # Here you could implement more sophisticated merging logic
                    # For now, we'll just delete the duplicates
                    for duplicate in duplicates_to_remove:
                        logger.info(f"   🗑️  Removing: ID {duplicate['id']} - {duplicate['name']}")
                        
                        # Check if contact has related records (invoices, sales orders, etc.)
                        has_relations = self.check_contact_relations(duplicate['id'])
                        
                        if has_relations:
                            logger.warning(f"   ⚠️  Contact ID {duplicate['id']} has related records. Consider manual review.")
                            # You might want to merge the related records or handle differently
                            continue
                        
                        # Delete the duplicate contact
                        self.models.execute_kw(
                            self.odoo_db_config['database'], 
                            self.uid, 
                            self.odoo_db_config['password'],
                            'res.partner', 
                            'unlink', 
                            [[duplicate['id']]]
                        )
                        merged_count += 1
                else:
                    for duplicate in duplicates_to_remove:
                        logger.info(f"   🗑️  Would remove: ID {duplicate['id']} - {duplicate['name']}")
                        merged_count += 1
                
            except Exception as e:
                error_count += 1
                logger.error(f"❌ Error merging {duplicate_key}: {e}")
        
        logger.info(f"\n📊 MERGE SUMMARY:")
        logger.info(f"   ✅ Contacts processed: {merged_count}")
        logger.info(f"   ❌ Errors: {error_count}")
        if dry_run:
            logger.info("   🚨 This was a DRY RUN - no actual changes made")

    def check_contact_relations(self, contact_id):
        """Check if contact has any related records"""
        try:
            # Check for invoices
            invoice_count = self.models.execute_kw(
                self.odoo_db_config['database'], 
                self.uid, 
                self.odoo_db_config['password'],
                'account.move', 
                'search_count', 
                [[('partner_id', '=', contact_id)]]
            )
            
            # Check for sales orders
            sale_count = self.models.execute_kw(
                self.odoo_db_config['database'], 
                self.uid, 
                self.odoo_db_config['password'],
                'sale.order', 
                'search_count', 
                [[('partner_id', '=', contact_id)]]
            )
            
            # Check for purchase orders
            purchase_count = self.models.execute_kw(
                self.odoo_db_config['database'], 
                self.uid, 
                self.odoo_db_config['password'],
                'purchase.order', 
                'search_count', 
                [[('partner_id', '=', contact_id)]]
            )
            
            return invoice_count > 0 or sale_count > 0 or purchase_count > 0
            
        except Exception as e:
            logger.warning(f"Could not check relations for contact {contact_id}: {e}")
            return True  # Assume it has relations to be safe

    def create_backup_prevention_rules(self):
        """Create rules to prevent future duplicates (example implementation)"""
        logger.info("\n🛡️  Creating duplicate prevention measures...")
        
        # This is a conceptual example - actual implementation would depend on Odoo version
        # and available modules
        logger.info("   💡 Recommendations for preventing future duplicates:")
        logger.info("   1. Enable partner deduplication module if available")
        logger.info("   2. Add email uniqueness constraint")
        logger.info("   3. Implement pre-creation duplicate checks in migration scripts")
        logger.info("   4. Use external IDs for tracking migrated records")

def main():
    logger.info("🚀 Starting Duplicate Contact Analysis and Fix")
    logger.info("="*60)
    
    fixer = DuplicateContactFixer()
    
    # Step 1: Find duplicates
    duplicates = fixer.find_duplicates()
    
    # Step 2: Analyze and report
    fixer.analyze_duplicates(duplicates)
    
    if duplicates:
        # Step 3: Ask user for confirmation
        print("\n" + "="*60)
        print("🤔 What would you like to do?")
        print("1. Perform DRY RUN (show what would be merged)")
        print("2. ACTUALLY MERGE duplicates (CAUTION: This will delete contacts)")
        print("3. Exit without making changes")
        print("="*60)
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            fixer.merge_contacts(duplicates, dry_run=True)
        elif choice == "2":
            confirm = input("⚠️  Are you sure you want to ACTUALLY delete duplicate contacts? Type 'YES' to confirm: ")
            if confirm == "YES":
                fixer.merge_contacts(duplicates, dry_run=False)
            else:
                logger.info("❌ Merge cancelled.")
        else:
            logger.info("👋 Exiting without changes.")
    
    # Step 4: Provide prevention recommendations
    fixer.create_backup_prevention_rules()

if __name__ == "__main__":
    main() 