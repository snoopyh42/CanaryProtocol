#!/usr/bin/env python3
"""
Data Archival System for Smart Canary Protocol
Automated cleanup and archival of old data with configurable retention policies
"""

import sqlite3
import os
import json
import shutil
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from .utils import log_info, log_error, log_warning, safe_db_operation
    from .config_loader import load_config
except ImportError:
    from utils import log_info, log_error, log_warning, safe_db_operation
    from config_loader import load_config


class DataArchivalManager:
    """Manages automated data archival and cleanup"""
    
    def __init__(self, db_path: str = "data/canary_protocol.db", config_path: str = "config/config.yaml"):
        self.db_path = db_path
        self.config = load_config(config_path)
        self.archive_dir = Path("data/archives")
        self.archive_dir.mkdir(exist_ok=True)
        
        # Default retention policies (days)
        self.retention_policies = {
            "daily_headlines": self.config.get("archival", {}).get("headlines_retention_days", 365),
            "daily_economic": self.config.get("archival", {}).get("economic_retention_days", 730),
            "weekly_digests": self.config.get("archival", {}).get("digests_retention_days", 1095),
            "user_feedback": self.config.get("archival", {}).get("feedback_retention_days", 1095),
            "individual_article_feedback": self.config.get("archival", {}).get("article_feedback_retention_days", 730),
            "learning_patterns": self.config.get("archival", {}).get("patterns_retention_days", 1095),
            "logs": self.config.get("archival", {}).get("logs_retention_days", 90)
        }
    
    def get_archival_candidates(self, table_name: str, date_column: str = "created_at") -> List[Dict[str, Any]]:
        """Get records that are candidates for archival"""
        retention_days = self.retention_policies.get(table_name, 365)
        cutoff_date = (datetime.now() - timedelta(days=retention_days)).isoformat()
        
        def get_candidates():
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(f"""
                SELECT * FROM {table_name} 
                WHERE {date_column} < ? 
                ORDER BY {date_column}
            """, (cutoff_date,))
            
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
        
        return safe_db_operation(self.db_path, get_candidates, default=[])
    
    def archive_table_data(self, table_name: str, date_column: str = "created_at") -> Dict[str, Any]:
        """Archive old data from a specific table"""
        candidates = self.get_archival_candidates(table_name, date_column)
        
        if not candidates:
            log_info(f"No data to archive from {table_name}")
            return {"archived_count": 0, "archive_file": None}
        
        # Create archive file
        archive_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_file = self.archive_dir / f"{table_name}_{archive_timestamp}.json.gz"
        
        try:
            # Write archived data to compressed JSON
            with gzip.open(archive_file, 'wt', encoding='utf-8') as f:
                json.dump({
                    "table": table_name,
                    "archived_at": datetime.now().isoformat(),
                    "record_count": len(candidates),
                    "retention_policy_days": self.retention_policies.get(table_name, 365),
                    "data": candidates
                }, f, indent=2, default=str)
            
            # Remove archived records from database
            record_ids = [record['id'] for record in candidates if 'id' in record]
            
            def delete_archived():
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                if record_ids:
                    placeholders = ','.join(['?'] * len(record_ids))
                    cursor.execute(f"DELETE FROM {table_name} WHERE id IN ({placeholders})", record_ids)
                
                conn.commit()
                deleted_count = cursor.rowcount
                conn.close()
                return deleted_count
            
            deleted_count = safe_db_operation(self.db_path, delete_archived, default=0)
            
            log_info(f"Archived {deleted_count} records from {table_name} to {archive_file}")
            
            return {
                "archived_count": deleted_count,
                "archive_file": str(archive_file),
                "retention_days": self.retention_policies.get(table_name, 365)
            }
            
        except Exception as e:
            log_error(f"Failed to archive {table_name}: {e}")
            return {"archived_count": 0, "archive_file": None, "error": str(e)}
    
    def archive_log_files(self) -> Dict[str, Any]:
        """Archive old log files"""
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return {"archived_count": 0, "archive_file": None}
        
        retention_days = self.retention_policies.get("logs", 90)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        old_log_files = []
        for log_file in logs_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                old_log_files.append(log_file)
        
        if not old_log_files:
            log_info("No old log files to archive")
            return {"archived_count": 0, "archive_file": None}
        
        # Create archive
        archive_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_file = self.archive_dir / f"logs_{archive_timestamp}.tar.gz"
        
        try:
            import tarfile
            
            with tarfile.open(archive_file, "w:gz") as tar:
                for log_file in old_log_files:
                    tar.add(log_file, arcname=log_file.name)
            
            # Remove original log files
            for log_file in old_log_files:
                log_file.unlink()
            
            log_info(f"Archived {len(old_log_files)} log files to {archive_file}")
            
            return {
                "archived_count": len(old_log_files),
                "archive_file": str(archive_file),
                "retention_days": retention_days
            }
            
        except Exception as e:
            log_error(f"Failed to archive log files: {e}")
            return {"archived_count": 0, "archive_file": None, "error": str(e)}
    
    def run_full_archival(self) -> Dict[str, Any]:
        """Run complete archival process for all tables and logs"""
        results = {
            "started_at": datetime.now().isoformat(),
            "tables": {},
            "logs": {},
            "total_archived": 0
        }
        
        # Archive database tables
        tables_to_archive = [
            ("daily_headlines", "created_at"),
            ("daily_economic", "created_at"),
            ("weekly_digests", "created_at"),
            ("user_feedback", "created_at"),
            ("individual_article_feedback", "created_at"),
            ("learning_patterns", "updated_at")
        ]
        
        for table_name, date_column in tables_to_archive:
            try:
                result = self.archive_table_data(table_name, date_column)
                results["tables"][table_name] = result
                results["total_archived"] += result.get("archived_count", 0)
            except Exception as e:
                log_error(f"Failed to archive {table_name}: {e}")
                results["tables"][table_name] = {"error": str(e), "archived_count": 0}
        
        # Archive log files
        try:
            log_result = self.archive_log_files()
            results["logs"] = log_result
            results["total_archived"] += log_result.get("archived_count", 0)
        except Exception as e:
            log_error(f"Failed to archive logs: {e}")
            results["logs"] = {"error": str(e), "archived_count": 0}
        
        results["completed_at"] = datetime.now().isoformat()
        
        # Save archival report
        report_file = self.archive_dir / f"archival_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        log_info(f"Archival completed. Total records archived: {results['total_archived']}")
        log_info(f"Archival report saved to: {report_file}")
        
        return results
    
    def get_archive_summary(self) -> Dict[str, Any]:
        """Get summary of archived data"""
        archive_files = list(self.archive_dir.glob("*.json.gz")) + list(self.archive_dir.glob("*.tar.gz"))
        
        summary = {
            "archive_directory": str(self.archive_dir),
            "total_archive_files": len(archive_files),
            "archives_by_type": {},
            "total_size_mb": 0,
            "oldest_archive": None,
            "newest_archive": None
        }
        
        if not archive_files:
            return summary
        
        # Analyze archive files
        archive_times = []
        for archive_file in archive_files:
            file_size_mb = archive_file.stat().st_size / (1024 * 1024)
            summary["total_size_mb"] += file_size_mb
            
            # Extract type from filename
            file_type = archive_file.stem.split('_')[0]
            if file_type not in summary["archives_by_type"]:
                summary["archives_by_type"][file_type] = {"count": 0, "size_mb": 0}
            
            summary["archives_by_type"][file_type]["count"] += 1
            summary["archives_by_type"][file_type]["size_mb"] += file_size_mb
            
            archive_times.append(archive_file.stat().st_mtime)
        
        if archive_times:
            summary["oldest_archive"] = datetime.fromtimestamp(min(archive_times)).isoformat()
            summary["newest_archive"] = datetime.fromtimestamp(max(archive_times)).isoformat()
        
        summary["total_size_mb"] = round(summary["total_size_mb"], 2)
        
        return summary
    
    def restore_from_archive(self, archive_file: str) -> Dict[str, Any]:
        """Restore data from an archive file (for emergency recovery)"""
        archive_path = Path(archive_file)
        
        if not archive_path.exists():
            return {"success": False, "error": "Archive file not found"}
        
        try:
            if archive_path.suffix == '.gz' and archive_path.stem.endswith('.json'):
                # JSON archive (database data)
                with gzip.open(archive_path, 'rt', encoding='utf-8') as f:
                    archive_data = json.load(f)
                
                table_name = archive_data["table"]
                records = archive_data["data"]
                
                def restore_records():
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    # Get table columns
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [col[1] for col in cursor.fetchall() if col[1] != 'id']
                    
                    # Insert records
                    placeholders = ','.join(['?' for _ in columns])
                    insert_sql = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
                    
                    restored_count = 0
                    for record in records:
                        try:
                            values = [record.get(col) for col in columns]
                            cursor.execute(insert_sql, values)
                            restored_count += 1
                        except sqlite3.IntegrityError:
                            # Skip duplicates
                            continue
                    
                    conn.commit()
                    conn.close()
                    return restored_count
                
                restored_count = safe_db_operation(self.db_path, restore_records, default=0)
                
                log_info(f"Restored {restored_count} records to {table_name} from {archive_file}")
                
                return {
                    "success": True,
                    "table": table_name,
                    "restored_count": restored_count,
                    "total_records": len(records)
                }
            
            else:
                return {"success": False, "error": "Unsupported archive format"}
                
        except Exception as e:
            log_error(f"Failed to restore from archive {archive_file}: {e}")
            return {"success": False, "error": str(e)}


