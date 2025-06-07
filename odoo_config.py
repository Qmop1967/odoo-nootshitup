#!/usr/bin/env python3
"""
Odoo Configuration File
Edit this file with your Odoo connection details
"""

# Odoo Connection Settings
ODOO_CONFIG = {
    # Your Odoo instance URL (found from existing scripts)
    'url': 'http://138.68.89.104:8069',
    
    # Your production database name (found from existing scripts)
    'source_database': 'odtshbrain',
    
    # Master/Admin password for database operations
    # NOTE: You need to provide the master password for database operations
    'master_password': 'admin123',
    
    # Username for connecting to Odoo (found from existing scripts)
    'username': 'khaleel@tsh.sale',
    
    # Password for the username above
    # NOTE: You need to provide the password for khaleel@tsh.sale
    'password': 'PLEASE_ENTER_YOUR_PASSWORD',
    
    # Suffix for test database (will create: odtshbrain_test)
    'test_suffix': '_test'
}

# Example configurations (uncomment and modify as needed):

# Example 1: Local Odoo instance
# ODOO_CONFIG = {
#     'url': 'http://localhost:8069',
#     'source_database': 'my_company',
#     'master_password': 'admin',
#     'username': 'admin',
#     'password': 'admin',
#     'test_suffix': '_test'
# }

# Example 2: Odoo.com hosted instance
# ODOO_CONFIG = {
#     'url': 'https://mycompany.odoo.com',
#     'source_database': 'mycompany-main-123456',
#     'master_password': 'your_master_password',
#     'username': 'admin',
#     'password': 'your_password',
#     'test_suffix': '_test'
# }

# Example 3: Custom hosted Odoo
# ODOO_CONFIG = {
#     'url': 'https://odoo.mycompany.com',
#     'source_database': 'production',
#     'master_password': 'secure_master_password',
#     'username': 'admin',
#     'password': 'admin_password',
#     'test_suffix': '_dev'
# }