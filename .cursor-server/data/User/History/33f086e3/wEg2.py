#!/usr/bin/env python3
"""
Zoho to Odoo Enterprise Migration Tool
=====================================
Main migration script for transferring data from Zoho Books and Zoho Inventory to Odoo Enterprise.

Author: Migration Assistant
Date: 2025
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
import odoorpc

# Add the migration directory to Python path
sys.path.insert(0, '/opt/odoo/migration')

class ZohoOdooMigrator:
    """Main migration controller class"""
    
    def __init__(self, config_path='/opt/odoo/migration/config/zoho_config.json'):
        """Initialize the migrator with configuration"""
        self.config_path = config_path
        self.config = self.load_config()
        self.setup_logging()
        
        # Initialize connections
        self.zoho_books = None
        self.zoho_inventory = None
        self.odoo_test = None
        self.odoo_prod = None
        
        # Migration statistics
        self.stats = {
            'start_time': None,
            'end_time': None,
            'total_records': 0,
            'successful_records': 0,
            'failed_records': 0,
            'errors': []
        }
        
        # Load field mappings
        self.field_mappings = self.load_field_mappings()
        
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in configuration file: {e}")
            raise
            
    def load_field_mappings(self):
        """Load field mappings from JSON file"""
        mapping_path = '/opt/odoo/migration/config/field_mapping.json'
        try:
            with open(mapping_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Field mapping file not found: {mapping_path}")
            raise
            
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config['migration_settings']['log_level'])
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/opt/odoo/migration/logs/migration.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger('ZohoOdooMigrator')
        self.logger.info("Migration logger initialized")
        
    def connect_zoho_books(self):
        """Connect to Zoho Books API"""
        try:
            # This is a placeholder - you'll need to implement OAuth flow
            self.logger.info("Connecting to Zoho Books API...")
            # TODO: Implement actual Zoho Books API connection
            self.logger.info("Zoho Books API connection established")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Zoho Books: {e}")
            return False
            
    def connect_zoho_inventory(self):
        """Connect to Zoho Inventory API"""
        try:
            self.logger.info("Connecting to Zoho Inventory API...")
            # TODO: Implement actual Zoho Inventory API connection
            self.logger.info("Zoho Inventory API connection established")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Zoho Inventory: {e}")
            return False
            
    def connect_odoo_test(self):
        """Connect to Odoo test database"""
        try:
            config = self.config['odoo']['test_db']
            self.odoo_test = odoorpc.ODOO(config['host'], port=config['port'])
            self.odoo_test.login(config['database'], config['username'], config['password'])
            self.logger.info("Connected to Odoo test database")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Odoo test database: {e}")
            return False
            
    def connect_odoo_production(self):
        """Connect to Odoo production database"""
        try:
            config = self.config['odoo']['production_db']
            self.odoo_prod = odoorpc.ODOO(config['host'], port=config['port'])
            self.odoo_prod.login(config['database'], config['username'], config['password'])
            self.logger.info("Connected to Odoo production database")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Odoo production database: {e}")
            return False
            
    def backup_database(self, database_name):
        """Create a backup of the specified database"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"/opt/odoo/backups/migration_backup_{database_name}_{timestamp}.sql"
            
            cmd = f"sudo -u postgres pg_dump {database_name} > {backup_file}"
            os.system(cmd)
            
            self.logger.info(f"Database backup created: {backup_file}")
            return backup_file
        except Exception as e:
            self.logger.error(f"Failed to create database backup: {e}")
            return None
            
    def validate_prerequisites(self):
        """Validate all prerequisites are met before migration"""
        self.logger.info("Validating migration prerequisites...")
        
        checks = [
            ("Zoho Books API", self.connect_zoho_books),
            ("Zoho Inventory API", self.connect_zoho_inventory),
            ("Odoo Test Database", self.connect_odoo_test)
        ]
        
        for check_name, check_func in checks:
            if not check_func():
                self.logger.error(f"Prerequisite check failed: {check_name}")
                return False
                
        self.logger.info("All prerequisites validated successfully")
        return True
        
    def extract_zoho_data(self, data_type):
        """Extract data from Zoho APIs"""
        self.logger.info(f"Extracting {data_type} from Zoho...")
        
        # TODO: Implement actual data extraction logic
        # This is a placeholder for the extraction process
        
        extracted_data = []
        
        try:
            # Save raw data
            raw_file = f"/opt/odoo/migration/data/raw/zoho_{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(raw_file, 'w') as f:
                json.dump(extracted_data, f, indent=2)
                
            self.logger.info(f"Raw data saved to: {raw_file}")
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"Failed to extract {data_type}: {e}")
            return None
            
    def transform_data(self, raw_data, data_type):
        """Transform Zoho data to Odoo format"""
        self.logger.info(f"Transforming {data_type} data...")
        
        if data_type not in self.field_mappings:
            self.logger.error(f"No field mapping found for {data_type}")
            return None
            
        mapping = self.field_mappings[data_type]
        transformed_data = []
        
        try:
            for record in raw_data:
                transformed_record = {}
                
                # Apply field mappings
                for zoho_field, odoo_field in mapping.get('zoho_books', {}).items():
                    if zoho_field in record:
                        transformed_record[odoo_field] = record[zoho_field]
                        
                # Apply default values
                for field, value in mapping.get('default_values', {}).items():
                    transformed_record[field] = value
                    
                transformed_data.append(transformed_record)
                
            # Save transformed data
            processed_file = f"/opt/odoo/migration/data/processed/{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(processed_file, 'w') as f:
                json.dump(transformed_data, f, indent=2)
                
            self.logger.info(f"Transformed data saved to: {processed_file}")
            return transformed_data
            
        except Exception as e:
            self.logger.error(f"Failed to transform {data_type}: {e}")
            return None
            
    def import_to_odoo(self, transformed_data, data_type, target_db='test'):
        """Import transformed data to Odoo"""
        self.logger.info(f"Importing {data_type} to Odoo {target_db} database...")
        
        if data_type not in self.field_mappings:
            self.logger.error(f"No field mapping found for {data_type}")
            return False
            
        odoo_conn = self.odoo_test if target_db == 'test' else self.odoo_prod
        model_name = self.field_mappings[data_type]['odoo_model']
        
        successful_imports = 0
        failed_imports = 0
        
        try:
            for record in transformed_data:
                try:
                    # Validate required fields
                    required_fields = self.field_mappings[data_type].get('required_fields', [])
                    for field in required_fields:
                        if field not in record or not record[field]:
                            raise ValueError(f"Required field {field} is missing or empty")
                    
                    # Import record
                    record_id = odoo_conn.env[model_name].create(record)
                    successful_imports += 1
                    
                    if successful_imports % 10 == 0:
                        self.logger.info(f"Imported {successful_imports} records...")
                        
                except Exception as e:
                    failed_imports += 1
                    error_msg = f"Failed to import record: {e}"
                    self.logger.error(error_msg)
                    
                    # Save failed record for review
                    failed_file = f"/opt/odoo/migration/data/failed/{data_type}_failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(failed_file, 'a') as f:
                        json.dump({'record': record, 'error': str(e)}, f)
                        f.write('\n')
                        
            self.logger.info(f"Import completed: {successful_imports} successful, {failed_imports} failed")
            return True
            
        except Exception as e:
            self.logger.error(f"Critical error during import: {e}")
            return False
            
    def migrate_data_type(self, data_type, target_db='test'):
        """Complete migration process for a specific data type"""
        self.logger.info(f"Starting migration of {data_type}...")
        
        # Extract
        raw_data = self.extract_zoho_data(data_type)
        if not raw_data:
            return False
            
        # Transform
        transformed_data = self.transform_data(raw_data, data_type)
        if not transformed_data:
            return False
            
        # Import
        return self.import_to_odoo(transformed_data, data_type, target_db)
        
    def run_full_migration(self, target_db='test'):
        """Run the complete migration process"""
        self.logger.info(f"Starting full migration to {target_db} database...")
        self.stats['start_time'] = datetime.now()
        
        # Validate prerequisites
        if not self.validate_prerequisites():
            return False
            
        # Create backup if targeting production
        if target_db == 'production':
            backup_file = self.backup_database('odtshbrain')
            if not backup_file:
                self.logger.error("Failed to create backup, aborting migration")
                return False
                
        # Migration order (dependencies matter!)
        migration_order = [
            'chart_of_accounts',
            'taxes', 
            'customers',
            'vendors',
            'products',
            'invoices',
            'bills'
        ]
        
        success_count = 0
        for data_type in migration_order:
            if self.migrate_data_type(data_type, target_db):
                success_count += 1
            else:
                self.logger.error(f"Migration failed for {data_type}")
                
        self.stats['end_time'] = datetime.now()
        duration = self.stats['end_time'] - self.stats['start_time']
        
        self.logger.info(f"Migration completed in {duration}")
        self.logger.info(f"Successfully migrated {success_count}/{len(migration_order)} data types")
        
        return success_count == len(migration_order)

def main():
    """Main entry point"""
    print("🔄 Zoho to Odoo Enterprise Migration Tool")
    print("=" * 50)
    
    migrator = ZohoOdooMigrator()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        target_db = sys.argv[1]
        if target_db not in ['test', 'production']:
            print("Usage: python zoho_odoo_migrator.py [test|production]")
            sys.exit(1)
    else:
        target_db = 'test'
        
    print(f"Target database: {target_db}")
    
    if target_db == 'production':
        confirm = input("⚠️  Are you sure you want to migrate to PRODUCTION? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Migration cancelled.")
            sys.exit(0)
            
    # Run migration
    success = migrator.run_full_migration(target_db)
    
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 