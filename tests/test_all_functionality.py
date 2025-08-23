#!/usr/bin/env python3
"""
Comprehensive test suite for Canary Protocol
Tests all core functionality, modules, and integrations
"""

import sys
import os
import traceback
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test results tracking
test_results = {
    'passed': 0,
    'failed': 0,
    'skipped': 0,
    'errors': []
}

def test_result(test_name: str, success: bool, error_msg: str = None):
    """Track test results"""
    if success:
        test_results['passed'] += 1
        print(f"✅ {test_name}")
    else:
        test_results['failed'] += 1
        test_results['errors'].append(f"{test_name}: {error_msg}")
        print(f"❌ {test_name}: {error_msg}")

def test_skip(test_name: str, reason: str):
    """Skip a test"""
    test_results['skipped'] += 1
    print(f"⏭️  {test_name}: {reason}")

def test_core_imports():
    """Test all core module imports"""
    print("\n🧪 Testing Core Module Imports")
    print("=" * 40)
    
    modules_to_test = [
        'core.utils',
        'core.config_loader', 
        'core.database_utils',
        'core.analysis_engine',
        'core.email_utils',
        'core.slack_utils',
        'core.social_media_utils',
        'core.economic_monitor',
        'core.adaptive_intelligence',
        'core.smart_feedback',
        'core.canary_protocol'
    ]
    
    for module in modules_to_test:
        try:
            __import__(module)
            test_result(f"Import {module}", True)
        except ImportError as e:
            test_result(f"Import {module}", False, str(e))
        except Exception as e:
            test_result(f"Import {module}", False, f"Unexpected error: {e}")

def test_database_operations():
    """Test database functionality"""
    print("\n🗄️  Testing Database Operations")
    print("=" * 40)
    
    try:
        from core.database_utils import init_db, save_digest_to_db, get_recent_digests
        
        # Test database initialization
        if init_db("data/test_canary.db"):
            test_result("Database initialization", True)
        else:
            test_result("Database initialization", False, "Init function returned False")
        
        # Test saving digest
        test_date = datetime.now().strftime("%Y-%m-%d")
        if save_digest_to_db(test_date, 5, "Test summary", "MEDIUM", "[]", "data/test_canary.db"):
            test_result("Save digest to database", True)
        else:
            test_result("Save digest to database", False, "Save function returned False")
        
        # Test retrieving digests
        digests = get_recent_digests(5, "data/test_canary.db")
        if isinstance(digests, list):
            test_result("Retrieve recent digests", True)
        else:
            test_result("Retrieve recent digests", False, "Did not return list")
            
    except Exception as e:
        test_result("Database operations", False, str(e))

def test_utility_functions():
    """Test utility functions"""
    print("\n🔧 Testing Utility Functions")
    print("=" * 40)
    
    try:
        from core.utils import log_error, log_info, create_directory, safe_get_nested
        
        # Test logging functions
        log_info("Test info message")
        test_result("Logging functions", True)
        
        # Test directory creation
        test_dir = "data/test_dir"
        if create_directory(test_dir):
            test_result("Directory creation", True)
            # Cleanup
            import shutil
            shutil.rmtree(test_dir, ignore_errors=True)
        else:
            test_result("Directory creation", False, "Function returned False")
        
        # Test nested dictionary access
        test_data = {'level1': {'level2': {'level3': 'value'}}}
        result = safe_get_nested(test_data, 'level1.level2.level3', 'default')
        if result == 'value':
            test_result("Nested dictionary access", True)
        else:
            test_result("Nested dictionary access", False, f"Expected 'value', got '{result}'")
            
        # Test with missing key
        result2 = safe_get_nested(test_data, 'missing.key', 'default')
        if result2 == 'default':
            test_result("Missing key default handling", True)
        else:
            test_result("Missing key default handling", False, f"Expected 'default', got '{result2}'")
            
    except Exception as e:
        test_result("Utility functions", False, str(e))

def test_email_utilities():
    """Test email utility functions"""
    print("\n📧 Testing Email Utilities")
    print("=" * 40)
    
    try:
        from core.email_utils import build_email_content, load_subscribers
        
        # Test email content building
        test_summary = "# Test Summary\nThis is a test."
        test_links = '[{"title": "Test Link", "url": "https://example.com"}]'
        
        email_content = build_email_content(test_summary, test_links)
        if isinstance(email_content, str) and len(email_content) > 0:
            test_result("Email content building", True)
        else:
            test_result("Email content building", False, "No content generated")
        
        # Test subscriber loading (will fail gracefully if file doesn't exist)
        subscribers = load_subscribers()
        if isinstance(subscribers, list):
            test_result("Subscriber loading", True)
        else:
            test_result("Subscriber loading", False, "Did not return list")
            
    except Exception as e:
        test_result("Email utilities", False, str(e))

