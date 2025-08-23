# Smart Canary Protocol - Troubleshooting Runbook

## 🚨 Quick Reference

### **Emergency Commands**
```bash
# System status check
./canary status

# View recent errors
./canary logs | grep -i error

# Test system without API calls
./canary test --no-openai

# Emergency analysis (bypass normal scheduling)
./canary emergency

# Database integrity check
python3 core/backup_verification.py --integrity-only data/canary_protocol.db
```

### **Log Locations**
- **Application Logs**: `logs/canary_*.log`
- **System Logs**: `journalctl -u canary` or `/var/log/syslog`
- **Cron Logs**: `journalctl -u cron` or `/var/log/cron`

## 🔍 Common Issues and Solutions

### **1. OpenAI API Issues**

#### **Problem**: API Key Invalid or Expired
```
Error: OpenAI API call failed: Incorrect API key provided
```

**Diagnosis:**
```bash
# Check API key configuration
grep OPENAI_API_KEY config/.env
python3 -c "import os; from dotenv import load_dotenv; load_dotenv('config/.env'); print('API Key:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')"
```

**Solution:**
1. Verify API key in OpenAI dashboard
2. Update `config/.env` with correct key
3. Restart any running processes
4. Test with: `./canary test --verbose`

#### **Problem**: Rate Limit Exceeded
```
Error: Rate limit reached for requests
```

**Diagnosis:**
```bash
# Check recent API usage
grep -i "rate limit" logs/*.log | tail -10
```

**Solution:**
1. Wait for rate limit reset (usually 1 minute)
2. Reduce analysis frequency in config
3. Implement exponential backoff (already included)
4. Consider upgrading OpenAI plan

#### **Problem**: Model Not Available
```
Error: The model 'gpt-4o' does not exist
```

**Solution:**
1. Check model availability in OpenAI dashboard
2. Update model name in `config/config.yaml`:
   ```yaml
   ai:
     model: "gpt-4"  # Fallback model
   ```

### **2. Database Issues**

#### **Problem**: Database Locked
```
Error: database is locked
```

**Diagnosis:**
```bash
# Check for running processes
ps aux | grep -i canary
lsof data/canary_protocol.db
```

**Solution:**
```bash
# Kill stuck processes
pkill -f "python3.*canary"

# Wait a moment, then test
sleep 5
./canary status

# If still locked, restart system services
sudo systemctl restart canary.timer
```

#### **Problem**: Database Corruption
```
Error: database disk image is malformed
```

**Diagnosis:**
```bash
# Check database integrity
sqlite3 data/canary_protocol.db "PRAGMA integrity_check;"
```

**Solution:**
```bash
# Stop all services
sudo systemctl stop canary.timer

# Backup current database
cp data/canary_protocol.db data/canary_protocol.db.corrupted

# Restore from latest backup
cp data/backups/$(ls -t data/backups/*.db | head -1) data/canary_protocol.db

# Verify restoration
./canary status

# Restart services
sudo systemctl start canary.timer
```

#### **Problem**: Migration Failures
```
Error: Migration 1.1.0 failed: no such column
```

**Diagnosis:**
```bash
# Check migration status
python3 core/database_migrations.py --status
```

**Solution:**
```bash
# Rollback failed migration
python3 core/database_migrations.py --rollback 1.1.0

# Check database schema
sqlite3 data/canary_protocol.db ".schema"

# Reapply migrations
python3 core/database_migrations.py --migrate
```

### **3. Email Delivery Issues**

#### **Problem**: Gmail Authentication Failed
```
Error: (535, '5.7.8 Username and Password not accepted')
```

**Diagnosis:**
```bash
# Test email configuration
python3 -c "
import smtplib
import os
from dotenv import load_dotenv
load_dotenv('config/.env')
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(os.getenv('GMAIL_USER'), os.getenv('GMAIL_APP_PASSWORD'))
    print('Email authentication successful')
    server.quit()
except Exception as e:
    print(f'Email authentication failed: {e}')
"
```

**Solution:**
1. Verify Gmail App Password is correct
2. Ensure 2FA is enabled on Gmail account
3. Generate new App Password if needed
4. Update `config/.env` with new credentials

