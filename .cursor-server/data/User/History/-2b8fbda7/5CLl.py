#!/usr/bin/env python3

import json
import requests
import xmlrpc.client
import logging
from datetime import datetime
import time
import base64
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImprovedContactMigrator:
    def __init__(self):
        self.load_config()
        self.connect_to_odoo()
        self.setup_country_state_mapping()
        self.existing_contacts = {}  # Cache for duplicate checking

    def load_config(self):
        """Load configuration"""
        with open('/opt/odoo/migration/config/zoho_config.json', 'r') as f:
            self.config = json.load(f)
        
        with open('/opt/odoo/migration/config/field_mapping.json', 'r') as f:
            self.field_mapping = json.load(f)
        
        self.zoho_config = self.config['zoho_books']
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

    def setup_country_state_mapping(self):
        """Setup country and state mapping from names/codes to Odoo IDs"""
        logger.info("🔄 Setting up Country/State mapping...")
        self.country_mapping = {}
        self.state_mapping = {}
        try:
            countries = self.models.execute_kw(
                self.odoo_db_config['database'], self.uid, self.odoo_db_config['password'],
                'res.country', 'search_read', [[]], {'fields': ['id', 'name', 'code']}
            )
            for country in countries:
                self.country_mapping[country['name'].lower()] = country['id']
                if country['code']:
                    self.country_mapping[country['code'].lower()] = country['id']
            
            states = self.models.execute_kw(
                self.odoo_db_config['database'], self.uid, self.odoo_db_config['password'],
                'res.country.state', 'search_read', [[]], {'fields': ['id', 'name', 'code', 'country_id']}
            )
            for state in states:
                self.state_mapping[state['name'].lower()] = state['id']
                if state['code']:
                     # Store with country to differentiate states with same code in different countries
                    self.state_mapping[f"{state['country_id'][0]}_{state['code'].lower()}"] = state['id']

            logger.info(f"✅ Country mapping created with {len(self.country_mapping)} countries.")
            logger.info(f"✅ State mapping created with {len(self.state_mapping)} states.")
        except Exception as e:
            logger.error(f"❌ Error setting up Country/State mapping: {e}. Address fields might not be mapped correctly.")

    def load_existing_contacts(self):
        """Load existing contacts for duplicate checking"""
        logger.info("🔄 Loading existing contacts for duplicate checking...")
        
        existing = self.models.execute_kw(
            self.odoo_db_config['database'], 
            self.uid, 
            self.odoo_db_config['password'],
            'res.partner', 
            'search_read', 
            [[]],
            {'fields': ['id', 'name', 'email', 'phone', 'mobile']}
        )
        
        # Create lookup dictionaries for fast duplicate checking
        for contact in existing:
            # Index by normalized name
            norm_name = self.normalize_string(contact.get('name', ''))
            if norm_name:
                if norm_name not in self.existing_contacts:
                    self.existing_contacts[norm_name] = []
                self.existing_contacts[norm_name].append(contact)
            
            # Index by email
            email = self.normalize_email(contact.get('email', ''))
            if email:
                key = f"email:{email}"
                if key not in self.existing_contacts:
                    self.existing_contacts[key] = []
                self.existing_contacts[key].append(contact)
            
            # Index by phone
            for phone_field in ['phone', 'mobile']:
                phone = self.normalize_phone(contact.get(phone_field, ''))
                if phone and len(phone) >= 7:
                    key = f"phone:{phone}"
                    if key not in self.existing_contacts:
                        self.existing_contacts[key] = []
                    self.existing_contacts[key].append(contact)
        
        logger.info(f"✅ Loaded {len(existing)} existing contacts for duplicate checking")

    def normalize_string(self, text):
        """Normalize string for comparison"""
        if not text:
            return ""
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
        return re.sub(r'[^\d]', '', str(phone))

    def check_for_duplicates(self, contact_data):
        """Check if contact already exists based on name, email, or phone"""
        potential_duplicates = []
        
        # Check by name
        norm_name = self.normalize_string(contact_data.get('name', ''))
        if norm_name and norm_name in self.existing_contacts:
            potential_duplicates.extend(self.existing_contacts[norm_name])
        
        # Check by email
        email = self.normalize_email(contact_data.get('email', ''))
        if email:
            key = f"email:{email}"
            if key in self.existing_contacts:
                potential_duplicates.extend(self.existing_contacts[key])
        
        # Check by phone
        for phone_field in ['phone', 'mobile']:
            if phone_field in contact_data:
                phone = self.normalize_phone(contact_data.get(phone_field, ''))
                if phone and len(phone) >= 7:
                    key = f"phone:{phone}"
                    if key in self.existing_contacts:
                        potential_duplicates.extend(self.existing_contacts[key])
        
        # Remove duplicates from the list and return unique matches
        seen_ids = set()
        unique_duplicates = []
        for dup in potential_duplicates:
            if dup['id'] not in seen_ids:
                unique_duplicates.append(dup)
                seen_ids.add(dup['id'])
        
        return unique_duplicates

    def get_country_id(self, country_name_or_code):
        if not country_name_or_code: return None
        return self.country_mapping.get(str(country_name_or_code).lower())

    def get_state_id(self, state_name_or_code, country_id=None):
        if not state_name_or_code: return None
        key = str(state_name_or_code).lower()
        if country_id and self.state_mapping.get(f"{country_id}_{key}"):
            return self.state_mapping.get(f"{country_id}_{key}")
        return self.state_mapping.get(key)

    def get_zoho_access_token(self):
        """Get fresh access token from Zoho"""
        token_url = "https://accounts.zoho.com/oauth/v2/token"
        token_params = {
            'refresh_token': self.zoho_config['refresh_token'],
            'client_id': self.zoho_config['client_id'],
            'client_secret': self.zoho_config['client_secret'],
            'grant_type': 'refresh_token'
        }
        response = requests.post(token_url, data=token_params)
        response.raise_for_status()
        return response.json()['access_token']

    def fetch_zoho_contacts(self, contact_type='customer'):
        """Fetch all contacts (customers or vendors) from Zoho Books"""
        access_token = self.get_zoho_access_token()
        headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
        
        all_contacts = []
        page = 1
        per_page = 200
        
        endpoint_url = f"{self.zoho_config['base_url']}/contacts"
        
        logger.info(f"Fetching Zoho {contact_type}s...")

        while True:
            params = {
                'organization_id': self.zoho_config['organization_id'],
                'page': page,
                'per_page': per_page,
            }
            
            try:
                response = requests.get(endpoint_url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to fetch page {page} for {contact_type}s: {e}")
                break
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON for page {page} for {contact_type}s: {e}. Response: {response.text}")
                break

            contacts_on_page = data.get('contacts', [])
            if not contacts_on_page:
                break
            
            # Filter based on contact_type
            if contact_type == 'customer':
                all_contacts.extend([c for c in contacts_on_page if c.get('contact_type') == 'customer'])
            elif contact_type == 'vendor':
                 all_contacts.extend([c for c in contacts_on_page if c.get('contact_type') == 'vendor'])
            else:
                all_contacts.extend(contacts_on_page)

            logger.info(f"Retrieved {len(contacts_on_page)} contacts from page {page}. Total {contact_type}s so far: {len(all_contacts)}")
            
            time.sleep(self.config.get('migration_settings', {}).get('delay_between_requests', 0.5))
            
            page_context = data.get('page_context', {})
            if not page_context.get('has_more_page', False):
                break
            page += 1
            
        logger.info(f"✅ Total {contact_type}s fetched from Zoho: {len(all_contacts)}")
        return all_contacts

    def transform_contact(self, zoho_contact, contact_mapping_config):
        """Transform a single Zoho contact to Odoo format"""
        odoo_contact = {}
        mapping = contact_mapping_config['zoho_books']

        for zoho_field, odoo_field_or_spec in mapping.items():
            if zoho_field in zoho_contact and zoho_contact[zoho_field] is not None:
                value = zoho_contact[zoho_field]
                if isinstance(odoo_field_or_spec, dict):
                    for zoho_addr_field, odoo_addr_field in odoo_field_or_spec.items():
                        if zoho_addr_field in value and value[zoho_addr_field]:
                            addr_val = value[zoho_addr_field]
                            if odoo_addr_field == 'country_id':
                                odoo_contact[odoo_addr_field] = self.get_country_id(addr_val)
                            elif odoo_addr_field == 'state_id':
                                country_id_for_state = odoo_contact.get('country_id')
                                odoo_contact[odoo_addr_field] = self.get_state_id(addr_val, country_id_for_state)
                            else:
                                odoo_contact[odoo_addr_field] = addr_val
                elif odoo_field_or_spec == 'currency_id': 
                    logger.debug(f"Skipping direct mapping of currency_id: {value} for contact {zoho_contact.get('contact_name')}")
                    pass
                else:
                    odoo_contact[odoo_field_or_spec] = value
        
        # Apply default values
        for field, def_value in contact_mapping_config.get('default_values', {}).items():
            odoo_contact[field] = def_value
        
        # Ensure required fields
        if 'name' not in odoo_contact or not odoo_contact['name']:
            odoo_contact['name'] = zoho_contact.get('contact_name') or zoho_contact.get('company_name') or f"Contact {zoho_contact.get('contact_id', 'Unknown')}"
        
        odoo_contact['name'] = str(odoo_contact['name']).strip()

        # Set is_company based on Zoho data
        if zoho_contact.get('company_name') and not zoho_contact.get('first_name'):
             odoo_contact['is_company'] = True
        elif 'is_company' not in odoo_contact:
             odoo_contact['is_company'] = False

        return odoo_contact

    def add_to_existing_cache(self, contact_id, contact_data):
        """Add newly created contact to the existing contacts cache"""
        contact_record = {'id': contact_id, 'name': contact_data.get('name', ''), 
                         'email': contact_data.get('email', ''), 
                         'phone': contact_data.get('phone', ''),
                         'mobile': contact_data.get('mobile', '')}
        
        # Add to name index
        norm_name = self.normalize_string(contact_data.get('name', ''))
        if norm_name:
            if norm_name not in self.existing_contacts:
                self.existing_contacts[norm_name] = []
            self.existing_contacts[norm_name].append(contact_record)
        
        # Add to email index
        email = self.normalize_email(contact_data.get('email', ''))
        if email:
            key = f"email:{email}"
            if key not in self.existing_contacts:
                self.existing_contacts[key] = []
            self.existing_contacts[key].append(contact_record)
        
        # Add to phone index
        for phone_field in ['phone', 'mobile']:
            phone = self.normalize_phone(contact_data.get(phone_field, ''))
            if phone and len(phone) >= 7:
                key = f"phone:{phone}"
                if key not in self.existing_contacts:
                    self.existing_contacts[key] = []
                self.existing_contacts[key].append(contact_record)

    def migrate_contact_type(self, contact_type_key):
        """Migrate a specific type of contacts with duplicate checking"""
        logger.info(f"🚀 Starting migration for {contact_type_key} with duplicate prevention...")
        contact_mapping_config = self.field_mapping[contact_type_key]
        odoo_model = contact_mapping_config['odoo_model']
        
        # Load existing contacts for duplicate checking
        self.load_existing_contacts()
        
        # Determine zoho_contact_type for fetching
        zoho_api_contact_type = 'customer' if contact_type_key == 'customers' else 'vendor'
        
        zoho_contacts = self.fetch_zoho_contacts(contact_type=zoho_api_contact_type)
        
        if not zoho_contacts:
            logger.warning(f"No {contact_type_key} found in Zoho to migrate.")
            return True

        success_count = 0
        error_count = 0
        duplicate_count = 0
        
        for i, zoho_contact in enumerate(zoho_contacts, 1):
            try:
                odoo_contact_payload = self.transform_contact(zoho_contact, contact_mapping_config)
                
                # Check for duplicates
                duplicates = self.check_for_duplicates(odoo_contact_payload)
                
                if duplicates:
                    duplicate_count += 1
                    logger.warning(f"[{i}/{len(zoho_contacts)}] DUPLICATE FOUND for {contact_type_key}: {odoo_contact_payload.get('name')}")
                    logger.warning(f"   🔍 Matches existing contact(s): {', '.join([f'ID {d['id']} ({d['name']})' for d in duplicates])}")
                    continue  # Skip creating duplicate
                
                logger.info(f"[{i}/{len(zoho_contacts)}] Migrating {contact_type_key}: {odoo_contact_payload.get('name')}")
                
                contact_id = self.models.execute_kw(
                    self.odoo_db_config['database'], 
                    self.uid, 
                    self.odoo_db_config['password'],
                    odoo_model, 
                    'create', 
                    [odoo_contact_payload]
                )
                
                if contact_id:
                    success_count += 1
                    # Add to cache for future duplicate checking in this session
                    self.add_to_existing_cache(contact_id, odoo_contact_payload)
                    
                    if success_count % 50 == 0:
                        logger.info(f"📊 Progress for {contact_type_key}: {success_count}/{len(zoho_contacts)} migrated.")
                else:
                    error_count += 1
                    logger.error(f"❌ Failed to create {contact_type_key}: {odoo_contact_payload.get('name')} in Odoo (no ID returned).")
                    
            except Exception as e:
                error_count += 1
                contact_name_for_log = zoho_contact.get('contact_name', zoho_contact.get('company_name', 'Unknown Zoho Contact'))
                logger.error(f"❌ Error migrating {contact_type_key} '{contact_name_for_log}': {e}")
                continue
        
        logger.info("\n" + "="*60)
        logger.info(f"🎉 {contact_type_key.upper()} MIGRATION COMPLETED!")
        logger.info("="*60)
        logger.info(f"✅ Successfully migrated: {success_count}")
        logger.info(f"⚠️  Duplicates skipped: {duplicate_count}")
        logger.info(f"❌ Errors encountered: {error_count}")
        logger.info(f"📊 Total {contact_type_key} processed: {len(zoho_contacts)}")
        if len(zoho_contacts) > 0:
            logger.info(f"🎯 Success rate: {(success_count/len(zoho_contacts)*100):.1f}%")
        logger.info("="*60)
        
        return error_count == 0

if __name__ == "__main__":
    migrator = ImprovedContactMigrator()
    all_successful = True

    logger.info("🚀 Starting Contact Migration with Duplicate Prevention...")

    # Migrate Customers
    if not migrator.migrate_contact_type('customers'):
        all_successful = False
    
    # Migrate Vendors
    if not migrator.migrate_contact_type('vendors'):
        all_successful = False

    if all_successful:
        print("🎉🎉🎉 Full Contact Migration completed successfully! 🎉🎉🎉")
    else:
        print("⚠️⚠️⚠️ Full Contact Migration completed with some errors. Please check logs. ⚠️⚠️⚠️") 