def create_archival_config():
    """Create example archival configuration"""
    config_example = {
        "archival": {
            "enabled": True,
            "schedule": "weekly",  # daily, weekly, monthly
            "headlines_retention_days": 365,
            "economic_retention_days": 730,
            "digests_retention_days": 1095,
            "feedback_retention_days": 1095,
            "article_feedback_retention_days": 730,
            "patterns_retention_days": 1095,
            "logs_retention_days": 90,
            "compress_archives": True,
            "max_archive_size_mb": 100
        }
    }
    
    config_file = Path("config/archival_config_example.yaml")
    
    import yaml
    with open(config_file, 'w') as f:
        yaml.dump(config_example, f, default_flow_style=False, indent=2)
    
    log_info(f"Created archival configuration example: {config_file}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Data Archival Manager")
    parser.add_argument("--run", action="store_true", help="Run full archival process")
    parser.add_argument("--summary", action="store_true", help="Show archive summary")
    parser.add_argument("--table", type=str, help="Archive specific table")
    parser.add_argument("--restore", type=str, help="Restore from archive file")
    parser.add_argument("--create-config", action="store_true", help="Create example config")
    
    args = parser.parse_args()
    
    manager = DataArchivalManager()
    
    if args.create_config:
        create_archival_config()
    elif args.run:
        results = manager.run_full_archival()
        print(f"Archival completed. Total records archived: {results['total_archived']}")
    elif args.summary:
        summary = manager.get_archive_summary()
        print(f"Archive directory: {summary['archive_directory']}")
        print(f"Total archive files: {summary['total_archive_files']}")
        print(f"Total size: {summary['total_size_mb']} MB")
        if summary['archives_by_type']:
            print("Archives by type:")
            for archive_type, info in summary['archives_by_type'].items():
                print(f"  {archive_type}: {info['count']} files, {info['size_mb']:.2f} MB")
    elif args.table:
        result = manager.archive_table_data(args.table)
        print(f"Archived {result['archived_count']} records from {args.table}")
    elif args.restore:
        result = manager.restore_from_archive(args.restore)
        if result['success']:
            print(f"Restored {result['restored_count']} records")
        else:
            print(f"Restore failed: {result['error']}")
    else:
        parser.print_help()
