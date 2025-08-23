import os
import sqlite3
import requests
import feedparser
import json
import argparse
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

# Load environment variables
from dotenv import load_dotenv
load_dotenv('config/.env')

# Import utility modules - handle both relative and absolute imports
try:
    from .utils import log_error, log_info, load_file_lines
    from .analysis_engine import analyze_headlines_with_ai, calculate_urgency_score
    from .email_utils import build_email_content, send_email
    from .slack_utils import send_to_slack
    from .database_utils import init_db, save_digest_to_db
    from .social_media_utils import initialize_x_monitor, get_social_media_analysis, get_social_urgency_boost, format_social_media_section
    from .config_loader import get_config, get_setting
except ImportError:
    # Fallback for standalone execution
    from utils import log_error, log_info, load_file_lines
    from analysis_engine import analyze_headlines_with_ai, calculate_urgency_score
    from email_utils import build_email_content, send_email
    from slack_utils import send_to_slack
    from database_utils import init_db, save_digest_to_db
    from social_media_utils import initialize_x_monitor, get_social_media_analysis, get_social_urgency_boost, format_social_media_section
    from config_loader import get_config, get_setting

# Load configuration
try:
    config = get_config()
    CONFIG_ENABLED = True
    print("✅ YAML configuration loaded")
except ImportError:
    CONFIG_ENABLED = False
    print("⚠️  YAML configuration not available, using defaults")

# Import adaptive intelligence
try:
    from .adaptive_intelligence import CanaryIntelligence
    ADAPTIVE_INTELLIGENCE_ENABLED = True
except ImportError:
    try:
        from adaptive_intelligence import CanaryIntelligence
        ADAPTIVE_INTELLIGENCE_ENABLED = True
    except ImportError:
        ADAPTIVE_INTELLIGENCE_ENABLED = False
        print("⚠️  Adaptive intelligence module not found. Using basic urgency assessment.")

# Economic data sources for monitoring instability
# Get configuration values


def get_economic_apis():
    """Get economic APIs from configuration"""
    if CONFIG_ENABLED:
        return get_setting('monitoring.economic_apis', {})
    else:
        return {
            "fed_rates": "https://api.stlouisfed.org/fred/series/observations?series_id=FEDFUNDS&api_key=YOUR_KEY&file_type=json&limit=5",
            "unemployment": "https://api.stlouisfed.org/fred/series/observations?series_id=UNRATE&api_key=YOUR_KEY&file_type=json&limit=5",
            "inflation": "https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCSL&api_key=YOUR_KEY&file_type=json&limit=5",
            "vix_fear": "https://api.stlouisfed.org/fred/series/observations?series_id=VIXCLS&api_key=YOUR_KEY&file_type=json&limit=5"}


def get_keywords():
    """Get keywords from configuration with smart fallbacks"""
    if CONFIG_ENABLED:
        keywords = get_setting('monitoring.keywords', [])
        if keywords:
            return keywords

    # Minimal fallback if config completely unavailable
    return [
        "constitutional crisis", "martial law", "bank failures",
        "election fraud", "economic recession", "emergency powers"
    ]


# Environment variables with safety checks
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# Initialize OpenAI client (modern v1.0+ API)
openai_client = None
if OPENAI_API_KEY:
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        print("✅ OpenAI client initialized (v1.0+ API)")
    except ImportError:
        print("⚠️  OpenAI library not available")
        openai_client = None
    except Exception as e:
        print(f"⚠️  OpenAI initialization failed: {e}")
        openai_client = None
else:
    print("⚠️  OpenAI API key not configured")

# Utility functions


# log_error function moved to utils.py


def load_subscribers(filename="config/subscribers.txt") -> List[str]:
    """Load email subscribers from file"""
    try:
        with open(filename, "r") as f:
            subscribers = [line.strip() for line in f if line.strip()]
        return subscribers
    except Exception as e:
        log_error(f"Failed to load subscribers: {e}")
        return []


# init_db function moved to database_utils.py

# Economic data monitoring


def fetch_economic_data() -> List[Dict[str, Any]]:
    """Fetch key economic indicators that signal instability"""
    try:
        # Import the enhanced economic monitoring
        from economic_monitor import get_market_indicators, get_crypto_indicators

        market_data = get_market_indicators()
        crypto_data = get_crypto_indicators()

        # Ensure we return a list of dictionaries
        result = []
        if isinstance(market_data, list):
            result.extend(market_data)
        if isinstance(crypto_data, dict):
            result.append(crypto_data)
        elif isinstance(crypto_data, list):
            result.extend(crypto_data)
        return result

    except ImportError:
        # Fallback to simple monitoring if enhanced module unavailable
        log_error("Enhanced economic monitoring unavailable, using fallback")
        return [
            {
                "indicator": "Market Volatility",
                "status": "Monitoring financial markets for unusual activity",
                "concern_level": "medium"
            },
            {
                "indicator": "Currency Stability",
                "status": "USD exchange rates and inflation trends",
                "concern_level": "low"
            }
        ]
    except Exception as e:
        log_error(f"Economic data fetch error: {e}")
        return []

