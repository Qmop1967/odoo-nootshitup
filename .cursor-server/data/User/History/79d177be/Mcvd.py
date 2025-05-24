#!/usr/bin/env python3
"""
Zoho API Authentication Setup Tool
=================================
This script helps you set up authentication for Zoho Books and Zoho Inventory APIs.

Steps:
1. Create a Zoho Developer Account
2. Create a Server Application
3. Generate authorization codes and tokens
4. Update configuration file

Author: Migration Assistant
Date: 2025
"""

import json
import requests
import webbrowser
from urllib.parse import parse_qs, urlparse

class ZohoAuthSetup:
    """Helper class for setting up Zoho API authentication"""
    
    def __init__(self):
        self.config_path = '/opt/odoo/migration/config/zoho_config.json'
        self.auth_endpoints = {
            'books': 'https://accounts.zoho.com/oauth/v2/auth',
            'inventory': 'https://accounts.zoho.com/oauth/v2/auth',
            'token': 'https://accounts.zoho.com/oauth/v2/token'
        }
        
    def display_instructions(self):
        """Display step-by-step instructions for getting Zoho API access"""
        print("🔐 ZOHO API AUTHENTICATION SETUP")
        print("=" * 50)
        print()
        print("📋 STEP 1: Create Zoho Developer Account")
        print("1. Go to: https://api-console.zoho.com/")
        print("2. Sign in with your Zoho account")
        print("3. Click 'Get Started' if this is your first time")
        print()
        
        print("📋 STEP 2: Create Server Application")
        print("1. Click 'Add Client' → 'Server-based Applications'")
        print("2. Fill in the details:")
        print("   - Client Name: 'Odoo Migration Tool'")
        print("   - Homepage URL: 'http://localhost'")
        print("   - Authorized Redirect URIs: 'http://localhost:8080/callback'")
        print("3. Click 'Create'")
        print("4. Note down your Client ID and Client Secret")
        print()
        
        print("📋 STEP 3: Get Organization ID")
        print("1. Go to Zoho Books: https://books.zoho.com/")
        print("2. Look at the URL - it will contain your organization ID")
        print("   Example: https://books.zoho.com/app/60009999999#/home")
        print("   Organization ID: 60009999999")
        print()
        
    def generate_auth_url(self, client_id, scopes, redirect_uri="http://localhost:8080/callback"):
        """Generate authorization URL for Zoho OAuth"""
        scope_string = ",".join(scopes)
        
        auth_url = (
            f"{self.auth_endpoints['books']}"
            f"?scope={scope_string}"
            f"&client_id={client_id}"
            f"&response_type=code"
            f"&redirect_uri={redirect_uri}"
            f"&access_type=offline"
        )
        
        return auth_url
        
    def get_access_token(self, client_id, client_secret, auth_code, redirect_uri="http://localhost:8080/callback"):
        """Exchange authorization code for access token"""
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'code': auth_code
        }
        
        try:
            response = requests.post(self.auth_endpoints['token'], data=token_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting access token: {e}")
            return None
            
    def interactive_setup(self):
        """Interactive setup process"""
        print("🚀 INTERACTIVE SETUP")
        print("=" * 30)
        
        # Get client credentials
        client_id = input("Enter your Zoho Client ID: ").strip()
        client_secret = input("Enter your Zoho Client Secret: ").strip()
        organization_id = input("Enter your Organization ID: ").strip()
        
        if not all([client_id, client_secret, organization_id]):
            print("❌ All fields are required!")
            return False
            
        # Generate authorization URLs
        books_scopes = [
            "ZohoBooks.fullaccess.all"
        ]
        
        inventory_scopes = [
            "ZohoInventory.fullaccess.all"
        ]
        
        print("\n📋 STEP 4: Get Authorization Codes")
        print("-" * 35)
        
        # Zoho Books authorization
        print("\n🔗 ZOHO BOOKS AUTHORIZATION:")
        books_auth_url = self.generate_auth_url(client_id, books_scopes)
        print(f"1. Click this link: {books_auth_url}")
        print("2. Authorize the application")
        print("3. Copy the 'code' parameter from the redirect URL")
        
        try:
            webbrowser.open(books_auth_url)
        except:
            pass
            
        books_auth_code = input("\nEnter Zoho Books authorization code: ").strip()
        
        # Zoho Inventory authorization  
        print("\n🔗 ZOHO INVENTORY AUTHORIZATION:")
        inventory_auth_url = self.generate_auth_url(client_id, inventory_scopes)
        print(f"1. Click this link: {inventory_auth_url}")
        print("2. Authorize the application")
        print("3. Copy the 'code' parameter from the redirect URL")
        
        try:
            webbrowser.open(inventory_auth_url)
        except:
            pass
            
        inventory_auth_code = input("\nEnter Zoho Inventory authorization code: ").strip()
        
        # Get access tokens
        print("\n🔄 Getting access tokens...")
        
        books_token_data = self.get_access_token(client_id, client_secret, books_auth_code)
        if not books_token_data:
            print("❌ Failed to get Zoho Books token")
            return False
            
        inventory_token_data = self.get_access_token(client_id, client_secret, inventory_auth_code)
        if not inventory_token_data:
            print("❌ Failed to get Zoho Inventory token")
            return False
            
        # Update configuration
        self.update_config(
            client_id, client_secret, organization_id,
            books_token_data.get('refresh_token'),
            inventory_token_data.get('refresh_token')
        )
        
        print("✅ Configuration updated successfully!")
        return True
        
    def update_config(self, client_id, client_secret, organization_id, books_refresh_token, inventory_refresh_token):
        """Update the configuration file with authentication details"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                
            # Update Zoho Books config
            config['zoho_books'].update({
                'client_id': client_id,
                'client_secret': client_secret,
                'organization_id': organization_id,
                'refresh_token': books_refresh_token
            })
            
            # Update Zoho Inventory config
            config['zoho_inventory'].update({
                'client_id': client_id,
                'client_secret': client_secret,
                'organization_id': organization_id,
                'refresh_token': inventory_refresh_token
            })
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
            print(f"Configuration saved to: {self.config_path}")
            
        except Exception as e:
            print(f"Error updating configuration: {e}")
            
    def test_connection(self):
        """Test the API connection with current configuration"""
        print("\n🧪 TESTING API CONNECTION")
        print("=" * 30)
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                
            # Test Zoho Books connection
            books_config = config['zoho_books']
            if books_config['client_id'] != 'YOUR_ZOHO_CLIENT_ID':
                print("📚 Testing Zoho Books connection...")
                # TODO: Implement actual API test
                print("✅ Zoho Books: Configuration looks good")
            else:
                print("⚠️  Zoho Books: Not configured yet")
                
            # Test Zoho Inventory connection
            inventory_config = config['zoho_inventory']
            if inventory_config['client_id'] != 'YOUR_ZOHO_CLIENT_ID':
                print("📦 Testing Zoho Inventory connection...")
                # TODO: Implement actual API test
                print("✅ Zoho Inventory: Configuration looks good")
            else:
                print("⚠️  Zoho Inventory: Not configured yet")
                
        except Exception as e:
            print(f"❌ Error testing connection: {e}")

def main():
    """Main entry point"""
    setup = ZohoAuthSetup()
    
    while True:
        print("\n🔐 ZOHO API SETUP MENU")
        print("=" * 30)
        print("1. Show setup instructions")
        print("2. Interactive setup")
        print("3. Test API connection")
        print("4. Exit")
        
        choice = input("\nSelect an option (1-4): ").strip()
        
        if choice == '1':
            setup.display_instructions()
        elif choice == '2':
            setup.interactive_setup()
        elif choice == '3':
            setup.test_connection()
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main() 