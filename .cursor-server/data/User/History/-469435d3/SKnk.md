# Zoho to Odoo Product Sync System

## 🎯 Overview

This system provides **one-way synchronization** of products from Zoho to Odoo with:

- ✅ **Enhanced image handling** from Zoho Books/Inventory
- ✅ **Smart change detection** (sync only what changed)
- ✅ **Automatic duplicate prevention**
- ✅ **Scheduled synchronization**
- ✅ **Complete image preservation**

## 📁 System Components

### 1. Core Sync Engine
**File**: `zoho_product_sync.py`
- Main synchronization logic
- Enhanced image downloading from multiple Zoho sources
- Change detection using checksums
- Smart duplicate prevention

### 2. Automated Scheduler
**File**: `product_sync_scheduler.py`
- Runs sync automatically at configurable intervals
- Error handling and recovery
- Full sync vs incremental sync scheduling

### 3. Configuration Files
- `config/zoho_config.json` - Zoho API credentials
- `config/field_mapping.json` - Field mapping between Zoho and Odoo
- `config/sync_schedule.json` - Scheduler configuration (auto-created)

### 4. Data Storage
- `data/product_sync_data.json` - Sync tracking and change detection
- `data/product_images/` - Local image cache for tracking

## 🚀 Quick Start

### Initial Product Sync

```bash
# Navigate to migration directory
cd /opt/odoo/migration

# Run manual sync (first time - choose option 2 for full sync)
python3 zoho_product_sync.py

# Check results
python3 check_migration_progress.py
```

### Setup Automated Sync

```bash
# Check scheduler status
python3 product_sync_scheduler.py status

# Configure sync interval (every 4 hours by default)
python3 product_sync_scheduler.py config --interval 6

# Start automated sync (runs in background)
python3 product_sync_scheduler.py start
```

## 🔧 Detailed Usage

### Manual Sync Options

```bash
# Smart sync (only changed products)
python3 zoho_product_sync.py
# Choose option 1

# Force full sync (all products)
python3 zoho_product_sync.py  
# Choose option 2
```

### Scheduler Management

```bash
# Show current status
python3 product_sync_scheduler.py status

# Run immediate sync
python3 product_sync_scheduler.py run-now

# Enable/disable scheduler
python3 product_sync_scheduler.py config --enable
python3 product_sync_scheduler.py config --disable

# Configure sync intervals
python3 product_sync_scheduler.py config --interval 4      # Every 4 hours
python3 product_sync_scheduler.py config --full-sync-days 7 # Full sync weekly

# Start scheduler daemon
python3 product_sync_scheduler.py start
```

## 🖼️ Image Handling Features

### Multiple Source Support
The system attempts to fetch images from:

1. **Zoho Books** item images
2. **Zoho Inventory** (if available) - often has better image support
3. Multiple image formats and URLs

### Image Processing
- ✅ Downloads images securely with proper authentication
- ✅ Converts to base64 for Odoo storage
- ✅ Saves local copies for change tracking
- ✅ Handles multiple image formats
- ✅ Proper error handling for missing/broken images

### Image Change Detection
- Images are tracked by MD5 hash
- Only downloads when image has changed
- Preserves bandwidth and processing time

## 🔄 Sync Logic

### Change Detection Algorithm
1. **Checksum Calculation**: Product data is hashed to detect changes
2. **Smart Comparison**: Only sync products that have actually changed
3. **Image Tracking**: Images tracked separately by hash
4. **Efficient Updates**: Only update changed fields

### Sync Types

#### Smart Sync (Default)
- Compares checksums to detect changes
- Only syncs products that have been modified
- Much faster for subsequent runs
- Recommended for scheduled operation

#### Full Sync
- Syncs all products regardless of changes
- Useful for initial migration or recovery
- Automatically scheduled weekly by default

### Duplicate Prevention
- **Zoho ID Tracking**: Uses Zoho item_id for exact matching
- **Name Matching**: Fallback to product name matching
- **Update vs Create**: Intelligently decides whether to update or create

## 📊 Monitoring & Tracking

### Sync Statistics
```bash
# View detailed status
python3 product_sync_scheduler.py status

# Output shows:
# - Last sync time
# - Products added/updated in last run
# - Total products tracked
# - Error counts
# - Schedule configuration
```

### Log Files
- `logs/product_sync_scheduler.log` - Detailed sync operations
- `logs/sync_notifications.log` - Summary notifications and errors

