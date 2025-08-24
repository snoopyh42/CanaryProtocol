# Smart Canary Protocol - Configuration Guide

## 📋 Configuration Overview

The Smart Canary Protocol uses a layered configuration system with YAML files, environment variables, and runtime settings to provide flexible and secure system management.

## 🔧 Configuration Files

### **Primary Configuration Files**

#### `config/config.yaml`
Main system configuration file containing all operational settings.

```yaml
# Core System Settings
system:
  debug_mode: false
  log_level: "INFO"
  max_retries: 3
  timeout_seconds: 30

# AI Analysis Configuration
ai:
  model: "gpt-4o"
  max_tokens: 2000
  temperature: 0.3
  analysis_prompt_template: "default"

# Monitoring Sources
monitoring:
  news_sources:
    - name: "NPR"
      url: "https://feeds.npr.org/1001/rss.xml"
      weight: 1.0
    - name: "Reuters"
      url: "https://feeds.reuters.com/reuters/topNews"
      weight: 1.2
  
  economic_indicators:
    - "VIX"
    - "Gold"
    - "USD_Index"
  
  request_timeout: 30
  max_articles_per_source: 50

# Learning System
learning:
  enable_adaptive_intelligence: true
  feedback_weight_multiplier: 2.0
  pattern_confidence_threshold: 0.7
  keyword_learning_rate: 0.1
  source_reliability_decay: 0.95

# Backup System
backup:
  auto_backup_enabled: true
  backup_retention_days: 90
  verify_backups: true
  compression_level: 6

# Notification Settings
notifications:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    use_tls: true
  
  slack:
    enabled: false
    channel: "#alerts"
  
  urgency_thresholds:
    low: 3
    medium: 6
    high: 8
    critical: 9

# Data Collection
collection:
  daily_collection_time: "08:00"
  weekly_analysis_day: "sunday"
  emergency_check_interval: 4
  data_retention_days: 365
```

#### `config/config_defaults.yaml`
System defaults and fallback values (read-only).

```yaml
# Default System Configuration
# DO NOT MODIFY - Copy settings to config.yaml to override

system:
  debug_mode: false
  log_level: "INFO"
  max_retries: 3
  timeout_seconds: 30
  environment: "production"

ai:
  model: "gpt-4o"
  max_tokens: 2000
  temperature: 0.3
  fallback_model: "gpt-4"

monitoring:
  request_timeout: 30
  max_articles_per_source: 50
  retry_attempts: 3

learning:
  enable_adaptive_intelligence: true
  feedback_weight_multiplier: 2.0
  pattern_confidence_threshold: 0.7

backup:
  auto_backup_enabled: true
  backup_retention_days: 90
  verify_backups: true

notifications:
  urgency_thresholds:
    low: 3
    medium: 6
    high: 8
    critical: 9
```

### **Environment Configuration**

#### `config/.env`
Sensitive credentials and API keys (never commit to version control).

```bash
# Required API Keys
OPENAI_API_KEY=sk-your-openai-api-key-here
GMAIL_USER=your-email@domain.com
GMAIL_APP_PASSWORD=your-gmail-app-password

# Optional Integrations
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
X_BEARER_TOKEN=your-x-bearer-token
REDDIT_CLIENT_ID=your-reddit-client-id
REDDIT_CLIENT_SECRET=your-reddit-client-secret

# System Environment
LOG_LEVEL=INFO
DEBUG_MODE=false
ENVIRONMENT=production
```

#### `config/env_example.txt`
Template for environment variables (safe to commit).

```bash
# Copy this file to config/.env and fill in your actual values

# Required Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
GMAIL_USER=your-email@domain.com
GMAIL_APP_PASSWORD=your-gmail-app-password

# Optional Integrations (leave blank if not using)
SLACK_WEBHOOK_URL=
X_BEARER_TOKEN=
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=

# System Settings (optional overrides)
LOG_LEVEL=INFO
DEBUG_MODE=false
ENVIRONMENT=production
```

### **Subscriber Configuration**

#### `config/subscribers.txt`
Email addresses for digest delivery (one per line).

```
admin@yourdomain.com
alerts@company.com
team-lead@organization.org
```

## 🔐 Security Configuration

### **API Key Management**

**OpenAI API Key:**
1. Create account at https://platform.openai.com/
2. Generate API key with GPT-4 access
3. Add to `config/.env`: `OPENAI_API_KEY=sk-...`

**Gmail App Password:**
1. Enable 2-Factor Authentication on Gmail account
2. Generate App Password: Google Account → Security → App passwords
3. Add to `config/.env`: `GMAIL_APP_PASSWORD=your-app-password`

