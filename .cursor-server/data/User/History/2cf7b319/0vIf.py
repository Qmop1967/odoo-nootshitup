#!/usr/bin/env python3

import json
import requests
import xmlrpc.client
import logging
from datetime import datetime
import time
import base64

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContactMigrator:
    def __init__(self):
        self.load_config()
        self.connect_to_odoo()
        self.setup_country_state_mapping()

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
        # (Same as in EnhancedProductMigrator, can be refactored to a common utility)
        token_url = "https://accounts.zoho.com/oauth/v2/token"
        token_params = {
            'refresh_token': self.zoho_config['refresh_token'],
            'client_id': self.zoho_config['client_id'],
            'client_secret': self.zoho_config['client_secret'],
            'grant_type': 'refresh_token'
        }
        response = requests.post(token_url, data=token_params)
        response.raise_for_status() # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        return response.json()['access_token']

    def fetch_zoho_contacts(self, contact_type='customer'):
        """Fetch all contacts (customers or vendors) from Zoho Books"""
        access_token = self.get_zoho_access_token()
        headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
        
        all_contacts = []
        page = 1
        per_page = 200 # Max allowed by Zoho
        
        # Zoho API uses 'contact_type' query parameter: 'customer', 'vendor'
        # However, the /contacts endpoint fetches all types. We can filter later or use specific Zoho filters if available.
        # For now, we fetch all and then filter by 'contact_type' field in the response if needed, or rely on Zoho's own filtering if 'contact_type' param is used.
        # The general /contacts endpoint might be enough.
        
        endpoint_url = f"{self.zoho_config['base_url']}/contacts"
        
        logger.info(f"Fetching Zoho {contact_type}s...")

        while True:
            params = {
                'organization_id': self.zoho_config['organization_id'],
                'page': page,
                'per_page': per_page,
                # 'contact_type': contact_type # This might be useful if Zoho supports it for /contacts
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
            
            # Filter based on contact_type from Zoho if we are fetching all from /contacts
            # Zoho's `contact_type` field can be `customer`, `vendor`, or `employee`.
            if contact_type == 'customer':
                all_contacts.extend([c for c in contacts_on_page if c.get('contact_type') == 'customer'])
            elif contact_type == 'vendor':
                 all_contacts.extend([c for c in contacts_on_page if c.get('contact_type') == 'vendor'])
            else: # Or fetch all if no specific type given
                all_contacts.extend(contacts_on_page)

            logger.info(f"Retrieved {len(contacts_on_page)} contacts (filtered for {contact_type}, added {len(all_contacts) - len(all_contacts) + len([c for c in contacts_on_page if c.get('contact_type') == contact_type])}) from page {page}. Total {contact_type}s so far: {len(all_contacts)}")
            
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
                if isinstance(odoo_field_or_spec, dict): # Nested address
                    # odoo_field_or_spec is the nested mapping for address
                    # value is the zoho address object
                    for zoho_addr_field, odoo_addr_field in odoo_field_or_spec.items():
                        if zoho_addr_field in value and value[zoho_addr_field]:
                            addr_val = value[zoho_addr_field]
                            if odoo_addr_field == 'country_id':
                                odoo_contact[odoo_addr_field] = self.get_country_id(addr_val)
                            elif odoo_addr_field == 'state_id':
                                country_id_for_state = odoo_contact.get('country_id') # Use already mapped country_id
                                odoo_contact[odoo_addr_field] = self.get_state_id(addr_val, country_id_for_state)
                            else:
                                odoo_contact[odoo_addr_field] = addr_val
                elif odoo_field_or_spec == 'currency_id': 
                    # `currency_id` is not a standard field on res.partner.
                    # It's usually on `property_purchase_currency_id` or inferred.
                    # We'll try to set it, if it fails, Odoo XMLRPC will error, log it.
                    # For now, let's assume it's a custom field or will be ignored.
                    # A better approach is to map to `property_purchase_currency_id` if it's a vendor.
                    # Or, map to an Odoo res.currency ID if Zoho provides a currency code.
                    # For now, let's skip it to avoid errors, unless explicitly handled.
                    logger.debug(f"Skipping direct mapping of currency_id: {value} for contact {zoho_contact.get('contact_name')}")
                    pass # Skip direct mapping of currency_id
                else:
                    odoo_contact[odoo_field_or_spec] = value
        
        # Apply default values
        for field, def_value in contact_mapping_config.get('default_values', {}).items():
            odoo_contact[field] = def_value
        
        # Ensure required fields (Odoo might have its own server-side required fields)
        if 'name' not in odoo_contact or not odoo_contact['name']:
            odoo_contact['name'] = zoho_contact.get('contact_name') or zoho_contact.get('company_name') or f"Contact {zoho_contact.get('contact_id', 'Unknown')}"
        
        odoo_contact['name'] = str(odoo_contact['name']).strip()

        # Zoho's contact_type vs Odoo's boolean fields (is_company, customer_rank, supplier_rank)
        # The default_values in field_mapping.json should handle customer_rank/supplier_rank.
        # `is_company` is also in default_values. If Zoho has an equivalent, it should be mapped.
        # Zoho: 'company_name' implies it might be a company.
        if zoho_contact.get('company_name') and not zoho_contact.get('first_name'): # Heuristic for company
             odoo_contact['is_company'] = True
        elif 'is_company' not in odoo_contact: # if not set by defaults and not clearly a company from Zoho name structure
             odoo_contact['is_company'] = False


        return odoo_contact

    def migrate_contact_type(self, contact_type_key): # 'customers' or 'vendors'
        """Migrate a specific type of contacts (customers or vendors)"""
        logger.info(f"🚀 Starting migration for {contact_type_key}...")
        contact_mapping_config = self.field_mapping[contact_type_key]
        odoo_model = contact_mapping_config['odoo_model'] # Should be 'res.partner'
        
        # Determine zoho_contact_type for fetching ('customer' or 'vendor')
        zoho_api_contact_type = 'customer' if contact_type_key == 'customers' else 'vendor'
        
        zoho_contacts = self.fetch_zoho_contacts(contact_type=zoho_api_contact_type)
        
        if not zoho_contacts:
            logger.warning(f"No {contact_type_key} found in Zoho to migrate.")
            return True # No error, just nothing to do

        success_count = 0
        error_count = 0
        
        for i, zoho_contact in enumerate(zoho_contacts, 1):
            odoo_contact_payload = None # For logging in case of error
            try:
                odoo_contact_payload = self.transform_contact(zoho_contact, contact_mapping_config)
                
                # Check for existing contact by name or email to avoid duplicates (optional, basic check)
                # More robust deduplication would involve external IDs or more complex checks.
                # For simplicity, we are creating new ones. Odoo might have its own deduplication logic.
                
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
                    if success_count % 50 == 0:
                        logger.info(f"📊 Progress for {contact_type_key}: {success_count}/{len(zoho_contacts)} migrated.")
                else:
                    error_count += 1
                    logger.error(f"❌ Failed to create {contact_type_key}: {odoo_contact_payload.get('name')} in Odoo (no ID returned).")
                    
            except Exception as e:
                error_count += 1
                contact_name_for_log = zoho_contact.get('contact_name', zoho_contact.get('company_name', 'Unknown Zoho Contact'))
                logger.error(f"❌ Error migrating {contact_type_key} '{contact_name_for_log}': {e}")
                if odoo_contact_payload:
                     logger.error(f"🔍 Payload causing error: {odoo_contact_payload}")
                # Continue with the next contact
                continue
        
        logger.info("\n" + "="*60)
        logger.info(f"🎉 {contact_type_key.upper()} MIGRATION COMPLETED!")
        logger.info("="*60)
        logger.info(f"✅ Successfully migrated: {success_count}")
        logger.info(f"❌ Errors encountered: {error_count}")
        logger.info(f"📊 Total {contact_type_key} processed: {len(zoho_contacts)}")
        if len(zoho_contacts) > 0:
            logger.info(f"🎯 Success rate: {(success_count/len(zoho_contacts)*100):.1f}%")
        logger.info("="*60)
        
        return error_count == 0


if __name__ == "__main__":
    migrator = ContactMigrator()
    all_successful = True

    logger.info("🚀 Starting Contact Migration (Customers & Vendors)...")

    # Migrate Customers
    if not migrator.migrate_contact_type('customers'):
        all_successful = False
    
    # Migrate Vendors
    if not migrator.migrate_contact_type('vendors'):
        all_successful = False

    if all_successful:
        print("🎉🎉🎉 Full Contact Migration (Customers & Vendors) completed successfully! 🎉🎉🎉")
    else:
        print("⚠️⚠️⚠️ Full Contact Migration (Customers & Vendors) completed with some errors. Please check logs. ⚠️⚠️⚠️")
        exit(1) 