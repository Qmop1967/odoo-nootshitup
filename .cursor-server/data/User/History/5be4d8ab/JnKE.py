#!/usr/bin/env python3
"""
Initialize Test Database for Migration
=====================================
This script initializes the test database with necessary modules and configurations.

Author: Migration Assistant
Date: 2025
"""

import subprocess
import sys
import time

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"📋 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd="/opt/odoo")
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error during {description}: {e}")
        return False

def main():
    """Initialize test database"""
    print("🚀 INITIALIZING TEST DATABASE FOR MIGRATION")
    print("=" * 55)
    
    # Create necessary directories
    print("📁 Creating directories...")
    subprocess.run("mkdir -p /opt/odoo/.local/share/Odoo_test", shell=True)
    subprocess.run("mkdir -p /var/log/odoo", shell=True)
    
    # Initialize base modules in test database
    init_command = (
        "source odoo-venv/bin/activate && "
        "python odoo-community/odoo-bin -c odoo_test.conf "
        "--init=base,account,sale,purchase,stock,website "
        "--stop-after-init --without-demo=False"
    )
    
    if run_command(init_command, "Initializing test database with base modules"):
        print("\n🎉 TEST DATABASE INITIALIZATION COMPLETED!")
        print("=" * 45)
        print()
        print("📊 NEXT STEPS:")
        print("1. Set up Zoho API credentials:")
        print("   python /opt/odoo/migration/setup_zoho_auth.py")
        print()
        print("2. Start test server (optional):")
        print("   cd /opt/odoo && source odoo-venv/bin/activate")
        print("   python odoo-community/odoo-bin -c odoo_test.conf")
        print("   Access at: http://localhost:8070")
        print()
        print("3. Run migration to test database:")
        print("   python /opt/odoo/migration/zoho_odoo_migrator.py test")
        print()
        print("✅ The test environment is ready for migration!")
    else:
        print("❌ Failed to initialize test database")
        sys.exit(1)

if __name__ == "__main__":
    main() 