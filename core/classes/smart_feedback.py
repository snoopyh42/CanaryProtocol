#!/usr/bin/env python3
"""
Smart Feedback System for Canary Protocol
Allows users to provide feedback to improve AI accuracy over time
"""

import sqlite3
import json
import os
import sys
import argparse
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from functions.utils import ensure_directory_exists
except ImportError:
    # Fallback for when running from different directory
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'functions'))
    from utils import ensure_directory_exists

try:
    from .base_db_class import BaseDBClass
except ImportError:
    try:
        from base_db_class import BaseDBClass
    except ImportError:
        # Fallback for when running from different directory
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from classes.base_db_class import BaseDBClass

class FeedbackSystem(BaseDBClass):
    def __init__(self, db_path="data/canary_protocol.db"):
        super().__init__(db_path)

    def init_db(self):
        """Initialize feedback tracking tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                digest_date TEXT,
                predicted_urgency INTEGER,
                user_rated_urgency INTEGER,
                feedback_type TEXT,
                comments TEXT,
                feedback_date TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS false_positives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                headline TEXT,
                predicted_urgency INTEGER,
                actual_urgency INTEGER,
                reason TEXT,
                date_reported TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS missed_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_description TEXT,
                should_have_detected TEXT,
                actual_urgency INTEGER,
                date_reported TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def collect_feedback(self, digest_date=None):
        """Interactive feedback collection"""
        if not digest_date:
            digest_date = datetime.now().strftime('%Y-%m-%d')

        print(f"📝 Canary Protocol Feedback for {digest_date}")
        print("=" * 50)

        # Get the latest digest
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if feedback already exists for this digest
        cursor.execute('''
            SELECT id, user_rated_urgency, feedback_type, comments, feedback_date
            FROM user_feedback
            WHERE digest_date = ?
        ''', (digest_date,))

        existing_feedback = cursor.fetchone()
        if existing_feedback:
            print(f"✅ You have already provided feedback for {digest_date}!")
            print(f"🎯 Your Rating: {existing_feedback[1]}/10")
            print(f"📝 Feedback Type: {existing_feedback[2]}")
            if existing_feedback[3]:
                print(f"💬 Your Comment: {existing_feedback[3]}")
            print(f"📅 Provided: {existing_feedback[4]}")
            print()

            # Ask if they want to see the digest again
            try:
                show_digest = input(
                    "🔍 Would you like to see the digest summary again? (y/n): ").lower().strip()
            except EOFError:
                show_digest = "n"
            if show_digest == 'y':
                cursor.execute('''
                    SELECT urgency_score, summary
                    FROM weekly_digests
                    WHERE date LIKE ?
                    ORDER BY date DESC LIMIT 1
                ''', (f'{digest_date}%',))

                result = cursor.fetchone()
                if result:
                    predicted_urgency, summary = result
                    print(f"\n🤖 AI Predicted Urgency: {predicted_urgency}/10")
                    print(f"📄 Digest Summary:")
                    print("=" * 80)
                    print(summary)
                    print("=" * 80)

            conn.close()
            return

        cursor.execute('''
            SELECT urgency_score, summary
            FROM weekly_digests
            WHERE date LIKE ?
            ORDER BY date DESC LIMIT 1
        ''', (f'{digest_date}%',))

        result = cursor.fetchone()
        if not result:
            print("❌ No digest found for that date")
            conn.close()
            return

        predicted_urgency, summary = result

        print(f"🤖 AI Predicted Urgency: {predicted_urgency}/10")
        print(f"📄 Full Digest Summary:")
        print("=" * 80)
        print(summary)
        print("=" * 80)
        print()

        # Collect user feedback
        while True:
            try:
                user_urgency = int(input("🧑 Your urgency rating (0-10): "))
                if 0 <= user_urgency <= 10:
                    break
                print("Please enter a number between 0 and 10")
            except ValueError:
                print("Please enter a valid number")

        feedback_type = "accurate" if abs(
            predicted_urgency - user_urgency) <= 1 else "inaccurate"

        comments = input("💬 Additional comments (optional): ")

        # Store feedback
        cursor.execute('''
            INSERT INTO user_feedback
            (digest_date, predicted_urgency, user_rated_urgency, feedback_type, comments, feedback_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (digest_date, predicted_urgency, user_urgency, feedback_type, comments, datetime.now().isoformat()))

        conn.commit()
        conn.close()

        print("✅ Feedback recorded! The AI will learn from this.")

        # Update intelligence based on feedback
        self._update_intelligence_from_feedback(
            predicted_urgency, user_urgency, comments)

    def _update_intelligence_from_feedback(self, predicted, actual, comments):
        """Update AI intelligence based on user feedback"""
        from .adaptive_intelligence import CanaryIntelligence

        intelligence = CanaryIntelligence()
        conn = sqlite3.connect(intelligence.db_path)
        cursor = conn.cursor()

        # Update prediction accuracy
        accuracy = 1.0 - abs(predicted - actual) / 10.0

        cursor.execute('''
            UPDATE prediction_tracking
            SET actual_urgency = ?, prediction_accuracy = ?
            WHERE prediction_date LIKE ? AND predicted_urgency = ?
            ORDER BY prediction_date DESC LIMIT 1
        ''', (actual, accuracy, f'{datetime.now().strftime("%Y-%m-%d")}%', predicted))

        # Learn from comments
        if comments and len(comments) > 10:
            self._extract_learning_from_comments(comments, actual, cursor)

        conn.commit()
        conn.close()

    def _extract_learning_from_comments(self, comments, urgency, cursor):
        """Extract learning insights from user comments"""
        comments_lower = comments.lower()

        # Look for mentioned keywords that user found important
        important_phrases = [
            "should have noticed", "missed", "important", "critical",
            "overreacted", "not urgent", "false alarm"
        ]

        for phrase in important_phrases:
            if phrase in comments_lower:
                # Extract context keywords around the phrase
                words = comments_lower.split()
                phrase_index = ' '.join(words).find(phrase)

                if phrase_index != -1:
                    # Store as learning pattern
                    pattern_data = {
                        'user_insight': phrase,
                        'context': comments[:100],
                        'corrected_urgency': urgency
                    }

                    cursor.execute('''
                        INSERT INTO learning_patterns
                        (pattern_type, pattern_data, effectiveness_score, last_updated)
                        VALUES (?, ?, ?, ?)
                    ''', ('user_feedback', json.dumps(pattern_data), urgency / 10.0, datetime.now().isoformat()))

    def report_false_positive(self, headline, reason):
        """Report a false positive detection"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO false_positives
            (headline, reason, date_reported)
            VALUES (?, ?, ?)
        ''', (headline, reason, datetime.now().isoformat()))

        conn.commit()
        conn.close()

        print("✅ False positive reported. AI will learn to avoid this pattern.")

    def report_missed_signal(self, event_description, details):
        """Report an important event that was missed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO missed_signals
            (event_description, should_have_detected, date_reported)
            VALUES (?, ?, ?)
        ''', (event_description, details, datetime.now().isoformat()))

        conn.commit()
        conn.close()

        print("✅ Missed signal reported. AI will learn to detect similar patterns.")

    def get_feedback_summary(self):
        """Generate summary of feedback and learning progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Accuracy trends
        cursor.execute('''
            SELECT AVG(prediction_accuracy), COUNT(*)
            FROM prediction_tracking
            WHERE prediction_accuracy IS NOT NULL
        ''')
        accuracy_data = cursor.fetchone()
        avg_accuracy = accuracy_data[0] or 0
        feedback_count = accuracy_data[1] or 0

        # Recent feedback
        cursor.execute('''
            SELECT feedback_type, COUNT(*)
            FROM user_feedback
            WHERE date(feedback_date) >= date('now', '-30 days')
            GROUP BY feedback_type
        ''')
        recent_feedback = dict(cursor.fetchall())

        # False positives
        cursor.execute('SELECT COUNT(*) FROM false_positives')
        false_positive_count = cursor.fetchone()[0]

        # Missed signals
        cursor.execute('SELECT COUNT(*) FROM missed_signals')
        missed_signal_count = cursor.fetchone()[0]

        conn.close()

        return f"""