def test_slack_utilities():
    """Test Slack utility functions"""
    print("\n💬 Testing Slack Utilities")
    print("=" * 40)
    
    try:
        from core.slack_utils import format_slack_message, build_slack_blocks
        
        # Test message formatting
        test_message = "# Test Header\n**Bold text**\n- List item"
        formatted = format_slack_message(test_message)
        if isinstance(formatted, str):
            test_result("Slack message formatting", True)
        else:
            test_result("Slack message formatting", False, "Did not return string")
        
        # Test block building
        blocks = build_slack_blocks(test_message)
        if isinstance(blocks, list) and len(blocks) > 0:
            test_result("Slack blocks building", True)
        else:
            test_result("Slack blocks building", False, "Did not return valid blocks")
            
    except Exception as e:
        test_result("Slack utilities", False, str(e))

def test_analysis_engine():
    """Test analysis engine functions"""
    print("\n🤖 Testing Analysis Engine")
    print("=" * 40)
    
    try:
        from core.analysis_engine import calculate_urgency_score
        
        # Test urgency calculation
        headlines = [
            {"title": "Breaking: Crisis situation develops", "url": "https://example.com"},
            {"title": "Normal news story", "url": "https://example.com"}
        ]
        
        urgency_score, urgency_level = calculate_urgency_score(headlines, [], ['crisis', 'recession'], {'max_urgency_score': 10, 'urgent_analysis_score': 7.0, 'critical_analysis_score': 4.0})
        if isinstance(urgency_score, (int, float)) and urgency_score >= 0 and urgency_level in ['LOW', 'MEDIUM', 'HIGH']:
            test_result("Urgency score calculation", True)
        else:
            test_result("Urgency score calculation", False, f"Invalid score: {urgency_score}, level: {urgency_level}")
            
    except Exception as e:
        test_result("Analysis engine", False, str(e))

def test_social_media_integration():
    """Test social media integration"""
    print("\n📱 Testing Social Media Integration")
    print("=" * 40)
    
    try:
        from core.social_media_utils import initialize_x_monitor, get_social_media_analysis, is_social_monitoring_enabled
        
        # Test monitoring status check
        is_enabled = is_social_monitoring_enabled()
        test_result("Social monitoring status check", True)
        
        # Test monitor initialization (will return None if not configured)
        x_monitor = initialize_x_monitor()
        test_result("X monitor initialization", True)
        
        # Test analysis (should work even with None monitor)
        analysis = get_social_media_analysis(x_monitor)
        if isinstance(analysis, dict) and 'status' in analysis:
            test_result("Social media analysis", True)
        else:
            test_result("Social media analysis", False, "Invalid analysis format")
            
    except Exception as e:
        test_result("Social media integration", False, str(e))

def test_configuration_loading():
    """Test configuration system"""
    print("\n⚙️  Testing Configuration Loading")
    print("=" * 40)
    
    try:
        from core.config_loader import get_config, get_setting
        
        # Test config loading
        config = get_config()
        # Config is expected to be a YAML object, not necessarily a dict
        if config is not None:
            test_result("Configuration loading", True)
        else:
            test_result("Configuration loading", False, "Config is None")
        
        # Test setting retrieval with default
        setting = get_setting('nonexistent.setting', 'default_value')
        if setting == 'default_value':
            test_result("Setting retrieval with default", True)
        else:
            test_result("Setting retrieval with default", False, f"Expected 'default_value', got '{setting}'")
            
    except Exception as e:
        test_result("Configuration loading", False, str(e))

def test_x_integration():
    """Test X/Twitter integration specifically"""
    print("\n🐦 Testing X/Twitter Integration")
    print("=" * 40)
    
    try:
        # Import and run the existing X integration test
        from tests.test_x_integration import test_x_integration
        
        # Capture the test output
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            test_x_integration()
        
        output = f.getvalue()
        if "Test failed" not in output:
            test_result("X/Twitter integration test", True)
        else:
            test_result("X/Twitter integration test", False, "X integration test reported failure")
            
    except Exception as e:
        test_result("X/Twitter integration test", False, str(e))

def run_all_tests():
    """Run all tests"""
    print("🧪 CANARY PROTOCOL COMPREHENSIVE TEST SUITE")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all test suites
    test_core_imports()
    test_utility_functions()
    test_database_operations()
    test_configuration_loading()
    test_analysis_engine()
    test_email_utilities()
    test_slack_utilities()
    test_social_media_integration()
    test_x_integration()
    
    # Print summary
    print("\n" + "=" * 50)
    print("🎯 TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"⏭️  Skipped: {test_results['skipped']}")
    
    total_tests = test_results['passed'] + test_results['failed'] + test_results['skipped']
    if total_tests > 0:
        success_rate = (test_results['passed'] / total_tests) * 100
        print(f"📊 Success Rate: {success_rate:.1f}%")
    
    if test_results['errors']:
        print(f"\n❌ FAILED TESTS:")
        for error in test_results['errors']:
            print(f"   • {error}")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Return exit code
    return 0 if test_results['failed'] == 0 else 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
