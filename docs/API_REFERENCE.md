# Smart Canary Protocol - API Documentation

## Core Modules

### CanaryTUI (`core/canary_tui.py`) ⭐ **NEW**
Interactive Terminal User Interface for system management.

**Key Features:**
- `CanaryTUI.run()` - Main interactive menu system
- `execute_command()` - Command execution with proper terminal handling
- `show_help()` - Built-in help system
- Navigation with arrow keys, vim-style keys, and shortcuts

### CanaryProtocol (`core/canary_protocol.py`)
Main analysis engine with adaptive intelligence integration.

**Key Functions:**
- `main()` - Primary entry point with argument parsing
- `fetch_news()` - Multi-source news aggregation
- `fetch_economic_data()` - Economic indicator collection
- `assess_urgency()` - Urgency scoring with AI fallback

### AdaptiveIntelligence (`core/adaptive_intelligence.py`)
Machine learning and pattern recognition system with enhanced individual article integration.

**Key Functions:**
- `learn_from_analysis(analysis, feedback)` - Updates learning models from digest data
- `learn_from_individual_articles(digest_date)` ⭐ **NEW** - High-priority learning from article feedback
- `predict_trend_urgency(headlines, economic_data)` - Enhanced AI prediction with article patterns
- `get_source_reliability(source)` - Source credibility scoring
- `get_intelligence_report()` - Learning progress and pattern analysis

**Enhanced Learning Methods:** ⭐ **NEW**
- `_process_article_feedback()` - Individual article learning with 2x weight
- `_process_irrelevant_article()` - Noise reduction from skipped articles
- `_get_individual_article_pattern_boost()` - Article pattern priority in predictions
- `_headline_matches_pattern()` - Structural headline pattern matching

### Production Management Modules ⭐ **NEW**

#### DatabaseMigrations (`core/database_migrations.py`)
Version-controlled database schema management.

**Key Functions:**
- `apply_migrations()` - Apply pending schema changes
- `rollback_migration()` - Revert specific migration
- `get_migration_status()` - Check applied migrations
- CLI interface for migration management

#### DataArchival (`core/data_archival.py`)
Automated data lifecycle management and cleanup.

**Key Functions:**
- `archive_old_data()` - Archive data based on retention policies
- `restore_from_archive()` - Emergency data restoration
- `cleanup_old_data()` - Remove archived data from database
- `generate_archival_report()` - Archival statistics and reporting

#### BackupVerification (`core/backup_verification.py`)
Backup integrity testing and validation.

**Key Functions:**
- `verify_backup_integrity()` - SHA256 checksum validation
- `test_backup_restoration()` - Restore to temporary database
- `validate_backup_schema()` - Schema consistency checks
- `generate_verification_report()` - Detailed verification results

### SmartFeedback (`core/smart_feedback.py`)
User feedback integration and learning system for digest-level feedback.

**Key Functions:**
- `collect_feedback()` - Interactive digest-level feedback collection
- `report_false_positive(content)` - False alarm reporting
- `update_learning_models()` - Apply feedback to ML models

### Individual Article Feedback System
Enhanced user feedback system for individual article training with 2x AI learning weight.

**Available via canary command:**
- `./canary articles` - Interactive article-by-article feedback collection
- `./canary feedback-summary` - Summary of individual article ratings and patterns
- `./canary feedback-clear` - Database cleanup and management

### Enhanced AI Training Integration ⭐ **NEW**
- **Individual Article Learning**: 2x weight vs digest feedback for targeted pattern recognition
- **Headline Pattern Analysis**: Learns structural patterns from specific headlines
- **Source-Content Correlation**: Article-level source reliability tracking
- **Irrelevant Pattern Learning**: Noise reduction from articles marked as irrelevant

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
Interactive digest-level feedback collection:
- Rate overall digest accuracy
- Report digest-level false positives
- Suggest digest improvements
- View digest feedback history

### ./canary articles (or feedback-individual) ⭐ **RECOMMENDED**
Enhanced individual article feedback with 2x AI training weight:
- Rate specific headlines (0-10 urgency scale)
- Mark irrelevant articles for noise reduction
- Train AI on headline patterns and source reliability
- Duplicate prevention (no re-rating processed articles)

### ./canary feedback-summary
Comprehensive feedback overview:
- Digest-level feedback summary
- Individual article rating statistics
- Source reliability by content type
- AI learning progress from both feedback types

### ./canary feedback-clear
Selective feedback data management:
- Clear digest-level feedback only
- Clear individual article feedback only
- Clear ALL feedback data
- Confirmation prompts for safety

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

### Main Database (`data/canary_protocol.db`)
Unified database containing all system data:

**AI Learning Tables:**
- `learning_patterns` - Headline patterns and urgency correlations (individual article feedback)
- `keyword_performance` - Tracked terms and urgency weights (2x weight from articles)
- `source_reliability` - Source credibility scores by content type
- `prediction_tracking` - Historical accuracy data and AI performance

**Digest & Analysis Tables:**
- `weekly_digests` - Generated digest summaries and AI urgency scores
- `daily_headlines` - Raw headline data from monitored sources
- `daily_economic` - Economic indicators and market data
- `news_analysis` - Processed news content and classifications

**User Feedback Tables:**
- `user_feedback` - Digest-level user ratings and comments
- `individual_article_feedback` ⭐ **NEW** - Article-specific ratings with 2x AI training weight
- `false_positives` - Reported false alarms and corrections
- `missed_signals` - User-reported missed important events

**System Tables:**
- `emergency_triggers` - Automated alert configurations
- `source_reliability` - News source credibility tracking

## Learning System

### Enhanced Pattern Recognition ⭐ **NEW**
- **Individual Article Analysis**: Learns from specific headline structures with 2x weight
- **Headline Pattern Matching**: Identifies urgency indicators in specific headlines
- **Keyword Effectiveness**: Tracks which words in headlines indicate real urgency
- **Irrelevant Pattern Learning**: Uses skipped articles to reduce false positives
- **Cross-Source Correlation**: Learns reliability patterns by content type

### Multi-Level Feedback Integration
- **Article-Level Training** (2x Priority): Specific headlines, sources, and patterns
- **Digest-Level Training**: Overall urgency assessment and broad accuracy
- **False Positive Reduction**: Irrelevant markings help filter noise
- **Duplicate Prevention**: No re-training on already processed content

### Source Intelligence
- **Article-Specific Reliability**: Tracks source accuracy by individual content
- **Content-Type Correlation**: Learns which sources are reliable for different topics
- **Bias Pattern Detection**: Identifies source bias in specific content areas
- **Speed vs Accuracy Balance**: Measures reliability vs timeliness by source

### Adaptive Weighting System
- **Individual Articles**: 2x multiplier for headline-specific feedback
- **Pattern Confidence**: Higher confidence (0.9) for article-based patterns
- **Keyword Correlation**: Enhanced keyword weights from article-level data
- **Prediction Priority**: Article patterns checked first in AI predictions

## API Integration

### OpenAI API (v1.0+)
- Modern OpenAI client integration
- GPT-4o model for enhanced analysis
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
