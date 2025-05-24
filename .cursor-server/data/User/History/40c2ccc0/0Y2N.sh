#!/bin/bash

# Odoo Backup Script
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/odoo/backups"
DB_NAME="your_database_name"  # Replace with your actual database name
KEEP_DAYS=7  # Keep backups for 7 days

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
echo "Starting database backup..."
sudo -u postgres pg_dump $DB_NAME > $BACKUP_DIR/db_${DB_NAME}_${DATE}.sql

# Filestore backup (contains uploaded files, attachments)
echo "Starting filestore backup..."
tar -czf $BACKUP_DIR/filestore_${DB_NAME}_${DATE}.tar.gz /opt/odoo/.local/share/Odoo/filestore/$DB_NAME/

# Configuration backup
cp /opt/odoo/odoo.conf $BACKUP_DIR/odoo.conf_${DATE}

# Remove old backups (older than KEEP_DAYS)
find $BACKUP_DIR -name "*.sql" -mtime +$KEEP_DAYS -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +$KEEP_DAYS -delete
find $BACKUP_DIR -name "odoo.conf_*" -mtime +$KEEP_DAYS -delete

echo "Backup completed: $DATE"
echo "Backup location: $BACKUP_DIR" 