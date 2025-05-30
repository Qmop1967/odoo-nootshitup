#!/bin/bash

# Odoo Test Database Tools Setup Script

echo "🚀 Setting up Odoo Test Database Tools"
echo "====================================="

# Make scripts executable
chmod +x create_test_db.sh
chmod +x create_odoo_test_database.py
chmod +x anonymize_test_data.py

echo "✅ Made scripts executable"

# Create backup directory
mkdir -p odoo_backups
echo "✅ Created backup directory: odoo_backups"

echo ""
echo "📋 Available Tools:"
echo ""
echo "1. 🔄 create_test_db.sh"
echo "   - Quick shell script to copy your database"
echo "   - Uses HTTP API for backup/restore"
echo "   - Automatic fallback methods"
echo ""
echo "2. 🐍 create_odoo_test_database.py"
echo "   - Advanced Python script with more features"
echo "   - Data anonymization capabilities"
echo "   - Better error handling"
echo ""
echo "3. 🔒 anonymize_test_data.py"
echo "   - Anonymizes sensitive data in test databases"
echo "   - Replaces emails, phones, addresses"
echo "   - Optional password reset"
echo ""
echo "4. 📖 ODOO_TEST_DATABASE_GUIDE.md"
echo "   - Comprehensive documentation"
echo "   - Troubleshooting guide"
echo "   - Best practices"
echo ""

echo "🎯 Quick Start:"
echo ""
echo "For simple database copy:"
echo "  ./create_test_db.sh"
echo ""
echo "For advanced features:"
echo "  python3 create_odoo_test_database.py"
echo ""
echo "To anonymize test data:"
echo "  python3 anonymize_test_data.py"
echo ""

echo "📚 Read the guide for detailed instructions:"
echo "  cat ODOO_TEST_DATABASE_GUIDE.md"
echo ""

echo "✅ Setup complete! Ready to create test databases."