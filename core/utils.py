#!/usr/bin/env python3
"""
Utility functions for Canary Protocol
Common operations and error handling utilities
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional


def log_error(message: str, log_file: str = "logs/error.log") -> None:
    """Log errors to file with timestamp"""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, "a") as f:
        f.write(f"{datetime.now().isoformat()}: {message}\n")


def log_info(message: str, log_file: str = "logs/info.log") -> None:
    """Log info messages to file with timestamp"""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, "a") as f:
        f.write(f"{datetime.now().isoformat()}: {message}\n")


def safe_db_operation(db_path: str, operation_func, *args, **kwargs) -> Any:
    """Safely execute database operations with proper error handling"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        result = operation_func(cursor, *args, **kwargs)
        conn.commit()
        return result
    except sqlite3.Error as e:
        log_error(f"Database operation failed: {e}")
        return None
    except Exception as e:
        log_error(f"Unexpected error in database operation: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()


def create_directory(path: str) -> bool:
    """Create directory if it doesn't exist"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        log_error(f"Failed to create directory {path}: {e}")
        return False


def ensure_directory_exists(path: str) -> bool:
    """Ensure directory exists, create if it doesn't"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        log_error(f"Failed to create directory {path}: {e}")
        return False


def load_file_lines(filename: str) -> List[str]:
    """Load lines from file, return empty list if file doesn't exist"""
    try:
        with open(filename, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        log_error(f"File not found: {filename}")
        return []
    except Exception as e:
        log_error(f"Error reading file {filename}: {e}")
        return []


def safe_get_nested(data: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """Safely get nested dictionary value using dot notation"""
    try:
        keys = key_path.split('.')
        value = data
        for key in keys:
            if value is None or not isinstance(value, dict):
                return default
            value = value.get(key)
        return value if value is not None else default
    except Exception:
        return default


class RetryHandler:
    """Handle retry logic for operations that might fail temporarily"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    def execute_with_retry(self, operation_func, *args, **kwargs) -> Any:
        """Execute function with exponential backoff retry"""
        import time
        
        for attempt in range(self.max_retries):
            try:
                return operation_func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    log_error(f"Operation failed after {self.max_retries} attempts: {e}")
                    raise
                
                delay = self.base_delay * (2 ** attempt)
                log_error(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage"""
    import re
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    # Limit length
    return sanitized[:255] if len(sanitized) > 255 else sanitized
