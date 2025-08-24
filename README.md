# 🧠 Smart Canary Protocol

**An Adaptive Political & Economic Monitoring System with Interactive TUI**

A sophisticated early warning system that uses artificial intelligence and machine learning to monitor political and economic conditions, helping assess stability and potential risks. The system **learns and improves over time** through user feedback and pattern recognition.

### ✨ **Latest Features**
- **🖥️ Interactive Terminal UI**: Navigate all functions through an intuitive menu system
- **💾 Advanced Backup System**: SHA256-verified tar.gz archives with automatic daily backups
- **🔧 Database Migrations**: Version-controlled schema management
- **📦 Data Archival**: Automated cleanup and archival of historical data
- **🧪 Comprehensive Test Suite**: 100% test coverage with isolated environments
- **📚 Production Documentation**: Complete deployment and troubleshooting guides

## 🎯 Purpose

This system is designed to provide intelligent analysis of:
- **Political stability indicators** across multiple news sources
- **Economic warning signs** from market data and indicators  
- **Historical pattern recognition** to identify concerning trends
- **Adaptive learning** that improves accuracy through user feedback

The goal is to provide calm, rational analysis rather than panic - helping users make informed decisions based on data rather than emotion.

## 🚀 Quick Start

### **1. Initial Setup**
```bash
# Clone or download this repository
cd CanaryProtocol

# Complete system setup (one command)
./canary setup
```

### **2. Interactive Interface**
```bash
# Launch interactive TUI menu (default)
./canary

# Or explicitly launch TUI
./canary tui
./canary menu
./canary interactive
```

### **3. Command Line Usage**
```bash
# Check learning progress and recent activity
./canary dashboard

# View recent log activity
./canary logs

# Get system status overview
./canary status

# Test system functionality
./canary test

# Run comprehensive test suite
python3 tests/test_comprehensive.py

# Create system backup
./canary backup

# Emergency analysis
./canary emergency
```

### **4. Improve the System**
```bash
# Provide feedback to train the AI (choose your preferred method)
./canary feedback            # Rate entire digest summary (quick)
./canary articles            # Rate individual articles (detailed training)

# View feedback summaries and learning progress
./canary feedback-summary

# Clear feedback data to start fresh
./canary feedback-clear

# Run emergency analysis if needed
./canary emergency
```

## 🔧 Command Interface

All system functionality is available through the `./canary` command:

### **🚀 Setup & Management**
```bash
./canary setup      # Complete system setup
./canary dashboard  # View learning progress
./canary status     # System status overview
./canary config     # Configuration management  
./canary backup     # Backup all data
./canary logs       # View recent system logs
./canary cron-reset # Reset cron jobs (fix duplicates)
```

### **🧪 Analysis & Testing**
```bash
./canary test       # Run in test mode
./canary emergency  # Emergency analysis

# Comprehensive testing
python3 tests/test_comprehensive.py  # Full system test suite
python3 tests/test_all_functionality.py  # Basic functionality tests
```

### **📝 User Feedback & Learning**
```bash
./canary feedback            # Rate digest summaries (quick)
./canary articles            # Rate individual articles (detailed)
./canary feedback-individual # Rate individual articles (full name)
./canary feedback-summary   # View all feedback summaries
./canary feedback-clear     # Clear feedback data
```

### **⚙️ Configuration**
```bash
./canary config show      # View current settings
./canary config create    # Create example config file  
./canary config validate  # Test configuration loading
```

The `./canary` script provides easy access to all system functions:

### **📋 Setup & Management**
```bash
./canary setup      # Complete system setup and configuration
./canary status     # System overview and health check
./canary backup     # Create SHA256-verified backup archive
./canary restore    # Interactive backup restoration
./canary config     # Configuration management (show/create/validate)
./canary cron-reset # Reset cron jobs (fix duplicates)
./canary uninstall  # Complete system removal
```

### **📊 Monitoring & Analysis**
```bash
./canary dashboard  # View learning progress and intelligence reports
./canary test       # Run system in test mode (no emails sent)
./canary emergency  # Run immediate emergency analysis
```

