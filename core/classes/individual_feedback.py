#!/usr/bin/env python3
"""
Individual Article Feedback System for Canary Protocol
Allows users to rate individual articles instead of entire digest
"""

import sqlite3
import json
import sys
import os
import argparse
from datetime import datetime
from urllib.parse import urlparse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from functions.utils import ensure_directory_exists, safe_db_operation
except ImportError:
    # Fallback for when running from different directory
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'functions'))
    from utils import ensure_directory_exists, safe_db_operation

try:
    from .base_db_class import BaseDBClass
except ImportError:
    try:
        from base_db_class import BaseDBClass
    except ImportError:
        # Fallback for when running from different directory
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from classes.base_db_class import BaseDBClass

class IndividualFeedbackSystem(BaseDBClass):
    def __init__(self, db_path="data/canary_protocol.db"):
        super().__init__(db_path)

    def init_db(self):
        """Initialize individual article feedback tracking tables"""
        def create_tables(cursor):
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS individual_article_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    digest_date TEXT,
                    article_url TEXT,
                    article_title TEXT,
                    article_summary TEXT,
                    ai_urgency_rating INTEGER,
                    user_urgency_rating INTEGER,
                    feedback_type TEXT,
                    feedback_notes TEXT,
                    timestamp TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_individual_feedback_date 
                ON individual_article_feedback(digest_date)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_individual_feedback_rating 
                ON individual_article_feedback(user_urgency_rating)
            ''')
        
        safe_db_operation(self.db_path, create_tables)

    def collect_individual_feedback(self, digest_date=None):
        """Collect feedback on individual articles from a digest"""
        if not digest_date:
            digest_date = datetime.now().strftime('%Y-%m-%d')

        print(f"📝 Starting individual article feedback collection...")
        print(f"📝 Individual Article Rating for {digest_date}")
        print("=" * 60)

        # Get the digest and its articles
        def get_digest_articles(cursor):
            # Try exact date match first
            cursor.execute('''
                SELECT top_headlines FROM weekly_digests 
                WHERE date = ? 
                ORDER BY date DESC LIMIT 1
            ''', (digest_date,))
            result = cursor.fetchone()
            
            # If no exact match, try date pattern matching for timestamps
            if not result:
                cursor.execute('''
                    SELECT top_headlines FROM weekly_digests 
                    WHERE date LIKE ? 
                    ORDER BY date DESC LIMIT 1
                ''', (f'{digest_date}%',))
                result = cursor.fetchone()
            
            # If still no match, try alternative date formats
            if not result:
                # Try "Month DD, YYYY" format
                from datetime import datetime
                try:
                    parsed_date = datetime.strptime(digest_date, '%Y-%m-%d')
                    alt_format = parsed_date.strftime('%B %d, %Y')
                    cursor.execute('''
                        SELECT top_headlines FROM weekly_digests 
                        WHERE date = ? 
                        ORDER BY date DESC LIMIT 1
                    ''', (alt_format,))
                    result = cursor.fetchone()
                except ValueError:
                    pass
            
            return result
        
        result = safe_db_operation(self.db_path, get_digest_articles)
        
        if not result:
            print("❌ No digest found for that date")
            return

        headlines_json = result[0]

        if not headlines_json:
            print("❌ No individual headlines found for this digest")
            return

        try:
            headlines = json.loads(headlines_json)
        except json.JSONDecodeError:
            print("❌ Error parsing headlines data")
            return

        # Check which articles have already been rated
        def get_rated_articles(cursor):
            cursor.execute('''
                SELECT article_url, user_urgency_rating FROM individual_article_feedback
                WHERE digest_date LIKE ?
            ''', (f'{digest_date}%',))
            return cursor.fetchall()
        
        rated_results = safe_db_operation(self.db_path, get_rated_articles) or []

        already_processed = {}
        for url, rating in rated_results:
            already_processed[url] = rating

        # Filter out already-processed articles
        unrated_headlines = []
        for article in headlines:
            url = article.get('url', '')
            if url not in already_processed:
                unrated_headlines.append(article)

        # Count rated vs irrelevant
        rated_count = sum(
            1 for rating in already_processed.values() if rating >= 0)
        irrelevant_count = sum(
            1 for rating in already_processed.values() if rating == -1)

        if not unrated_headlines:
            print(f"✅ All articles for {digest_date} have been processed!")
            print(f"📊 Rated articles: {rated_count}")
            print(f"⏭️  Irrelevant articles: {irrelevant_count}")
            print(f"📈 Total training data: {len(already_processed)} articles")
            print(f"💡 Run './canary feedback-summary' to see your ratings.")

            # Offer to show previously rated articles (only in interactive mode)
            try:
                show_rated = input(
                    "\n🔍 Would you like to see your previous ratings for this digest? (y/n): ").strip().lower()
                if show_rated in ['y', 'yes']:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    self._show_previous_ratings(digest_date, cursor)
                    conn.close()
            except EOFError:
                # Non-interactive mode, skip the prompt
                pass
            return

        # Get AI overall urgency from the digest (default to 5 if not found)
        ai_overall_urgency = 5  # Default value
        
        print(f"🤖 AI's Overall Digest Urgency: {ai_overall_urgency}/10")
        print(f"📰 Found {len(unrated_headlines)} unprocessed articles (out of {len(headlines)} total)")
        if already_processed:
            print(f"✅ Already processed: {len(already_processed)} articles ({rated_count} rated, {irrelevant_count} irrelevant)")
        print("=" * 60)

        rated_count = 0
        skipped_count = 0

        for i, article in enumerate(unrated_headlines, 1):
            title = article.get('title', 'No title')
            url = article.get('url', '')
            source = self._extract_source_from_url(url)

            print(f"\n📰 Article {i}/{len(unrated_headlines)}")
            print(f"🏷️  Source: {source}")
            print(f"📄 Title: {title}")
            print(f"🔗 URL: {url}")
            print("-" * 50)

            # Get user rating
            while True:
                try:
                    response = input(
                        "🧑 Your urgency rating (0-10, 's' = irrelevant, 'q' to quit): ").strip().lower()

                    if response == 'q':
                        print(
                            f"\n✅ Completed feedback on {rated_count} articles")
                        return
                    elif response == 's':
                        # Store skipped article as "irrelevant" training data
                        def store_irrelevant(cursor):
                            cursor.execute('''
                                INSERT INTO individual_article_feedback
                                (digest_date, article_url, article_title, article_source,
                                 user_urgency_rating, ai_overall_urgency, feedback_type,
                                 comments, feedback_date)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (digest_date, url, title, source, -1,
                                  ai_overall_urgency, "irrelevant",
                                  "User marked as irrelevant to urgency assessment",
                                  datetime.now().isoformat()))
                        
                        safe_db_operation(self.db_path, store_irrelevant)

                        skipped_count += 1
                        print("⏭️  Marked as irrelevant (valuable training data!)")
                        break

                    user_urgency = int(response)
                    if 0 <= user_urgency <= 10:
                        # Get optional comments
                        comments = input(
                            "💬 Comments (optional, Enter to skip): ").strip()

                        # Determine feedback type
                        feedback_type = self._determine_feedback_type(
                            user_urgency, ai_overall_urgency)

                        # Store feedback
                        def store_feedback(cursor):
                            cursor.execute('''
                                INSERT INTO individual_article_feedback
                                (digest_date, article_url, article_title, article_source,
                                 user_urgency_rating, ai_overall_urgency, feedback_type,
                                 comments, feedback_date)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (digest_date, url, title, source, user_urgency,
                                  ai_overall_urgency, feedback_type, comments,
                                  datetime.now().isoformat()))
                        
                        safe_db_operation(self.db_path, store_feedback)

                        rated_count += 1
                        print(f"✅ Rating saved for this article")
                        break
                    else:
                        print("Please enter a number between 0 and 10")
                except ValueError:
                    print(
                        "Please enter a valid number, 's' for irrelevant, or 'q' to quit")

        print(f"\n🎉 Feedback session complete!")
        print(f"✅ Rated: {rated_count} articles")
        print(f"⏭️  Marked irrelevant: {skipped_count} articles")
        print(f"📊 Total training data: {rated_count + skipped_count} articles")
        print(
            f"🧠 The AI will learn from both your ratings AND what you consider irrelevant!")

        # Train the AI with individual article feedback (higher priority than
        # digest feedback)
        if rated_count > 0 or skipped_count > 0:
            print(f"\n🚀 Training AI with your individual article feedback...")
            try:
                from .adaptive_intelligence import CanaryIntelligence
                intelligence = CanaryIntelligence()
                intelligence.learn_from_individual_articles(digest_date)
            except Exception as e:
                print(f"⚠️  AI training failed: {e}")
                print("📝 Your feedback was still saved for future training")

    def _extract_source_from_url(self, url):
        """Extract source name from URL"""
        if 'foxnews.com' in url:
            return 'Fox News'
        elif 'cnn.com' in url:
            return 'CNN'
        elif 'npr.org' in url:
            return 'NPR'
        elif 'bloomberg.com' in url:
            return 'Bloomberg'
        elif 'reuters.com' in url:
            return 'Reuters'
        elif 'wsj.com' in url:
            return 'Wall Street Journal'
        elif 'reddit.com' in url:
            if '/r/politics' in url:
                return 'Reddit r/politics'
            elif '/r/Conservative' in url:
                return 'Reddit r/Conservative'
            elif '/r/Economics' in url:
                return 'Reddit r/Economics'
            elif '/r/democrats' in url:
                return 'Reddit r/democrats'
            elif '/r/OutOfTheLoop' in url:
                return 'Reddit r/OutOfTheLoop'
            else:
                return 'Reddit'
        elif 'bbc.com' in url:
            return 'BBC'
        elif 'propublica.org' in url:
            return 'ProPublica'
        else:
            # Extract domain
            try:
                domain = urlparse(url).netloc
                return domain.replace('www.', '').title()
            except BaseException:
                return 'Unknown Source'

    def _determine_feedback_type(self, user_rating, ai_rating):
        """Determine if feedback indicates the article was over/under-rated"""
        if user_rating <= 3 and ai_rating >= 7:
            return "ai_overrated"  # AI thought digest was urgent, user thinks this article isn't
        elif user_rating >= 7 and ai_rating <= 3:
            return "ai_underrated"  # AI thought digest wasn't urgent, user thinks this article is
        elif abs(user_rating - ai_rating) <= 2:
            return "reasonable_match"
        else:
            return "significant_difference"

    def show_feedback_summary(self, days=7):
        """Show summary of recent individual article feedback"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                article_source,
                COUNT(*) as total_articles,
                COUNT(CASE WHEN user_urgency_rating >= 0 THEN 1 END) as rated_articles,
                COUNT(CASE WHEN user_urgency_rating = -1 THEN 1 END) as irrelevant_articles,
                AVG(CASE WHEN user_urgency_rating >= 0 THEN user_urgency_rating END) as avg_user_rating,
                feedback_type
            FROM individual_article_feedback
            WHERE feedback_date >= date('now', '-{} days')
            GROUP BY article_source, feedback_type
            ORDER BY article_source, feedback_type
        '''.format(days))

        results = cursor.fetchall()

        if not results:
            print(f"📊 No individual article feedback in the last {days} days")
            return

        print(f"📊 Individual Article Feedback Summary (Last {days} days)")
        print("=" * 60)

        current_source = None
        for source, total, rated, irrelevant, avg_user, feedback_type in results:
            if source != current_source:
                if current_source is not None:
                    print()
                print(f"📰 {source}:")
                current_source = source

            if feedback_type == "irrelevant":
                print(f"  ⏭️  {irrelevant} articles marked irrelevant")
            else:
                avg_text = f"(Avg rating: {avg_user:.1f})" if avg_user else ""
                print(f"  • {feedback_type}: {rated} articles {avg_text}")

        conn.close()

    def clear_all_feedback(self, confirm=False):
        """Clear all individual article feedback from the database"""
        if not confirm:
            print("⚠️  This will delete ALL individual article feedback data!")
            print("This action cannot be undone.")
            response = input(
                "Are you sure you want to continue? (type 'YES' to confirm): ")
            if response != 'YES':
                print("❌ Operation cancelled")
                return False

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get count before deletion
        cursor.execute('SELECT COUNT(*) FROM individual_article_feedback')
        count = cursor.fetchone()[0]

        if count == 0:
            print("📊 No individual article feedback to clear")
            conn.close()
            return True

        # Delete all feedback
        cursor.execute('DELETE FROM individual_article_feedback')
        conn.commit()
        conn.close()

        print(f"✅ Cleared {count} individual article feedback entries")
        return True

    def _show_previous_ratings(self, digest_date, cursor):
        """Show previous ratings for articles from this digest"""
        cursor.execute('''
            SELECT article_title, article_source, user_urgency_rating, comments, feedback_date
            FROM individual_article_feedback
            WHERE digest_date LIKE ?
            ORDER BY feedback_date
        ''', (f'{digest_date}%',))

        ratings = cursor.fetchall()
        if not ratings:
            print("📊 No previous ratings found")
            return

        print(f"\n📊 Your Previous Ratings for {digest_date}")
        print("=" * 60)

        for title, source, rating, comments, date in ratings:
            print(f"\n🏷️  {source}")
            print(f"📄 {title[:80]}{'...' if len(title) > 80 else ''}")
            if rating == -1:
                print(f"⏭️  Marked as: IRRELEVANT")
            else:
                print(f"🎯 Your Rating: {rating}/10")
            if comments:
                print(f"💬 Comment: {comments}")
            print(f"📅 Processed: {date.split('T')[0]}")
            print("-" * 40)


def main():
    parser = argparse.ArgumentParser(
        description='Individual Article Feedback System')
    parser.add_argument(
        '--date',
        '-d',
        help='Date for feedback (YYYY-MM-DD), defaults to today')
    parser.add_argument(
        '--summary',
        '-s',
        action='store_true',
        help='Show feedback summary')
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Days to include in summary (default: 7)')
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear all individual article feedback')

    args = parser.parse_args()

    feedback_system = IndividualFeedbackSystem()

    if args.clear:
        feedback_system.clear_all_feedback()
    elif args.summary:
        feedback_system.show_feedback_summary(args.days)
    else:
        feedback_system.collect_individual_feedback(args.date)


if __name__ == "__main__":
    main()
