"""
Core Functions Module for Canary Protocol

This module contains all utility functions and helper modules for the Canary Protocol system.
Functions are organized here for better code structure and maintainability.
"""

# Import all utility functions for easy access
from .utils import (
    log_error, log_info, safe_db_operation, create_directory, 
    ensure_directory_exists, load_file_lines, RetryHandler
)
from .database_utils import (
    init_db, save_digest_to_db, get_recent_digests, 
    save_feedback_to_db, get_feedback_summary
)
from .email_utils import build_email_content, send_email
from .slack_utils import send_to_slack, build_slack_blocks
from .social_media_utils import (
    initialize_x_monitor, get_social_media_analysis, 
    get_social_urgency_boost, format_social_media_section
)
from .analysis_engine import analyze_headlines_with_ai, calculate_urgency_score
from .economic_monitor import get_market_indicators, get_crypto_indicators

__all__ = [
    # Utils
    'log_error', 'log_info', 'safe_db_operation', 'create_directory',
    'ensure_directory_exists', 'load_file_lines', 'RetryHandler',
    
    # Database Utils
    'init_db', 'save_digest_to_db', 'get_recent_digests',
    'save_feedback_to_db', 'get_feedback_summary',
    
    # Communication Utils
    'build_email_content', 'send_email', 'send_to_slack', 'format_slack_blocks',
    
    # Social Media Utils
    'initialize_x_monitor', 'get_social_media_analysis',
    'get_social_urgency_boost', 'format_social_media_section',
    
    # Analysis Functions
    'analyze_headlines_with_ai', 'calculate_urgency_score',
    
    # Economic Functions
    'get_market_indicators', 'get_crypto_indicators',
]
