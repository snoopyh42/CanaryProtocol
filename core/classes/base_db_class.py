#!/usr/bin/env python3
"""
Base Database Class for Canary Protocol
Provides common database initialization and utility methods
"""

import os
import sys
from abc import ABC, abstractmethod

# Add the functions directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions'))

try:
    from utils import ensure_directory_exists
except ImportError:
    # Fallback: create a simple ensure_directory_exists function
    def ensure_directory_exists(path: str) -> bool:
        """Ensure directory exists, create if it doesn't"""
        try:
            if path:  # Only create if path is not empty
                os.makedirs(path, exist_ok=True)
            return True
        except Exception:
            return False


class BaseDBClass(ABC):
    """Base class for all database-dependent classes in Canary Protocol"""
    
    def __init__(self, db_path: str = "data/canary_protocol.db"):
        self.db_path = db_path
        # Ensure data directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir:  # Only create directory if dirname is not empty
            ensure_directory_exists(db_dir)
        self.init_db()
    
    @abstractmethod
    def init_db(self):
        """Initialize database tables - must be implemented by subclasses"""
        pass
