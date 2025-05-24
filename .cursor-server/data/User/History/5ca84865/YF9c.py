#!/usr/bin/env python3

import xmlrpc.client
import json
import logging
from collections import defaultdict
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def quick_duplicate_summary():
    """Quick summary of duplicate contacts"""
    
    # Load config
    with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
        config = json.load(f)
    odoo_db_config = config['odoo']['test_db']

    # Connect to Odoo
    url = f"http://{odoo_db_config['host']}:{odoo_db_config['port']}"
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(
        odoo_db_config['database'], 
        odoo_db_config['username'], 
        odoo_db_config['password'], 
        {}
    )
    
    if not uid:
        raise Exception("Failed to authenticate with Odoo")
        
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    logger.info("✅ Connected to Odoo successfully")

    # Fetch all contacts
    logger.info("🔍 Fetching contacts...")
    contacts = models.execute_kw(
        odoo_db_config['database'], 
        uid, 
        odoo_db_config['password'],
        'res.partner', 
        'search_read', 
        [[]],
        {'fields': ['id', 'name', 'email', 'phone', 'mobile', 'create_date']}
    )
    
    logger.info(f"📊 Total contacts: {len(contacts)}")
    
    # Normalize and group
    def normalize_string(text):
        if not text: return ""
        return re.sub(r'[^\w\s]', '', str(text).lower().strip())
    
    def normalize_email(email):
        if not email: return ""
        return str(email).lower().strip()
    
    def normalize_phone(phone):
        if not phone: return ""
        return re.sub(r'[^\d]', '', str(phone))

    name_groups = defaultdict(list)
    email_groups = defaultdict(list)
    phone_groups = defaultdict(list)
    
    for contact in contacts:
        # Group by name
        norm_name = normalize_string(contact.get('name', ''))
        if norm_name:
            name_groups[norm_name].append(contact)
        
        # Group by email
        norm_email = normalize_email(contact.get('email', ''))
        if norm_email:
            email_groups[norm_email].append(contact)
        
        # Group by phone
        for phone_field in ['phone', 'mobile']:
            norm_phone = normalize_phone(contact.get(phone_field, ''))
            if norm_phone and len(norm_phone) >= 7:
                phone_groups[norm_phone].append(contact)
    
    # Count duplicates
    name_duplicates = sum(1 for contacts_list in name_groups.values() if len(contacts_list) > 1)
    email_duplicates = sum(1 for contacts_list in email_groups.values() if len(contacts_list) > 1)
    phone_duplicates = sum(1 for contacts_list in phone_groups.values() if len(contacts_list) > 1)
    
    total_duplicate_contacts = (
        sum(len(contacts_list) - 1 for contacts_list in name_groups.values() if len(contacts_list) > 1) +
        sum(len(contacts_list) - 1 for contacts_list in email_groups.values() if len(contacts_list) > 1) +
        sum(len(contacts_list) - 1 for contacts_list in phone_groups.values() if len(contacts_list) > 1)
    )
    
    logger.info("\n" + "="*60)
    logger.info("📊 DUPLICATE CONTACTS SUMMARY")
    logger.info("="*60)
    logger.info(f"👥 Total contacts in database: {len(contacts)}")
    logger.info(f"📛 Duplicate groups by name: {name_duplicates}")
    logger.info(f"📧 Duplicate groups by email: {email_duplicates}")
    logger.info(f"📞 Duplicate groups by phone: {phone_duplicates}")
    logger.info(f"🗑️  Estimated duplicate contacts to remove: ~{total_duplicate_contacts}")
    logger.info("="*60)
    
    # Show a few examples
    logger.info("📝 Examples of duplicates:")
    
    example_count = 0
    for name, contacts_list in name_groups.items():
        if len(contacts_list) > 1 and example_count < 3:
            logger.info(f"   Name: '{contacts_list[0]['name']}' - {len(contacts_list)} duplicates")
            example_count += 1
    
    example_count = 0
    for email, contacts_list in email_groups.items():
        if len(contacts_list) > 1 and example_count < 3:
            logger.info(f"   Email: '{email}' - {len(contacts_list)} duplicates")
            example_count += 1

if __name__ == "__main__":
    quick_duplicate_summary() 