**Slack Integration (Optional):**
1. Create Slack webhook in your workspace
2. Add to `config/.env`: `SLACK_WEBHOOK_URL=https://hooks.slack.com/...`

### **File Permissions**
```bash
# Secure configuration files
chmod 600 config/.env              # Environment variables
chmod 644 config/config.yaml       # Main configuration
chmod 644 config/subscribers.txt   # Email list
chmod 755 config/                  # Directory access
```

## ⚙️ Configuration Management

### **Loading Configuration**

The system uses a hierarchical configuration loading system:

1. **Defaults**: Load `config/config_defaults.yaml`
2. **User Settings**: Override with `config/config.yaml`
3. **Environment**: Apply environment variable overrides
4. **Runtime**: Apply command-line arguments

```python
# Example configuration access
from core.functions.utils import load_config

config = load_config()
model = config.get('ai', {}).get('model', 'gpt-4')
timeout = config.get('monitoring', {}).get('request_timeout', 30)
```

### **Configuration Validation**

```bash
# Validate configuration syntax
python3 -c "
from core.functions.utils import load_config
try:
    config = load_config()
    print('✓ Configuration loaded successfully')
    print(f'AI Model: {config.get(\"ai\", {}).get(\"model\", \"not set\")}')
    print(f'Debug Mode: {config.get(\"system\", {}).get(\"debug_mode\", False)}')
except Exception as e:
    print(f'✗ Configuration error: {e}')
"

# Test environment variables
./canary status
```

### **Configuration Updates**

**Safe Configuration Changes:**
```bash
# 1. Backup current configuration
cp config/config.yaml config/config.yaml.backup

# 2. Edit configuration
nano config/config.yaml

# 3. Validate changes
python3 -c "from core.functions.utils import load_config; load_config()"

# 4. Test system
./canary test --no-openai

# 5. If issues, restore backup
# cp config/config.yaml.backup config/config.yaml
```

## 📊 Configuration Sections

### **AI Analysis Settings**

```yaml
ai:
  model: "gpt-4o"                    # OpenAI model to use
  max_tokens: 2000                   # Maximum response tokens
  temperature: 0.3                   # Creativity (0.0-1.0)
  analysis_prompt_template: "default" # Prompt template name
  fallback_model: "gpt-4"           # Backup model if primary fails
  rate_limit_delay: 1                # Seconds between API calls
```

### **Monitoring Configuration**

```yaml
monitoring:
  news_sources:
    - name: "Source Name"
      url: "https://example.com/rss.xml"
      weight: 1.0                    # Importance multiplier
      enabled: true                  # Enable/disable source
  
  economic_indicators:
    - "VIX"                         # Volatility Index
    - "Gold"                        # Gold prices
    - "USD_Index"                   # Dollar strength
  
  request_timeout: 30               # HTTP timeout seconds
  max_articles_per_source: 50       # Limit per RSS feed
  retry_attempts: 3                 # Failed request retries
  user_agent: "CanaryProtocol/1.0"  # HTTP user agent
```

### **Learning System Settings**

```yaml
learning:
  enable_adaptive_intelligence: true     # Enable AI learning
  feedback_weight_multiplier: 2.0       # Article feedback weight
  pattern_confidence_threshold: 0.7     # Pattern acceptance threshold
  keyword_learning_rate: 0.1            # Learning speed
  source_reliability_decay: 0.95        # Reliability decay rate
  max_patterns_stored: 1000             # Pattern storage limit
  learning_history_days: 180            # Learning data retention
```

### **Backup System Configuration**

```yaml
backup:
  auto_backup_enabled: true             # Enable automatic backups
  backup_retention_days: 90             # Keep backups for N days
  verify_backups: true                  # SHA256 verification
  compression_level: 6                  # Gzip compression (1-9)
  backup_location: "data/backups/"      # Backup directory
  include_logs: true                    # Include logs in backup
  max_backup_size_mb: 500              # Maximum backup size
```

### **Notification Settings**

```yaml
notifications:
  email:
    enabled: true                       # Enable email notifications
    smtp_server: "smtp.gmail.com"       # SMTP server
    smtp_port: 587                      # SMTP port
    use_tls: true                       # Use TLS encryption
    from_name: "Smart Canary Protocol"  # Sender name
    subject_prefix: "[CANARY]"          # Email subject prefix
  
  slack:
    enabled: false                      # Enable Slack notifications
    channel: "#alerts"                  # Slack channel
    username: "CanaryBot"               # Bot username
    icon_emoji: ":warning:"             # Bot icon
  
  urgency_thresholds:
    low: 3                             # Low urgency threshold
    medium: 6                          # Medium urgency threshold
    high: 8                            # High urgency threshold
    critical: 9                        # Critical urgency threshold
```

