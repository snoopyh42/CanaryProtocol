# Smart Canary Protocol - Production Deployment Guide

## 🚀 Production Deployment Overview

This guide covers deploying the Smart Canary Protocol in production environments with proper security, monitoring, and reliability practices.

## 📋 Pre-Deployment Checklist

### **System Requirements**
- [ ] **Operating System**: Ubuntu 20.04+ / CentOS 8+ / macOS 10.15+
- [ ] **Python**: 3.8 or higher with pip
- [ ] **Memory**: Minimum 2GB RAM (4GB+ recommended)
- [ ] **Storage**: 10GB+ available space for data and logs
- [ ] **Network**: Outbound HTTPS access for API calls and news feeds

### **Required Credentials**
- [ ] **OpenAI API Key** (GPT-4o access required)
- [ ] **Gmail Account** with App Password enabled
- [ ] **Slack Webhook URL** (optional but recommended)
- [ ] **X/Twitter Bearer Token** (optional for social media monitoring)

### **Security Prerequisites**
- [ ] Firewall configured (only necessary outbound ports)
- [ ] SSL/TLS certificates for any web interfaces
- [ ] Secure storage for environment variables
- [ ] Regular security updates enabled

## 🔧 Production Installation

### **1. System Setup**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian
# OR
sudo yum update -y                      # CentOS/RHEL

# Install required system packages
sudo apt install -y python3 python3-pip python3-venv git cron
```

### **2. Application Deployment**
```bash
# Create application user (recommended)
sudo useradd -m -s /bin/bash canary
sudo su - canary

# Clone repository
git clone https://github.com/snoopyh42/CanaryProtocol.git
cd CanaryProtocol