#### **Problem**: No Email Recipients
```
Warning: No subscribers found
```

**Solution:**
```bash
# Check subscribers file
cat config/subscribers.txt

# Add email addresses (one per line)
echo "admin@yourdomain.com" >> config/subscribers.txt
```

### **4. News Feed Issues**

#### **Problem**: RSS Feed Timeouts
```
Error: HTTPSConnectionPool timeout
```

**Diagnosis:**
```bash
# Test network connectivity
curl -I https://feeds.npr.org/1001/rss.xml
ping -c 3 feeds.npr.org
```

**Solution:**
1. Check internet connectivity
2. Verify RSS URLs in `config/config.yaml`
3. Increase timeout in configuration:
   ```yaml
   monitoring:
     request_timeout: 30
   ```

#### **Problem**: No Headlines Collected
```
Warning: Fetched 0 headlines
```

**Diagnosis:**
```bash
# Test news source manually
python3 -c "
import feedparser
feed = feedparser.parse('https://feeds.npr.org/1001/rss.xml')
print(f'Entries: {len(feed.entries)}')
if feed.entries:
    print(f'Latest: {feed.entries[0].title}')
"
```

**Solution:**
1. Update RSS URLs in configuration
2. Check if news sources changed their feed URLs
3. Add alternative news sources

### **5. System Resource Issues**

#### **Problem**: High Memory Usage
```
Error: MemoryError
```

**Diagnosis:**
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head -10
```

**Solution:**
```bash
# Restart services to free memory
sudo systemctl restart canary.timer