### Sync Data Tracking
The system maintains detailed tracking in `data/product_sync_data.json`:
```json
{
  "last_sync": "2025-05-23T17:30:00",
  "products": {
    "zoho_item_id": {
      "odoo_id": 123,
      "last_modified": "2025-05-23T17:30:00", 
      "checksum": "abc123..."
    }
  },
  "sync_stats": {
    "total_synced": 1250,
    "last_run_added": 5,
    "last_run_updated": 12
  }
}
```

## ⚙️ Configuration

### Zoho Configuration
Ensure your `config/zoho_config.json` includes:
```json
{
  "zoho_books": {
    "base_url": "https://www.zohoapis.com/books/v3",
    "inventory_base_url": "https://www.zohoapis.com/inventory/v1",
    "client_id": "your_client_id",
    "client_secret": "your_client_secret", 
    "refresh_token": "your_refresh_token",
    "organization_id": "your_org_id"
  }
}
```

### Field Mapping
Product fields are mapped in `config/field_mapping.json`:
```json
{
  "products": {
    "zoho_books": {
      "name": "name",
      "description": "description", 
      "rate": "list_price",
      "purchase_rate": "standard_price",
      "unit": "uom_id"
    },
    "default_values": {
      "sale_ok": true,
      "purchase_ok": true,
      "type": "product"
    }
  }
}
```

### Scheduler Configuration
Auto-created in `config/sync_schedule.json`:
```json
{
  "enabled": true,
  "sync_interval_hours": 4,
  "force_full_sync_days": 7,
  "max_consecutive_errors": 5,
  "notifications": {
    "log_file": "/opt/odoo/migration/logs/sync_notifications.log"
  }
}
```

## 🛡️ Error Handling

### Automatic Recovery
- **Rate Limiting**: Respects Zoho API limits
- **Connection Errors**: Automatic retry with backoff
- **Image Failures**: Continues sync even if images fail
- **Partial Failures**: Logs errors but continues with other products

### Error Escalation
- Tracks consecutive failures
- Automatically disables scheduler after 5 consecutive failures
- Requires manual intervention to re-enable

### Manual Recovery
```bash
# Reset error count and re-enable
python3 product_sync_scheduler.py config --enable

# Force full sync to recover
python3 zoho_product_sync.py   # Choose option 2
```

## 🔍 Troubleshooting

### Common Issues

#### "No products fetched from Zoho"
- Check Zoho API credentials
- Verify organization_id is correct
- Check network connectivity

#### "Failed to download image"
- Images may not be publicly accessible
- Check Zoho permissions
- Images will be skipped, product still synced

#### "Scheduler disabled"
- Check for consecutive errors in logs
- Use `--enable` flag to re-enable
- Review error logs for root cause

### Debug Mode
Add debugging to sync:
```python
# In zoho_product_sync.py, change logging level:
logging.basicConfig(level=logging.DEBUG, ...)
```

## 📈 Performance Optimization

### Recommended Settings
- **Development**: Sync every 1-2 hours
- **Production**: Sync every 4-6 hours  
- **Low-change environments**: Sync daily

### Resource Usage
- **Smart Sync**: Very low resource usage
- **Full Sync**: Higher CPU/memory usage
- **Image Downloads**: Network intensive

### Scaling Considerations
- For >10,000 products: Consider reducing batch sizes
- Monitor memory usage during image downloads
- Use dedicated server for large inventories

## 🎯 Best Practices

### Initial Setup
1. Run full sync manually first
2. Verify image downloads work properly
3. Test scheduler with short intervals
4. Monitor logs for first few runs

### Ongoing Maintenance
1. Monitor sync logs regularly
2. Check for failed image downloads
3. Verify product counts match expectations
4. Keep backups of sync data

### Data Management
1. Images are cached locally - monitor disk space
2. Sync data file grows with product count
3. Log files should be rotated regularly

## 🔗 Integration with Existing Scripts

### Migration Progress Check
```bash
# Enhanced to show product sync status
python3 check_migration_progress.py
```

### Backup Integration
```bash
# Backup before major syncs
pg_dump odtshbrain > backup_before_sync_$(date +%Y%m%d).sql
```

## 🚀 Next Steps

After successful product sync setup:

1. **Monitor** the first few sync cycles
2. **Adjust** intervals based on your change frequency
3. **Set up** systemd service for production (optional)
4. **Configure** additional monitoring/alerting

## 📞 Support

This product sync system provides enterprise-grade synchronization with:
- Complete image preservation
- Intelligent change detection  
- Robust error handling
- Comprehensive logging

Your Zoho products will now stay automatically synchronized with Odoo! 🎉 