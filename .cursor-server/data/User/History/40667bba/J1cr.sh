#!/bin/bash
echo "🔧 FIXING ODOO TEST INSTANCE"
echo "=============================="

# Step 1: Clean up any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "odoo_test.conf" 2>/dev/null || true
pkill -f "port.*8070" 2>/dev/null || true
sleep 3

# Step 2: Kill anything using port 8070
echo "🔌 Freeing port 8070..."
fuser -k 8070/tcp 2>/dev/null || true
sleep 2

# Step 3: Check if port is free
if ss -tlnp | grep -q ":8070"; then
    echo "❌ Port 8070 still in use. Manual intervention needed."
    ss -tlnp | grep ":8070"
    exit 1
else
    echo "✅ Port 8070 is free"
fi

# Step 4: Ensure test database exists and is properly initialized
echo "🗄️ Checking test database..."
cd /opt/odoo
source odoo-venv/bin/activate

# Check if database exists
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "odtshbrain_test"; then
    echo "✅ Test database exists"
else
    echo "📝 Creating test database..."
    sudo -u postgres createdb odtshbrain_test
fi

# Step 5: Initialize the database properly
echo "🚀 Initializing test database with base modules..."
timeout 120 python /opt/odoo/odoo-community/odoo-bin \
    -c /opt/odoo/odoo_test.conf \
    -d odtshbrain_test \
    -i base,web,mail,contacts,sale,purchase,account,stock \
    --stop-after-init \
    --without-demo=all \
    --workers=0 \
    --limit-time-cpu=600 \
    --limit-time-real=1200

if [ $? -eq 0 ]; then
    echo "✅ Database initialization completed"
else
    echo "❌ Database initialization failed"
    exit 1
fi

# Step 6: Start the test instance
echo "🎯 Starting Odoo test instance..."
nohup python /opt/odoo/odoo-community/odoo-bin \
    -c /opt/odoo/odoo_test.conf \
    --workers=1 \
    --limit-time-cpu=300 \
    --limit-time-real=600 \
    --max-cron-threads=0 > /var/log/odoo/odoo_test_startup.log 2>&1 &

# Step 7: Wait and verify startup
echo "⏳ Waiting for startup (30 seconds)..."
sleep 30

# Check if it's running
if ss -tlnp | grep -q ":8070"; then
    echo "✅ Odoo test instance is running on port 8070"
    
    # Test web access
    if curl -s -f http://localhost:8070/web/database/manager > /dev/null; then
        echo "✅ Web interface is accessible"
    else
        echo "⚠️ Web interface may still be loading..."
    fi
    
    echo ""
    echo "🎉 ODOO TEST INSTANCE READY!"
    echo "   Port: 8070"
    echo "   Database: odtshbrain_test" 
    echo "   Web: http://localhost:8070"
    echo ""
    
else
    echo "❌ Failed to start Odoo test instance"
    echo "📋 Last 20 lines of startup log:"
    tail -20 /var/log/odoo/odoo_test_startup.log
    exit 1
fi 