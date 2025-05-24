#!/bin/bash
echo "🚀 Starting Odoo Test Instance..."

# Check if test instance is already running
if netstat -tlnp | grep -q ":8070"; then
    echo "✅ Test instance already running on port 8070"
    exit 0
fi

# Start test instance
cd /opt/odoo
source odoo-venv/bin/activate

echo "📝 Starting Odoo test database on port 8070..."
nohup python /opt/odoo/odoo-community/odoo-bin \
    -c /opt/odoo/odoo_test.conf \
    --without-demo=all \
    --load-language=en_US > /var/log/odoo/odoo_test_startup.log 2>&1 &

# Wait a moment and check if it started
sleep 10

if netstat -tlnp | grep -q ":8070"; then
    echo "✅ Odoo test instance started successfully on port 8070"
    echo "📊 Test database: odtshbrain_test"
else
    echo "❌ Failed to start test instance. Check logs:"
    tail -20 /var/log/odoo/odoo_test_startup.log
    exit 1
fi 