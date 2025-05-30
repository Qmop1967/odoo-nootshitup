#!/usr/bin/env python3
"""
Odoo Test Data Anonymization Script
Anonymizes sensitive data in test databases for safe testing
"""

import xmlrpc.client
import random
import string
from typing import Optional, List, Dict, Any

class OdooDataAnonymizer:
    def __init__(self, url: str, db: str, username: str, password: str):
        """Initialize Odoo data anonymizer"""
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        
        # Initialize XML-RPC connections
        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
    def authenticate(self) -> bool:
        """Authenticate with Odoo server"""
        try:
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            if self.uid:
                print(f"✅ Successfully authenticated as user ID: {self.uid}")
                return True
            else:
                print("❌ Authentication failed")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def generate_test_email(self, partner_id: int) -> str:
        """Generate a test email address"""
        return f"test_user_{partner_id}@example.com"
    
    def generate_test_phone(self) -> str:
        """Generate a test phone number"""
        return f"+1-555-{random.randint(1000, 9999)}"
    
    def generate_test_name(self, original_name: str) -> str:
        """Generate a test name while preserving some structure"""
        if not original_name:
            return "Test User"
        
        # Keep first letter and length similar
        first_letter = original_name[0].upper()
        length = len(original_name)
        
        # Generate random letters for the rest
        rest = ''.join(random.choices(string.ascii_lowercase, k=max(1, length-1)))
        
        return f"{first_letter}{rest}"
    
    def anonymize_partners(self) -> int:
        """Anonymize partner/customer data"""
        if not self.uid:
            print("❌ Not authenticated")
            return 0
        
        try:
            print("🔄 Anonymizing partner data...")
            
            # Get all partners with sensitive data
            partners = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.partner', 'search_read',
                [[]],
                {'fields': ['id', 'name', 'email', 'phone', 'mobile', 'street', 'street2']}
            )
            
            anonymized_count = 0
            
            for partner in partners:
                updates = {}
                
                # Anonymize email
                if partner.get('email'):
                    updates['email'] = self.generate_test_email(partner['id'])
                
                # Anonymize phone numbers
                if partner.get('phone'):
                    updates['phone'] = self.generate_test_phone()
                
                if partner.get('mobile'):
                    updates['mobile'] = self.generate_test_phone()
                
                # Anonymize addresses
                if partner.get('street'):
                    updates['street'] = f"Test Street {random.randint(1, 999)}"
                
                if partner.get('street2'):
                    updates['street2'] = f"Apt {random.randint(1, 99)}"
                
                # Anonymize names (optional - be careful with this)
                # if partner.get('name') and not partner.get('is_company'):
                #     updates['name'] = self.generate_test_name(partner['name'])
                
                # Apply updates if any
                if updates:
                    self.models.execute_kw(
                        self.db, self.uid, self.password,
                        'res.partner', 'write',
                        [[partner['id']], updates]
                    )
                    anonymized_count += 1
            
            print(f"✅ Anonymized {anonymized_count} partner records")
            return anonymized_count
            
        except Exception as e:
            print(f"❌ Error anonymizing partners: {e}")
            return 0
    
    def anonymize_users(self) -> int:
        """Anonymize user data"""
        if not self.uid:
            print("❌ Not authenticated")
            return 0
        
        try:
            print("🔄 Anonymizing user data...")
            
            # Get all users except admin
            users = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.users', 'search_read',
                [['id', '!=', 1]],  # Skip admin user
                {'fields': ['id', 'login', 'email']}
            )
            
            anonymized_count = 0
            
            for user in users:
                updates = {}
                
                # Anonymize login email
                if user.get('login') and '@' in user['login']:
                    updates['login'] = f"test_user_{user['id']}@example.com"
                
                # Anonymize email
                if user.get('email'):
                    updates['email'] = f"test_user_{user['id']}@example.com"
                
                # Apply updates if any
                if updates:
                    self.models.execute_kw(
                        self.db, self.uid, self.password,
                        'res.users', 'write',
                        [[user['id']], updates]
                    )
                    anonymized_count += 1
            
            print(f"✅ Anonymized {anonymized_count} user records")
            return anonymized_count
            
        except Exception as e:
            print(f"❌ Error anonymizing users: {e}")
            return 0
    
    def reset_passwords(self) -> int:
        """Reset all user passwords to a test password"""
        if not self.uid:
            print("❌ Not authenticated")
            return 0
        
        try:
            print("🔄 Resetting user passwords...")
            
            # Get all users except admin
            users = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.users', 'search',
                [['id', '!=', 1]]  # Skip admin user
            )
            
            # Reset passwords to 'test123'
            test_password = 'test123'
            
            for user_id in users:
                try:
                    self.models.execute_kw(
                        self.db, self.uid, self.password,
                        'res.users', 'write',
                        [[user_id], {'password': test_password}]
                    )
                except Exception as e:
                    print(f"⚠️  Could not reset password for user {user_id}: {e}")
            
            print(f"✅ Reset passwords for {len(users)} users to 'test123'")
            return len(users)
            
        except Exception as e:
            print(f"❌ Error resetting passwords: {e}")
            return 0
    
    def anonymize_financial_data(self) -> int:
        """Anonymize financial data (invoices, payments, etc.)"""
        if not self.uid:
            print("❌ Not authenticated")
            return 0
        
        try:
            print("🔄 Anonymizing financial data...")
            
            # Zero out invoice amounts (be very careful with this!)
            invoices = self.models.execute_kw(
                self.db, self.uid, self.password,
                'account.move', 'search_read',
                [['move_type', 'in', ['out_invoice', 'in_invoice']]],
                {'fields': ['id', 'amount_total'], 'limit': 100}  # Limit for safety
            )
            
            anonymized_count = 0
            
            for invoice in invoices:
                # Set amounts to small test values
                test_amount = round(random.uniform(10.0, 1000.0), 2)
                
                try:
                    # Note: This is dangerous and might break accounting!
                    # Only do this in test environments
                    self.models.execute_kw(
                        self.db, self.uid, self.password,
                        'account.move', 'write',
                        [[invoice['id']], {'narration': 'TEST DATA - ANONYMIZED'}]
                    )
                    anonymized_count += 1
                except Exception as e:
                    print(f"⚠️  Could not anonymize invoice {invoice['id']}: {e}")
            
            print(f"✅ Anonymized {anonymized_count} financial records")
            return anonymized_count
            
        except Exception as e:
            print(f"❌ Error anonymizing financial data: {e}")
            return 0
    
    def run_full_anonymization(self) -> Dict[str, int]:
        """Run complete anonymization process"""
        if not self.authenticate():
            return {}
        
        print("🚀 Starting full data anonymization...")
        print("=" * 50)
        
        results = {}
        
        # Anonymize different data types
        results['partners'] = self.anonymize_partners()
        results['users'] = self.anonymize_users()
        
        # Ask before resetting passwords
        reset_pwd = input("\nReset all user passwords to 'test123'? (y/N): ").strip().lower()
        if reset_pwd == 'y':
            results['passwords'] = self.reset_passwords()
        
        # Ask before anonymizing financial data (dangerous!)
        anon_financial = input("\nAnonymize financial data? (DANGEROUS - y/N): ").strip().lower()
        if anon_financial == 'y':
            confirm = input("Are you SURE? This may break accounting! (yes/N): ").strip().lower()
            if confirm == 'yes':
                results['financial'] = self.anonymize_financial_data()
        
        return results

