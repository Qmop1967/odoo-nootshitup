#!/bin/bash

echo "🔧 Setting up automated sync monitoring..."

# Create cron job for monitoring
echo "# Zoho-Odoo Sync Health Check - runs every 15 minutes" > /tmp/sync_cron
echo "*/15 * * * * cd /opt/odoo/migration && python3 prevent_sync_issues.py >> /opt/odoo/migration/logs/monitoring_cron.log 2>&1" >> /tmp/sync_cron

# Install cron job
crontab /tmp/sync_cron
rm /tmp/sync_cron

echo "✅ Monitoring cron job installed"

# Create log rotation
cat > /etc/logrotate.d/zoho-sync << 'EOF'
/opt/odoo/migration/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    notifempty
    create 644 root root
}
EOF

echo "✅ Log rotation configured"

# Set up service auto-restart on failure
systemctl edit --force zoho-odoo-sync-images << 'EOF'
[Service]
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3
EOF

echo "✅ Service auto-restart configured"

echo ""
echo "🎉 MONITORING SETUP COMPLETE!"
echo ""
echo "Features enabled:"
echo "  ✅ Health check every 15 minutes"
echo "  ✅ Automatic service restart on failure"
echo "  ✅ Log rotation (30 days)"
echo "  ✅ Alert logging"
echo ""
echo "Manual commands:"
echo "  Check health: python3 prevent_sync_issues.py"
echo "  View alerts: tail -f /opt/odoo/migration/logs/sync_monitoring.log"
echo "  Service status: systemctl status zoho-odoo-sync-images" 