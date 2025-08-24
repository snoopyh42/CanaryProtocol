#!/usr/bin/env python3
"""
Database Migration System for Smart Canary Protocol
Handles version-controlled schema changes and database upgrades
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from functions.utils import log_info, log_error, safe_db_operation
except ImportError:
    # Fallback for when running from different directory
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'functions'))
    from utils import log_info, log_error, safe_db_operation


class DatabaseMigration:
    """Represents a single database migration"""
    
    def __init__(self, version: str, description: str, up_sql: str, down_sql: str = ""):
        self.version = version
        self.description = description
        self.up_sql = up_sql
        self.down_sql = down_sql
        self.timestamp = datetime.now().isoformat()


class MigrationManager:
    """Manages database schema migrations"""
    
    def __init__(self, db_path: str = "data/canary_protocol.db"):
        self.db_path = db_path
        self.migrations_dir = Path("migrations")
        self.migrations_dir.mkdir(exist_ok=True)
        self._ensure_migration_table()
    
    def _ensure_migration_table(self):
        """Create migrations tracking table if it doesn't exist"""
        def create_table(cursor):
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                checksum TEXT
            )
            """)
            return True
        
        safe_db_operation(self.db_path, create_table)
    
    def get_current_version(self) -> str:
        """Get the current database schema version"""
        def get_version(cursor):
            cursor.execute(
                "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1"
            )
            result = cursor.fetchone()
            return result[0] if result else "0.0.0"
        
        result = safe_db_operation(self.db_path, get_version)
        return result if result is not None else "0.0.0"
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        def get_migrations(cursor):
            cursor.execute("SELECT version FROM schema_migrations ORDER BY version")
            results = cursor.fetchall()
            return [row[0] for row in results]
        
        result = safe_db_operation(self.db_path, get_migrations)
        return result if result is not None else []
    
    def create_migration(self, version: str, description: str, up_sql: str, down_sql: str = ""):
        """Create a new migration file"""
        migration = DatabaseMigration(version, description, up_sql, down_sql)
        
        migration_file = self.migrations_dir / f"{version}_{description.replace(' ', '_').lower()}.json"
        
        migration_data = {
            "version": migration.version,
            "description": migration.description,
            "up_sql": migration.up_sql,
            "down_sql": migration.down_sql,
            "created_at": migration.timestamp
        }
        
        with open(migration_file, 'w') as f:
            json.dump(migration_data, f, indent=2)
        
        log_info(f"Created migration: {migration_file}")
        return migration_file
    
    def load_migrations(self) -> List[Dict[str, Any]]:
        """Load all migration files"""
        migrations = []
        
        for migration_file in sorted(self.migrations_dir.glob("*.json")):
            try:
                with open(migration_file, 'r') as f:
                    migration_data = json.load(f)
                    migrations.append(migration_data)
            except Exception as e:
                log_error(f"Failed to load migration {migration_file}: {e}")
        
        return migrations
    
    def apply_migration(self, migration: Dict[str, Any]) -> bool:
        """Apply a single migration"""
        try:
            def execute_migration(cursor):
                # Execute the migration SQL
                for statement in migration['up_sql'].split(';'):
                    statement = statement.strip()
                    if statement:
                        cursor.execute(statement)
                
                # Record the migration as applied
                cursor.execute(
                    "INSERT INTO schema_migrations (version, description) VALUES (?, ?)",
                    (migration['version'], migration['description'])
                )
                return True
            
            result = safe_db_operation(self.db_path, execute_migration)
            
            if result:
                log_info(f"Applied migration {migration['version']}: {migration['description']}")
                return True
            else:
                log_error(f"Failed to apply migration {migration['version']}")
                return False
            
        except Exception as e:
            log_error(f"Migration {migration['version']} failed: {e}")
            return False
    
    def rollback_migration(self, version: str) -> bool:
        """Rollback a specific migration"""
        migrations = self.load_migrations()
        migration = next((m for m in migrations if m['version'] == version), None)
        
        if not migration:
            log_error(f"Migration {version} not found")
            return False
        
        if not migration.get('down_sql'):
            log_error(f"Migration {version} has no rollback SQL")
            return False
        
        try:
            def execute_rollback(cursor):
                # Execute rollback SQL
                for statement in migration['down_sql'].split(';'):
                    statement = statement.strip()
                    if statement:
                        cursor.execute(statement)
                
                # Remove migration record
                cursor.execute("DELETE FROM schema_migrations WHERE version = ?", (version,))
                return True
            
            result = safe_db_operation(self.db_path, execute_rollback)
            
            if result:
                log_info(f"Rolled back migration {version}")
                return True
            else:
                log_error(f"Failed to rollback migration {version}")
                return False
            
        except Exception as e:
            log_error(f"Rollback of migration {version} failed: {e}")
            return False
    
    def migrate_up(self, target_version: str = None) -> bool:
        """Apply all pending migrations up to target version"""
        applied_migrations = set(self.get_applied_migrations())
        available_migrations = self.load_migrations()
        
        pending_migrations = [
            m for m in available_migrations 
            if m['version'] not in applied_migrations
        ]
        
        if target_version:
            pending_migrations = [
                m for m in pending_migrations 
                if m['version'] <= target_version
            ]
        
        if not pending_migrations:
            log_info("No pending migrations to apply")
            return True
        
        log_info(f"Applying {len(pending_migrations)} migrations...")
        
        for migration in sorted(pending_migrations, key=lambda x: x['version']):
            if not self.apply_migration(migration):
                log_error(f"Migration failed at version {migration['version']}")
                return False
        
        log_info("All migrations applied successfully")
        return True
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status"""
        current_version = self.get_current_version()
        applied_migrations = self.get_applied_migrations()
        available_migrations = self.load_migrations()
        
        pending_migrations = [
            m for m in available_migrations 
            if m['version'] not in applied_migrations
        ]
        
        return {
            "current_version": current_version,
            "applied_count": len(applied_migrations),
            "pending_count": len(pending_migrations),
            "applied_migrations": applied_migrations,
            "pending_migrations": [m['version'] for m in pending_migrations]
        }


