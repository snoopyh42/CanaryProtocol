#!/usr/bin/env python3
"""
Smart Feedback System for Canary Protocol
Allows users to provide feedback to improve AI accuracy over time
"""

import sqlite3
import json
import sys
from datetime import datetime
import argparse

class FeedbackSystem:
    def __init__(self, db_path="data/canary_protocol.db"):
        self.db_path = db_path
        # Ensure data directory exists
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_feedback_db()
    
    def init_feedback_db(self):
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
        
        cursor.execute('''
            SELECT urgency_score, summary 
            FROM digests 
            WHERE date LIKE ? 
            ORDER BY date DESC LIMIT 1
        ''', (f'{digest_date}%',))
        
        result = cursor.fetchone()
        if not result:
            print("❌ No digest found for that date")
            return
        
        predicted_urgency, summary = result
        
        print(f"🤖 AI Predicted Urgency: {predicted_urgency}/10")
        print(f"📄 Summary: {summary[:200]}...")
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
        
        feedback_type = "accurate" if abs(predicted_urgency - user_urgency) <= 1 else "inaccurate"
        
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
        self._update_intelligence_from_feedback(predicted_urgency, user_urgency, comments)
    
    def _update_intelligence_from_feedback(self, predicted, actual, comments):
        """Update AI intelligence based on user feedback"""
        from adaptive_intelligence import CanaryIntelligence
        
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
- Total Feedback Sessions: {feedback_count}
- Recent Accurate Predictions: {recent_feedback.get('accurate', 0)}
- Recent Inaccurate Predictions: {recent_feedback.get('inaccurate', 0)}

🔍 Error Analysis:
- False Positives Reported: {false_positive_count}
- Missed Signals Reported: {missed_signal_count}

📈 Learning Status:
{'🟢 IMPROVING' if avg_accuracy > 0.7 else '🟡 LEARNING' if avg_accuracy > 0.5 else '🔴 NEEDS ATTENTION'}

💡 Recommendation:
{'Continue current approach - accuracy is high!' if avg_accuracy > 0.8 else 
 'Provide more feedback to improve accuracy' if feedback_count < 10 else
 'Review false positives and missed signals for pattern improvements'}
"""

def main():
    parser = argparse.ArgumentParser(description='Canary Protocol Feedback System')
    parser.add_argument('--feedback', action='store_true', help='Provide feedback on latest digest')
    parser.add_argument('--false-positive', type=str, help='Report false positive headline')
    parser.add_argument('--missed-signal', type=str, help='Report missed important event')
    parser.add_argument('--summary', action='store_true', help='Show feedback summary')
    parser.add_argument('--date', type=str, help='Specific date for feedback (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    feedback_system = FeedbackSystem()
    
    if args.feedback:
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
        print("Use --help to see available options")

if __name__ == "__main__":
    main()
