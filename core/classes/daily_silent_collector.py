#!/usr/bin/env python3
"""
Daily Silent Data Collector for Canary Protocol
Collects data daily without analysis - feeds into weekly AI processing
"""

import sqlite3
import json
import os
import sys
import time
import random
import feedparser
import yfinance as yf
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../functions'))

try:
    from functions.utils import ensure_directory_exists
except ImportError:
    # Fallback for when running from different directory
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'functions'))
    from utils import ensure_directory_exists

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from .base_db_class import BaseDBClass
except ImportError:
    try:
        from base_db_class import BaseDBClass
    except ImportError:
        # Fallback for when running from different directory
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from classes.base_db_class import BaseDBClass

class SilentCollector(BaseDBClass):
    def __init__(self, db_path="data/canary_protocol.db"):
        super().__init__(db_path)

    def init_db(self):
        """Initialize daily collection tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_headlines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                headlines_json TEXT,
                headline_count INTEGER,
                urgency_keywords_found TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_economic (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                economic_json TEXT,
                high_concern_count INTEGER,
                vix_level REAL,
                trend_direction TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emergency_triggers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                trigger_type TEXT,
                trigger_data TEXT,
                urgency_level INTEGER,
                should_alert BOOLEAN
            )
        ''')

        conn.commit()
        conn.close()

    def collect_daily_data(self, verbose=False):
        """Silently collect daily data for later analysis"""
        if verbose:
            print(
                f"📊 Silent daily collection - {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        # Collect headlines using simple RSS feeds
        headlines = self._fetch_simple_news()
        headline_count = len(headlines)

        # Collect economic data using yfinance
        economic_data = self._fetch_simple_economic_data()

        # Basic urgency keyword detection (no AI)
        urgency_keywords = self._detect_urgency_keywords(headlines)

        # Economic trend analysis
        vix_level, trend_direction, high_concern_count = self._analyze_economic_trends(
            economic_data)

        # Store data
        self._store_daily_data(headlines, economic_data, urgency_keywords,
                               vix_level, trend_direction, high_concern_count)

        # Check for emergency triggers
        emergency_level = self._check_emergency_triggers(
            headlines, economic_data, urgency_keywords)

        collected_items = headline_count + len(economic_data)
        max_emergency_level = emergency_level

        if verbose:
            print(f"   📰 Headlines: {headline_count}")
            print(f"   📈 Economic indicators: {len(economic_data)}")
            print(f"   🚨 Urgency keywords: {len(urgency_keywords)}")
        # Log collection summary
        self.log_daily_collection(collected_items, max_emergency_level)

        # Create daily backup after data collection
        self.create_daily_backup(verbose)

        if verbose:
            print(f"✅ Daily collection complete: {collected_items} items, max emergency level: {max_emergency_level}")

        return max_emergency_level

    def _fetch_simple_news(self) -> List[Dict[str, str]]:
        """Fetch news from a few key RSS feeds"""
        headlines = []
        feeds = [
            "https://rss.cnn.com/rss/cnn_us.rss",
            "https://feeds.reuters.com/reuters/businessNews",
            "https://feeds.apnews.com/rss"
        ]
        
        for feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]:  # Limit to 5 per feed
                    headlines.append({
                        'title': entry.title,
                        'url': entry.link,
                        'source': feed_url
                    })
            except Exception as e:
                if hasattr(self, 'verbose') and self.verbose:
                    print(f"Error fetching {feed_url}: {e}")
                continue
        
        return headlines
    
    def _fetch_simple_economic_data(self) -> List[Dict[str, Any]]:
        """Fetch basic economic indicators"""
        economic_data = []
        
        try:
            # Get VIX data
            vix = yf.Ticker("^VIX")
            vix_data = vix.history(period="1d")
            if not vix_data.empty:
                vix_close = vix_data['Close'].iloc[-1]
                concern_level = 'high' if vix_close > 30 else 'medium' if vix_close > 20 else 'low'
                economic_data.append({
                    'indicator': 'VIX Fear Index',
                    'status': f'Level: {vix_close:.2f}',
                    'concern_level': concern_level
                })
        except Exception:
            pass
        
        try:
            # Get USD Index
            dxy = yf.Ticker("DX-Y.NYB")
            dxy_data = dxy.history(period="5d")
            if not dxy_data.empty and len(dxy_data) > 1:
                current = dxy_data['Close'].iloc[-1]
                previous = dxy_data['Close'].iloc[-2]
                change_pct = ((current - previous) / previous) * 100
                concern_level = 'high' if abs(change_pct) > 2 else 'medium' if abs(change_pct) > 1 else 'low'
                economic_data.append({
                    'indicator': 'USD Index',
                    'status': f'Change: {change_pct:.2f}%',
                    'concern_level': concern_level
                })
        except Exception:
            pass
            
        return economic_data

    def _detect_urgency_keywords(self, headlines):
        """Simple keyword detection without AI"""
        emergency_terms = [
            "martial law",
            "emergency powers",
            "constitutional crisis",
            "bank run",
            "currency collapse",
            "market crash",
            "civil unrest",
            "nationwide protests",
            "government shutdown",
            "supreme court overturns",
            "mass arrests",
            "declaration of emergency"]

        found_keywords = []
        all_text = " ".join([h.get('title', '') for h in headlines]).lower()

        for term in emergency_terms:
            if term in all_text:
                found_keywords.append(term)

        return found_keywords

    def _analyze_economic_trends(self, economic_data):
        """Basic economic trend analysis"""
        vix_level = 0
        high_concern_count = 0
        trend_direction = "stable"

        for indicator in economic_data:
            if indicator.get('concern_level') == 'high':
                high_concern_count += 1

            if indicator.get('indicator') == 'VIX Fear Index':
                try:
                    vix_text = indicator.get('status', '0')
                    vix_level = float(
                        vix_text.split(':')[1].split('-')[0].strip())
                except BaseException:
                    vix_level = 0

        # Determine trend direction
        if high_concern_count >= 3:
            trend_direction = "concerning"
        elif high_concern_count >= 2:
            trend_direction = "mixed"

        return vix_level, trend_direction, high_concern_count

    def _store_daily_data(self, headlines, economic_data, urgency_keywords,
                          vix_level, trend_direction, high_concern_count):
        """Store daily collection data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        today = datetime.now().strftime('%Y-%m-%d')

        # Store headlines
        cursor.execute('''
            INSERT OR REPLACE INTO daily_headlines
            (date, headlines_json, headline_count, urgency_keywords_found)
            VALUES (?, ?, ?, ?)
        ''', (today, json.dumps(headlines), len(headlines), json.dumps(urgency_keywords)))

        # Store economic data
        cursor.execute('''
            INSERT OR REPLACE INTO daily_economic
            (date, economic_json, high_concern_count, vix_level, trend_direction)
            VALUES (?, ?, ?, ?, ?)
        ''', (today, json.dumps(economic_data), high_concern_count, vix_level, trend_direction))

        conn.commit()
        conn.close()

    def _check_emergency_triggers(
            self,
            headlines,
            economic_data,
            urgency_keywords):
        """Check if emergency analysis should be triggered"""
        emergency_level = 0

        # High urgency keywords found
        if len(urgency_keywords) >= 3:
            emergency_level = max(emergency_level, 8)
        elif len(urgency_keywords) >= 2:
            emergency_level = max(emergency_level, 6)
        elif len(urgency_keywords) >= 1:
            emergency_level = max(emergency_level, 4)

        # Economic emergency indicators
        high_concern_count = sum(
            1 for e in economic_data if e.get('concern_level') == 'high')
        if high_concern_count >= 3:
            emergency_level = max(emergency_level, 7)

        # Store emergency trigger if significant
        if emergency_level >= 6:
            self._store_emergency_trigger(
                emergency_level, urgency_keywords, high_concern_count)

        return emergency_level

    def _store_emergency_trigger(self, level, keywords, economic_concerns):
        """Store emergency trigger for potential immediate analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        trigger_data = {
            'urgency_keywords': keywords,
            'economic_concerns': economic_concerns,
            'trigger_level': level
        }

        cursor.execute('''
            INSERT INTO emergency_triggers
            (date, trigger_type, trigger_data, urgency_level, should_alert)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), 'daily_check', json.dumps(trigger_data), level, level >= 8))

        conn.commit()
        conn.close()

    def get_weekly_summary(self, days_back=7):
        """Generate summary of collected data for weekly analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        start_date = (
            datetime.now() -
            timedelta(
                days=days_back)).strftime('%Y-%m-%d')

        # Get daily headlines
        cursor.execute('''
            SELECT date, headline_count, urgency_keywords_found
            FROM daily_headlines
            WHERE date >= ?
            ORDER BY date DESC
        ''', (start_date,))

        headlines_data = cursor.fetchall()

        # Get economic trends
        cursor.execute('''
            SELECT date, high_concern_count, vix_level, trend_direction
            FROM daily_economic
            WHERE date >= ?
            ORDER BY date DESC
        ''', (start_date,))

        economic_data = cursor.fetchall()

        # Get emergency triggers
        cursor.execute('''
            SELECT date, urgency_level, trigger_data
            FROM emergency_triggers
            WHERE date >= ?
            ORDER BY urgency_level DESC
        ''', (start_date,))

        emergency_data = cursor.fetchall()

        conn.close()

        # Compile summary
        total_urgency_keywords = 0
        max_vix = 0
        concerning_days = 0

        for date, count, keywords_json in headlines_data:
            try:
                keywords = json.loads(keywords_json)
                total_urgency_keywords += len(keywords)
            except BaseException:
                pass

        for date, concern_count, vix, trend in economic_data:
            max_vix = max(max_vix, vix or 0)
            if trend == "concerning":
                concerning_days += 1

        summary = {
            'collection_period': f"{start_date} to {datetime.now().strftime('%Y-%m-%d')}",
            'days_collected': len(headlines_data),
            'total_urgency_keywords': total_urgency_keywords,
            'max_vix_level': max_vix,
            'concerning_economic_days': concerning_days,
            'emergency_triggers': len(emergency_data),
            'highest_emergency_level': max([e[1] for e in emergency_data], default=0)
        }

        return summary

    def should_trigger_emergency_analysis(self):
        """Check if emergency analysis should be triggered"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check for recent high-level triggers
        cursor.execute('''
            SELECT COUNT(*) FROM emergency_triggers
            WHERE date >= date('now', '-1 day') AND urgency_level >= 8
        ''')

        high_triggers = cursor.fetchone()[0]
        conn.close()

        return high_triggers > 0

    def create_daily_backup(self, verbose=False):
        """Create automated daily backup"""
        try:
            import subprocess
            import os
            
            # Change to project root directory
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            if verbose:
                print("   💾 Creating daily backup...")
            
            # Run backup script
            result = subprocess.run(
                ['bash', 'scripts/backup_learning_data.sh'],
                cwd=script_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                if verbose:
                    print("   ✅ Daily backup created successfully")
                # Log backup creation
                ensure_directory_exists('logs')
                with open('logs/daily_collection.log', 'a') as f:
                    f.write(f"{datetime.now().isoformat()}: Daily backup created successfully\n")
            else:
                if verbose:
                    print(f"   ⚠️  Backup failed: {result.stderr}")
                # Log backup failure
                ensure_directory_exists('logs')
                with open('logs/daily_collection.log', 'a') as f:
                    f.write(f"{datetime.now().isoformat()}: Daily backup failed: {result.stderr}\n")
                    
        except Exception as e:
            if verbose:
                print(f"   ⚠️  Backup error: {e}")
            # Log backup error
            try:
                ensure_directory_exists('logs')
                with open('logs/daily_collection.log', 'a') as f:
                    f.write(f"{datetime.now().isoformat()}: Daily backup error: {e}\n")
            except:
                pass

    def log_daily_collection(self, items_collected: int, max_emergency_level: int):
        """Log daily collection summary"""
        try:
            ensure_directory_exists('logs')
            with open('logs/daily_collection.log', 'a') as f:
                f.write(f"{datetime.now().isoformat()}: Collected {items_collected} items, "
                       f"max emergency level: {max_emergency_level}\n")
        except Exception as e:
            print(f"Warning: Could not log daily collection: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Daily Silent Data Collector')
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show collection details')
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show weekly summary')
    parser.add_argument(
        '--check-emergency',
        action='store_true',
        help='Check for emergency triggers')
    
    # Handle positional arguments manually
    import sys
    command = 'collect'  # default
    if len(sys.argv) > 1 and not sys.argv[1].startswith('--'):
        command = sys.argv[1]
        # Remove the command from sys.argv so argparse doesn't see it
        sys.argv = [sys.argv[0]] + sys.argv[2:]

    args = parser.parse_args()

    collector = SilentCollector()

    if command == 'summary' or args.summary:
        summary = collector.get_weekly_summary()
        print("📊 WEEKLY DATA COLLECTION SUMMARY")
        print("=" * 40)
        print(f"Period: {summary['collection_period']}")
        print(f"Days collected: {summary['days_collected']}")
        print(f"Total urgency keywords: {summary['total_urgency_keywords']}")
        print(f"Max VIX level: {summary['max_vix_level']}")
        print(f"Concerning economic days: {summary['concerning_economic_days']}")
        print(f"Emergency triggers: {summary['emergency_triggers']}")
        print(f"Highest emergency level: {summary['highest_emergency_level']}")

    elif command == 'check-emergency' or args.check_emergency:
        should_trigger = collector.should_trigger_emergency_analysis()
        if should_trigger:
            print(" EMERGENCY ANALYSIS RECOMMENDED")
            print("High-urgency triggers detected in the last 24 hours.")
            print("Consider running: python3 canary_protocol.py --emergency")
        else:
            print(" No emergency triggers detected")

    else:  # Default to 'collect' command
        emergency_level = collector.collect_daily_data(verbose=args.verbose)
        if emergency_level >= 8 and not args.verbose:
            print(f" Emergency trigger detected: Level {emergency_level}")
            print("Consider running immediate analysis.")

if __name__ == "__main__":
    main()
