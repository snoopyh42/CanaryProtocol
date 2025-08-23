"""
Public Social Media Monitoring Module
Scrapes public data sources to avoid API rate limits
Alternative to X/Twitter API with free, reliable data sources
"""

import requests
import json
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from collections import Counter
import sqlite3
import time

class PublicSocialMonitor:
    """
    Monitor social media trends using public data sources
    No API keys required, no rate limits
    """
    
    def __init__(self, db_path="data/canary_protocol.db"):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self._setup_tables()
    
    def _setup_tables(self):
        """Setup database tables for public social monitoring"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS public_social_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                trend_topic TEXT,
                trend_score INTEGER,
                sentiment_indicators TEXT,
                collection_date TEXT,
                raw_data TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_weekly_social_analysis(self):
        """Get comprehensive social media analysis from public sources"""
        print("🌐 Analyzing public social media data...")
        
        analysis = {
            'reddit_political_trends': self._get_reddit_trends(),
            'reddit_economic_trends': self._get_reddit_economic_trends(),
            'news_social_mentions': self._get_news_social_mentions(),
            'trending_topics': self._get_general_trending_topics(),
            'analysis_date': datetime.now().isoformat()
        }
        
        # Calculate urgency score from public data
        urgency_score = self._calculate_public_urgency_score(analysis)
        analysis['urgency_boost'] = min(urgency_score, 3)  # Cap at +3
        
        # Generate summary
        summary = self._generate_public_social_summary(analysis)
        analysis['summary'] = summary
        
        # Store in database
        self._store_public_analysis(analysis)
        
        return analysis
    
    def _get_reddit_trends(self):
        """Get political trends from Reddit (already in config)"""
        print("  📊 Analyzing Reddit political trends...")
        
        subreddits = ['politics', 'democrats', 'conservative', 'OutOfTheLoop']
        all_trends = []
        
        for subreddit in subreddits:
            try:
                url = f'https://www.reddit.com/r/{subreddit}/hot.json?limit=20'
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get('data', {}).get('children', [])
                    
                    for post in posts:
                        post_data = post.get('data', {})
                        trend_item = {
                            'title': post_data.get('title', ''),
                            'score': post_data.get('score', 0),
                            'comments': post_data.get('num_comments', 0),
                            'subreddit': subreddit,
                            'url': post_data.get('url', ''),
                            'created': post_data.get('created_utc', 0)
                        }
                        all_trends.append(trend_item)
                        
                    print(f"    ✅ r/{subreddit}: {len(posts)} posts")
                else:
                    print(f"    ⚠️  r/{subreddit}: HTTP {response.status_code}")
                    
                time.sleep(1)  # Be respectful to Reddit
                
            except Exception as e:
                print(f"    ❌ r/{subreddit}: {e}")
                continue
        
        # Sort by engagement score (score + comments)
        all_trends.sort(key=lambda x: x['score'] + x['comments'], reverse=True)
        
        return all_trends[:20]  # Top 20 trending political topics
    
    def _get_reddit_economic_trends(self):
        """Get economic trends from Reddit"""
        print("  💰 Analyzing Reddit economic trends...")
        
        economic_subreddits = ['economics', 'investing', 'StockMarket', 'personalfinance']
        economic_trends = []
        
        for subreddit in economic_subreddits:
            try:
                url = f'https://www.reddit.com/r/{subreddit}/hot.json?limit=15'
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get('data', {}).get('children', [])
                    
                    for post in posts:
                        post_data = post.get('data', {})
                        economic_trends.append({
                            'title': post_data.get('title', ''),
                            'score': post_data.get('score', 0),
                            'comments': post_data.get('num_comments', 0),
                            'subreddit': subreddit
                        })
                        
                    print(f"    ✅ r/{subreddit}: {len(posts)} posts")
                else:
                    print(f"    ⚠️  r/{subreddit}: HTTP {response.status_code}")
                    
                time.sleep(1)
                
            except Exception as e:
                print(f"    ❌ r/{subreddit}: {e}")
                continue
        
        economic_trends.sort(key=lambda x: x['score'] + x['comments'], reverse=True)
        return economic_trends[:15]
    
    def _get_news_social_mentions(self):
        """Extract social media mentions from news headlines"""
        print("  📰 Analyzing news for social media mentions...")
        
        # Keywords that indicate social media activity/trends
        social_indicators = [
            'viral', 'trending', 'twitter', 'social media', 'hashtag', 'meme',
            'online', 'internet', 'digital', 'facebook', 'instagram', 'tiktok',
            'goes viral', 'sparks outrage', 'online backlash', 'social reaction'
        ]
        
        mentions = []
        
        # Check current news sources for social media mentions
        try:
            # Use existing RSS feeds from config
            rss_feeds = [
                'https://feeds.reuters.com/reuters/businessNews',
                'https://www.politico.com/rss/politics08.xml',
                'https://feeds.npr.org/1001/rss.xml'
            ]
            
            for feed_url in rss_feeds:
                try:
                    response = self.session.get(feed_url, timeout=10)
                    if response.status_code == 200:
                        # Simple text search for social media indicators
                        content = response.text.lower()
                        
                        for indicator in social_indicators:
                            if indicator in content:
                                # Count occurrences
                                count = content.count(indicator)
                                if count > 0:
                                    mentions.append({
                                        'indicator': indicator,
                                        'count': count,
                                        'source': feed_url.split('/')[2]  # Extract domain
                                    })
                        
                        print(f"    ✅ {feed_url.split('/')[2]}: Scanned")
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"    ⚠️  {feed_url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"    ❌ News scanning error: {e}")
        
        return mentions
    
    def _get_general_trending_topics(self):
        """Get general trending topics from multiple sources"""
        print("  🔥 Gathering general trending topics...")
        
        trending_topics = []
        
        # Method 1: Extract topics from Reddit titles
        try:
            response = self.session.get('https://www.reddit.com/r/trending/.json?limit=10', timeout=10)
            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', {}).get('children', [])
                for post in posts:
                    title = post.get('data', {}).get('title', '')
                    if title:
                        trending_topics.append({
                            'topic': title,
                            'source': 'reddit_trending',
                            'score': post.get('data', {}).get('score', 0)
                        })
                print("    ✅ Reddit trending: Collected")
        except:
            print("    ⚠️  Reddit trending: Not available")
        
        # Method 2: Extract keywords from high-engagement posts
        political_keywords = [
            'trump', 'biden', 'congress', 'supreme court', 'election', 'voting',
            'democrat', 'republican', 'senate', 'house', 'president', 'governor'
        ]
        
        economic_keywords = [
            'economy', 'inflation', 'recession', 'stock market', 'unemployment',
            'fed', 'federal reserve', 'interest rates', 'gdp', 'dollar', 'crypto'
        ]
        
        # Count keyword mentions across all collected data
        keyword_mentions = Counter()
        
        # This would be populated from the Reddit data we already collected
        # For now, return a basic structure
        
        return trending_topics[:10]
    
    def _calculate_public_urgency_score(self, analysis):
        """Calculate urgency score from public social media data"""
        urgency_score = 0
        
        # High engagement Reddit posts (+1 point each, max 2)
        political_trends = analysis.get('reddit_political_trends', [])
        high_engagement_posts = [p for p in political_trends if (p['score'] + p['comments']) > 1000]
        urgency_score += min(len(high_engagement_posts), 2)
        
        # Economic concern indicators (+1 point, max 1)
        economic_trends = analysis.get('reddit_economic_trends', [])
        recession_posts = [p for p in economic_trends if any(word in p['title'].lower() 
                         for word in ['recession', 'crash', 'crisis', 'inflation', 'collapse'])]
        if recession_posts:
            urgency_score += 1
        
        # Social media mentions in news (+1 point if high volume)
        social_mentions = analysis.get('news_social_mentions', [])
        total_mentions = sum(m['count'] for m in social_mentions)
        if total_mentions > 10:
            urgency_score += 1
        
        return urgency_score
    
    def _generate_public_social_summary(self, analysis):
        """Generate summary from public social media analysis"""
        summary_parts = []
        
        # Political trends summary
        political_trends = analysis.get('reddit_political_trends', [])
        if political_trends:
            top_political = political_trends[:3]
            summary_parts.append("🗳️ **Top Political Discussions:**")
            for i, trend in enumerate(top_political):
                engagement = trend['score'] + trend['comments']
                title = trend['title'][:80] + "..." if len(trend['title']) > 80 else trend['title']
                summary_parts.append(f"  {i+1}. {title} ({engagement:,} engagement)")
        
        # Economic trends summary
        economic_trends = analysis.get('reddit_economic_trends', [])
        if economic_trends:
            top_economic = economic_trends[:3]
            summary_parts.append("\n💰 **Top Economic Discussions:**")
            for i, trend in enumerate(top_economic):
                engagement = trend['score'] + trend['comments']
                title = trend['title'][:80] + "..." if len(trend['title']) > 80 else trend['title']
                summary_parts.append(f"  {i+1}. {title} ({engagement:,} engagement)")
        
        # Social media mention indicators
        social_mentions = analysis.get('news_social_mentions', [])
        if social_mentions:
            total_mentions = sum(m['count'] for m in social_mentions)
            summary_parts.append(f"\n📱 **Social Media Activity**: {total_mentions} mentions in news sources")
        
        # Urgency indicator
        urgency_boost = analysis.get('urgency_boost', 0)
        if urgency_boost > 0:
            summary_parts.append(f"\n🎯 **Public Sentiment Urgency**: +{urgency_boost} boost detected")
        
        if not summary_parts:
            return "📊 **Public Social Media Analysis**: No significant trends detected in public data sources."
        
        final_summary = "📊 **Public Social Media Analysis (Past 7 Days)**\n\n" + "\n".join(summary_parts)
        final_summary += f"\n\n📅 *Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
        
        return final_summary
    
    def _store_public_analysis(self, analysis):
        """Store public social media analysis in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store main analysis
        cursor.execute('''
            INSERT INTO public_social_trends 
            (source, trend_topic, trend_score, sentiment_indicators, collection_date, raw_data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            'public_social_monitor',
            'weekly_analysis',
            analysis.get('urgency_boost', 0),
            json.dumps(analysis.get('news_social_mentions', [])),
            datetime.now().strftime('%Y-%m-%d'),
            json.dumps(analysis, default=str)
        ))
        
        conn.commit()
        conn.close()
    
    def get_urgency_boost_from_public_data(self):
        """Get urgency boost from recent public social media analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT trend_score FROM public_social_trends 
            WHERE source = 'public_social_monitor' 
            AND collection_date >= date('now', '-7 days')
            ORDER BY collection_date DESC LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 0

def main():
    """Test public social media monitoring"""
    monitor = PublicSocialMonitor()
    
    print("🌐 Testing Public Social Media Monitoring")
    print("=" * 50)
    
    analysis = monitor.get_weekly_social_analysis()
    
    print("\n" + "="*50)
    print("SUMMARY:")
    print("="*50)
    print(analysis['summary'])
    
    urgency_boost = analysis.get('urgency_boost', 0)
    print(f"\n🎯 Urgency Boost: +{urgency_boost} points")

if __name__ == "__main__":
    main()