🎯 FEEDBACK & LEARNING SUMMARY
==============================

📊 Overall Performance:
- Prediction Accuracy: {avg_accuracy:.1%}
- Total Feedback Entries: {feedback_count}
- Recent Accurate Predictions: {recent_feedback.get('accurate', 0)}
- Recent Inaccurate Predictions: {recent_feedback.get('inaccurate', 0)}

🔍 Error Tracking:
- False Positives Reported: {false_positive_count}
- Missed Signals Reported: {missed_signal_count}

📈 Learning Status: {'🟢 ACTIVE' if feedback_count > 0 else '🟡 WAITING FOR FEEDBACK'}
"""

    def clear_all_feedback(self, confirm=False):
        """Clear all digest-level feedback from the database"""
        if not confirm:
            print("⚠️  This will delete ALL digest-level feedback data!")
            print(
                "This includes user_feedback, false_positives, missed_signals, and prediction_tracking")
            print("This action cannot be undone.")
            response = input(
                "Are you sure you want to continue? (type 'YES' to confirm): ")
            if response != 'YES':
                print("❌ Operation cancelled")
                return False

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get counts before deletion
        tables_to_clear = [
            'user_feedback',
            'false_positives',
            'missed_signals',
            'prediction_tracking']
        total_count = 0

        for table in tables_to_clear:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                total_count += count
                print(f"  📊 {table}: {count} entries")
            except BaseException:
                print(f"  ❓ {table}: Table not found")

        if total_count == 0:
            print("📊 No digest-level feedback to clear")
            conn.close()
            return True

        print(f"\n🗑️  Total entries to delete: {total_count}")

        # Delete from all feedback tables
        for table in tables_to_clear:
            try:
                cursor.execute(f'DELETE FROM {table}')
                print(f"  ✅ Cleared {table}")
            except Exception as e:
                print(f"  ⚠️  Could not clear {table}: {e}")

        conn.commit()
        conn.close()

        print(f"\n✅ Cleared all digest-level feedback data")
        return True


def main():
    parser = argparse.ArgumentParser(
        description='Canary Protocol Feedback System')
    parser.add_argument(
        '--feedback',
        action='store_true',
        help='Provide feedback on latest digest')
    parser.add_argument(
        '--false-positive',
        type=str,
        help='Report false positive headline')
    parser.add_argument(
        '--missed-signal',
        type=str,
        help='Report missed important event')
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show feedback summary')
    parser.add_argument(
        '--date',
        type=str,
        help='Specific date for feedback (YYYY-MM-DD)')
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear all digest-level feedback')

    args = parser.parse_args()

    feedback_system = FeedbackSystem()

    if args.clear:
        feedback_system.clear_all_feedback()
    elif args.feedback:
        feedback_system.collect_feedback(args.date)
    elif args.false_positive:
        reason = input("Why was this a false positive? ")
        feedback_system.report_false_positive(args.false_positive, reason)
    elif args.missed_signal:
        details = input("What should the system have detected? ")
        feedback_system.report_missed_signal(args.missed_signal, details)
    elif args.summary:
        print(feedback_system.get_feedback_summary())
    else:
        # Default to collecting feedback
        feedback_system.collect_feedback(args.date)


if __name__ == "__main__":
    main()
