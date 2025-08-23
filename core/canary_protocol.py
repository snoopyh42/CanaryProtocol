import os
import smtplib
import sqlite3
import requests
import openai
import feedparser
import re
import time
import markdown2
import json
import argparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv('config/.env')

# Load configuration
try:
    from config_loader import get_config, get_setting, get_section
    config = get_config()
    CONFIG_ENABLED = True
    print("✅ YAML configuration loaded")
except ImportError:
    CONFIG_ENABLED = False
    print("⚠️  YAML configuration not available, using defaults")

# Import adaptive intelligence
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
            "vix_fear": "https://api.stlouisfed.org/fred/series/observations?series_id=VIXCLS&api_key=YOUR_KEY&file_type=json&limit=5"
        }

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
def log_error(message):
    """Log errors to file"""
    import os
    os.makedirs("logs", exist_ok=True)
    with open("logs/error.log", "a") as f:
        f.write(f"{datetime.now().isoformat()}: {message}\n")

def load_subscribers(filename="config/subscribers.txt"):
    """Load email subscribers from file"""
    try:
        with open(filename, "r") as f:
            subscribers = [line.strip() for line in f if line.strip()]
        return subscribers
    except Exception as e:
        log_error(f"Failed to load subscribers: {e}")
        return []

def init_db():
    """Initialize database with required tables"""
    import os
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect('data/canary_protocol.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_digests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            urgency_score INTEGER,
            summary TEXT,
            tone_used TEXT,
            top_headlines TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            headline TEXT,
            urgency_score INTEGER,
            analysis TEXT,
            source TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Economic data monitoring
def fetch_economic_data():
    """Fetch key economic indicators that signal instability"""
    try:
        # Import the enhanced economic monitoring
        from economic_monitor import get_market_indicators, get_crypto_indicators
        
        market_data = get_market_indicators()
        crypto_data = get_crypto_indicators()
        
        return market_data + [crypto_data]
        
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
def fetch_news():
    """Fetch news from configured sources"""
    # Get news sources from configuration
    if CONFIG_ENABLED:
        feeds = get_setting('monitoring.news_sources', [])
        if feeds:
            print(f"📰 Using {len(feeds)} configured news sources")
        else:
            print("⚠️  No news sources configured, using minimal fallback")
            feeds = ["https://feeds.npr.org/1001/rss.xml", "https://rss.cnn.com/rss/edition.rss"]
    else:
        print("⚠️  Configuration unavailable, using minimal fallback")
        feeds = ["https://feeds.npr.org/1001/rss.xml", "https://rss.cnn.com/rss/edition.rss"]
    
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
def assess_urgency(headlines, economic_data):
    """Assess urgency using adaptive intelligence if available"""
    
    # Get configuration values
    keywords = get_keywords()
    high_urgency_weight = get_setting('monitoring.scoring.high_urgency_keywords', 3)
    medium_urgency_weight = get_setting('monitoring.scoring.medium_urgency_keywords', 2)
    low_urgency_weight = get_setting('monitoring.scoring.low_urgency_keywords', 1)
    max_score = get_setting('system.max_urgency_score', 10)
    urgent_threshold = get_setting('system.urgent_analysis_score', 7.0)
    critical_threshold = get_setting('system.critical_analysis_score', 4.0)
    
    if ADAPTIVE_INTELLIGENCE_ENABLED:
        try:
            intelligence = CanaryIntelligence()
            return intelligence.predict_trend_urgency(headlines, economic_data)
        except Exception as e:
            print(f"⚠️  Adaptive intelligence failed: {e}")
            print("🔄 Falling back to configured urgency assessment...")
    
    # Rule-based scoring using configured keywords
    urgency_score = 0
    all_text = " ".join([h.get('title', '') for h in headlines]).lower()
    
    # Analyze against configured keywords
    for keyword in keywords:
        if keyword.lower() in all_text:
            # Different weights based on keyword importance
            if any(term in keyword.lower() for term in ['crisis', 'crash', 'violence', 'fraud', 'martial', 'collapse']):
                urgency_score += high_urgency_weight
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

# Summarize headlines
def summarize_all_topics(headlines, economic_data=None, urgency_level="LOW"):
    if not headlines:
        return "Summary not available."
    
    # Include economic data in analysis
    economic_context = ""
    if economic_data:
        high_concern_econ = [e for e in economic_data if e.get('concern_level') == 'high']
        if high_concern_econ:
            economic_context = f"\n\nCurrent economic concerns: {', '.join([e['indicator'] + ': ' + e['status'] for e in high_concern_econ])}"
    
    joined_text = "\n".join([f"{h['title']} - {h['url']}" for h in headlines])
    
    prompt = f"""You are an expert political and economic analyst specializing in U.S. stability assessment. Your role is to provide objective, fact-based analysis for citizens monitoring potential risks.

ANALYSIS FRAMEWORK:
Current urgency level: {urgency_level}
Economic context: {economic_context}

INSTRUCTIONS:
1. Focus ONLY on U.S. domestic events and their direct impacts
2. Prioritize developments that affect civil liberties, democratic institutions, or economic stability
3. Use factual, measured language - avoid sensationalism but don't downplay genuine risks
4. Include clickable markdown links: **[article title](URL)** for all sources

REQUIRED SECTIONS:

## 🏛️ POLITICAL & INSTITUTIONAL STABILITY (150-250 words)
Analyze changes to:
- Democratic processes and voting rights
- Constitutional protections and civil liberties  
- Government emergency powers or extraordinary measures
- Supreme Court decisions affecting fundamental rights

## 📊 ECONOMIC STABILITY INDICATORS (100-200 words)
Assess:
- Market volatility and financial system stress
- Currency/inflation concerns affecting daily life
- Employment and housing market changes
- Economic policies impacting middle class

## �️ SAFETY ASSESSMENT BY GROUP
For each group, provide: Status (� SAFE | 🟠 MIXED | 🔴 UNSAFE) + brief explanation

**LGBTQ+ Persons:**
Status + recent policy/legal changes affecting rights and safety

**Political Progressives:**
Status + assessment of political climate and potential targeting

**Neurodivergent Individuals:**
Status + education, healthcare, and discrimination policy changes

**California Residents:**
Status + federal vs state conflicts, economic impacts, natural disasters

## 📈 TREND ANALYSIS (100-150 words)
- Week-over-week changes in key indicators
- Emerging patterns requiring attention
- Comparison to historical precedents if relevant

## 🎯 KEY TAKEAWAYS (75-125 words)
3-5 bullet points of most important developments for monitoring

Headlines to analyze:
{joined_text}

RESPONSE FORMAT: Use clear markdown headers, bullet points, and **bold links** to sources. Be thorough but concise.

FALLBACK INSTRUCTIONS FOR MISSING DATA:
- If fewer than 10 headlines available: Focus on quality over quantity, acknowledge limited data
- If no economic data: State "Economic indicators unavailable" and focus on news analysis
- If headlines lack URLs: Reference source name only, no markdown links
- If urgency level is unclear: Default to MEDIUM and explain uncertainty
- If group safety cannot be assessed: Mark as 🟠 MIXED with explanation of data limitations
- If no trend data available: Focus on current snapshot rather than changes over time

QUALITY STANDARDS:
- Each section must meet minimum word count or explain why it cannot
- Include confidence level in assessments when data is limited
- Distinguish between confirmed facts and reasonable inferences
- Always include at least one specific, measurable detail per section when possible"""
    
    # Check if OpenAI client is available
    if not openai_client:
        log_error("OpenAI client not available - check API key configuration")
        return "AI analysis unavailable - configuration issue."
    
    # Get AI settings from configuration
    model = get_setting('intelligence.model', 'gpt-4o')
    temperature = get_setting('intelligence.temperature', 0.2)
    max_tokens = get_setting('intelligence.max_tokens', 3000)
    
    retries = 3
    for attempt in range(retries):
        try:
            response = openai_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert political and economic analyst with 20+ years experience monitoring U.S. stability. You provide objective, factual analysis for informed citizens. Your assessments are measured, evidence-based, and actionable."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=temperature,      # From configuration
                max_tokens=max_tokens,       # From configuration
                top_p=0.9,                   # Slightly more focused responses
                frequency_penalty=0.1,       # Reduce repetition
                presence_penalty=0.1         # Encourage diverse topics
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if "rate_limit" in str(e).lower():
                log_error(f"OpenAI rate limit exceeded: {e}. Retrying in {2**attempt * 5} seconds...")
                time.sleep(2**attempt * 5)
            elif "invalid_request" in str(e).lower():
                log_error(f"OpenAI invalid request: {e}")
                return "Analysis unavailable due to request error."
            elif "connection" in str(e).lower():
                log_error(f"OpenAI connection error: {e}. Retrying in {2**attempt} seconds...")
                time.sleep(2**attempt)
            else:
                log_error(f"OpenAI API error: {e}. Retrying in {2**attempt} seconds...")
                time.sleep(2**attempt)
    
    return "Summary not available after multiple attempts."

# Send summary to Slack
def send_to_slack(summary_text, test_mode=False):
    if test_mode:
        print("\n" + "="*60)
        print("SLACK MESSAGE (TEST MODE - NOT SENT)")
        print("="*60)
        print(summary_text[:1000] + "..." if len(summary_text) > 1000 else summary_text)
        print("="*60)
        return
        
    if not SLACK_WEBHOOK_URL:
        log_error("Slack webhook URL missing.")
        return

    slack_text = summary_text
    slack_text = re.sub(r'^#### (.*)$', r'*\1*', slack_text, flags=re.MULTILINE)
    slack_text = re.sub(r'^### (.*)$', r'*\1*', slack_text, flags=re.MULTILINE)
    slack_text = re.sub(r'^## (.*)$', r'*\1*', slack_text, flags=re.MULTILINE)
    slack_text = re.sub(r'^# (.*)$', r'*\1*', slack_text, flags=re.MULTILINE)
    slack_text = slack_text.replace("\n- ", "\n• ")
    slack_text = slack_text.replace("**", "*")
    slack_text = slack_text.replace("\n\n", "\n")

    blocks = [
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*Canary Protocol Weekly Digest - {datetime.now().strftime('%B %d, %Y')}*"}},
        {"type": "divider"}
    ]

    chunk_size = 2900
    current_chunk = ""
    for line in slack_text.splitlines():
        if line.startswith("*") and line.endswith("*") and current_chunk:
            blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": current_chunk.strip()}})
            blocks.append({"type": "divider"})
            current_chunk = line + "\n"
        else:
            current_chunk += line + "\n"

    if current_chunk.strip():
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": current_chunk.strip()}})

    slack_payload = {"blocks": blocks}

    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=slack_payload)
        if response.status_code != 200:
            log_error(f"Slack webhook error: {response.status_code} {response.text}")
    except Exception as e:
        log_error(f"Slack send error: {e}")