# Fetch news headlines


def fetch_news() -> str:
    """Fetch news from configured sources"""
    # Get news sources from configuration
    if CONFIG_ENABLED:
        feeds = get_setting('monitoring.news_sources', [])
        if feeds:
            print(f"📰 Using {len(feeds)} configured news sources")
        else:
            print("⚠️  No news sources configured, using minimal fallback")
            feeds = [
                "https://feeds.npr.org/1001/rss.xml",
                "https://rss.cnn.com/rss/edition.rss"]
    else:
        print("⚠️  Configuration unavailable, using minimal fallback")
        feeds = ["https://feeds.npr.org/1001/rss.xml",
                 "https://rss.cnn.com/rss/edition.rss"]

    headlines = []
    for feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:3]:
                title = entry.title
                link = entry.link
                headlines.append({"url": link, "title": title})
        except Exception as e:
            log_error(f"Failed to fetch from {feed_url}: {e}")
    return json.dumps(headlines)

# Assess urgency based on content analysis


def assess_urgency(headlines_data: List[Dict[str, Any]], economic_data: Optional[List[Dict[str, Any]]] = None) -> Tuple[int, str]:
    """Assess urgency using adaptive intelligence if available"""

    # Get configuration values
    keywords = get_keywords()
    high_urgency_weight = get_setting(
        'monitoring.scoring.high_urgency_keywords', 3)
    medium_urgency_weight = get_setting(
        'monitoring.scoring.medium_urgency_keywords', 2)
    low_urgency_weight = get_setting(
        'monitoring.scoring.low_urgency_keywords', 1)
    max_score = get_setting('system.max_urgency_score', 10)
    urgent_threshold = get_setting('system.urgent_analysis_score', 7.0)
    critical_threshold = get_setting('system.critical_analysis_score', 4.0)

    if ADAPTIVE_INTELLIGENCE_ENABLED:
        try:
            intelligence = CanaryIntelligence()
            return intelligence.predict_trend_urgency(headlines_data, economic_data)
        except Exception as e:
            print(f"⚠️  Adaptive intelligence failed: {e}")
            print("🔄 Falling back to configured urgency assessment...")

    # Rule-based scoring using configured keywords
    urgency_score = 0
    all_text = " ".join([h.get('title', '') for h in headlines_data]).lower()

    # Analyze against configured keywords
    for keyword in keywords:
        if keyword.lower() in all_text:
            # Different weights based on keyword importance
            if any(
                term in keyword.lower() for term in [
                    'crisis',
                    'crash',
                    'violence',
                    'fraud',
                    'martial',
                    'collapse']):
                urgency_score += len([h for h in headlines_data if any(
                    keyword.lower() in h['title'].lower() for keyword in ['crisis', 'crash', 'violence', 'fraud', 'martial', 'collapse'])])
            elif any(term in keyword.lower() for term in ['recession', 'unemployment', 'discrimination', 'inflation']):
                urgency_score += medium_urgency_weight
            else:
                urgency_score += low_urgency_weight

    # Factor in economic indicators
    for indicator in economic_data:
        if indicator.get('concern_level') == 'high':
            urgency_score += medium_urgency_weight
        elif indicator.get('concern_level') == 'medium':
            urgency_score += low_urgency_weight

    # Cap at maximum score and determine level using configured thresholds
    urgency_score = min(urgency_score, max_score)

    if urgency_score >= urgent_threshold:
        return 10, "HIGH"
    elif urgency_score >= critical_threshold:
        return 5, "MEDIUM"
    else:
        return 1, "LOW"

# The summarize_all_topics function has been moved to analysis_engine.py

# Send summary to Slack


# Slack functionality moved to slack_utils.py

# Build email content


# Email building and sending functionality moved to email_utils.py

# Save record to DB


# Database functionality moved to database_utils.py