# Set proper permissions
chmod +x canary
chmod +x scripts/*.sh
```

### **3. Environment Configuration**
```bash
# Copy and configure environment variables
cp config/env_example.txt config/.env
chmod 600 config/.env  # Secure permissions

# Edit configuration (use secure editor)
nano config/.env
```

**Required Environment Variables:**
```bash
# Core Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
GMAIL_USER=your-production-email@domain.com
GMAIL_APP_PASSWORD=your-gmail-app-password

# Optional but Recommended
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
X_BEARER_TOKEN=your-x-bearer-token

# Production Settings
LOG_LEVEL=INFO
DEBUG_MODE=false
ENVIRONMENT=production
```

### **4. Application Configuration**
```bash
# Copy and customize main configuration
cp config/config_example.yaml config/config.yaml

# Configure email subscribers
cp config/subscribers.txt.example config/subscribers.txt
# Add production email addresses (one per line)
```

### **5. Database and Dependencies Setup**
```bash
# Run complete setup
./canary setup

# Verify installation
./canary status
./canary test --no-openai  # Test without API calls

# Run comprehensive test suite
python3 tests/test_comprehensive.py
```

## 🔒 Security Hardening

### **File Permissions**
```bash
# Set secure permissions
chmod 700 data/                    # Database directory
chmod 600 config/.env             # Environment variables
chmod 644 config/*.yaml           # Configuration files
chmod 755 scripts/*.sh            # Shell scripts
chmod 644 logs/                   # Log directory
```

### **Environment Variable Security**
```bash
# Use systemd environment files (recommended)
sudo mkdir -p /etc/systemd/system/canary.service.d/
sudo tee /etc/systemd/system/canary.service.d/environment.conf << EOF
[Service]
EnvironmentFile=/home/canary/CanaryProtocol/config/.env
EOF
```

### **Network Security**
```bash
# Configure firewall (example for UFW)
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
# Only allow necessary inbound connections
```

### **Log Security**
```bash
# Set up log rotation
sudo tee /etc/logrotate.d/canary << EOF
/home/canary/CanaryProtocol/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 canary canary
}
EOF
```

## ⚙️ Production Services Setup

### **Systemd Service Configuration**
```bash
# Create systemd service file
sudo tee /etc/systemd/system/canary.service << EOF
[Unit]
Description=Smart Canary Protocol
After=network.target

[Service]
Type=oneshot
User=canary
Group=canary
WorkingDirectory=/home/canary/CanaryProtocol
ExecStart=/home/canary/CanaryProtocol/canary emergency
EnvironmentFile=/home/canary/CanaryProtocol/config/.env
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create timer for regular execution
sudo tee /etc/systemd/system/canary.timer << EOF
[Unit]
Description=Run Smart Canary Protocol Analysis
Requires=canary.service

[Timer]
OnCalendar=Sun 09:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable canary.timer
sudo systemctl start canary.timer
```

### **Cron Jobs (Alternative to Systemd)**
```bash
# Edit crontab as canary user
crontab -e

# Add production cron jobs
# Daily collection at 8 AM
0 8 * * * /home/canary/CanaryProtocol/scripts/run_daily_collection.sh

# Weekly analysis on Sunday at 9 AM
0 9 * * 0 /home/canary/CanaryProtocol/canary emergency

# Daily backup at 2 AM (automatic via daily collector)
0 2 * * * /home/canary/CanaryProtocol/scripts/run_daily_collection.sh

# Weekly archival on Saturday at 3 AM
0 3 * * 6 /usr/bin/python3 /home/canary/CanaryProtocol/core/data_archival.py --run

# Monthly backup verification on 1st at 4 AM
0 4 1 * * cd /home/canary/CanaryProtocol && ./canary verify
```

## 🧪 Testing and Validation

### **Comprehensive Test Suite**
The Smart Canary Protocol includes a robust test suite with 100% coverage:

```bash
# Run full comprehensive test suite
python3 tests/test_comprehensive.py

# Run basic functionality tests
python3 tests/test_all_functionality.py

# Test specific components
python3 -m pytest tests/ -v
```

**Test Coverage Includes:**
- Core system imports and database operations
- Backup and restore system with SHA256 verification
- Learning systems (adaptive intelligence, feedback)
- Data collection with mocked external APIs
- Shell script syntax validation
- Integration workflow testing
- Isolated test environments with automatic cleanup

### **Pre-Production Testing**
```bash
# Test backup system
./canary backup
./canary verify

# Test restore system (dry run)
./canary restore list

# Test learning systems
./canary test

# Validate configuration
./canary status
```

### **Continuous Integration**
```bash
# Add to CI/CD pipeline
#!/bin/bash
set -e

# Setup test environment
python3 -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt

# Run comprehensive tests
python3 tests/test_comprehensive.py

# Validate shell scripts
for script in scripts/*.sh; do
    bash -n "$script"
done

# Check code quality
flake8 core/ tests/ --max-line-length=100

echo "All tests passed!"
```

## 📊 Monitoring and Alerting

### **Health Check Script**
```bash
# Create health check script
tee scripts/health_check.sh << 'EOF'
#!/bin/bash
source scripts/common.sh

# Check database
if ! sqlite3 data/canary_protocol.db "SELECT 1;" >/dev/null 2>&1; then
    log_error "Database health check failed"
    exit 1
fi

# Check disk space
DISK_USAGE=$(df /home/canary/CanaryProtocol | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    log_warning "Disk usage high: ${DISK_USAGE}%"
fi

# Check log file size
LOG_SIZE=$(du -sm logs/ | cut -f1)
if [ "$LOG_SIZE" -gt 1000 ]; then
    log_warning "Log directory size: ${LOG_SIZE}MB"
fi

log_info "Health check completed successfully"
EOF

chmod +x scripts/health_check.sh
```

### **Monitoring Cron Job**
```bash
# Add to crontab - check every 15 minutes
*/15 * * * * /home/canary/CanaryProtocol/scripts/health_check.sh
```

### **Log Monitoring**
```bash
# Set up log monitoring with logwatch (optional)
sudo apt install logwatch

