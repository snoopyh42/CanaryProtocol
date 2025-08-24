"""
X/Twitter Social Media Monitoring Module for Smart Canary Protocol
Analyzes social media trends to enhance threat detection and urgency assessment
"""

import sqlite3
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os


class XMonitor:
    """
    X/Twitter monitoring system for political and economic trend analysis
    Designed to work within API rate limits and provide meaningful insights
    """

    def __init__(
            self,
            db_path="data/canary_protocol.db",
            config_path="config/.env"):
        self.db_path = db_path
        self.base_url = "https://api.twitter.com/2"

        # Load configuration
        try:
            import sys
            import os
            sys.path.append(
                os.path.dirname(
                    os.path.dirname(
                        os.path.abspath(__file__))))
            from .config_loader import get_config, get_setting
            self.config = get_config()
            self.social_config = get_setting('monitoring.social_media', {})
            self.config_enabled = True
        except ImportError:
            self.config_enabled = False
            self.social_config = {}
            print("⚠️  YAML configuration not available, using defaults")

        # Load X API credentials
        self.bearer_token = self._load_api_credentials(config_path)
        if not self.bearer_token:
            raise ValueError("X_BEARER_TOKEN not found in environment")

        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }

        # Initialize database tables
        self._setup_database()

    def _load_api_credentials(self, config_path):
        """Load API credentials from environment file"""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    for line in f:
                        if line.startswith('X_BEARER_TOKEN='):
                            return line.split('=', 1)[1].strip().strip('"\'')

            # Fallback to environment variable
            return os.getenv('X_BEARER_TOKEN')
        except Exception as e:
            print(f"❌ Error loading credentials: {e}")
            return None

    def _setup_database(self):
        """Initialize database tables for X/Twitter monitoring"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # X trends table for storing weekly analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS x_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                political_hashtags TEXT,
                economic_hashtags TEXT,
                viral_content TEXT,
                engagement_metrics TEXT,
                urgency_signals INTEGER,
                collection_date TEXT
            )
        ''')

        # X political activity tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS x_political_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT,
                tweet_count INTEGER,
                engagement_score REAL,
                sentiment_score REAL,
                trending_velocity REAL,
                collection_date TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def get_weekly_trends(self):
        """Analyze X/Twitter trends over the past 7 days - optimized for rate limits"""
        print("🐦 Analyzing X/Twitter trends (past 7 days)...")

        # Get keywords from configuration or use defaults
        if self.config_enabled and self.social_config.get('enabled', True):
            political_keywords = self.social_config.get(
                'political_keywords', [
                    "Trump", "Biden", "Congress", "Supreme Court", "protest", "voting"])
            economic_keywords = self.social_config.get(
                'economic_keywords', [
                    "economy", "inflation", "recession", "stock market", "Fed", "unemployment"])
            max_keywords = self.social_config.get(
                'max_keywords_per_request', 8)
        else:
            # Fallback defaults
            political_keywords = [
                "Trump",
                "Biden",
                "Congress",
                "Supreme Court",
                "protest",
                "voting"]
            economic_keywords = [
                "economy",
                "inflation",
                "recession",
                "stock market",
                "Fed",
                "unemployment"]
            max_keywords = 8

        # Limit keywords to respect rate limits
        political_keywords = political_keywords[:max_keywords // 2]
        economic_keywords = economic_keywords[:max_keywords // 2]

        print(f"🔍 Political keywords: {', '.join(political_keywords)}")
        print(f"🔍 Economic keywords: {', '.join(economic_keywords)}")

        # Get trends for the past 7 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        political_trends = self._analyze_keyword_trends(
            political_keywords, start_date, end_date, "political")

        # Only proceed with economic if we have API calls left
        economic_trends = {}
        if political_trends:  # If we got political data successfully
            economic_trends = self._analyze_keyword_trends(
                economic_keywords, start_date, end_date, "economic")

        # Monitor notable accounts if configured and we have API calls
        # remaining
        account_activity = {}
        if self.config_enabled and political_trends and economic_trends:
            account_activity = self._monitor_notable_accounts(
                start_date, end_date)

        # Store results
        self._store_weekly_analysis(
            political_trends,
            economic_trends,
            account_activity)

        return {
            'political_trends': political_trends,
            'economic_trends': economic_trends,
            'analysis_period': f"{
                start_date.strftime('%Y-%m-%d')} to {
                end_date.strftime('%Y-%m-%d')}",
            'collection_time': datetime.now().isoformat()}

    def _analyze_keyword_trends(
            self,
            keywords,
            start_date,
            end_date,
            category):
        """Analyze trends for specific keyword categories with conservative rate limiting"""
        trends = {}

        # Check if we should skip due to rate limits (free tier)
        if not self._check_rate_limit_status():
            print(f"⚠️  Skipping {category} analysis due to rate limits")
            return trends

        # Very conservative approach - only analyze 1-2 keywords per category
        limited_keywords = keywords[:2] if len(keywords) > 2 else keywords
        print(
            f"🔍 Analyzing {
                len(limited_keywords)} {category} keywords (rate limit conservation)")

        for i, keyword in enumerate(limited_keywords):
            try:
                # Progressive delay - start with longer delays
                base_delay = self.social_config.get(
                    'request_delay_seconds', 5) if self.config_enabled else 5
                delay = base_delay + (i * 2)  # Increase delay for each request

                print(f"   ⏳ Waiting {delay}s before analyzing '{keyword}'...")
                time.sleep(delay)

                trend_data = self._search_keyword_week(
                    keyword, start_date, end_date)
                if trend_data:
                    trends[keyword] = trend_data
                    print(
                        f"   ✅ {keyword}: {
                            trend_data.get(
                                'tweet_count',
                                0)} tweets")
                else:
                    print(f"   ⚠️  {keyword}: No data available")
                    # If we get no data, it's likely rate limited, so stop
                    if i == 0:  # If first keyword fails, abort category
                        print(
                            f"   🛑 Aborting {category} analysis - likely rate limited")
                        break

            except Exception as e:
                print(f"   ❌ Error analyzing {keyword}: {e}")
                continue

        return trends

    def _check_rate_limit_status(self):
        """Check if we can make API calls without getting rate limited"""
        try:
            # Make a very light API call to check status
            response = requests.get(
                f"{self.base_url}/tweets/search/recent",
                headers=self.headers,
                params={'query': 'test', 'max_results': 10},
                timeout=10
            )

            if response.status_code == 429:
                reset_time = response.headers.get('x-rate-limit-reset', '')
                if reset_time:
                    try:
                        reset_timestamp = int(reset_time)
                        wait_time = reset_timestamp - int(time.time())
                        print(
                            f"⏰ Rate limited. Reset in {wait_time} seconds ({
                                wait_time // 60} minutes)")
                    except BaseException:
                        print("⏰ Rate limited. Unknown reset time")
                return False
            elif response.status_code == 200:
                remaining = response.headers.get(
                    'x-rate-limit-remaining', 'unknown')
                print(f"✅ API available. Remaining calls: {remaining}")
                return True
            else:
                print(f"⚠️  API status unclear: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Cannot check rate limit status: {e}")
            return False

    def _monitor_notable_accounts(self, start_date, end_date):
        """Monitor activity from notable political and news accounts"""
        if not self.config_enabled:
            return {}

        notable_accounts = self.social_config.get('notable_accounts', {})
        if not notable_accounts:
            return {}

        print("👥 Monitoring notable accounts...")
        account_activity = {}

        # Get delay from config
        delay = self.social_config.get('request_delay_seconds', 3)

        # Monitor up to 3 accounts to preserve API quota
        all_accounts = []
        for category, accounts in notable_accounts.items():
            for account in accounts[:2]:  # Max 2 per category
                all_accounts.append((account, category))

        for i, (username, category) in enumerate(
                all_accounts[:3]):  # Max 3 total
            try:
                print(f"   Checking @{username} ({category})...")
                time.sleep(delay)

                activity = self._get_account_activity(
                    username, start_date, end_date)
                if activity:
                    account_activity[username] = {
                        **activity, 'category': category}
                    print(
                        f"   ✅ @{username}: {activity.get('tweet_count', 0)} tweets")
                else:
                    print(f"   ⚠️  @{username}: No data")

            except Exception as e:
                print(f"   ❌ Error monitoring @{username}: {e}")
                continue

        return account_activity

    def _get_account_activity(self, username, start_date, end_date):
        """Get recent activity for a specific account"""
        # Use user lookup and recent tweets endpoint
        query = f'from:{username} -is:retweet lang:en'

        params = {
            'query': query,
            'max_results': 25,  # Conservative limit
            'tweet.fields': 'created_at,public_metrics,lang',
            'expansions': 'author_id',
            'user.fields': 'verified,public_metrics'
        }

        try:
            response = requests.get(
                f"{self.base_url}/tweets/search/recent",
                headers=self.headers,
                params=params,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                return self._process_tweet_data(data, f"@{username}")
            elif response.status_code == 429:
                print(f"   ⚠️  Rate limited for @{username}")
                return None
            else:
                return None

        except Exception as e:
            print(f"   ❌ Request failed for @{username}: {e}")
            return None

    def _search_keyword_week(self, keyword, start_date, end_date):
        """Search for keyword activity over the past week with better error handling"""
        # Build search query - use recent search endpoint instead of full
        # archive
        query = f'{keyword} -is:retweet lang:en'

        # Use only recent timeline (past 7 days) which has higher limits
        params = {
            'query': query,
            'max_results': 50,  # Reduced from 100 to be more conservative
            'tweet.fields': 'created_at,public_metrics,lang',
            'expansions': 'author_id',
            'user.fields': 'verified,public_metrics'
        }

        try:
            response = requests.get(
                f"{self.base_url}/tweets/search/recent",
                headers=self.headers,
                params=params,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                return self._process_tweet_data(data, keyword)
            elif response.status_code == 429:
                print(f"⚠️  Rate limited for {keyword}")
                # Check rate limit headers
                reset_time = response.headers.get('x-rate-limit-reset', '')
                if reset_time:
                    try:
                        reset_timestamp = int(reset_time)
                        wait_time = max(60, reset_timestamp - int(time.time()))
                        print(
                            f"⏰ Waiting {wait_time} seconds for rate limit reset")
                        if wait_time < 300:  # Only wait if less than 5 minutes
                            time.sleep(wait_time + 5)
                            # Retry once after waiting
                            response = requests.get(f"{self.base_url}/tweets/search/recent",
                                                    headers=self.headers, params=params, timeout=15)
                            if response.status_code == 200:
                                data = response.json()
                                return self._process_tweet_data(data, keyword)
                    except BaseException:
                        pass
                return None
            elif response.status_code == 400:
                print(f"⚠️  Bad request for {keyword} (query may be invalid)")
                return None
            elif response.status_code == 401:
                print(f"❌ Authentication failed - check X_BEARER_TOKEN")
                return None
            else:
                print(f"⚠️  API error for {keyword}: {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            print(f"⚠️  Timeout for {keyword}")
            return None
        except Exception as e:
            print(f"❌ Request failed for {keyword}: {e}")
            return None

    def _process_tweet_data(self, data, keyword):
        """Process Twitter API response data"""
        if not data.get('data'):
            return None

        tweets = data['data']
        users = {
            user['id']: user for user in data.get(
                'includes', {}).get(
                'users', [])}

        # Calculate metrics
        total_tweets = len(tweets)
        total_likes = sum(
            tweet.get(
                'public_metrics',
                {}).get(
                'like_count',
                0) for tweet in tweets)
        total_retweets = sum(
            tweet.get(
                'public_metrics',
                {}).get(
                'retweet_count',
                0) for tweet in tweets)
        total_replies = sum(
            tweet.get(
                'public_metrics',
                {}).get(
                'reply_count',
                0) for tweet in tweets)

        # Calculate engagement score
        engagement_score = (total_likes + total_retweets *
                            2 + total_replies) / max(total_tweets, 1)

        # Sentiment analysis (basic - could be enhanced)
        sentiment_keywords = {
            'positive': [
                'good',
                'great',
                'excellent',
                'amazing',
                'wonderful',
                'fantastic'],
            'negative': [
                'bad',
                'terrible',
                'awful',
                'horrible',
                'disaster',
                'crisis',
                'fail']}

        positive_count = 0
        negative_count = 0

        for tweet in tweets:
            text = tweet.get('text', '').lower()
            positive_count += sum(
                1 for word in sentiment_keywords['positive'] if word in text)
            negative_count += sum(
                1 for word in sentiment_keywords['negative'] if word in text)

        sentiment_score = (positive_count - negative_count) / \
            max(total_tweets, 1)

        return {
            'keyword': keyword,
            'tweet_count': total_tweets,
            'total_engagement': total_likes + total_retweets + total_replies,
            'engagement_score': round(engagement_score, 2),
            'sentiment_score': round(sentiment_score, 2),
            'likes': total_likes,
            'retweets': total_retweets,
            'replies': total_replies,
            'trending_velocity': self._calculate_trending_velocity(tweets)
        }

    def _calculate_trending_velocity(self, tweets):
        """Calculate how quickly a topic is trending"""
        if not tweets:
            return 0

        # Group tweets by day
        daily_counts = {}
        for tweet in tweets:
            try:
                created_at = datetime.strptime(
                    tweet['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
                day = created_at.strftime('%Y-%m-%d')
                daily_counts[day] = daily_counts.get(day, 0) + 1
            except BaseException:
                continue

        if len(daily_counts) < 2:
            return 0

        # Calculate velocity (change over time)
        days = sorted(daily_counts.keys())
        recent_days = days[-2:]  # Last 2 days

        if len(recent_days) == 2:
            velocity = daily_counts[recent_days[1]] - \
                daily_counts[recent_days[0]]
            return velocity / max(daily_counts[recent_days[0]], 1)

        return 0

    def _store_weekly_analysis(
            self,
            political_trends,
            economic_trends,
            account_activity=None):
        """Store weekly analysis in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Generate summary data
        summary_data = {
            'political_hashtags': ', '.join([k for k in political_trends.keys()]),
            'economic_hashtags': ', '.join([k for k in economic_trends.keys()]),
            'viral_content': self._extract_viral_content(political_trends, economic_trends, account_activity),
            'engagement_metrics': self._calculate_engagement_metrics(political_trends, economic_trends, account_activity),
            'urgency_signals': self._calculate_urgency_score(political_trends, economic_trends, account_activity),
            'collection_date': datetime.now().strftime('%Y-%m-%d')
        }

        cursor.execute('''
            INSERT INTO x_trends
            (political_hashtags, economic_hashtags, viral_content,
             engagement_metrics, urgency_signals, collection_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            summary_data['political_hashtags'],
            summary_data['economic_hashtags'],
            summary_data['viral_content'],
            summary_data['engagement_metrics'],
            summary_data['urgency_signals'],
            summary_data['collection_date']
        ))

        conn.commit()
        conn.close()

    def _extract_viral_content(
            self,
            political_trends,
            economic_trends,
            account_activity=None):
        """Extract most viral content indicators"""
        viral_indicators = []

        # Check political trends for viral content
        for keyword, data in political_trends.items():
            if data.get(
                'engagement_score',
                    0) > 50:  # High engagement threshold
                viral_indicators.append(
                    f"{keyword}: {
                        data['engagement_score']} engagement")

        # Check economic trends for viral content
        for keyword, data in economic_trends.items():
            if data.get('engagement_score', 0) > 50:
                viral_indicators.append(
                    f"{keyword}: {
                        data['engagement_score']} engagement")

        # Check notable account activity
        if account_activity:
            for username, data in account_activity.items():
                if data.get(
                    'engagement_score',
                        0) > 75:  # Higher threshold for accounts
                    viral_indicators.append(
                        f"@{username}: {data['engagement_score']} engagement")

        return '; '.join(viral_indicators[:5])  # Top 5 viral indicators

    def _calculate_engagement_metrics(
            self,
            political_trends,
            economic_trends,
            account_activity=None):
        """Calculate overall engagement metrics"""
        total_engagement = 0
        total_tweets = 0

        for trends in [political_trends, economic_trends]:
            for data in trends.values():
                total_engagement += data.get('total_engagement', 0)
                total_tweets += data.get('tweet_count', 0)

        # Include account activity
        if account_activity:
            for data in account_activity.values():
                total_engagement += data.get('total_engagement', 0)
                total_tweets += data.get('tweet_count', 0)

        avg_engagement = total_engagement / max(total_tweets, 1)
        return f"Avg engagement: {
            avg_engagement:.1f}, Total tweets: {total_tweets}"

    def _calculate_urgency_score(
            self,
            political_trends,
            economic_trends,
            account_activity=None):
        """Calculate urgency score based on social media activity"""
        urgency_score = 0

        # Get thresholds from config
        if self.config_enabled:
            thresholds = self.social_config.get('urgency_thresholds', {})
            high_engagement = thresholds.get('high_engagement', 100)
            medium_engagement = thresholds.get('medium_engagement', 50)
            negative_sentiment = thresholds.get('negative_sentiment', -0.5)
            trending_velocity = thresholds.get('trending_velocity', 2.0)
        else:
            high_engagement, medium_engagement = 100, 50
            negative_sentiment, trending_velocity = -0.5, 2.0

        # Check for high engagement
        for trends in [political_trends, economic_trends]:
            for data in trends.values():
                if data.get('engagement_score', 0) > high_engagement:
                    urgency_score += 2
                elif data.get('engagement_score', 0) > medium_engagement:
                    urgency_score += 1

                # Check for negative sentiment spikes
                if data.get('sentiment_score', 0) < negative_sentiment:
                    urgency_score += 1

                # Check for rapid trending
                if data.get('trending_velocity', 0) > trending_velocity:
                    urgency_score += 1

        # Check notable account activity
        if account_activity:
            for data in account_activity.values():
                if data.get('engagement_score', 0) > high_engagement:
                    urgency_score += 2
                elif data.get('engagement_score', 0) > medium_engagement:
                    urgency_score += 1

        max_boost = self.social_config.get(
            'urgency_thresholds', {}).get(
            'max_urgency_boost', 5) if self.config_enabled else 5
        return min(urgency_score, max_boost)  # Cap at configured max

    def generate_social_media_summary(self):
        """Generate comprehensive social media analysis summary for weekly digest"""
        print("📱 Generating social media summary...")

        try:
            # Get weekly trends
            trends_data = self.get_weekly_trends()

            political_trends = trends_data.get('political_trends', {})
            economic_trends = trends_data.get('economic_trends', {})

            # Generate summary sections
            summary_parts = []

            # Political trends summary
            if political_trends:
                pol_summary = self._summarize_trend_category(
                    political_trends, "Political")
                summary_parts.append(pol_summary)

            # Economic trends summary
            if economic_trends:
                econ_summary = self._summarize_trend_category(
                    economic_trends, "Economic")
                summary_parts.append(econ_summary)

            # Overall analysis
            urgency_boost = self.get_urgency_boost_from_social()
            if urgency_boost > 0:
                summary_parts.append(
                    f"\n🎯 Social Media Urgency Indicator: +{urgency_boost} (elevated activity detected)")

            # Combine all parts
            if summary_parts:
                final_summary = "📱 **Social Media Trends Analysis (Past 7 Days)**\n\n" + "\n".join(
                    summary_parts)
                final_summary += f"\n\n📊 *Analysis Period: {
                    trends_data.get(
                        'analysis_period',
                        'Past 7 days')}*"
                return final_summary
            else:
                return self._generate_minimal_summary()

        except Exception as e:
            print(f"❌ Error generating social media summary: {e}")
            return self._generate_error_summary()

    def _summarize_trend_category(self, trends, category):
        """Summarize trends for a specific category"""
        if not trends:
            return f"📊 {category} Trends: No significant activity detected"

        # Sort by engagement score
        sorted_trends = sorted(
            trends.items(), key=lambda x: x[1].get(
                'engagement_score', 0), reverse=True)

        summary = f"📊 **{category} Trends:**\n"

        for keyword, data in sorted_trends[:3]:  # Top 3 trends
            tweet_count = data.get('tweet_count', 0)
            engagement = data.get('engagement_score', 0)
            sentiment = data.get('sentiment_score', 0)

            sentiment_emoji = "📈" if sentiment > 0 else "📉" if sentiment < -0.2 else "➡️"

            summary += f"• **{keyword}**: {tweet_count} posts, {engagement} avg engagement {sentiment_emoji}\n"

        return summary

    def _generate_minimal_summary(self):
        """Generate minimal summary when no trend data is available"""
        return """📱 **Social Media Trends Analysis (Past 7 Days)**

📊 Social media monitoring active - no significant anomalies detected in available data.
🔍 Continuous monitoring for emerging trends and sentiment shifts.
"""

    def _generate_error_summary(self):
        """Generate summary when there's an error"""
        return """📱 **Social Media Trends Analysis (Past 7 Days)**

⚠️  Social media analysis temporarily unavailable.
🔧 Systems will resume monitoring in next cycle.
"""

    def get_urgency_boost_from_social(self):
        """Calculate urgency boost based on recent social media activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get recent trends (last 7 days)
        cursor.execute('''
            SELECT urgency_signals, engagement_metrics
            FROM x_trends
            WHERE collection_date >= date('now', '-7 days')
            ORDER BY collection_date DESC LIMIT 1
        ''')

        trends = cursor.fetchall()
        conn.close()

        if not trends:
            return 0

        urgency_signals = trends[0][0] or 0

        # Calculate urgency boost
        urgency_boost = 0

        # High urgency signals
        if urgency_signals >= 4:
            urgency_boost += 2
        elif urgency_signals >= 2:
            urgency_boost += 1

        return min(urgency_boost, 3)  # Cap at +3 urgency points

    def _get_fallback_analysis(self):
        """Provide fallback analysis when API is unavailable"""
        return {
            'political_trends': {},
            'economic_trends': {},
            'analysis_period': f"{
                (
                    datetime.now() -
                    timedelta(
                        days=7)).strftime('%Y-%m-%d')} to {
                datetime.now().strftime('%Y-%m-%d')}",
            'collection_time': datetime.now().isoformat(),
            'status': 'limited_data',
            'message': 'Social media analysis limited due to API constraints'}


def main():
    """Test the X monitoring system"""
    monitor = XMonitor()

    print("🐦 Testing X/Twitter monitoring system...")
    print("=" * 50)

    # Test weekly trends analysis
    summary = monitor.generate_social_media_summary()
    print(summary)

    # Test urgency boost calculation
    boost = monitor.get_urgency_boost_from_social()
    print(f"\n🎯 Social Media Urgency Boost: +{boost} points")


if __name__ == "__main__":
    main()
