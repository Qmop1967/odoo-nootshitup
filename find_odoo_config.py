#!/usr/bin/env python3
"""
Odoo Configuration Finder
Helps you find existing Odoo configuration in your system
"""

import os
import glob
import json
import configparser
from pathlib import Path

def find_odoo_configs():
    """Find potential Odoo configuration files"""
    print("🔍 Searching for Odoo configuration files...")
    print("=" * 45)
    
    config_patterns = [
        # Common Odoo config file locations
        '/etc/odoo/*.conf',
        '/etc/odoo*.conf',
        '~/.odoorc',
        '~/.openerp_serverrc',
        './odoo.conf',
        './openerp-server.conf',
        # Docker and custom locations
        './config/odoo.conf',
        './docker-compose.yml',
        './docker-compose.yaml',
        # Python config files
        './*.py',
    ]
    
    found_configs = []
    
    for pattern in config_patterns:
        expanded_pattern = os.path.expanduser(pattern)
        matches = glob.glob(expanded_pattern)
        
        for match in matches:
            if os.path.isfile(match):
                found_configs.append(match)
    
    return found_configs

def analyze_config_file(filepath):
    """Analyze a configuration file for Odoo settings"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Check if it's an Odoo config file
        odoo_indicators = [
            'db_host', 'db_port', 'db_user', 'db_password',
            'xmlrpc_port', 'addons_path', 'data_dir',
            'odoo', 'openerp'
        ]
        
        if any(indicator in content.lower() for indicator in odoo_indicators):
            print(f"\n📄 Found Odoo config: {filepath}")
            
            # Try to parse as INI file
            try:
                config = configparser.ConfigParser()
                config.read(filepath)
                
                for section in config.sections():
                    print(f"   [{section}]")
                    for key, value in config.items(section):
                        if 'password' in key.lower():
                            value = '*' * len(value)  # Hide passwords
                        print(f"     {key} = {value}")
                
            except:
                # Show relevant lines
                lines = content.split('\n')
                relevant_lines = [line for line in lines if any(ind in line.lower() for ind in odoo_indicators)]
                
                for line in relevant_lines[:10]:  # Show first 10 relevant lines
                    if 'password' in line.lower():
                        line = line.split('=')[0] + '= ****'  # Hide passwords
                    print(f"     {line.strip()}")
                
                if len(relevant_lines) > 10:
                    print(f"     ... and {len(relevant_lines) - 10} more lines")
            
            return True
    
    except Exception as e:
        pass
    
    return False

def check_environment_variables():
    """Check for Odoo-related environment variables"""
    print("\n🌍 Checking environment variables...")
    
    odoo_env_vars = [
        'ODOO_URL', 'ODOO_DB', 'ODOO_USER', 'ODOO_PASSWORD',
        'ODOO_HOST', 'ODOO_PORT', 'ODOO_DATABASE',
        'DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD'
    ]
    
    found_vars = {}
    for var in odoo_env_vars:
        value = os.environ.get(var)
        if value:
            if 'password' in var.lower():
                value = '*' * len(value)
            found_vars[var] = value
    
    if found_vars:
        print("   Found environment variables:")
        for var, value in found_vars.items():
            print(f"     {var} = {value}")
    else:
        print("   No Odoo environment variables found")

def check_docker_compose():
    """Check Docker Compose files for Odoo configuration"""
    print("\n🐳 Checking Docker Compose files...")
    
    compose_files = ['docker-compose.yml', 'docker-compose.yaml']
    
    for compose_file in compose_files:
        if os.path.exists(compose_file):
            try:
                with open(compose_file, 'r') as f:
                    content = f.read()
                
                if 'odoo' in content.lower():
                    print(f"   Found Odoo in {compose_file}")
                    
                    # Extract relevant lines
                    lines = content.split('\n')
                    in_odoo_service = False
                    
                    for line in lines:
                        if 'odoo' in line.lower() and ':' in line:
                            in_odoo_service = True
                            print(f"     {line.strip()}")
                        elif in_odoo_service and line.strip().startswith('-'):
                            if 'password' in line.lower():
                                line = line.split('=')[0] + '=****'
                            print(f"     {line.strip()}")
                        elif in_odoo_service and not line.startswith(' ') and line.strip():
                            in_odoo_service = False
            
            except Exception as e:
                print(f"   Error reading {compose_file}: {e}")

def provide_configuration_template():
    """Provide a configuration template based on findings"""
    print("\n📝 Configuration Template")
    print("=" * 25)
    print("Edit odoo_config.py with your details:")
    print()
    print("ODOO_CONFIG = {")
    print("    'url': 'https://your-odoo-instance.com',  # Your Odoo URL")
    print("    'source_database': 'your_production_db',   # Database to copy")
    print("    'master_password': 'your_master_password', # Master/admin password")
    print("    'username': 'your_username',               # Your login username")
    print("    'password': 'your_password',               # Your login password")
    print("    'test_suffix': '_test'                     # Suffix for test DB")
    print("}")
    print()
    print("💡 Common configurations:")
    print("   - Local: http://localhost:8069")
    print("   - Odoo.com: https://yourcompany.odoo.com")
    print("   - Custom: https://odoo.yourcompany.com")

def main():
    """Main function"""
    print("🔍 Odoo Configuration Finder")
    print("=" * 30)
    print("This tool helps you find existing Odoo configuration")
    print()
    
    # Find configuration files
    configs = find_odoo_configs()
    
    found_odoo_config = False
    
    if configs:
        for config_file in configs:
            if analyze_config_file(config_file):
                found_odoo_config = True
    
    if not found_odoo_config:
        print("📄 No Odoo configuration files found")
    
    # Check environment variables
    check_environment_variables()
    
    # Check Docker Compose
    check_docker_compose()
    
    # Provide template
    provide_configuration_template()
    
    print("\n🚀 Next Steps:")
    print("1. Edit odoo_config.py with your Odoo details")
    print("2. Run: python3 create_test_db_auto.py")
    print("3. Or use interactive mode: python3 create_odoo_test_database.py")

if __name__ == "__main__":
    main()