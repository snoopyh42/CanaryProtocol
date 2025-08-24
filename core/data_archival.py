#!/usr/bin/env python3
"""
Data Archival System for Canary Protocol
Manages archiving of old data to keep the system performant
"""

import os
import sys
import sqlite3
import shutil
import argparse
from datetime import datetime, timedelta
import tarfile
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from functions.utils import log_info, log_error, ensure_directory_exists
except ImportError:
    # Fallback for when running from different directory
    sys.path.append(os.path.join(os.path.dirname(__file__), 'functions'))
    from utils import log_info, log_error, ensure_directory_exists

class DataArchivalSystem:
    def __init__(self, db_path="data/canary_protocol.db"):
        self.db_path = db_path
        self.archive_dir = "data/archives"
        ensure_directory_exists(self.archive_dir)

    def archive_old_data(self, days_old=90):
        """Archive data older than specified days"""
        print(f"📦 Archiving data older than {days_old} days...")
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cutoff_str = cutoff_date.strftime('%Y-%m-%d')
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count records to archive
            cursor.execute('''
                SELECT COUNT(*) FROM weekly_digests 
                WHERE date < ?
            ''', (cutoff_str,))
            digest_count = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT COUNT(*) FROM individual_article_feedback 
                WHERE digest_date < ?
            ''', (cutoff_str,))
            feedback_count = cursor.fetchone()[0]
            
            if digest_count == 0 and feedback_count == 0:
                print(f"✅ No data older than {days_old} days found")
                conn.close()
                return
            
            print(f"📊 Found {digest_count} digests and {feedback_count} feedback entries to archive")
            
            # Create archive file
            archive_filename = f"archive_{cutoff_date.strftime('%Y%m%d')}.tar.gz"
            archive_path = os.path.join(self.archive_dir, archive_filename)
            
            # Export data to JSON
            temp_dir = "temp_archive"
            ensure_directory_exists(temp_dir)
            
            # Export weekly digests
            cursor.execute('''
                SELECT * FROM weekly_digests 
                WHERE date < ?
            ''', (cutoff_str,))
            digests = cursor.fetchall()
            
            if digests:
                with open(os.path.join(temp_dir, 'weekly_digests.json'), 'w') as f:
                    json.dump([dict(zip([col[0] for col in cursor.description], row)) for row in digests], f, indent=2)
            
            # Export feedback
            cursor.execute('''
                SELECT * FROM individual_article_feedback 
                WHERE digest_date < ?
            ''', (cutoff_str,))
            feedback = cursor.fetchall()
            
            if feedback:
                with open(os.path.join(temp_dir, 'individual_feedback.json'), 'w') as f:
                    json.dump([dict(zip([col[0] for col in cursor.description], row)) for row in feedback], f, indent=2)
            
            # Create archive
            with tarfile.open(archive_path, 'w:gz') as tar:
                tar.add(temp_dir, arcname='.')
            
            # Remove archived data from database
            cursor.execute('DELETE FROM weekly_digests WHERE date < ?', (cutoff_str,))
            cursor.execute('DELETE FROM individual_article_feedback WHERE digest_date < ?', (cutoff_str,))
            
            conn.commit()
            conn.close()
            
            # Clean up temp directory
            shutil.rmtree(temp_dir)
            
            print(f"✅ Archived {digest_count} digests and {feedback_count} feedback entries")
            print(f"📁 Archive saved to: {archive_path}")
            log_info(f"Data archival completed: {digest_count} digests, {feedback_count} feedback entries archived to {archive_path}")
            
        except Exception as e:
            log_error(f"Data archival failed: {e}")
            print(f"❌ Archival failed: {e}")
            if 'conn' in locals():
                conn.close()

    def list_archives(self):
        """List available archives"""
        print("📁 Available Archives:")
        print("=" * 40)
        
        if not os.path.exists(self.archive_dir):
            print("No archives found")
            return
        
        archives = [f for f in os.listdir(self.archive_dir) if f.endswith('.tar.gz')]
        
        if not archives:
            print("No archives found")
            return
        
        for archive in sorted(archives):
            archive_path = os.path.join(self.archive_dir, archive)
            size = os.path.getsize(archive_path)
            mtime = datetime.fromtimestamp(os.path.getmtime(archive_path))
            
            print(f"  {archive}")
            print(f"    Size: {size:,} bytes")
            print(f"    Created: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            print()

def main():
    parser = argparse.ArgumentParser(description='Canary Protocol Data Archival System')
    parser.add_argument('--days', type=int, default=90, help='Archive data older than N days (default: 90)')
    parser.add_argument('--list', action='store_true', help='List available archives')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be archived without doing it')
    
    args = parser.parse_args()
    
    archival = DataArchivalSystem()
    
    if args.list:
        archival.list_archives()
    else:
        if args.dry_run:
            print("🔍 DRY RUN MODE - No changes will be made")
        archival.archive_old_data(args.days)

if __name__ == "__main__":
    main()
