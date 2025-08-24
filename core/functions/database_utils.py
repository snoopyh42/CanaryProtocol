#!/usr/bin/env python3
"""
Database utilities for Canary Protocol
Handles database initialization, operations, and migrations
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
try:
    from .utils import log_error, log_info, create_directory
except ImportError:
    from utils import log_error, log_info, create_directory


def init_db(db_path: str = "data/canary_protocol.db") -> bool:
    """Initialize the database with required tables"""
    try:
        # Ensure data directory exists
        create_directory(os.path.dirname(db_path))
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        _create_weekly_digests_table(cursor)
        _create_feedback_table(cursor)
        _create_learning_data_table(cursor)
        _create_ab_test_table(cursor)
        
        conn.commit()
        conn.close()
        log_info("Database initialized successfully")
        return True
        
    except Exception as e:
        log_error(f"Database initialization error: {e}")
        return False


def _create_weekly_digests_table(cursor: sqlite3.Cursor) -> None:
    """Create weekly_digests table"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_digests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            urgency_score INTEGER NOT NULL,
            summary TEXT NOT NULL,
            tone_used TEXT,
            top_headlines TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')


def _create_feedback_table(cursor: sqlite3.Cursor) -> None:
    """Create feedback table"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            digest_date TEXT NOT NULL,
            feedback_type TEXT NOT NULL,
            rating INTEGER,
            comments TEXT,
            false_positive BOOLEAN DEFAULT 0,
            missed_signal BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')


def _create_learning_data_table(cursor: sqlite3.Cursor) -> None:
    """Create learning_data table for adaptive intelligence"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            urgency_weight REAL DEFAULT 1.0,
            source_reliability REAL DEFAULT 1.0,
            feedback_score REAL DEFAULT 0.0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')


def _create_ab_test_table(cursor: sqlite3.Cursor) -> None:
    """Create ab_tests table"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ab_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_name TEXT NOT NULL,
            variant TEXT NOT NULL,
            user_id TEXT,
            outcome TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')


def save_digest_to_db(date: str, urgency: int, summary: str, tone: str, 
                     headlines: str, db_path: str = "data/canary_protocol.db") -> bool:
    """Save digest record to database"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO weekly_digests (date, urgency_score, summary, tone_used, top_headlines)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, urgency, summary, tone, headlines))
        conn.commit()
        conn.close()
        log_info(f"Digest saved to database: {date}")
        return True
    except Exception as e:
        log_error(f"Database save error: {e}")
        return False


def get_recent_digests(limit: int = 10, db_path: str = "data/canary_protocol.db") -> List[Dict[str, Any]]:
    """Get recent digest records from database"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM weekly_digests 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
        
    except Exception as e:
        log_error(f"Database query error: {e}")
        return []


def save_feedback_to_db(digest_date: str, feedback_type: str, rating: Optional[int] = None,
                       comments: Optional[str] = None, false_positive: bool = False,
                       missed_signal: bool = False, db_path: str = "data/canary_protocol.db") -> bool:
    """Save user feedback to database"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO feedback (digest_date, feedback_type, rating, comments, 
                                false_positive, missed_signal)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (digest_date, feedback_type, rating, comments, false_positive, missed_signal))
        conn.commit()
        conn.close()
        log_info(f"Feedback saved for digest: {digest_date}")
        return True
    except Exception as e:
        log_error(f"Feedback save error: {e}")
        return False


def get_learning_data(db_path: str = "data/canary_protocol.db") -> Dict[str, Dict[str, float]]:
    """Get learning data for adaptive intelligence"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM learning_data')
        rows = cursor.fetchall()
        conn.close()
        
        learning_data = {}
        for row in rows:
            learning_data[row['keyword']] = {
                'urgency_weight': row['urgency_weight'],
                'source_reliability': row['source_reliability'],
                'feedback_score': row['feedback_score']
            }
        
        return learning_data
        
    except Exception as e:
        log_error(f"Learning data query error: {e}")
        return {}


def update_learning_data(keyword: str, urgency_weight: float, source_reliability: float,
                        feedback_score: float, db_path: str = "data/canary_protocol.db") -> bool:
    """Update or insert learning data for a keyword"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Use INSERT OR REPLACE to update existing or create new
        cursor.execute('''
            INSERT OR REPLACE INTO learning_data 
            (keyword, urgency_weight, source_reliability, feedback_score, last_updated)
            VALUES (?, ?, ?, ?, ?)
        ''', (keyword, urgency_weight, source_reliability, feedback_score, datetime.now()))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        log_error(f"Learning data update error: {e}")
        return False


def get_database_stats(db_path: str = "data/canary_protocol.db") -> Dict[str, int]:
    """Get database statistics"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Count records in each table
        tables = ['weekly_digests', 'feedback', 'learning_data', 'ab_tests']
        for table in tables:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            stats[table] = cursor.fetchone()[0]
        
        conn.close()
        return stats
        
    except Exception as e:
        log_error(f"Database stats error: {e}")
        return {}


def cleanup_old_data(days_to_keep: int = 90, db_path: str = "data/canary_protocol.db") -> bool:
    """Clean up old data beyond retention period"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Clean up old digests
        cursor.execute('''
            DELETE FROM weekly_digests 
            WHERE created_at < datetime('now', '-{} days')
        '''.format(days_to_keep))
        
        # Clean up old feedback
        cursor.execute('''
            DELETE FROM feedback 
            WHERE created_at < datetime('now', '-{} days')
        '''.format(days_to_keep))
        
        conn.commit()
        deleted_rows = cursor.rowcount
        conn.close()
        
        log_info(f"Cleaned up {deleted_rows} old database records")
        return True
        
    except Exception as e:
        log_error(f"Database cleanup error: {e}")
        return False


def get_feedback_summary(days: int = 7, db_path: str = "data/canary_protocol.db") -> Dict[str, Any]:
    """Get summary of user feedback over specified days"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get feedback counts by type
        cursor.execute('''
            SELECT feedback_type, COUNT(*) as count, AVG(rating) as avg_rating
            FROM feedback 
            WHERE digest_date >= date('now', '-{} days')
            GROUP BY feedback_type
        '''.format(days))
        
        feedback_data = {}
        for row in cursor.fetchall():
            feedback_data[row['feedback_type']] = {
                'count': row['count'],
                'avg_rating': row['avg_rating'] if row['avg_rating'] else 0
            }
        
        conn.close()
        return feedback_data
    except Exception as e:
        log_error(f"Error getting feedback summary: {e}")
        return {}
