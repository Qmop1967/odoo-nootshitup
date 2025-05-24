#!/bin/bash

echo "🚀 STARTING ODOO AND MIGRATION SCRIPT"
echo "====================================="

# Step 1: Stop any existing Odoo processes
echo "🧹 Cleaning up existing processes..."
pkill -f "odoo-bin" 2>/dev/null || true
sleep 3

# Step 2: Start Odoo service
echo "🔄 Starting Odoo service..."
cd /opt/odoo
source odoo-venv/bin/activate

# Start Odoo in background
nohup python /opt/odoo/odoo-community/odoo-bin -c /opt/odoo/odoo.conf > /var/log/odoo/odoo_startup.log 2>&1 &

echo "⏳ Waiting for Odoo to start (30 seconds)..."
sleep 30

# Step 3: Check if Odoo is running
if curl -s -f http://localhost:8069/web/database/manager > /dev/null; then
    echo "✅ Odoo is running on port 8069"
else
    echo "❌ Odoo failed to start. Checking logs..."
    tail -20 /var/log/odoo/odoo_startup.log
    exit 1
fi

# Step 4: Run the migration
echo "🔄 Starting migration..."
cd /opt/odoo/migration
python run_full_migration.py

echo "�� Script completed!" 