# Build email content
def build_email(summary_text, top_links_html, economic_data=None):
    try:
        top_links = json.loads(top_links_html)
    except Exception:
        top_links = []

    # Add economic indicators to summary if available
    if economic_data:
        try:
            from economic_monitor import format_economic_summary
            economic_section = format_economic_summary(economic_data)
            summary_text = f"{summary_text}\n\n{economic_section}"
        except ImportError:
            pass

    summary_html = markdown2.markdown(summary_text)
    today = datetime.now().strftime("%B %d, %Y")

    legend_block = """
    <div style='text-align:center; margin-bottom: 20px;'>
        <strong>Sentiment Legend:</strong>
        🟢 SAFE | 🟠 MIXED | 🔴 UNSAFE
    </div>
    <hr style='margin-top: 20px; margin-bottom: 20px; border: none; border-top: 2px solid #003366;'>
    """

    banner_block = f"""
    <div style='background-color:#003366; color:white; padding: 10px; text-align:center; font-size: 24px; font-weight: bold;'>
        The Canary Protocol Weekly Digest — {today}
    </div>
    """

    footer_block = """
    <div style='text-align:center; font-size: 12px; color: #666; margin-top: 40px;'>
        Stay alert. Stay informed. 🕊️
    </div>
    """

    top_links_block = ""
    for link in top_links:
        top_links_block += f"""
        <div style='margin-bottom: 12px;'>
            <div style='font-size: 14px;'>
                <a href='{link['url']}' target='_blank' style='color: #0066cc; text-decoration: none;'>
                    {link['title']}
                </a>
            </div>
        </div>
        """

    # Load email template from config directory
    template_path = "config/email_template.html"
    try:
        with open(template_path, "r") as f:
            template = f.read()
    except FileNotFoundError:
        log_error(f"Email template not found at {template_path}")
        # Fallback to a basic template
        template = """
        <html>
        <body>
        <h2>Smart Canary Protocol Alert</h2>
        {banner_block}
        {legend_block}
        {summary_block}
        {top_links_block}
        {footer_block}
        </body>
        </html>
        """

    return template.format(
        banner_block=banner_block,
        legend_block=legend_block,
        summary_block=summary_html,
        top_links_block=top_links_block,
        footer_block=footer_block
    )

