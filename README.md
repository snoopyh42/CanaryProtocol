# 🧠 Smart Canary Protocol

**An Adaptive Political & Economic Monitoring System**

A sophisticated early warning system that uses artificial intelligence and machine learning to monitor political and economic conditions, helping assess stability and potential risks. The system **learns and improves over time** through user feedback and pattern recognition.

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

### **2. Daily Usage**
```bash
# Check learning progress and recent activity
./canary dashboard

# View recent log activity
./canary logs

# Get system status overview
./canary status
```

### **3. Improve the System**
```bash
# Provide feedback on digest accuracy (after receiving weekly email)
./canary feedback

# Run emergency analysis if needed
./canary emergency
```

## 🔧 Command Interface

The `./canary` script provides easy access to all system functions:

### **📋 Setup & Management**
```bash
./canary setup      # Complete system setup and configuration
./canary status     # System overview and health check
./canary backup     # Backup all learning data and logs
```

### **📊 Monitoring & Analysis**
```bash
./canary dashboard  # View learning progress and intelligence reports
./canary logs       # View recent system activity from log files
./canary test       # Run system in test mode (no emails sent)
```

### **🚨 Emergency & Feedback**
```bash
./canary emergency  # Run immediate emergency analysis
./canary feedback   # Provide feedback to improve system accuracy
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
- **Daily Silent Collection** (8 AM): Gathers data without sending notifications
- **Weekly Intelligent Analysis** (Sunday 9 AM): Full AI analysis with email digest
- **Emergency Detection**: Automatic triggers for urgent situations requiring immediate analysis

### **User Feedback Integration**
- **Accuracy Rating**: Rate digest predictions to improve future analysis
- **False Positive Reporting**: Help system learn what to ignore
- **Missed Signal Reporting**: Improve detection of important events

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
└── .env                     # API keys and secrets
```

**Pro Tip:** Copy `config_example.yaml` to `config.yaml` and customize to your preferences!

## 📁 Repository Structure

```
CanaryProtocol/
├── 🔧 canary                    # Main command interface
├── 📁 core/                     # Python modules
│   ├── canary_protocol.py       # Main intelligent analysis system
│   ├── adaptive_intelligence.py # Machine learning and pattern recognition
│   ├── smart_feedback.py        # User feedback system
│   ├── daily_silent_collector.py# Daily data collection
│   ├── economic_monitor.py      # Economic indicator monitoring
│   ├── ab_testing.py           # A/B testing framework
│   └── analysis_examples.py    # Good/bad analysis examples
├── 📁 scripts/                  # Automation scripts
│   ├── setup_complete_smart_system.sh    # Main setup script
│   ├── learning_dashboard.sh             # Learning progress monitor
│   ├── emergency_analysis.sh             # Emergency analysis mode
│   └── backup_learning_data.sh           # Data backup utility
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
│   └── SMART_CANARY_GUIDE.md   # Detailed smart features guide
├── 📁 logs/                     # System logs (created during operation)
├── 📁 data/                     # Database files (created during operation)
└── 📁 venv/                     # Python virtual environment (created during setup)
```

## ⚙️ Configuration

### **Required Setup**
1. **Environment Variables**: Copy `config/.env.example` to `config/.env` and configure:
   - `OPENAI_API_KEY` - OpenAI API key for AI analysis
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
1. **Provide Regular Feedback**: Rate weekly digests for accuracy
2. **Report False Positives**: Help system learn what to ignore
3. **Flag Missed Signals**: Improve detection of important events
4. **Be Specific**: Detailed feedback comments improve learning quality

### **Monitoring Progress**
```bash
./canary dashboard  # View learning statistics and progress
./canary status     # Quick system health check
./canary logs       # Recent activity and execution logs
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

# Verify configuration
python3 core/canary_protocol.py --test --verbose
```

### **Getting Help**
- Check `docs/SMART_CANARY_GUIDE.md` for detailed feature documentation
- Review log files in `logs/` for specific error messages
- Ensure all configuration files are properly set up in `config/`

## 📝 License & Disclaimer

**License:** This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

**Disclaimer:** This system is for informational purposes only. Political and economic analysis should not be the sole basis for major life decisions. Always consult multiple sources and professional advisors for important decisions.

**Data Sources:** This system aggregates public news feeds and economic indicators. Users are responsible for ensuring compliance with terms of service of individual data sources.

---

**🧠 The system gets smarter with every digest and feedback session!**

For detailed information about smart features and learning capabilities, see [`docs/SMART_CANARY_GUIDE.md`](docs/SMART_CANARY_GUIDE.md).
