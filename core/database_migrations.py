#!/usr/bin/env python3
"""
Database Migration System for Canary Protocol
Manages database schema changes and data migrations
"""

import os
import sys
import sqlite3
import argparse
from datetime import datetime
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from functions.utils import log_info, log_error, safe_db_operation
except ImportError:
    # Fallback for when running from different directory
    sys.path.append(os.path.join(os.path.dirname(__file__), 'functions'))
    from utils import log_info, log_error, safe_db_operation

class DatabaseMigrationSystem:
    def __init__(self, db_path="data/canary_protocol.db"):
        self.db_path = db_path
        self.migrations = [
            {
                'version': 1,
                'name': 'initial_schema',
                'description': 'Create initial database schema',
                'sql': self._migration_v1
            },
            {
                'version': 2,
                'name': 'add_feedback_tables',
                'description': 'Add individual article feedback tables',
                'sql': self._migration_v2
            },
            {
                'version': 3,
                'name': 'fix_column_names',
                'description': 'Standardize column names (user_rating -> user_urgency_rating)',
                'sql': self._migration_v3
            }
        ]

    def _migration_v1(self, cursor):
        """Initial schema creation"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_digests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE,
                top_headlines TEXT,
                urgency_score INTEGER,
                ai_analysis TEXT,
                economic_data TEXT,
                social_sentiment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keyword_performance (
                keyword TEXT PRIMARY KEY,
                accuracy_score REAL DEFAULT 0.5,
                total_occurrences INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    def _migration_v2(self, cursor):
        """Add individual article feedback tables"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS individual_article_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                digest_date TEXT,
                article_url TEXT,
                article_title TEXT,
                article_source TEXT,
                user_urgency_rating INTEGER,
                ai_overall_urgency INTEGER,
                feedback_type TEXT,
                comments TEXT,
                feedback_date TEXT,
                FOREIGN KEY (digest_date) REFERENCES weekly_digests(date)
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_article_feedback_date 
            ON individual_article_feedback(digest_date)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_article_feedback_source 
            ON individual_article_feedback(article_source)
        ''')

    def _migration_v3(self, cursor):
        """Fix column naming inconsistencies"""
        # Check if old column exists
        cursor.execute("PRAGMA table_info(individual_article_feedback)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'user_rating' in columns and 'user_urgency_rating' not in columns:
            # Rename column
            cursor.execute('''
                ALTER TABLE individual_article_feedback 
                RENAME COLUMN user_rating TO user_urgency_rating
            ''')
            log_info("Renamed user_rating column to user_urgency_rating")

    def get_current_version(self):
        """Get current database version"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create migrations table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS migrations (
                    version INTEGER PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('SELECT MAX(version) FROM migrations')
            result = cursor.fetchone()
            version = result[0] if result[0] is not None else 0
            
            conn.close()
            return version
        except Exception as e:
            log_error(f"Failed to get database version: {e}")
            return 0

    def apply_migration(self, migration):
        """Apply a single migration"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            print(f"📝 Applying migration {migration['version']}: {migration['name']}")
            
            # Run the migration
            migration['sql'](cursor)
            
            # Record the migration
            cursor.execute('''
                INSERT INTO migrations (version, name, description)
                VALUES (?, ?, ?)
            ''', (migration['version'], migration['name'], migration['description']))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Migration {migration['version']} applied successfully")
            log_info(f"Applied migration {migration['version']}: {migration['name']}")
            
        except Exception as e:
            log_error(f"Migration {migration['version']} failed: {e}")
            print(f"❌ Migration {migration['version']} failed: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            raise

    def migrate(self):
        """Run all pending migrations"""
        current_version = self.get_current_version()
        pending_migrations = [m for m in self.migrations if m['version'] > current_version]
        
        if not pending_migrations:
            print("✅ Database is up to date")
            return
        
        print(f"🔧 Current database version: {current_version}")
        print(f"📈 Latest version: {max(m['version'] for m in self.migrations)}")
        print(f"🔄 Applying {len(pending_migrations)} migrations...")
        
        for migration in pending_migrations:
            self.apply_migration(migration)
        
        print("🎉 All migrations completed successfully!")

    def status(self):
        """Show migration status"""
        current_version = self.get_current_version()
        latest_version = max(m['version'] for m in self.migrations)
        
        print("🔧 Database Migration Status")
        print("=" * 40)
        print(f"Current Version: {current_version}")
        print(f"Latest Version: {latest_version}")
        
        if current_version < latest_version:
            pending = len([m for m in self.migrations if m['version'] > current_version])
            print(f"Pending Migrations: {pending}")
        else:
            print("Status: ✅ Up to date")
        
        print("\nAvailable Migrations:")
        for migration in self.migrations:
            status = "✅ Applied" if migration['version'] <= current_version else "⏳ Pending"
            print(f"  v{migration['version']}: {migration['name']} - {status}")
            print(f"    {migration['description']}")

    def rollback(self, target_version):
        """Rollback to a specific version (limited support)"""
        current_version = self.get_current_version()
        
        if target_version >= current_version:
            print(f"❌ Cannot rollback to version {target_version} (current: {current_version})")
            return
        
        print(f"⚠️  Rollback functionality is limited")
        print(f"🔄 Rolling back from v{current_version} to v{target_version}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Remove migration records
            cursor.execute('DELETE FROM migrations WHERE version > ?', (target_version,))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Rollback completed to version {target_version}")
            print("⚠️  Note: Schema changes are not automatically reverted")
            
        except Exception as e:
            log_error(f"Rollback failed: {e}")
            print(f"❌ Rollback failed: {e}")

def main():
    parser = argparse.ArgumentParser(description='Canary Protocol Database Migration System')
    parser.add_argument('--migrate', action='store_true', help='Run pending migrations')
    parser.add_argument('--status', action='store_true', help='Show migration status')
    parser.add_argument('--rollback', type=int, help='Rollback to specific version')
    
    args = parser.parse_args()
    
    migration_system = DatabaseMigrationSystem()
    
    if args.status:
        migration_system.status()
    elif args.rollback is not None:
        migration_system.rollback(args.rollback)
    elif args.migrate:
        migration_system.migrate()
    else:
        print("🔧 Database Migration System")
        print("Available commands:")
        print("  --migrate  : Run pending migrations")
        print("  --status   : Show migration status")
        print("  --rollback : Rollback to version")

if __name__ == "__main__":
    main()
