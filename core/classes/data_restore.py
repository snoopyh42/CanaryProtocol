#!/usr/bin/env python3
"""
Data Restore Manager for Smart Canary Protocol
Handles backup restoration with safety features and multiple format support
"""

import os
import sys
import shutil
import subprocess
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from abc import ABC

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from functions.utils import log_info, log_error, log_warning, ensure_directory_exists
    from classes.base_db_class import BaseDBClass
except ImportError:
    # Fallback imports for standalone execution
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'functions'))
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'classes'))
    from utils import log_info, log_error, log_warning, ensure_directory_exists
    from base_db_class import BaseDBClass


class DataRestoreManager(BaseDBClass):
    """
    Manages data restoration from backups with safety features
    """
    
    def __init__(self, db_path: str = "data/canary_protocol.db", backup_dir: str = "backups"):
        super().__init__(db_path)
        self.backup_dir = backup_dir
        ensure_directory_exists(self.backup_dir)
    
    def init_db(self):
        """Initialize database tables for restore operations"""
        def create_tables(cursor):
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS restore_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    backup_file TEXT NOT NULL,
                    restore_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    notes TEXT
                )
            ''')
        
        from functions.utils import safe_db_operation
        safe_db_operation(self.db_path, create_tables)
    
    def list_available_backups(self) -> List[Dict[str, any]]:
        """
        List all available backup files with metadata
        
        Returns:
            List of backup file dictionaries with name, path, size, timestamp
        """
        if not os.path.exists(self.backup_dir):
            log_warning(f"Backup directory not found: {self.backup_dir}")
            return []
        
        backup_files = []
        supported_extensions = ['.db', '.json', '.tar.gz', '.sql', '.zip']
        
        for file in os.listdir(self.backup_dir):
            if any(file.endswith(ext) for ext in supported_extensions):
                file_path = os.path.join(self.backup_dir, file)
                try:
                    file_stat = os.stat(file_path)
                    backup_files.append({
                        'name': file,
                        'path': file_path,
                        'size': file_stat.st_size,
                        'timestamp': file_stat.st_mtime,
                        'formatted_time': datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                        'type': self._detect_backup_type(file)
                    })
                except OSError as e:
                    log_error(f"Error reading backup file {file}: {e}")
        
        # Sort by timestamp, most recent first
        backup_files.sort(key=lambda x: x['timestamp'], reverse=True)
        return backup_files
    
    def _detect_backup_type(self, filename: str) -> str:
        """Detect backup type from filename"""
        if filename.endswith('.db'):
            return 'database'
        elif filename.endswith('.json'):
            return 'json_data'
        elif filename.endswith('.tar.gz'):
            return 'full_system'
        elif filename.endswith('.sql'):
            return 'sql_dump'
        elif filename.endswith('.zip'):
            return 'archive'
        else:
            return 'unknown'
    
    def create_safety_backup(self, target_path: str) -> Optional[str]:
        """
        Create a safety backup of current data before restore
        
        Args:
            target_path: Path to file being replaced
            
        Returns:
            Path to safety backup file or None if failed
        """
        if not os.path.exists(target_path):
            return None
        
        timestamp = int(time.time())
        safety_backup = f"{target_path}.safety_backup.{timestamp}"
        
        try:
            shutil.copy2(target_path, safety_backup)
            log_info(f"Safety backup created: {safety_backup}")
            return safety_backup
        except Exception as e:
            log_error(f"Failed to create safety backup: {e}")
            return None
    
    def restore_database(self, backup_file: str, confirm_callback=None) -> bool:
        """
        Restore database from backup file
        
        Args:
            backup_file: Path to backup file
            confirm_callback: Optional function to confirm restore operation
            
        Returns:
            True if restore successful, False otherwise
        """
        if not os.path.exists(backup_file):
            log_error(f"Backup file not found: {backup_file}")
            return False
        
        target_db = self.db_path
        
        # Confirmation check
        if confirm_callback and not confirm_callback(f"Restore database from {os.path.basename(backup_file)}?"):
            log_info("Database restore cancelled by user")
            return False
        
        try:
            # Create safety backup
            safety_backup = self.create_safety_backup(target_db)
            
            # Perform restore
            shutil.copy2(backup_file, target_db)
            
            # Log restore operation
            self._log_restore_operation(backup_file, 'database', 'success', 
                                      f"Safety backup: {safety_backup}" if safety_backup else None)
            
            log_info(f"Database restored successfully from {os.path.basename(backup_file)}")
            return True
            
        except Exception as e:
            log_error(f"Database restore failed: {e}")
            self._log_restore_operation(backup_file, 'database', 'failed', str(e))
            return False
    
    def restore_full_system(self, backup_file: str, confirm_callback=None) -> bool:
        """
        Restore full system from bundled tar.gz backup
        
        Args:
            backup_file: Path to tar.gz backup bundle
            confirm_callback: Optional function to confirm restore operation
            
        Returns:
            True if restore successful, False otherwise
        """
        if not os.path.exists(backup_file):
            log_error(f"Backup bundle not found: {backup_file}")
            return False
        
        if not backup_file.endswith('.tar.gz'):
            log_error(f"Invalid backup format for full system restore: {backup_file}")
            return False
        
        # Confirmation check
        if confirm_callback and not confirm_callback(f"Restore full system from {os.path.basename(backup_file)}? This will overwrite current data."):
            log_info("Full system restore cancelled by user")
            return False
        
        try:
            # Create safety backups before restore
            safety_backups = []
            if os.path.exists('data/canary_protocol.db'):
                safety_backup = self.create_safety_backup('data/canary_protocol.db')
                if safety_backup:
                    safety_backups.append(f"Database: {safety_backup}")
            
            # Extract bundle to temporary location
            temp_dir = f"temp_restore_{int(time.time())}"
            os.makedirs(temp_dir, exist_ok=True)
            
            result = subprocess.run(['tar', '-xzf', backup_file, '-C', temp_dir], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                log_error(f"Failed to extract backup bundle: {result.stderr}")
                shutil.rmtree(temp_dir, ignore_errors=True)
                return False
            
            # Find the extracted bundle directory
            bundle_dirs = [d for d in os.listdir(temp_dir) if d.startswith('canary_backup_')]
            if not bundle_dirs:
                log_error("No valid backup bundle found in archive")
                shutil.rmtree(temp_dir, ignore_errors=True)
                return False
            
            bundle_path = os.path.join(temp_dir, bundle_dirs[0])
            
            # Restore database
            db_source = os.path.join(bundle_path, 'data', 'canary_protocol.db')
            if os.path.exists(db_source):
                ensure_directory_exists('data')
                shutil.copy2(db_source, 'data/canary_protocol.db')
                log_info("Database restored from bundle")
            
            # Restore configuration files
            config_source = os.path.join(bundle_path, 'config')
            if os.path.exists(config_source):
                ensure_directory_exists('config')
                for config_file in os.listdir(config_source):
                    src = os.path.join(config_source, config_file)
                    dst = os.path.join('config', config_file)
                    shutil.copy2(src, dst)
                log_info("Configuration files restored from bundle")
            
            # Restore logs
            logs_source = os.path.join(bundle_path, 'logs')
            if os.path.exists(logs_source) and os.listdir(logs_source):
                ensure_directory_exists('logs')
                for log_file in os.listdir(logs_source):
                    src = os.path.join(logs_source, log_file)
                    dst = os.path.join('logs', log_file)
                    if os.path.isfile(src):
                        shutil.copy2(src, dst)
                    elif os.path.isdir(src):
                        if os.path.exists(dst):
                            shutil.rmtree(dst)
                        shutil.copytree(src, dst)
                log_info("Log files restored from bundle")
            
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            self._log_restore_operation(backup_file, 'full_system', 'success', 
                                      f"Safety backups: {'; '.join(safety_backups)}" if safety_backups else None)
            log_info(f"Complete system restored successfully from {os.path.basename(backup_file)}")
            return True
                
        except Exception as e:
            log_error(f"Full system restore failed: {e}")
            self._log_restore_operation(backup_file, 'full_system', 'failed', str(e))
            return False
    
    def restore_from_backup(self, backup_file: str, restore_type: str = 'auto', confirm_callback=None) -> bool:
        """
        Restore from backup file with automatic type detection
        
        Args:
            backup_file: Path to backup file
            restore_type: Type of restore ('auto', 'database', 'full_system')
            confirm_callback: Optional function to confirm restore operation
            
        Returns:
            True if restore successful, False otherwise
        """
        if restore_type == 'auto':
            restore_type = self._detect_backup_type(os.path.basename(backup_file))
        
        if restore_type == 'database':
            return self.restore_database(backup_file, confirm_callback)
        elif restore_type == 'full_system':
            return self.restore_full_system(backup_file, confirm_callback)
        else:
            log_error(f"Unsupported restore type: {restore_type}")
            return False
    
    def _log_restore_operation(self, backup_file: str, restore_type: str, status: str, notes: str = None):
        """Log restore operation to database"""
        def log_operation(cursor):
            cursor.execute('''
                INSERT INTO restore_history (timestamp, backup_file, restore_type, status, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (datetime.now().isoformat(), backup_file, restore_type, status, notes))
        
        from functions.utils import safe_db_operation
        safe_db_operation(self.db_path, log_operation)
    
    def get_restore_history(self, limit: int = 10) -> List[Dict[str, any]]:
        """
        Get recent restore history
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of restore history records
        """
        def get_history(cursor):
            cursor.execute('''
                SELECT timestamp, backup_file, restore_type, status, notes
                FROM restore_history
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()
        
        from functions.utils import safe_db_operation
        result = safe_db_operation(self.db_path, get_history)
        
        if result:
            return [
                {
                    'timestamp': row[0],
                    'backup_file': row[1],
                    'restore_type': row[2],
                    'status': row[3],
                    'notes': row[4]
                }
                for row in result
            ]
        return []
    
    def interactive_restore(self):
        """
        Interactive restore interface for command-line usage
        """
        print("🔄 Smart Canary Protocol - Data Restore")
        print("=" * 40)
        print()
        
        backups = self.list_available_backups()
        
        if not backups:
            print("❌ No backup files found in backup directory")
            print(f"   Backup directory: {self.backup_dir}")
            print("   Run a backup first using the 'Backup System' option")
            return False
        
        print("📁 Available Backups:")
        for i, backup in enumerate(backups[:10], 1):  # Show up to 10 most recent
            print(f"{i:2d}. {backup['name']} ({backup['size']} bytes, {backup['formatted_time']}) [{backup['type']}]")
        
        print()
        print("🔧 Restore Options:")
        print("1-10. Restore specific backup file")
        print("11.   Show restore history")
        print("12.   Return to main menu")
        print()
        
        try:
            choice = input("Select option (1-12): ").strip()
            
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= min(10, len(backups)):
                    selected_backup = backups[choice_num - 1]
                    
                    def confirm_restore(message):
                        return input(f"{message} (y/N): ").strip().lower() == 'y'
                    
                    success = self.restore_from_backup(selected_backup['path'], confirm_callback=confirm_restore)
                    if success:
                        print("✅ Restore completed successfully!")
                    else:
                        print("❌ Restore failed!")
                    return success
                
                elif choice_num == 11:
                    self._show_restore_history()
                    return True
                elif choice_num == 12:
                    return True
                else:
                    print("❌ Invalid option")
            else:
                print("❌ Invalid input")
                
        except EOFError:
            print("❌ Operation cancelled")
            return False
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled")
            return False
        
        return False
    
    def _show_restore_history(self):
        """Show restore history"""
        history = self.get_restore_history()
        
        if not history:
            print("📋 No restore history found")
            return
        
        print("📋 Recent Restore History:")
        print("-" * 60)
        for record in history:
            status_icon = "✅" if record['status'] == 'success' else "❌"
            print(f"{status_icon} {record['timestamp'][:19]} - {record['restore_type']}")
            print(f"   File: {os.path.basename(record['backup_file'])}")
            if record['notes']:
                print(f"   Notes: {record['notes']}")
            print()


if __name__ == "__main__":
    """Command-line interface for data restore"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart Canary Protocol - Data Restore Manager")
    parser.add_argument('--list', action='store_true', help='List available backups')
    parser.add_argument('--file', type=str, help='Restore from specific backup file')
    parser.add_argument('--type', type=str, choices=['auto', 'database', 'full_system'], 
                       default='auto', help='Restore type')
    parser.add_argument('--history', action='store_true', help='Show restore history')
    parser.add_argument('--interactive', action='store_true', help='Interactive restore mode')
    
    args = parser.parse_args()
    
    restore_manager = DataRestoreManager()
    
    if args.list:
        backups = restore_manager.list_available_backups()
        if backups:
            print("📁 Available Backups:")
            for backup in backups:
                print(f"  {backup['name']} ({backup['size']} bytes, {backup['formatted_time']}) [{backup['type']}]")
        else:
            print("❌ No backups found")
    
    elif args.file:
        def confirm_restore(message):
            return input(f"{message} (y/N): ").strip().lower() == 'y'
        
        backup_path = args.file if os.path.exists(args.file) else os.path.join('backups', args.file)
        success = restore_manager.restore_from_backup(backup_path, args.type, confirm_restore)
        if success:
            print("✅ Restore completed successfully!")
        else:
            print("❌ Restore failed!")
    
    elif args.history:
        restore_manager._show_restore_history()
    
    elif args.interactive:
        restore_manager.interactive_restore()
    
    else:
        restore_manager.interactive_restore()