# Configure custom logwatch for canary logs
sudo mkdir -p /etc/logwatch/conf/logfiles
sudo tee /etc/logwatch/conf/logfiles/canary.conf << EOF
LogFile = /home/canary/CanaryProtocol/logs/*.log
Archive = /home/canary/CanaryProtocol/logs/*.log.*
EOF
```

## 🔄 Database Management

### **Database Migrations**
```bash
# Check migration status
./canary migrate --status

# Apply pending migrations
./canary migrate

# Create initial migrations (first deployment)
./canary migrate --create-initial
```

### **Backup Strategy**
```bash
# Manual backup (creates SHA256-verified tar.gz bundle)
./canary backup

# Verify backup integrity
./canary verify

# List available backups with metadata
./canary restore list

# Test backup restoration (interactive)
./canary restore
```

### **Data Archival**
```bash
# Run data archival
./canary archive --run

# Check archive summary
./canary archive --summary

# Archive specific table
./canary archive --table daily_headlines
```

## 🚨 Disaster Recovery

### **Backup Locations**
- **Primary**: Local `data/backups/` directory
- **Secondary**: External storage (configure rsync/cloud sync)
- **Offsite**: Cloud storage (AWS S3, Google Cloud, etc.)

### **Recovery Procedures**

**1. Database Corruption Recovery:**
```bash
# Stop all services
sudo systemctl stop canary.timer

# Use interactive restore system
./canary restore
# Select latest verified backup from list

# Verify restoration
./canary status
python3 tests/test_comprehensive.py

# Restart services
sudo systemctl start canary.timer
```

**2. Complete System Recovery:**
```bash
# Reinstall application
git clone https://github.com/snoopyh42/CanaryProtocol.git
cd CanaryProtocol

# Restore configuration
cp /backup/location/config/.env config/.env
cp /backup/location/config/config.yaml config/config.yaml

# Use restore system for data recovery
./canary restore
# Select appropriate backup bundle

# Run setup and comprehensive verification
./canary setup
./canary status
python3 tests/test_comprehensive.py
```

## 📈 Performance Optimization

### **Database Optimization**
```bash
# Regular database maintenance
sqlite3 data/canary_protocol.db "VACUUM;"
sqlite3 data/canary_protocol.db "ANALYZE;"

# Add to monthly cron
0 3 1 * * sqlite3 /home/canary/CanaryProtocol/data/canary_protocol.db "VACUUM; ANALYZE;"
```

### **Log Management**
```bash
# Compress old logs
find logs/ -name "*.log" -mtime +7 -exec gzip {} \;

# Clean very old logs
find logs/ -name "*.gz" -mtime +90 -delete
```

### **Memory Management**
```bash
# Monitor memory usage
ps aux | grep python3 | grep canary

# Set memory limits in systemd service
echo "MemoryMax=1G" | sudo tee -a /etc/systemd/system/canary.service
sudo systemctl daemon-reload
```

## 🔍 Troubleshooting Production Issues

### **Common Issues and Solutions**

**API Rate Limits:**
```bash
# Check API usage in logs
grep -i "rate limit" logs/*.log

# Implement exponential backoff (already included in code)
# Monitor API usage dashboard
```

**Database Lock Issues:**
```bash
# Check for long-running processes
sqlite3 data/canary_protocol.db ".timeout 30000"

# Kill stuck processes if necessary
pkill -f "python3.*canary"
```

**Disk Space Issues:**
```bash
# Clean old archives
find data/archives/ -name "*.gz" -mtime +365 -delete

# Run data archival
./canary archive --run
```

**Email Delivery Issues:
```bash
# Test email configuration
./canary test --verbose

# Check Gmail app password
# Verify SMTP settings in logs
```

## 📋 Maintenance Schedule

### **Daily**
- [ ] Health check monitoring
- [ ] Log review for errors
- [ ] Disk space monitoring

### **Weekly**
- [ ] Backup verification (`./canary verify`)
- [ ] Run comprehensive test suite (`python3 tests/test_comprehensive.py`)
- [ ] Performance review
- [ ] Security log review

### **Monthly**
- [ ] Database optimization
- [ ] Archive old data
- [ ] Security updates
- [ ] Configuration review

### **Quarterly**
- [ ] Full disaster recovery test with restore validation
- [ ] Complete test suite validation in production environment
- [ ] Security audit
- [ ] Performance optimization
- [ ] Documentation updates

## 🔐 Security Best Practices

1. **Regular Updates**: Keep system and dependencies updated
2. **Access Control**: Use dedicated service account with minimal privileges
3. **Encryption**: Encrypt sensitive data at rest and in transit
4. **Monitoring**: Implement comprehensive logging and alerting
5. **Backups**: Regular, tested backups with offsite storage
6. **Network Security**: Firewall rules and network segmentation
7. **Secrets Management**: Secure storage of API keys and credentials

## 📞 Support and Maintenance

### **Log Locations**
- Application logs: `logs/canary_*.log`
- System logs: `/var/log/syslog` or `journalctl -u canary`
- Cron logs: `/var/log/cron` or `journalctl -u cron`

### **Key Commands**
```bash
# System status
./canary status

# View recent logs
./canary logs

# Test configuration
./canary test --no-openai

# Emergency analysis
./canary emergency

# Database status
python3 core/database_migrations.py --status

# Backup verification
./canary verify

# Run comprehensive tests
python3 tests/test_comprehensive.py
```

### **Performance Monitoring**
```bash
# Check system resources
htop
df -h
free -h

# Monitor database size
du -sh data/

# Check log sizes
du -sh logs/
```

---

**📝 Note**: This deployment guide assumes a Linux production environment. Adapt commands and paths as necessary for your specific operating system and infrastructure setup.

**🔒 Security Warning**: Always review and customize security settings for your specific environment. This guide provides baseline security practices but may need additional hardening based on your security requirements.
