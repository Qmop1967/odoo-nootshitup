#!/bin/bash

echo "🔍 ODOO SYSTEM STATUS CHECK"
echo "================================"
echo "Date: $(date)"
echo ""

# 1. Service Status
echo "📊 SERVICE STATUS:"
if systemctl is-active --quiet odoo; then
    echo "✅ Odoo Service: RUNNING"
else
    echo "❌ Odoo Service: STOPPED"
fi

if systemctl is-active --quiet postgresql; then
    echo "✅ PostgreSQL: RUNNING"
else
    echo "❌ PostgreSQL: STOPPED"
fi
echo ""

# 2. Disk Space
echo "💾 DISK SPACE:"
df -h / | tail -1 | awk '{print "   Root Partition: " $4 " available (" $5 " used)"}'
echo ""

# 3. Memory Usage
echo "🧠 MEMORY USAGE:"
free -h | grep "Mem:" | awk '{print "   Total: " $2 ", Used: " $3 ", Available: " $7}'
echo ""

# 4. Recent Backups
echo "💾 RECENT BACKUPS:"
if [ -d "/opt/odoo/backups" ]; then
    backup_count=$(ls /opt/odoo/backups/db_*.sql 2>/dev/null | wc -l)
    if [ $backup_count -gt 0 ]; then
        echo "   Total backups: $backup_count"
        echo "   Latest backup: $(ls -t /opt/odoo/backups/db_*.sql 2>/dev/null | head -1 | xargs ls -lh | awk '{print $6 " " $7 " " $8}')"
    else
        echo "   ❌ No backups found!"
    fi
else
    echo "   ❌ Backup directory not found!"
fi
echo ""

# 5. Web Accessibility
echo "🌐 WEB ACCESSIBILITY:"
if curl -s --max-time 5 http://localhost:8069 > /dev/null 2>&1; then
    echo "✅ Odoo Web Interface: ACCESSIBLE"
else
    echo "❌ Odoo Web Interface: NOT ACCESSIBLE"
fi
echo ""

# 6. Recent Errors
echo "⚠️ RECENT ERRORS (last 24 hours):"
error_count=$(grep -c "ERROR" /var/log/odoo/odoo.log 2>/dev/null || echo 0)
echo "   Error count in logs: $error_count"
if [ $error_count -gt 0 ]; then
    echo "   Latest error:"
    grep "ERROR" /var/log/odoo/odoo.log | tail -1 | cut -c1-80
fi
echo ""

echo "================================"
echo "💡 Run: cat /opt/odoo/MAINTENANCE_GUIDE.md for detailed maintenance info" 