# Main run
if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Canary Protocol - Political and Economic Monitoring System')
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode (no emails or Slack messages sent)')
    parser.add_argument(
        '--no-openai',
        action='store_true',
        help='Skip OpenAI analysis (useful for testing other components)')
    parser.add_argument('--verbose', action='store_true',
                        help='Show detailed output including raw data')

    args = parser.parse_args()

    if args.test:
        print("🧪 RUNNING IN TEST MODE")
        print("=" * 50)
        print("No emails or Slack messages will be sent.")
        print("Analysis will be displayed in console.")
        print("=" * 50)

    init_db()

    print("📰 Fetching news headlines...")
    headlines_html = fetch_news()
    headlines_data = json.loads(headlines_html)

    if args.verbose:
        print(f"Fetched {len(headlines_data)} headlines")

    print("📊 Fetching economic data...")
    # Fetch economic data
    economic_data = fetch_economic_data()
    
    print("📱 Initializing social media monitoring...")
    # Initialize X/Twitter monitoring if available
    x_monitor = initialize_x_monitor()
    if x_monitor:
        log_info("Social media monitoring active")
    else:
        log_info("Social media monitoring disabled")

    if args.verbose:
        print(f"Economic indicators: {len(economic_data)}")
        for indicator in economic_data[:3]:  # Show first 3
            print(
                f"  - {indicator.get('indicator', 'Unknown')}: {indicator.get('status', 'N/A')}")

    all_titles = headlines_data

    print("🔍 Assessing urgency level...")
    # Enhanced urgency assessment with social media boost
    base_urgency_score, urgency_level = assess_urgency(
        headlines_data, economic_data)
    
    # Add social media urgency boost
    social_urgency_boost = get_social_urgency_boost(x_monitor)
    urgency_score = base_urgency_score + social_urgency_boost
    
    if social_urgency_boost > 0:
        log_info(f"Social media added +{social_urgency_boost} to urgency score")

    print(f"📈 Urgency Assessment: {urgency_level} (Score: {urgency_score}/10)")

    if args.no_openai:
        summary_text = f"""# TEST MODE - OpenAI Analysis Skipped

**Urgency Level:** {urgency_level} (Score: {urgency_score}/10)

**Headlines Processed:** {len(headlines_data)}

**Economic Indicators:** {len(economic_data)}

This would normally contain AI-generated analysis of current political and economic conditions.
"""
        print("⚠️  Skipping OpenAI analysis (--no-openai flag)")
    else:
        print("🤖 Generating AI analysis...")
        # Get social media analysis
        social_analysis = get_social_media_analysis(x_monitor)
        
        # Enhanced summary with economic and social context
        summary_text = analyze_headlines_with_ai(
            headlines_data, economic_data, urgency_level)
        
        # Add social media section to summary
        social_section = format_social_media_section(social_analysis)
        if social_section:
            summary_text += social_section

    # Adjust tone based on urgency
    if urgency_level == "HIGH":
        tone = "urgent"
    elif urgency_level == "MEDIUM":
        tone = "concerned"
    else:
        tone = "calm"

    print("📧 Building email content...")
    email_html = build_email_content(summary_text, headlines_html, economic_data)

    today = datetime.now().strftime("%B %d, %Y")
    subject = f"The Canary Protocol - Weekly Digest ({today}) - {urgency_level} URGENCY"

    # Always save to database (even in test mode)
    save_digest_to_db(today, urgency_score, summary_text, urgency_level, headlines_html)

    # Learn from this digest if adaptive intelligence is enabled
    if ADAPTIVE_INTELLIGENCE_ENABLED:
        try:
            intelligence = CanaryIntelligence()
            digest_data = {
                'urgency_score': urgency_score,
                'summary': summary_text,
                'top_headlines': headlines_data[:10],  # Top 10 headlines
                'economic_data': economic_data,
                'sources': [h.get('link', '') for h in headlines_data if h.get('link')]
            }
            intelligence.learn_from_digest(digest_data)

            if args.verbose:
                print("🧠 Adaptive intelligence updated with new patterns")

        except Exception as e:
            if args.verbose:
                print(f"⚠️  Could not update adaptive intelligence: {e}")

    # Send notifications
    if not args.test:
        send_email(subject, email_html, GMAIL_USER, GMAIL_APP_PASSWORD)
        send_to_slack(summary_text, SLACK_WEBHOOK_URL)
        print(
            f"✅ Digest sent with {urgency_level} urgency level (score: {urgency_score})")
    else:
        send_email(subject, email_html, GMAIL_USER, GMAIL_APP_PASSWORD, test_mode=True)
        send_to_slack(summary_text, SLACK_WEBHOOK_URL, test_mode=True)
        print(
            f"✅ Test completed - {urgency_level} urgency level (score: {urgency_score})")
        print("💾 Analysis saved to database for review")


def main():
    """Main entry point for the canary protocol"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart Canary Protocol')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--emergency', action='store_true', help='Run emergency analysis')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Initialize database
    if not init_db():
        print("❌ Failed to initialize database")
        return 1
    
    # Run the main analysis
    try:
        if args.emergency:
            print("🚨 Running emergency analysis...")
        elif args.test:
            print("🧪 Running in test mode...")
        else:
            print("📊 Running standard analysis...")
            
        # For now, just run a basic test
        headlines = fetch_news()
        economic_data = fetch_economic_data()
        
        if headlines:
            print(f"✅ Fetched {len(headlines)} headlines")
        else:
            print("⚠️  No headlines fetched")
            
        if economic_data:
            print(f"✅ Fetched {len(economic_data)} economic indicators")
        else:
            print("⚠️  No economic data fetched")
            
        print("✅ Analysis completed successfully")
        return 0
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
