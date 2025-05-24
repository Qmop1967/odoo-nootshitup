# 🔄 Continuous Zoho-Odoo Sync Server Guide

## 🎯 **What It Does**

The Continuous Sync Server maintains **EXACT synchronization** between your Zoho Books and Odoo products:

✅ **Same product count** in both systems (2000 in Zoho = 2000 in Odoo)  
✅ **Continuous monitoring** for changes every 5 minutes  
✅ **Automatic sync** when changes are detected  
✅ **USD to IQD conversion** at 1500 rate  
✅ **Change detection** - only syncs what changed  
✅ **Complete logging** and monitoring  

---

## 🚀 **Quick Start**

### **Option 1: Interactive Mode**
```bash
cd /opt/odoo/migration
python3 continuous_sync_server.py
```
Then select option 1 to start with 5-minute intervals.

### **Option 2: Direct Start (Recommended)**
```bash
cd /opt/odoo/migration
python3 start_sync_server.py
```
This starts immediately with default settings.

### **Option 3: Background Service**
```bash
# Copy service file
sudo cp zoho-odoo-sync.service /etc/systemd/system/

# Enable and start service
sudo systemctl enable zoho-odoo-sync
sudo systemctl start zoho-odoo-sync

# Check status
sudo systemctl status zoho-odoo-sync
```

---

## 📊 **Monitoring**

### **Real-time Monitor**
```bash
cd /opt/odoo/migration
python3 sync_monitor.py
```

Options:
- **Option 1**: Show current status
- **Option 2**: Watch mode (auto-refresh every 30 seconds)

### **Check Logs**
```bash
# Live log monitoring
tail -f /opt/odoo/migration/logs/sync_server.log

# Recent logs
tail -100 /opt/odoo/migration/logs/sync_server.log
```

---

## ⚙️ **Configuration**

### **Sync Intervals**
- **Default**: 300 seconds (5 minutes)
- **Minimum**: 60 seconds (1 minute)
- **Recommended**: 300-600 seconds for production

### **Environment Variables**
```bash
export SYNC_INTERVAL=300    # Sync every 5 minutes
export PYTHONPATH=/opt/odoo/migration
```

### **Custom Interval**
```bash
# Start with custom 10-minute interval
SYNC_INTERVAL=600 python3 start_sync_server.py
```

---

## 📁 **File Structure**

```
/opt/odoo/migration/
├── continuous_sync_server.py    # Main sync server
├── start_sync_server.py        # Auto-start script
├── sync_monitor.py             # Monitoring tool
├── zoho-odoo-sync.service      # Systemd service
├── logs/
│   ├── sync_server.log         # Main log file
│   └── sync_service.log        # Service log
└── data/sync_server/
    └── sync_tracking.json      # Sync state tracking
```

---

## 🔍 **What Gets Synced**

### **Product Data**
- ✅ Product names
- ✅ Prices (USD → IQD conversion)
- ✅ SKU/codes
- ✅ Descriptions
- ✅ Units of measure
- ✅ Status (active/inactive)

### **Smart Features**
- 🧠 **Change Detection**: Only syncs products that changed
- 🔄 **Duplicate Prevention**: Finds existing products
- 💱 **Currency Conversion**: Automatic USD to IQD (×1500)
- 📊 **Count Matching**: Ensures exact same number in both systems
- 🛡️ **Error Recovery**: Continues on individual product errors

---

## 📊 **Status Information**

### **Sync Status**
- 🔄 **Running**: Server is actively syncing
- ⏸️ **Stopped**: Server is not running
- ✅ **Last Sync**: When last sync completed
- 📈 **Statistics**: Success rate, products synced, etc.

### **Product Count Verification**
- 📦 **Zoho Count**: Number of products in Zoho
- 📦 **Odoo Count**: Number of products in Odoo  
- ✅ **Match Status**: Whether counts are identical

### **Sync History**
- 📝 Last 50 sync operations
- ➕ Products added per sync
- 🔄 Products updated per sync
- ⏱️ Duration of each sync

---

## 🛑 **Stopping the Server**

### **Interactive Mode**
- Press `Ctrl+C` in the terminal

### **Background Service**
```bash
sudo systemctl stop zoho-odoo-sync
```

### **Find and Kill Process**
```bash
# Find process
ps aux | grep continuous_sync_server

# Kill by PID
sudo kill -TERM <PID>
```

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. Zoho API Authentication Errors**
```
❌ Error getting Zoho token: 400 Client Error
```
**Solution**: Refresh Zoho OAuth credentials in `config/zoho_config.json`

#### **2. Odoo Connection Errors**
```
❌ Failed to authenticate with Odoo
```
**Solution**: Check Odoo database config in `config/zoho_config.json`

#### **3. Count Mismatch**
```
❌ Count Match: NO (Difference: -50)
```
**Solution**: Run one-time full sync to resolve

### **Diagnostic Commands**
```bash
# Check current status
python3 sync_monitor.py

# Test Zoho connection
python3 -c "from continuous_sync_server import ContinuousSyncServer; s=ContinuousSyncServer(); print('✅ Connected')"

# Check recent logs
tail -50 /opt/odoo/migration/logs/sync_server.log | grep ERROR
```

---

## 🎯 **Use Cases**

### **1. Testing Phase** (Current)
- Run sync server on test database
- Monitor for several days/weeks
- Verify data integrity
- Test with manual changes in Zoho

### **2. Pre-Migration**
- Keep test database in perfect sync
- Validate all product data
- Test business processes
- Train users

### **3. Go-Live Preparation**
- Stop sync server
- Backup current state
- Switch to production database
- Final data validation

---

## ⚡ **Performance**

### **Expected Performance**
- **2000 products**: ~30-60 seconds per sync
- **Memory usage**: ~100-200 MB
- **CPU usage**: Low (only during sync periods)
- **Network**: Minimal (only changed products)

### **Optimization Tips**
- Use 5-10 minute intervals for production
- Monitor logs for any recurring errors
- Keep Zoho API rate limits in mind
- Regular cleanup of old log files

---

## 🔮 **Next Steps**

1. **Start the sync server** with default settings
2. **Monitor for 24 hours** to ensure stability  
3. **Test manual changes** in Zoho to verify sync
4. **Adjust interval** if needed based on change frequency
5. **Prepare for production** migration when ready

---

## 📞 **Support Commands**

```bash
# Quick status check
cd /opt/odoo/migration && python3 sync_monitor.py

# Start sync server
cd /opt/odoo/migration && python3 start_sync_server.py

# Stop all sync processes
sudo pkill -f continuous_sync_server

# View live logs
tail -f /opt/odoo/migration/logs/sync_server.log
```

---

**🎉 Your sync server is ready to maintain perfect Zoho-Odoo synchronization!** 