# Reduce batch sizes in config
# Add memory limits to systemd service
sudo systemctl edit canary.service
# Add:
# [Service]
# MemoryMax=1G
```

#### **Problem**: Disk Space Full
```
Error: No space left on device
```

**Diagnosis:**
```bash
# Check disk usage
df -h
du -sh /home/canary/CanaryProtocol/*
```

**Solution:**
```bash
# Clean old logs
find logs/ -name "*.log" -mtime +30 -delete

# Run data archival
python3 core/data_archival.py --run

# Clean old archives
find data/archives/ -name "*.gz" -mtime +365 -delete

# Compress current logs
gzip logs/*.log
```

### **6. Cron Job Issues**

#### **Problem**: Cron Jobs Not Running
```
No recent analysis found
```

**Diagnosis:**
```bash
# Check cron status
sudo systemctl status cron
crontab -l

# Check cron logs
journalctl -u cron | tail -20
```

**Solution:**
```bash
# Restart cron service
sudo systemctl restart cron

# Verify cron jobs
crontab -e

# Test manual execution
/home/canary/CanaryProtocol/scripts/run_daily_collection.sh
```

#### **Problem**: Permission Denied in Cron
```
Error: Permission denied: '/home/canary/CanaryProtocol/canary'
```

**Solution:**
```bash
# Fix file permissions
chmod +x /home/canary/CanaryProtocol/canary
chmod +x /home/canary/CanaryProtocol/scripts/*.sh

# Ensure cron runs as correct user
crontab -e
# Add: SHELL=/bin/bash
# Add: PATH=/usr/local/bin:/usr/bin:/bin
```

### **7. Configuration Issues**

#### **Problem**: Configuration File Not Found
```
Error: Configuration file not found: config/config.yaml
```

**Solution:**
```bash
# Create configuration from example
cp config/config_example.yaml config/config.yaml

# Verify file exists and is readable
ls -la config/config.yaml
```

#### **Problem**: Invalid YAML Configuration
```
Error: yaml.scanner.ScannerError
```

**Diagnosis:**
```bash
# Validate YAML syntax
python3 -c "
import yaml
try:
    with open('config/config.yaml', 'r') as f:
        yaml.safe_load(f)
    print('YAML is valid')
except yaml.YAMLError as e:
    print(f'YAML error: {e}')
"
```

**Solution:**
1. Fix YAML syntax errors (check indentation)
2. Use online YAML validator
3. Restore from backup: `cp config/config.yaml.backup config/config.yaml`

## 🔧 Diagnostic Tools

### **System Health Check**
```bash
#!/bin/bash
# Save as scripts/full_diagnostic.sh

echo "=== Smart Canary Protocol Diagnostic ==="
echo "Timestamp: $(date)"
echo

echo "1. System Status:"
./canary status
echo

echo "2. Database Check:"
sqlite3 data/canary_protocol.db "SELECT COUNT(*) as total_digests FROM weekly_digests;"
echo

echo "3. Recent Logs (last 10 errors):"
grep -i error logs/*.log | tail -10
echo

echo "4. Disk Usage:"
df -h | grep -E "(Filesystem|/home)"
echo

echo "5. Memory Usage:"
free -h
echo

echo "6. Process Check:"
ps aux | grep -E "(python3.*canary|cron)" | grep -v grep
echo

echo "7. Network Connectivity:"
curl -s -o /dev/null -w "%{http_code}" https://api.openai.com/v1/models || echo "OpenAI API unreachable"
echo

echo "8. Configuration Validation:"
python3 -c "
try:
    from core.config_loader import load_config
    config = load_config()
    print('Configuration loaded successfully')
except Exception as e:
    print(f'Configuration error: {e}')
"
```

### **Performance Monitor**
```bash
#!/bin/bash
# Save as scripts/performance_monitor.sh

echo "=== Performance Monitoring ==="
echo "Timestamp: $(date)"
echo

echo "Database Size:"
du -sh data/canary_protocol.db

echo "Log Directory Size:"
du -sh logs/

echo "Archive Directory Size:"
du -sh data/archives/

echo "Recent Analysis Times:"
grep "Analysis completed" logs/*.log | tail -5 | while read line; do
    echo "$line" | grep -o "[0-9]\+\.[0-9]\+ seconds"
done

echo "API Response Times:"
grep "OpenAI API call" logs/*.log | tail -5 | while read line; do
    echo "$line" | grep -o "[0-9]\+ms"
done
```

## 🚨 Emergency Procedures

### **Complete System Recovery**
```bash
# 1. Stop all services
sudo systemctl stop canary.timer
pkill -f "python3.*canary"

# 2. Backup current state
cp -r data/ data_backup_$(date +%Y%m%d_%H%M%S)

# 3. Restore from known good backup
cp data/backups/latest_verified.db data/canary_protocol.db

# 4. Verify restoration
./canary status

# 5. Test functionality
./canary test --no-openai

# 6. Restart services
sudo systemctl start canary.timer
```

### **Database Emergency Recovery**
```bash
# 1. Create emergency backup
sqlite3 data/canary_protocol.db ".backup emergency_backup.db"

# 2. Export critical data
sqlite3 data/canary_protocol.db ".mode csv" ".output critical_data.csv" "SELECT * FROM weekly_digests;"

# 3. Recreate database from scratch
rm data/canary_protocol.db
./canary setup

# 4. Import critical data if needed
# (Manual process based on exported CSV)
```

## 📞 Escalation Procedures

### **Level 1: Self-Service**
- Check this runbook
- Review recent logs
- Run diagnostic scripts
- Attempt standard solutions

### **Level 2: System Administrator**
- Database corruption issues
- System resource problems
- Network connectivity issues
- Service configuration problems

### **Level 3: Developer Support**
- Code-related errors
- API integration issues
- Complex configuration problems
- Feature requests or bugs

## 📋 Maintenance Checklist

### **Daily Checks**
- [ ] System status: `./canary status`
- [ ] Recent errors: `grep -i error logs/*.log | tail -5`
- [ ] Disk space: `df -h`
- [ ] Process status: `ps aux | grep canary`

### **Weekly Checks**
- [ ] Backup verification: `python3 core/backup_verification.py --verify`
- [ ] Log rotation: Check log sizes
- [ ] Performance review: Run performance monitor
- [ ] Configuration validation: Test configuration loading

### **Monthly Checks**
- [ ] Database optimization: `sqlite3 data/canary_protocol.db "VACUUM; ANALYZE;"`
- [ ] Archive old data: `python3 core/data_archival.py --run`
- [ ] Security updates: Update system packages
- [ ] Full diagnostic: Run complete system check

---

**📝 Note**: Keep this runbook updated as new issues are discovered and resolved. Document any custom solutions specific to your environment.

**🔒 Security**: Ensure diagnostic outputs don't expose sensitive information like API keys or personal data when sharing logs for support.