def send_email(subject, html_content, test_mode=False):
    if test_mode:
        print("\n" + "="*60)
        print("EMAIL (TEST MODE - NOT SENT)")
        print("="*60)
        print(f"Subject: {subject}")
        print(f"To: {load_subscribers()}")
        print("\nHTML Content Preview:")
        print("-" * 40)
        # Convert HTML to readable text for preview
        import re
        text_content = re.sub('<[^<]+?>', '', html_content)
        text_content = re.sub(r'\n\s*\n', '\n\n', text_content)
        print(text_content[:2000] + "..." if len(text_content) > 2000 else text_content)
        print("="*60)
        return
        
    try:
        # Validate email configuration first
        if not GMAIL_USER or not GMAIL_APP_PASSWORD:
            log_error("Email credentials not configured - check GMAIL_USER and GMAIL_APP_PASSWORD in config/.env")
            return
            
        subscribers = load_subscribers()
        if not subscribers:
            log_error("No subscribers to send to.")
            return

        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = ", ".join(subscribers)
        msg['Subject'] = subject
        msg.attach(MIMEText(html_content, 'html'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, subscribers, msg.as_string())
            print(f"✅ Email sent to {len(subscribers)} subscribers")
    except Exception as e:
        log_error(f"Email sending error: {e}")

# Save record to DB
def save_to_db(date, urgency, summary, tone, headlines):
    conn = sqlite3.connect('data/canary_protocol.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO weekly_digests (date, urgency_score, summary, tone_used, top_headlines)
        VALUES (?, ?, ?, ?, ?)
    ''', (date, urgency, summary, tone, headlines))
    conn.commit()
    conn.close()

# Main run
if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Canary Protocol - Political and Economic Monitoring System')
    parser.add_argument('--test', action='store_true', 
                       help='Run in test mode (no emails or Slack messages sent)')
    parser.add_argument('--no-openai', action='store_true',
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
    
    if args.verbose:
        print(f"Economic indicators: {len(economic_data)}")
        for indicator in economic_data[:3]:  # Show first 3
            print(f"  - {indicator.get('indicator', 'Unknown')}: {indicator.get('status', 'N/A')}")

    all_titles = headlines_data

    print("🔍 Assessing urgency level...")
    # Enhanced urgency assessment
    urgency_score, urgency_level = assess_urgency(headlines_data, economic_data)
    
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
        # Enhanced summary with economic context
        summary_text = summarize_all_topics(all_titles, economic_data, urgency_level)

    # Adjust tone based on urgency
    if urgency_level == "HIGH":
        tone = "urgent"
    elif urgency_level == "MEDIUM":
        tone = "concerned"
    else:
        tone = "calm"

    print("📧 Building email content...")
    email_html = build_email(summary_text, headlines_html, economic_data)

    today = datetime.now().strftime("%B %d, %Y")
    subject = f"The Canary Protocol - Weekly Digest ({today}) - {urgency_level} URGENCY"

    # Always save to database (even in test mode)
    save_to_db(datetime.now().isoformat(), urgency_score, summary_text, tone, headlines_html)
    
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
    
    if args.test:
        print("\n" + "="*60)
        print("GENERATED ANALYSIS SUMMARY")
        print("="*60)
        print(summary_text)
        print("\n" + "="*60)
        print(f"Analysis saved to database with {urgency_level} urgency")
        print("="*60)
    
    # Send notifications (or show in test mode)
    send_email(subject, email_html, test_mode=args.test)
    send_to_slack(summary_text, test_mode=args.test)

    if not args.test:
        print(f"✅ Digest sent with {urgency_level} urgency level (score: {urgency_score})")
    else:
        print(f"✅ Test completed - {urgency_level} urgency level (score: {urgency_score})")
        print("💾 Analysis saved to database for review")