### **📝 User Interaction & Configuration**
```bash
./canary feedback   # Provide feedback to improve system accuracy
./canary config show     # View current configuration settings
./canary config create   # Create example configuration file
./canary config validate # Test configuration loading
```

### **ℹ️ Help & Information**
```bash
./canary help       # Show all available commands
./canary --help     # Same as above
./canary           # Shows help if no command specified
```

## 🧠 Smart Learning Features

### **Adaptive Intelligence**
- **Pattern Recognition**: Learns from historical events and outcomes
- **Keyword Intelligence**: Tracks which terms correlate with actual urgency
- **Source Reliability**: Monitors accuracy of different news sources
- **False Positive Reduction**: Reduces noise and improves signal quality

### **Hybrid Learning System**
- **Daily Silent Collection** (8 AM): Gathers data without sending notifications + **automatic backup creation**
- **Weekly Intelligent Analysis** (Sunday 9 AM): Full AI analysis with email digest
- **Emergency Detection**: Automatic triggers for urgent situations requiring immediate analysis
- **Backup Verification**: SHA256 checksum validation ensures data integrity

### **User Feedback Integration**
- **Individual Article Rating** ⭐ **HIGH PRIORITY AI TRAINING**: Detailed feedback on specific headlines and sources with 2x learning weight
- **Digest-Level Rating**: Quick overall assessment of daily digest accuracy
- **Irrelevant Article Tracking**: AI learns noise patterns from articles you skip/mark irrelevant
- **False Positive Reporting**: Help system learn what to ignore
- **Missed Signal Reporting**: Improve detection of important events
- **Source Reliability Learning**: AI learns which news sources are most/least reliable by content type

### **🚀 Enhanced AI Learning (NEW!)**
- **Headline Pattern Recognition**: AI learns which headline structures correlate with actual urgency
- **Keyword Effectiveness**: Tracks which words in headlines indicate real vs false urgency  
- **Source-Content Correlation**: Learns reliability patterns specific to content types and topics
- **False Positive Reduction**: Uses irrelevant markings to filter noise and improve signal quality
- **Higher Weight Individual Training**: Article-level feedback gets 2x priority vs digest feedback

## 🎯 Understanding Urgency Ratings

The system uses a **0-10 urgency scale** for rating political and economic developments:

### **📊 Urgency Scale Guide**
- **0-1**: Minimal urgency (routine political noise)
- **2-3**: Low urgency (noteworthy but not concerning)  
- **4-5**: Moderate urgency (significant developments requiring attention)
- **6-7**: High urgency (serious developments affecting preparation timeline)
- **8-9**: Critical urgency (immediate threats requiring action acceleration)
- **10**: Maximum urgency (existential threats requiring emergency action)

### **🧠 Training Methods**
- **Targeted Article Training** ⭐ **RECOMMENDED**: Rate individual articles to train AI on specific patterns, sources, and headline structures (2x learning weight)
- **Quick Digest Training**: Rate entire digest summaries for overall accuracy assessment
- **Irrelevant Pattern Learning**: Mark irrelevant articles to help AI filter noise and reduce false positives
- **Best Results**: Use individual article rating for 2-3 weeks, then switch to quick digest rating

*See [`docs/SMART_CANARY_GUIDE.md`](docs/SMART_CANARY_GUIDE.md) for detailed urgency rating examples and best practices.*

## ⚙️ Configuration System

The Smart Canary Protocol uses a comprehensive YAML-based configuration system that allows you to customize all monitoring parameters without modifying code.

### **Configuration Management**
```bash
./canary config show      # View current configuration
./canary config create    # Create example config file
./canary config validate  # Test configuration loading
```

### **Key Configuration Areas**
- **📰 News Sources** (18 default): Political, economic, and social media feeds
- **🔍 Keywords** (52 default): Monitoring terms for different urgency levels
- **💰 Economic APIs** (4 sources): Federal Reserve and market indicators
- **🤖 AI Settings**: Model selection, temperature, token limits
- **⚡ Urgency Thresholds**: Customizable scoring and alert levels