## 🔄 Environment-Specific Configuration

### **Development Environment**

```yaml
# config/config.yaml for development
system:
  debug_mode: true
  log_level: "DEBUG"
  environment: "development"

ai:
  model: "gpt-4"                       # Use cheaper model for dev
  max_tokens: 1000

monitoring:
  max_articles_per_source: 10          # Reduce for faster testing

backup:
  auto_backup_enabled: false           # Disable auto-backup in dev

notifications:
  email:
    enabled: false                     # Disable emails in dev
```

### **Production Environment**

```yaml
# config/config.yaml for production
system:
  debug_mode: false
  log_level: "INFO"
  environment: "production"

ai:
  model: "gpt-4o"                      # Use best model for production
  max_tokens: 2000

monitoring:
  max_articles_per_source: 50          # Full article collection

backup:
  auto_backup_enabled: true            # Enable automatic backups
  verify_backups: true                 # Verify backup integrity

notifications:
  email:
    enabled: true                      # Enable email notifications
```

## 🧪 Testing Configuration

### **Test Environment Setup**

```bash
# Create test configuration
cp config/config.yaml config/config_test.yaml

# Modify for testing
cat >> config/config_test.yaml << EOF
system:
  debug_mode: true
  log_level: "DEBUG"

monitoring:
  max_articles_per_source: 5

backup:
  auto_backup_enabled: false

notifications:
  email:
    enabled: false
EOF

# Run tests with test config
CONFIG_FILE=config/config_test.yaml python3 tests/test_comprehensive.py
```

### **Configuration Testing**

```bash
# Test configuration loading
python3 -c "
from core.functions.utils import load_config
config = load_config()
print('Configuration sections:')
for section in config.keys():
    print(f'  - {section}')
"

# Test environment variables
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv('config/.env')
required_vars = ['OPENAI_API_KEY', 'GMAIL_USER', 'GMAIL_APP_PASSWORD']
for var in required_vars:
    status = '✓' if os.getenv(var) else '✗'
    print(f'{status} {var}')
"

# Validate YAML syntax
python3 -c "
import yaml
try:
    with open('config/config.yaml', 'r') as f:
        yaml.safe_load(f)
    print('✓ YAML syntax valid')
except yaml.YAMLError as e:
    print(f'✗ YAML syntax error: {e}')
"
```

## 🔧 Troubleshooting Configuration

### **Common Configuration Issues**

**Invalid YAML Syntax:**
```bash
# Check YAML syntax
python3 -c "import yaml; yaml.safe_load(open('config/config.yaml'))"

# Fix common issues:
# - Check indentation (use spaces, not tabs)
# - Ensure proper quoting of strings with special characters
# - Validate nested structure
```

**Missing Environment Variables:**
```bash
# Check required variables
grep -E "^[A-Z_]+=" config/.env

# Test variable loading
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv('config/.env')
print('OPENAI_API_KEY:', 'SET' if os.getenv('OPENAI_API_KEY') else 'MISSING')
"
```

**Configuration Override Issues:**
```bash
# Check configuration hierarchy
python3 -c "
from core.functions.utils import load_config
config = load_config()
print('Final configuration:')
import json
print(json.dumps(config, indent=2, default=str))
"
```

## 📋 Configuration Checklist

### **Initial Setup**
- [ ] Copy `config/env_example.txt` to `config/.env`
- [ ] Set required API keys in `.env` file
- [ ] Copy `config/config_example.yaml` to `config/config.yaml`
- [ ] Configure email subscribers in `config/subscribers.txt`
- [ ] Set secure file permissions (`chmod 600 config/.env`)
- [ ] Validate configuration with `./canary status`

### **Production Deployment**
- [ ] Use production-grade API keys
- [ ] Enable automatic backups
- [ ] Configure proper logging levels
- [ ] Set up email notifications
- [ ] Configure monitoring sources
- [ ] Test configuration with `./canary test`

### **Security Review**
- [ ] Verify `.env` file is not in version control
- [ ] Check file permissions on sensitive files
- [ ] Validate API key access levels
- [ ] Review notification settings
- [ ] Test backup and restore procedures

---

**📝 Note**: Always backup configuration files before making changes. Use the test suite to validate configuration changes before deploying to production.

**🔒 Security**: Never commit `.env` files or API keys to version control. Use environment-specific configuration files for different deployment environments.