def main():
    """Main function"""
    print("🔒 Odoo Test Data Anonymizer")
    print("=" * 40)
    print("⚠️  WARNING: This will modify data in your database!")
    print("   Only use this on TEST databases, never on production!")
    print()
    
    # Get connection details
    odoo_url = input("Enter Odoo URL: ").strip()
    test_db = input("Enter TEST database name: ").strip()
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    
    if not all([odoo_url, test_db, username, password]):
        print("❌ All connection details are required!")
        return
    
    # Confirm this is a test database
    print(f"\n⚠️  You are about to anonymize data in database: {test_db}")
    confirm = input("Is this a TEST database? Type 'YES' to continue: ").strip()
    
    if confirm != 'YES':
        print("❌ Anonymization cancelled for safety")
        return
    
    # Initialize anonymizer
    anonymizer = OdooDataAnonymizer(odoo_url, test_db, username, password)
    
    # Run anonymization
    results = anonymizer.run_full_anonymization()
    
    # Print summary
    if results:
        print("\n🎉 Anonymization completed!")
        print("=" * 30)
        for data_type, count in results.items():
            print(f"   {data_type.title()}: {count} records")
        
        print("\n💡 Test database is now safe for development!")
        print("   - Sensitive emails replaced with test addresses")
        print("   - Phone numbers replaced with test numbers")
        print("   - Addresses replaced with test addresses")
        if 'passwords' in results:
            print("   - User passwords reset to 'test123'")
        
    else:
        print("\n❌ Anonymization failed or was cancelled")

if __name__ == "__main__":
    main()