#!/usr/bin/env python3
"""
Backup Verification System for Smart Canary Protocol
Tests backup restoration regularly to ensure data integrity
"""

import sqlite3
import os
import shutil
import tempfile
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

try:
    from .utils import log_info, log_error, log_warning, safe_db_operation
    from .config_loader import load_config
except ImportError:
    from utils import log_info, log_error, log_warning, safe_db_operation
    from config_loader import load_config


class BackupVerificationManager:
    """Manages backup verification and restoration testing"""
    
    def __init__(self, db_path: str = "data/canary_protocol.db", config_path: str = "config/config.yaml"):
        self.db_path = db_path
        self.config = load_config(config_path)
        self.backup_dir = Path("data/backups")
        self.verification_dir = Path("data/verification")
        self.verification_dir.mkdir(exist_ok=True)
        
        # Verification settings
        self.verification_config = self.config.get("backup_verification", {
            "enabled": True,
            "schedule": "weekly",
            "max_backup_age_days": 30,
            "test_sample_size": 100,
            "integrity_checks": True
        })
    
    def calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            log_error(f"Failed to calculate checksum for {file_path}: {e}")
            return ""
    
    def get_database_schema(self, db_path: str) -> Dict[str, Any]:
        """Get database schema information"""
        def get_schema():
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            schema = {}
            for table in tables:
                # Get table info
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]
                
                schema[table] = {
                    "columns": [{"name": col[1], "type": col[2], "notnull": col[3], "pk": col[5]} for col in columns],
                    "row_count": row_count
                }
            
            conn.close()
            return schema
        
        return safe_db_operation(db_path, get_schema, default={})
    
    def verify_backup_integrity(self, backup_file: Path) -> Dict[str, Any]:
        """Verify the integrity of a backup file"""
        verification_result = {
            "backup_file": str(backup_file),
            "verified_at": datetime.now().isoformat(),
            "file_exists": backup_file.exists(),
            "file_size_bytes": 0,
            "checksum": "",
            "database_readable": False,
            "schema_valid": False,
            "data_sample_valid": False,
            "errors": []
        }
        
        if not backup_file.exists():
            verification_result["errors"].append("Backup file does not exist")
            return verification_result
        
        try:
            # Check file size and checksum
            verification_result["file_size_bytes"] = backup_file.stat().st_size
            verification_result["checksum"] = self.calculate_file_checksum(backup_file)
            
            # Test database readability
            try:
                conn = sqlite3.connect(str(backup_file))
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                conn.close()
                
                verification_result["database_readable"] = True
                verification_result["table_count"] = len(tables)
                
            except Exception as e:
                verification_result["errors"].append(f"Database not readable: {e}")
                return verification_result
            
            # Verify schema
            try:
                backup_schema = self.get_database_schema(str(backup_file))
                original_schema = self.get_database_schema(self.db_path)
                
                schema_matches = True
                for table_name, table_info in original_schema.items():
                    if table_name not in backup_schema:
                        schema_matches = False
                        verification_result["errors"].append(f"Missing table in backup: {table_name}")
                    else:
                        # Compare column structure
                        backup_columns = {col["name"]: col for col in backup_schema[table_name]["columns"]}
                        original_columns = {col["name"]: col for col in table_info["columns"]}
                        
                        if backup_columns != original_columns:
                            schema_matches = False
                            verification_result["errors"].append(f"Schema mismatch in table: {table_name}")
                
                verification_result["schema_valid"] = schema_matches
                verification_result["schema_comparison"] = {
                    "original_tables": len(original_schema),
                    "backup_tables": len(backup_schema),
                    "matching_tables": len(set(original_schema.keys()) & set(backup_schema.keys()))
                }
                
            except Exception as e:
                verification_result["errors"].append(f"Schema verification failed: {e}")
            
            # Sample data verification
            try:
                sample_valid = self.verify_data_sample(str(backup_file))
                verification_result["data_sample_valid"] = sample_valid
                
            except Exception as e:
                verification_result["errors"].append(f"Data sample verification failed: {e}")
            
        except Exception as e:
            verification_result["errors"].append(f"General verification error: {e}")
        
        verification_result["overall_valid"] = (
            verification_result["file_exists"] and
            verification_result["database_readable"] and
            verification_result["schema_valid"] and
            verification_result["data_sample_valid"] and
            len(verification_result["errors"]) == 0
        )
        
        return verification_result
    
    def verify_data_sample(self, backup_db_path: str) -> bool:
        """Verify a sample of data from the backup"""
        try:
            sample_size = self.verification_config.get("test_sample_size", 100)
            
            def check_sample():
                conn = sqlite3.connect(backup_db_path)
                cursor = conn.cursor()
                
                # Test key tables with sample data
                test_tables = ["weekly_digests", "daily_headlines", "user_feedback"]
                
                for table in test_tables:
                    try:
                        # Check if table exists and has data
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        
                        if count > 0:
                            # Sample some records
                            cursor.execute(f"SELECT * FROM {table} LIMIT {min(sample_size, count)}")
                            sample_records = cursor.fetchall()
                            
                            # Basic validation - ensure records have expected structure
                            if not sample_records:
                                return False
                            
                            # Check for null values in critical fields
                            cursor.execute(f"PRAGMA table_info({table})")
                            columns = cursor.fetchall()
                            
                            for record in sample_records[:10]:  # Check first 10 records
                                for i, col_info in enumerate(columns):
                                    if col_info[3] and record[i] is None:  # NOT NULL constraint violated
                                        return False
                    
                    except sqlite3.Error:
                        # Table might not exist, which is okay for some tables
                        continue
                
                conn.close()
                return True
            
            return safe_db_operation(backup_db_path, check_sample, default=False)
            
        except Exception as e:
            log_error(f"Data sample verification failed: {e}")
            return False
    
    def test_backup_restoration(self, backup_file: Path) -> Dict[str, Any]:
        """Test full restoration of a backup to a temporary location"""
        restoration_result = {
            "backup_file": str(backup_file),
            "tested_at": datetime.now().isoformat(),
            "restoration_successful": False,
            "temp_db_path": "",
            "data_integrity_verified": False,
            "performance_metrics": {},
            "errors": []
        }
        
        if not backup_file.exists():
            restoration_result["errors"].append("Backup file does not exist")
            return restoration_result
        
        # Create temporary database for restoration test
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_db_path = temp_db.name
            restoration_result["temp_db_path"] = temp_db_path
        
        try:
            start_time = datetime.now()
            
            # Copy backup to temporary location
            shutil.copy2(backup_file, temp_db_path)
            
            copy_time = datetime.now()
            restoration_result["performance_metrics"]["copy_time_seconds"] = (copy_time - start_time).total_seconds()
            
            # Verify the restored database
            verification_result = self.verify_backup_integrity(Path(temp_db_path))
            restoration_result["restoration_successful"] = verification_result["overall_valid"]
            restoration_result["data_integrity_verified"] = verification_result["data_sample_valid"]
            
            if verification_result["errors"]:
                restoration_result["errors"].extend(verification_result["errors"])
            
            # Test some basic operations on restored database
            try:
                def test_operations():
                    conn = sqlite3.connect(temp_db_path)
                    cursor = conn.cursor()
                    
                    # Test basic queries
                    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                    table_count = cursor.fetchone()[0]
                    
                    # Test a simple join if possible
                    cursor.execute("""
                        SELECT COUNT(*) FROM weekly_digests w 
                        LEFT JOIN user_feedback f ON w.date = f.digest_date
                    """)
                    join_result = cursor.fetchone()[0]
                    
                    conn.close()
                    return {"table_count": table_count, "join_test": join_result}
                
                operation_results = safe_db_operation(temp_db_path, test_operations, default={})
                restoration_result["operation_tests"] = operation_results
                
            except Exception as e:
                restoration_result["errors"].append(f"Operation test failed: {e}")
            
            end_time = datetime.now()
            restoration_result["performance_metrics"]["total_time_seconds"] = (end_time - start_time).total_seconds()
            restoration_result["performance_metrics"]["verification_time_seconds"] = (end_time - copy_time).total_seconds()
            
        except Exception as e:
            restoration_result["errors"].append(f"Restoration test failed: {e}")
        
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(temp_db_path):
                    os.unlink(temp_db_path)
            except Exception as e:
                log_warning(f"Failed to clean up temporary file {temp_db_path}: {e}")
        
        return restoration_result
    
    def run_backup_verification(self) -> Dict[str, Any]:
        """Run comprehensive backup verification"""
        verification_report = {
            "started_at": datetime.now().isoformat(),
            "backup_directory": str(self.backup_dir),
            "backups_found": 0,
            "backups_verified": 0,
            "backups_failed": 0,
            "verification_results": [],
            "summary": {}
        }
        
        if not self.backup_dir.exists():
            verification_report["error"] = "Backup directory does not exist"
            return verification_report
        
        # Find backup files
        backup_files = list(self.backup_dir.glob("*.db")) + list(self.backup_dir.glob("*.sql"))
        verification_report["backups_found"] = len(backup_files)
        
        if not backup_files:
            verification_report["error"] = "No backup files found"
            return verification_report
        
        # Filter backups by age
        max_age_days = self.verification_config.get("max_backup_age_days", 30)
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        
        recent_backups = []
        for backup_file in backup_files:
            backup_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
            if backup_time > cutoff_date:
                recent_backups.append(backup_file)
        
        log_info(f"Found {len(recent_backups)} recent backups to verify")
        
        # Verify each backup
        for backup_file in recent_backups:
            try:
                log_info(f"Verifying backup: {backup_file}")
                
                # Basic integrity check
                integrity_result = self.verify_backup_integrity(backup_file)
                
                # Full restoration test (for critical backups)
                restoration_result = None
                if backup_file.name.endswith('.db'):  # Only test SQLite backups
                    restoration_result = self.test_backup_restoration(backup_file)
                
                verification_result = {
                    "backup_file": str(backup_file),
                    "backup_age_days": (datetime.now() - datetime.fromtimestamp(backup_file.stat().st_mtime)).days,
                    "integrity_check": integrity_result,
                    "restoration_test": restoration_result,
                    "overall_status": "PASS" if integrity_result["overall_valid"] else "FAIL"
                }
                
                if restoration_result and not restoration_result["restoration_successful"]:
                    verification_result["overall_status"] = "FAIL"
                
                verification_report["verification_results"].append(verification_result)
                
                if verification_result["overall_status"] == "PASS":
                    verification_report["backups_verified"] += 1
                else:
                    verification_report["backups_failed"] += 1
                    
            except Exception as e:
                log_error(f"Failed to verify backup {backup_file}: {e}")
                verification_report["backups_failed"] += 1
                verification_report["verification_results"].append({
                    "backup_file": str(backup_file),
                    "overall_status": "ERROR",
                    "error": str(e)
                })
        
        # Generate summary
        verification_report["summary"] = {
            "success_rate": (verification_report["backups_verified"] / len(recent_backups) * 100) if recent_backups else 0,
            "oldest_verified_backup": None,
            "newest_verified_backup": None,
            "total_backup_size_mb": sum(b.stat().st_size for b in recent_backups) / (1024 * 1024)
        }
        
        # Find oldest and newest verified backups
        verified_backups = [r for r in verification_report["verification_results"] if r["overall_status"] == "PASS"]
        if verified_backups:
            ages = [r["backup_age_days"] for r in verified_backups]
            verification_report["summary"]["oldest_verified_backup"] = max(ages)
            verification_report["summary"]["newest_verified_backup"] = min(ages)
        
        verification_report["completed_at"] = datetime.now().isoformat()
        
        # Save verification report
        report_file = self.verification_dir / f"verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(verification_report, f, indent=2, default=str)
        
        log_info(f"Backup verification completed. {verification_report['backups_verified']}/{verification_report['backups_found']} backups verified successfully")
        log_info(f"Verification report saved to: {report_file}")
        
        return verification_report
    
    def get_verification_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get verification history for the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        history = []
        for report_file in sorted(self.verification_dir.glob("verification_report_*.json")):
            try:
                file_time = datetime.fromtimestamp(report_file.stat().st_mtime)
                if file_time > cutoff_date:
                    with open(report_file, 'r') as f:
                        report_data = json.load(f)
                        history.append(report_data)
            except Exception as e:
                log_warning(f"Failed to load verification report {report_file}: {e}")
        
        return history


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Backup Verification Manager")
    parser.add_argument("--verify", action="store_true", help="Run backup verification")
    parser.add_argument("--test-restore", type=str, help="Test restoration of specific backup file")
    parser.add_argument("--history", type=int, default=30, help="Show verification history (days)")
    parser.add_argument("--integrity-only", type=str, help="Check integrity of specific backup file")
    
    args = parser.parse_args()
    
    manager = BackupVerificationManager()
    
    if args.verify:
        results = manager.run_backup_verification()
        print(f"Verification completed: {results['backups_verified']}/{results['backups_found']} backups verified")
        print(f"Success rate: {results['summary']['success_rate']:.1f}%")
    elif args.test_restore:
        backup_file = Path(args.test_restore)
        result = manager.test_backup_restoration(backup_file)
        if result["restoration_successful"]:
            print(f"Restoration test PASSED for {backup_file}")
        else:
            print(f"Restoration test FAILED for {backup_file}")
            for error in result["errors"]:
                print(f"  Error: {error}")
    elif args.integrity_only:
        backup_file = Path(args.integrity_only)
        result = manager.verify_backup_integrity(backup_file)
        if result["overall_valid"]:
            print(f"Integrity check PASSED for {backup_file}")
        else:
            print(f"Integrity check FAILED for {backup_file}")
            for error in result["errors"]:
                print(f"  Error: {error}")
    elif args.history:
        history = manager.get_verification_history(args.history)
        print(f"Verification history (last {args.history} days):")
        for report in history[-5:]:  # Show last 5 reports
            print(f"  {report['started_at']}: {report['backups_verified']}/{report['backups_found']} verified")
    else:
        parser.print_help()
