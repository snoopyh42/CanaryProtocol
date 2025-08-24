#!/usr/bin/env python3
"""
Base Database Class for Canary Protocol
Provides common database initialization and utility methods
"""

import os
from abc import ABC, abstractmethod

try:
    from ..functions.utils import ensure_directory_exists
except ImportError:
    from functions.utils import ensure_directory_exists


class BaseDBClass(ABC):
    """Base class for all database-dependent classes in Canary Protocol"""
    
    def __init__(self, db_path: str = "data/canary_protocol.db"):
        self.db_path = db_path
        # Ensure data directory exists
        ensure_directory_exists(os.path.dirname(self.db_path))
        self.init_db()
    
    @abstractmethod
    def init_db(self):
        """Initialize database tables - must be implemented by subclasses"""
        pass
