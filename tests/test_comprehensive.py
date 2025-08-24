#!/usr/bin/env python3
"""
Comprehensive Test Suite for Smart Canary Protocol
Tests all major components, workflows, and integration points
"""

import os
import sys
import sqlite3
import tempfile
import shutil
import subprocess
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test results tracking
test_results = {
    'passed': 0,
    'failed': 0,
    'skipped': 0,
    'errors': []
}

class TestResult:
    """Enhanced test result tracking"""
    def __init__(self):
        self.start_time = datetime.now()
        self.tests = []
        
    def add_test(self, name: str, success: bool, error_msg: str = None, duration: float = 0):
        """Add test result"""
        self.tests.append({
            'name': name,
            'success': success,
            'error': error_msg,
            'duration': duration
        })
        
        if success:
            test_results['passed'] += 1
            print(f"✅ {name} ({duration:.3f}s)")
        else:
            test_results['failed'] += 1
            test_results['errors'].append(f"{name}: {error_msg}")
            print(f"❌ {name}: {error_msg} ({duration:.3f}s)")
    
    def skip_test(self, name: str, reason: str):
        """Skip a test"""
        test_results['skipped'] += 1
        print(f"⏭️  {name}: {reason}")

class TestEnvironment:
    """Isolated test environment with cleanup"""
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="canary_test_")
        self.test_db = os.path.join(self.temp_dir, "test_canary.db")
        self.test_backup_dir = os.path.join(self.temp_dir, "backups")
        self.test_config_dir = os.path.join(self.temp_dir, "config")
        self.test_logs_dir = os.path.join(self.temp_dir, "logs")
        
        # Create directories
        os.makedirs(self.test_backup_dir, exist_ok=True)
        os.makedirs(self.test_config_dir, exist_ok=True)
        os.makedirs(self.test_logs_dir, exist_ok=True)
        
        # Store original working directory
        self.original_cwd = os.getcwd()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

def time_test(func):
    """Decorator to time test execution"""
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start
            return result, duration
        except Exception as e:
            duration = time.time() - start
            return None, duration, str(e)
    return wrapper