### **Configuration Files**
```
config/
├── config.yaml              # Your custom settings
├── config_defaults.yaml     # System defaults (fallback)
├── config_example.yaml      # Example configuration
├── .env                     # API keys and secrets
├── env_example.txt          # Environment variables template
└── subscribers.txt.example  # Email subscriber list template
```

**Pro Tip:** Copy `config_example.yaml` to `config.yaml` and customize to your preferences!

## 📁 Repository Structure

```
CanaryProtocol/
├── 🔧 canary                    # Main command interface
├── 📁 core/                     # Python modules
│   ├── 📁 classes/              # Core system classes
│   │   ├── adaptive_intelligence.py # Machine learning and pattern recognition
│   │   ├── smart_feedback.py        # User feedback system
│   │   ├── daily_silent_collector.py# Daily data collection with auto-backup
│   │   ├── backup_verification.py   # SHA256 backup verification
│   │   ├── data_restore.py          # Backup restoration system
│   │   ├── data_archival.py         # Data cleanup and archival
│   │   ├── database_migrations.py   # Schema version management
│   │   └── config_loader.py         # YAML configuration system
│   ├── 📁 functions/            # Utility functions
│   │   ├── analysis_engine.py       # AI analysis and urgency scoring
│   │   ├── database_utils.py        # Database operations
│   │   ├── email_utils.py           # Email formatting and sending
│   │   ├── slack_utils.py           # Slack integration
│   │   └── utils.py                 # Common utilities
│   ├── canary_protocol.py       # Main intelligent analysis system
│   ├── canary_tui.py           # Interactive terminal interface
│   └── ab_testing.py           # A/B testing framework
├── 📁 scripts/                  # Automation scripts
│   ├── setup_complete_smart_system.sh    # Main setup script
│   ├── backup_learning_data.sh           # SHA256-verified backup creation
│   ├── daily_learning_check.sh           # Learning progress monitor
│   ├── emergency_analysis.sh             # Emergency analysis mode
│   └── uninstall_canary_protocol.sh      # Complete system removal
├── 📁 tests/                    # Test suites
│   ├── test_comprehensive.py    # Full system test suite (100% coverage)
│   ├── test_all_functionality.py# Basic functionality tests
│   └── test_x_integration.py    # Social media integration tests
├── 📁 config/                   # Configuration files
│   ├── config.yaml             # User customizations (YAML)
│   ├── config_defaults.yaml    # System defaults (YAML)
│   ├── config_example.yaml     # Example configuration (YAML)
│   ├── .env                    # Environment variables & API keys
│   ├── .env.example            # Environment variables template
│   ├── requirements.txt        # Python dependencies
│   ├── subscribers.txt         # Email subscriber list
│   ├── subscribers.txt.example # Email subscriber list template
│   └── email_template.html     # Email formatting template
├── 📁 docs/                     # Documentation
│   ├── SMART_CANARY_GUIDE.md   # Detailed smart features guide
│   ├── API_REFERENCE.md        # Complete API documentation
│   ├── DEPLOYMENT_GUIDE.md     # Production deployment guide
│   └── TROUBLESHOOTING_RUNBOOK.md # Operational procedures
├── 📁 backups/                  # System backups (created during operation)
├── 📁 logs/                     # System logs (created during operation)
├── 📁 data/                     # Database files (created during operation)
└── 📁 venv/                     # Python virtual environment (created during setup)
```

## ⚙️ Configuration

### **Required Setup**
1. **Environment Variables**: Copy `config/env_example.txt` to `config/.env` and configure:
   - `OPENAI_API_KEY` - OpenAI API key for AI analysis (uses modern v1.0+ API)
   - `GMAIL_USER` - Gmail address for sending digests
   - `GMAIL_APP_PASSWORD` - Gmail app password

2. **Email Subscribers**: Copy `config/subscribers.txt.example` to `config/subscribers.txt` and add email addresses

3. **Run Setup**: Execute `./canary setup` to initialize databases and cron jobs

### **Optional Configuration**
- **Slack Integration**: Add `SLACK_WEBHOOK_URL` to `.env` for Slack notifications
- **Economic APIs**: Add API keys for enhanced economic data (system works without these)

