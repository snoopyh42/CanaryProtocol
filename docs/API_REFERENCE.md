# Smart Canary Protocol - API Documentation

## Core Modules

### CanaryProtocol (`core/canary_protocol.py`)
Main analysis engine with adaptive intelligence integration.

**Key Functions:**
- `analyze_current_situation()` - Performs comprehensive analysis
- `generate_digest()` - Creates intelligent summaries
- `emergency_assessment()` - Rapid threat evaluation

### AdaptiveIntelligence (`core/adaptive_intelligence.py`)
Machine learning and pattern recognition system.

**Key Functions:**
- `learn_from_analysis(analysis, feedback)` - Updates learning models
- `predict_urgency(content)` - AI-powered urgency prediction
- `get_source_reliability(source)` - Source credibility scoring

### SmartFeedback (`core/smart_feedback.py`)
User feedback integration and learning system.

**Key Functions:**
- `collect_feedback()` - Interactive feedback collection
- `report_false_positive(content)` - False alarm reporting
- `update_learning_models()` - Apply feedback to ML models

## Command Interface

### ./canary setup
Initializes the complete smart system:
- Creates Python virtual environment
- Installs all dependencies
- Sets up configuration files
- Configures automated scheduling

### ./canary dashboard
Opens the learning analytics dashboard:
- Pattern recognition accuracy
- Source reliability metrics
- User feedback integration status
- System performance indicators

### ./canary feedback
Interactive feedback collection:
- Rate recent analyses
- Report false positives
- Suggest improvements
- View feedback history

### ./canary emergency
Immediate threat assessment:
- Rapid current situation analysis
- Emergency-level urgency scoring
- Immediate action recommendations
- Real-time alert generation

### ./canary test
System validation and testing:
- Run sample analyses
- Verify AI integration
- Test email notifications
- Validate learning systems

### ./canary status
System health and status:
- Learning system status
- Database integrity
- Cron job status
- Configuration validation

### ./canary logs
Log file management:
- View recent activity
- Monitor error logs
- Check learning progress
- System diagnostics

## Configuration Files

### config/env_example.txt
Template for environment variables:
- OpenAI API key (required)
- Email credentials (required)
- Optional integrations (Slack, Reddit, Twitter)

### config/config_defaults.yaml
System configuration:
- Learning parameters
- Analysis thresholds
- Monitoring sources
- Notification settings

## Database Schema

### Intelligence Database (`data/intelligence.db`)
Learning and pattern storage:
- `patterns` - Recognized urgency patterns
- `keywords` - Tracked terms and weights
- `sources` - Source reliability scores
- `predictions` - Historical accuracy data

### Feedback Database (`data/feedback.db`)
User interaction tracking:
- `feedback` - User ratings and comments
- `false_positives` - Reported false alarms
- `improvements` - Suggested enhancements

## Learning System

### Pattern Recognition
- Analyzes headline structures
- Identifies urgency indicators
- Tracks prediction accuracy
- Adapts weights automatically

### Source Intelligence
- Monitors source reliability
- Tracks bias patterns
- Measures speed vs accuracy
- Updates credibility scores

### User Integration
- Processes feedback ratings
- Learns from corrections
- Integrates improvements
- Tracks user preferences

## API Integration

### OpenAI GPT-4o
- Enhanced analysis engine
- Natural language processing
- Urgency assessment
- Context understanding

### Economic Data
- yfinance for market data
- VIX volatility tracking
- Gold price monitoring
- Currency stability metrics

### News Sources
- RSS feed processing
- Multiple source aggregation
- Content classification
- Source verification

## Security Features

### Data Protection
- Local database storage
- Encrypted API keys
- Secure configuration
- Privacy-focused design

### Access Control
- Environment-based secrets
- Configuration validation
- Secure log handling
- Protected credentials