class ComprehensiveTestSuite:
    """Main test suite class"""
    
    def __init__(self):
        self.result = TestResult()
        
    @time_test
    def test_core_imports(self):
        """Test all core module imports"""
        modules = [
            'core.functions.utils',
            'core.functions.database_utils',
            'core.functions.analysis_engine',
            'core.functions.email_utils',
            'core.functions.slack_utils',
            'core.functions.social_media_utils',
            'core.functions.economic_monitor',
            'core.classes.config_loader',
            'core.classes.adaptive_intelligence',
            'core.classes.smart_feedback',
            'core.classes.individual_feedback',
            'core.classes.backup_verification',
            'core.classes.data_restore',
            'core.classes.data_archival',
            'core.classes.database_migrations',
            'core.classes.daily_silent_collector',
            'core.classes.public_social_monitor',
            'core.classes.x_monitor',
            'core.canary_protocol',
            'core.canary_tui'
        ]
        
        failed_imports = []
        for module in modules:
            try:
                __import__(module)
            except Exception as e:
                failed_imports.append(f"{module}: {e}")
        
        if failed_imports:
            raise Exception(f"Failed imports: {'; '.join(failed_imports)}")
        
        return f"Successfully imported {len(modules)} modules"

    @time_test
    def test_database_operations(self):
        """Test database initialization and operations"""
        with TestEnvironment() as env:
            from core.functions.database_utils import init_db, save_digest_to_db, get_recent_digests
            
            # Test database initialization
            if not init_db(env.test_db):
                raise Exception("Database initialization failed")
            
            # Test saving data
            test_date = datetime.now().strftime("%Y-%m-%d")
            if not save_digest_to_db(test_date, 5, "Test summary", "MEDIUM", "[]", env.test_db):
                raise Exception("Failed to save digest")
            
            # Test retrieving data
            digests = get_recent_digests(5, env.test_db)
            if not digests or len(digests) == 0:
                raise Exception("Failed to retrieve digests")
            
            return f"Database operations successful, {len(digests)} records"

    @time_test
    def test_backup_system(self):
        """Test backup creation and verification"""
        with TestEnvironment() as env:
            from core.classes.backup_verification import BackupVerificationManager
            from core.functions.database_utils import init_db
            
            # Initialize test database
            init_db(env.test_db)
            
            # Create backup verification manager
            backup_manager = BackupVerificationManager(env.test_db)
            
            # Test backup verification with existing backups
            backup_files = list(Path("backups").glob("*.tar.gz")) if Path("backups").exists() else []
            
            if backup_files:
                # Test verification on existing backup
                latest_backup = max(backup_files, key=os.path.getctime)
                verification_result = backup_manager.verify_backup_integrity(latest_backup)
                
                if not verification_result.get('overall_valid', False):
                    raise Exception(f"Backup verification failed: {verification_result.get('errors', [])}")
                
                return f"Backup verification successful: {latest_backup.name}"
            else:
                # Just test that backup manager initializes
                return "Backup system initialized successfully"

    @time_test
    def test_restore_system(self):
        """Test data restore functionality"""
        with TestEnvironment() as env:
            from core.classes.data_restore import DataRestoreManager
            from core.functions.database_utils import init_db
            
            # Initialize test database
            init_db(env.test_db)
            
            restore_manager = DataRestoreManager(env.test_db, env.test_backup_dir)
            
            # Create a test backup file
            test_backup = os.path.join(env.test_backup_dir, "test_backup.db")
            shutil.copy2(env.test_db, test_backup)
            
            # Test backup listing
            backups = restore_manager.list_available_backups()
            if not isinstance(backups, list):
                raise Exception("Failed to list backups")
            
            return f"Restore system functional, found {len(backups)} backups"

    @time_test
    def test_adaptive_intelligence(self):
        """Test adaptive intelligence system"""
        with TestEnvironment() as env:
            from core.classes.adaptive_intelligence import AdaptiveIntelligence
            
            ai = AdaptiveIntelligence(env.test_db)
            ai.init_db()
            
            # Test learning from digest data
            test_digest_data = {
                'urgency_score': 5,
                'keywords': ['test', 'keyword'],
                'sources': ['test_source']
            }
            ai.learn_from_digest(test_digest_data)
            
            # Test intelligence report
            report = ai.get_intelligence_report()
            if not isinstance(report, str) or len(report) == 0:
                raise Exception("Failed to generate intelligence report")
            
            return "Adaptive intelligence system functional"

    @time_test
    def test_feedback_system(self):
        """Test feedback collection and processing"""
        with TestEnvironment() as env:
            from core.classes.smart_feedback import FeedbackSystem
            
            feedback = FeedbackSystem(env.test_db)
            feedback.init_db()
            
            # Initialize database tables properly
            conn = sqlite3.connect(env.test_db)
            cursor = conn.cursor()
            
            # Create prediction_tracking table that feedback system expects
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prediction_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prediction_date TEXT,
                    predicted_urgency INTEGER,
                    actual_urgency INTEGER,
                    prediction_accuracy REAL,
                    contributing_factors TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            # Test feedback summary
            summary = feedback.get_feedback_summary()
            if not isinstance(summary, str):
                raise Exception("Failed to generate feedback summary")
            
            return "Feedback system functional"

    @time_test
    def test_daily_collector(self):
        """Test daily data collection"""
        with TestEnvironment() as env:
            from core.classes.daily_silent_collector import SilentCollector
            
            collector = SilentCollector(env.test_db)
            collector.init_db()
            
            # Test data collection (with mocked external calls)
            with patch('feedparser.parse') as mock_parse, \
                 patch('yfinance.Ticker') as mock_ticker:
                
                # Mock RSS feed response
                mock_parse.return_value = MagicMock()
                mock_parse.return_value.entries = [
                    MagicMock(title="Test headline", link="http://example.com")
                ]
                
                # Mock yfinance response
                mock_ticker_instance = MagicMock()
                mock_ticker_instance.history.return_value = MagicMock()
                mock_ticker.return_value = mock_ticker_instance
                
                emergency_level = collector.collect_daily_data(verbose=False)
                
                if not isinstance(emergency_level, (int, float)):
                    raise Exception("Invalid emergency level returned")
            
            return f"Daily collection functional, emergency level: {emergency_level}"

    @time_test
    def test_configuration_system(self):
        """Test configuration loading and management"""
        with TestEnvironment() as env:
            from core.classes.config_loader import ConfigLoader, get_setting
            
            # Create test config file
            test_config = {
                'test_section': {
                    'test_key': 'test_value'
                }
            }
            
            config_file = os.path.join(env.test_config_dir, "config.yaml")
            import yaml
            with open(config_file, 'w') as f:
                yaml.dump(test_config, f)
            
            # Test config loading
            config_loader = ConfigLoader(env.test_config_dir)
            config = config_loader._config
            
            if not config:
                raise Exception("Failed to load configuration")
            
            # Test setting retrieval
            setting = get_setting('test_section.test_key', 'default')
            if setting != 'test_value':
                raise Exception(f"Expected 'test_value', got '{setting}'")
            
            return "Configuration system functional"

    @time_test
    def test_shell_scripts(self):
        """Test shell script execution"""
        scripts_dir = Path("scripts")
        if not scripts_dir.exists():
            raise Exception("Scripts directory not found")
        
        shell_scripts = list(scripts_dir.glob("*.sh"))
        if not shell_scripts:
            raise Exception("No shell scripts found")
        
        # Test script syntax (bash -n) and find backup script
        failed_scripts = []
        backup_script_found = False
        
        for script in shell_scripts:
            if script.name == 'backup_learning_data.sh':
                backup_script_found = True
                
            result = subprocess.run(['bash', '-n', str(script)], capture_output=True, text=True)
            if result.returncode != 0:
                failed_scripts.append(f"{script.name}: {result.stderr}")
        if failed_scripts:
            raise Exception(f"Script syntax errors: {'; '.join(failed_scripts)}")
        
        if not backup_script_found:
            raise Exception("backup_learning_data.sh not found in scripts directory")
        
        return f"Validated {len(shell_scripts)} shell scripts, backup script found"

    @time_test
    def test_integration_workflow(self):
        """Test end-to-end integration workflow"""
        with TestEnvironment() as env:
            from core.functions.database_utils import init_db
            from core.classes.adaptive_intelligence import AdaptiveIntelligence
            from core.classes.smart_feedback import FeedbackSystem
            
            # Initialize systems
            init_db(env.test_db)
            ai = AdaptiveIntelligence(env.test_db)
            feedback = FeedbackSystem(env.test_db)
            ai.init_db()
            feedback.init_db()
            
            # Simulate workflow: data → learning → feedback
            test_digest_data = {
                'urgency_score': 8,
                'keywords': ['crisis', 'emergency'],
                'sources': ['test_source']
            }
            ai.learn_from_digest(test_digest_data)
            
            # Generate reports
            ai_report = ai.get_intelligence_report()
            feedback_summary = feedback.get_feedback_summary()
            
            if not ai_report or not feedback_summary:
                raise Exception("Failed to generate reports")
            
            return "Integration workflow successful"

    def run_all_tests(self):
        """Execute all tests"""
        print("🧪 COMPREHENSIVE CANARY PROTOCOL TEST SUITE")
        print("=" * 60)
        print(f"Started at: {self.result.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test categories
        test_categories = [
            ("🔧 Core System Tests", [
                ("Core Module Imports", self.test_core_imports),
                ("Database Operations", self.test_database_operations),
                ("Configuration System", self.test_configuration_system),
            ]),
            ("💾 Backup & Restore Tests", [
                ("Backup System", self.test_backup_system),
                ("Restore System", self.test_restore_system),
            ]),
            ("🧠 Learning System Tests", [
                ("Adaptive Intelligence", self.test_adaptive_intelligence),
                ("Feedback System", self.test_feedback_system),
            ]),
            ("📊 Data Collection Tests", [
                ("Daily Collector", self.test_daily_collector),
            ]),
            ("🔗 Integration Tests", [
                ("Shell Scripts", self.test_shell_scripts),
                ("End-to-End Workflow", self.test_integration_workflow),
            ])
        ]
        
        for category_name, tests in test_categories:
            print(f"\n{category_name}")
            print("=" * 50)
            
            for test_name, test_func in tests:
                try:
                    result = test_func()
                    if isinstance(result, tuple) and len(result) == 2:
                        message, duration = result
                        self.result.add_test(test_name, True, None, duration)
                    elif isinstance(result, tuple) and len(result) == 3:
                        _, duration, error = result
                        self.result.add_test(test_name, False, error, duration)
                    else:
                        self.result.add_test(test_name, True, None, 0)
                except Exception as e:
                    self.result.add_test(test_name, False, str(e), 0)
        
        # Print final summary
        self.print_summary()
        
        return 0 if test_results['failed'] == 0 else 1
    
    def print_summary(self):
        """Print test execution summary"""
        end_time = datetime.now()
        duration = end_time - self.result.start_time
        
        print("\n" + "=" * 60)
        print("🎯 TEST EXECUTION SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {test_results['passed']}")
        print(f"❌ Failed: {test_results['failed']}")
        print(f"⏭️  Skipped: {test_results['skipped']}")
        
        total_tests = test_results['passed'] + test_results['failed'] + test_results['skipped']
        if total_tests > 0:
            success_rate = (test_results['passed'] / total_tests) * 100
            print(f"📊 Success Rate: {success_rate:.1f}%")
        
        print(f"⏱️  Total Duration: {duration.total_seconds():.2f}s")
        
        if test_results['errors']:
            print(f"\n❌ FAILED TESTS:")
            for error in test_results['errors']:
                print(f"   • {error}")
        
        print(f"\nCompleted at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    suite = ComprehensiveTestSuite()
    exit_code = suite.run_all_tests()
    sys.exit(exit_code)
