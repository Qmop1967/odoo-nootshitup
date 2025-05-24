# 🛡️ Odoo Enterprise Protection & Maintenance Guide

## ✅ AUTOMATED PROTECTIONS (Already Set Up)

### 1. Daily Backups ✓
- **When:** Every day at 2:00 AM
- **What:** Database + Files + Configuration
- **Location:** `/opt/odoo/backups/`
- **Retention:** 7 days (automatic cleanup)
- **Log:** `/var/log/odoo_backup.log`

### 2. System Service ✓
- **Service:** `systemctl status odoo`
- **Auto-restart:** Yes (on failure)
- **Auto-start:** Yes (on boot)

## 🔧 SIMPLE WEEKLY MAINTENANCE (5 minutes)

### Check System Health
```bash
# 1. Check Odoo service
systemctl status odoo

# 2. Check backup status
ls -la /opt/odoo/backups/ | tail -5

# 3. Check disk space
df -h

# 4. Check logs for errors
tail -20 /var/log/odoo/odoo.log | grep ERROR
```

## 🔒 SECURITY RECOMMENDATIONS

### 1. Change Default Passwords
- **Master Password:** Change from `admin123` to something stronger
- **Database Password:** Set a strong password in PostgreSQL

### 2. Firewall (Simple Setup)
```bash
# Allow only necessary ports
ufw enable
ufw allow 22    # SSH
ufw allow 8069  # Odoo
ufw deny 5432   # PostgreSQL (block external access)
```

### 3. SSL Certificate (Optional but Recommended)
- Use Cloudflare or Let's Encrypt for HTTPS
- Redirect HTTP to HTTPS

## 📊 MONITORING CHECKLIST

### Daily (Automated)
- ✅ Automatic backups
- ✅ Service monitoring

### Weekly (Manual - 5 minutes)
- [ ] Check backup files exist
- [ ] Check disk space (>20% free)
- [ ] Review error logs
- [ ] Test Odoo accessibility

### Monthly (Manual - 15 minutes)
- [ ] Update system packages: `apt update && apt upgrade`
- [ ] Check Odoo Enterprise updates
- [ ] Review user access permissions
- [ ] Test backup restoration (important!)

## 🚨 EMERGENCY PROCEDURES

### If Odoo Won't Start
```bash
# 1. Check service status
systemctl status odoo

# 2. Restart service
systemctl restart odoo

# 3. Check logs
tail -50 /var/log/odoo/odoo.log

# 4. Check PostgreSQL
systemctl status postgresql
```

### Database Recovery
```bash
# 1. Stop Odoo
systemctl stop odoo

# 2. Restore database (replace BACKUP_FILE with actual file)
sudo -u postgres dropdb odtshbrain
sudo -u postgres createdb odtshbrain
sudo -u postgres psql odtshbrain < /opt/odoo/backups/BACKUP_FILE.sql

# 3. Restore filestore
tar -xzf /opt/odoo/backups/filestore_BACKUP_FILE.tar.gz -C /

# 4. Start Odoo
systemctl start odoo
```

## 📞 QUICK COMMANDS REFERENCE

```bash
# Service Management
systemctl start odoo         # Start Odoo
systemctl stop odoo          # Stop Odoo
systemctl restart odoo       # Restart Odoo
systemctl status odoo        # Check status

# Manual Backup
/opt/odoo/backup_odoo.sh     # Run backup now

# Check Logs
tail -f /var/log/odoo/odoo.log        # Live logs
tail -f /var/log/odoo_backup.log      # Backup logs

# Database Access
sudo -u postgres psql odtshbrain      # Access database
```

## 💡 PERFORMANCE TIPS

1. **Monitor Memory Usage:** `htop` or `free -h`
2. **Database Maintenance:** Run VACUUM monthly
3. **Log Rotation:** Keep logs under control
4. **Module Updates:** Only install trusted modules

## 📋 MONTHLY CHECKLIST

- [ ] System updates applied
- [ ] Backup restoration tested
- [ ] Disk space sufficient (>20%)
- [ ] No critical errors in logs
- [ ] Enterprise subscription active
- [ ] User access reviewed
- [ ] Performance acceptable

---
**Remember:** Simple, consistent maintenance is better than complex procedures! 