def create_initial_migrations():
    """Create initial migration files for existing schema"""
    manager = MigrationManager()
    
    # Migration 1.0.0: Initial schema
    initial_schema = """
    CREATE TABLE IF NOT EXISTS weekly_digests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT UNIQUE,
        content TEXT,
        urgency_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS daily_headlines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        source TEXT,
        title TEXT,
        url TEXT,
        content TEXT,
        urgency_keywords TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS daily_economic (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        indicator TEXT,
        value REAL,
        change_percent REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS user_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        digest_date TEXT,
        rating INTEGER,
        comments TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS learning_patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pattern_type TEXT,
        pattern_data TEXT,
        confidence REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS keyword_performance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT UNIQUE,
        urgency_correlation REAL,
        frequency INTEGER DEFAULT 0,
        last_seen TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    manager.create_migration(
        "1.0.0",
        "Initial database schema",
        initial_schema,
        "DROP TABLE IF EXISTS weekly_digests; DROP TABLE IF EXISTS daily_headlines; DROP TABLE IF EXISTS daily_economic; DROP TABLE IF EXISTS user_feedback; DROP TABLE IF EXISTS learning_patterns; DROP TABLE IF EXISTS keyword_performance;"
    )
    
    # Migration 1.1.0: Add individual article feedback
    article_feedback_schema = """
    CREATE TABLE IF NOT EXISTS individual_article_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        digest_date TEXT,
        article_title TEXT,
        article_source TEXT,
        article_url TEXT,
        user_rating INTEGER,
        relevance_rating INTEGER,
        comments TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX IF NOT EXISTS idx_article_feedback_date ON individual_article_feedback(digest_date);
    CREATE INDEX IF NOT EXISTS idx_article_feedback_source ON individual_article_feedback(article_source)
    """
    
    manager.create_migration(
        "1.1.0",
        "Add individual article feedback system",
        article_feedback_schema,
        "DROP TABLE IF EXISTS individual_article_feedback;"
    )
    
    log_info("Initial migration files created")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Migration Manager")
    parser.add_argument("--create-initial", action="store_true", help="Create initial migration files")
    parser.add_argument("--migrate", action="store_true", help="Apply pending migrations")
    parser.add_argument("--status", action="store_true", help="Show migration status")
    parser.add_argument("--rollback", type=str, help="Rollback to specific version")
    
    args = parser.parse_args()
    
    if args.create_initial:
        create_initial_migrations()
    elif args.migrate:
        manager = MigrationManager()
        manager.migrate_up()
    elif args.status:
        manager = MigrationManager()
        status = manager.get_migration_status()
        print(f"Current version: {status['current_version']}")
        print(f"Applied migrations: {status['applied_count']}")
        print(f"Pending migrations: {status['pending_count']}")
        if status['pending_migrations']:
            print(f"Pending: {', '.join(status['pending_migrations'])}")
    elif args.rollback:
        manager = MigrationManager()
        manager.rollback_migration(args.rollback)
    else:
        parser.print_help()