## 📈 Learning & Improvement

### **Learning Timeline**
- **Week 1-2**: System establishes baseline patterns and learns your preferences
- **Week 3-4**: Pattern recognition becomes active, accuracy improves
- **Month 2+**: High accuracy predictions (80%+ with regular feedback)

### **How to Help It Learn**
1. **Choose Your Training Method**:
   - **Individual Article Rating** (`./canary articles`): Best for initial training - rate specific headlines and sources
   - **Digest Rating** (`./canary feedback`): Quick overall assessment once AI is trained
   
2. **Provide Regular Feedback**: Rate 5-10 articles per session or weekly digests consistently

3. **Be Accurate with Ratings**: Use the 0-10 urgency scale consistently (see urgency guide above)

4. **Report Issues**: Flag false positives and missed signals to improve accuracy

5. **Add Comments**: Specific feedback helps AI learn faster than ratings alone

### **Training Strategy**
- **Weeks 1-3**: Use `./canary articles` to train on individual headlines (best initial training)
- **Month 2+**: Switch to `./canary feedback` for quick digest ratings (maintenance mode)
- **Anytime**: Use `./canary feedback-clear` to reset and start fresh training

### **Monitoring Progress**
```bash
./canary dashboard        # View learning statistics and progress
./canary feedback-summary # Detailed feedback analysis by source
./canary status          # Quick system health check
./canary logs            # Recent activity and execution logs
```

### **Feedback Management**
```bash
./canary articles         # Rate individual articles (best training)
./canary feedback         # Rate digest summaries (quick assessment)  
./canary feedback-summary # View learning progress by news source
./canary feedback-clear   # Reset all feedback data to start fresh
```

## 🔒 Privacy & Security

- **Local Processing**: All learning data stays on your system
- **No External Training**: Your data is never sent to external AI training services
- **Encrypted Storage**: Sensitive configuration data should be properly secured
- **Anonymized Patterns**: Learning patterns are abstracted and anonymized

## 📊 Data Sources

### **News Sources**
- CNN, Fox News, NPR, Politico (political coverage)
- Bloomberg, MarketWatch, Financial Times (economic coverage)
- Reddit political communities (social sentiment)
- Official government sources (Federal Reserve, Treasury, etc.)

### **Economic Indicators**
- VIX Fear Index (market volatility)
- Gold price movements (safe haven demand)
- US Dollar Index (currency strength)
- Bitcoin trends (alternative asset sentiment)

## 🛠️ Technical Requirements

- **Python 3.8+** with pip
- **Internet connection** for data collection and AI analysis
- **Gmail account** with app password for email delivery
- **OpenAI API key** for intelligent analysis
- **Linux/macOS** (tested on Ubuntu/Debian)

## 🆘 Troubleshooting

### **Common Issues**
```bash
# Check system status
./canary status

# View recent errors
./canary logs

# Test system without sending emails
./canary test

# Launch interactive menu for guided operations
./canary

# Verify configuration
python3 core/canary_protocol.py --test --verbose
```

### **Getting Help**
- Check `docs/SMART_CANARY_GUIDE.md` for detailed feature documentation
- Review `docs/API_REFERENCE.md` for complete function reference
- Check `docs/DEPLOYMENT_GUIDE.md` for production setup
- Review `docs/TROUBLESHOOTING_RUNBOOK.md` for operational procedures
- Run `python3 tests/test_comprehensive.py` for system validation
- Review log files in `logs/` for specific error messages
- Ensure all configuration files are properly set up in `config/`

## 📝 License & Disclaimer

**License:** This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

**Disclaimer:** This system is for informational purposes only. Political and economic analysis should not be the sole basis for major life decisions. Always consult multiple sources and professional advisors for important decisions.

**Data Sources:** This system aggregates public news feeds and economic indicators. Users are responsible for ensuring compliance with terms of service of individual data sources.

---

**🧠 The system gets smarter with every digest and feedback session!**

For detailed information about smart features and learning capabilities, see [`docs/SMART_CANARY_GUIDE.md`](docs/SMART_CANARY_GUIDE.md).
