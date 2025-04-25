import os
import sys
import json
import time
import logging
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime
from queue import Queue
from pathlib import Path

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

class LogLevel:
    """Custom log levels for the Seven Sisters system."""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    SISTER = 25  # Custom level for sister-specific logs
    ACTION = 35  # Custom level for action-related logs

class LogEntry:
    """Represents a single log entry with all relevant information."""
    def __init__(self, 
                 timestamp: float,
                 level: int,
                 sister: str,
                 message: str,
                 category: str,
                 details: Optional[Dict] = None):
        self.timestamp = timestamp
        self.level = level
        self.sister = sister
        self.message = message
        self.category = category
        self.details = details or {}
    
    def to_dict(self) -> Dict:
        """Convert the log entry to a dictionary."""
        return {
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "level": self.level,
            "level_name": logging.getLevelName(self.level),
            "sister": self.sister,
            "message": self.message,
            "category": self.category,
            "details": self.details
        }
    
    def to_json(self) -> str:
        """Convert the log entry to a JSON string."""
        return json.dumps(self.to_dict())
    
    def __str__(self) -> str:
        """Convert the log entry to a human-readable string."""
        level_name = logging.getLevelName(self.level)
        return f"[{datetime.fromtimestamp(self.timestamp).isoformat()}] {level_name} [{self.sister}] {self.message}"

class SisterLogger:
    """
    A centralized logging system for the Seven Sisters.
    Handles log creation, formatting, and management.
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize the logging system.
        
        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up the main log file
        self.main_log = self.log_dir / "seven_sisters.log"
        self.setup_file_handler(self.main_log)
        
        # Set up category-specific log files
        self.category_logs = {}
        self.category_handlers = {}
        
        # Set up real-time log queue
        self.log_queue = Queue()
        self.realtime_listeners = []
        
        # Start the real-time log processor
        self.processor_thread = threading.Thread(target=self._process_log_queue, daemon=True)
        self.processor_thread.start()
        
        # Register custom log levels
        logging.addLevelName(LogLevel.SISTER, "SISTER")
        logging.addLevelName(LogLevel.ACTION, "ACTION")
    
    def setup_file_handler(self, log_file: Path, level: int = logging.INFO):
        """Set up a file handler for logging."""
        handler = logging.FileHandler(log_file)
        handler.setLevel(level)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(name)s] - %(message)s'
        )
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
    
    def get_category_log(self, category: str) -> Path:
        """Get or create a category-specific log file."""
        if category not in self.category_logs:
            category_dir = self.log_dir / "categories"
            category_dir.mkdir(exist_ok=True)
            self.category_logs[category] = category_dir / f"{category}.log"
            self.setup_file_handler(self.category_logs[category])
        return self.category_logs[category]
    
    def log(self, 
            level: int,
            sister: str,
            message: str,
            category: str = "general",
            details: Optional[Dict] = None):
        """
        Log a message with the specified parameters.
        
        Args:
            level: Log level
            sister: Name of the sister generating the log
            message: Log message
            category: Log category
            details: Additional details to include in the log
        """
        entry = LogEntry(
            timestamp=time.time(),
            level=level,
            sister=sister,
            message=message,
            category=category,
            details=details
        )
        
        # Add to queue for real-time processing
        self.log_queue.put(entry)
        
        # Write to appropriate log files
        log_message = str(entry)
        logging.log(level, log_message)
        
        # Write to category-specific log
        category_log = self.get_category_log(category)
        with open(category_log, 'a', encoding='utf-8') as f:
            f.write(f"{entry.to_json()}\n")
    
    def _process_log_queue(self):
        """Process the log queue and notify real-time listeners."""
        while True:
            entry = self.log_queue.get()
            for listener in self.realtime_listeners:
                try:
                    listener(entry)
                except Exception as e:
                    logging.error(f"Error in log listener: {e}")
            self.log_queue.task_done()
    
    def add_realtime_listener(self, listener):
        """Add a real-time log listener."""
        self.realtime_listeners.append(listener)
    
    def remove_realtime_listener(self, listener):
        """Remove a real-time log listener."""
        if listener in self.realtime_listeners:
            self.realtime_listeners.remove(listener)
    
    def get_recent_logs(self, 
                       category: Optional[str] = None,
                       sister: Optional[str] = None,
                       level: Optional[int] = None,
                       limit: int = 100) -> List[LogEntry]:
        """
        Get recent log entries with optional filtering.
        
        Args:
            category: Filter by category
            sister: Filter by sister
            level: Filter by log level
            limit: Maximum number of entries to return
            
        Returns:
            List of LogEntry objects
        """
        log_file = self.get_category_log(category) if category else self.main_log
        entries = []
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in reversed(list(f)):
                    try:
                        entry_dict = json.loads(line.strip())
                        entry = LogEntry(
                            timestamp=entry_dict['timestamp'],
                            level=entry_dict['level'],
                            sister=entry_dict['sister'],
                            message=entry_dict['message'],
                            category=entry_dict['category'],
                            details=entry_dict['details']
                        )
                        
                        # Apply filters
                        if sister and entry.sister != sister:
                            continue
                        if level and entry.level != level:
                            continue
                        
                        entries.append(entry)
                        if len(entries) >= limit:
                            break
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass
        
        return entries
    
    def clear_logs(self, category: Optional[str] = None):
        """
        Clear logs, optionally for a specific category.
        
        Args:
            category: Category to clear, or None for all logs
        """
        if category:
            log_file = self.get_category_log(category)
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('')
        else:
            # Clear main log
            with open(self.main_log, 'w', encoding='utf-8') as f:
                f.write('')
            
            # Clear all category logs
            for category_log in self.category_logs.values():
                with open(category_log, 'w', encoding='utf-8') as f:
                    f.write('')

# Create a global logger instance
logger = SisterLogger()

# Convenience functions for logging
def log_debug(sister: str, message: str, category: str = "general", details: Optional[Dict] = None):
    """Log a debug message."""
    logger.log(LogLevel.DEBUG, sister, message, category, details)

def log_info(sister: str, message: str, category: str = "general", details: Optional[Dict] = None):
    """Log an info message."""
    logger.log(LogLevel.INFO, sister, message, category, details)

def log_warning(sister: str, message: str, category: str = "general", details: Optional[Dict] = None):
    """Log a warning message."""
    logger.log(LogLevel.WARNING, sister, message, category, details)

def log_error(sister: str, message: str, category: str = "general", details: Optional[Dict] = None):
    """Log an error message."""
    logger.log(LogLevel.ERROR, sister, message, category, details)

def log_critical(sister: str, message: str, category: str = "general", details: Optional[Dict] = None):
    """Log a critical message."""
    logger.log(LogLevel.CRITICAL, sister, message, category, details)

def log_sister(sister: str, message: str, category: str = "general", details: Optional[Dict] = None):
    """Log a sister-specific message."""
    logger.log(LogLevel.SISTER, sister, message, category, details)

def log_action(sister: str, message: str, category: str = "general", details: Optional[Dict] = None):
    """Log an action-related message."""
    logger.log(LogLevel.ACTION, sister, message, category, details) 