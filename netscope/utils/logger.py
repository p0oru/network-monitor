"""
Logger - Handles application logging and event tracking
"""
from datetime import datetime
from typing import List, Optional
from enum import Enum


class LogLevel(Enum):
    """Log levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"
    EVENT = "EVENT"


class Logger:
    """Application logger"""
    
    def __init__(self, max_logs: int = 1000):
        """Initialize logger"""
        self.max_logs = max_logs
        self.logs: List[Dict] = []
        self.callback: Optional[callable] = None
    
    def log(self, level: LogLevel, message: str, data: Optional[dict] = None):
        """Add a log entry"""
        log_entry = {
            'timestamp': datetime.now(),
            'level': level.value,
            'message': message,
            'data': data
        }
        
        self.logs.append(log_entry)
        
        # Keep only recent logs
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]
        
        # Call callback if set
        if self.callback:
            self.callback(log_entry)
    
    def info(self, message: str, data: Optional[dict] = None):
        """Log info message"""
        self.log(LogLevel.INFO, message, data)
    
    def warning(self, message: str, data: Optional[dict] = None):
        """Log warning message"""
        self.log(LogLevel.WARNING, message, data)
    
    def error(self, message: str, data: Optional[dict] = None):
        """Log error message"""
        self.log(LogLevel.ERROR, message, data)
    
    def success(self, message: str, data: Optional[dict] = None):
        """Log success message"""
        self.log(LogLevel.SUCCESS, message, data)
    
    def event(self, message: str, data: Optional[dict] = None):
        """Log event message"""
        self.log(LogLevel.EVENT, message, data)
    
    def get_logs(self, limit: Optional[int] = None) -> List[Dict]:
        """Get log entries"""
        if limit:
            return self.logs[-limit:]
        return self.logs.copy()
    
    def clear_logs(self):
        """Clear all logs"""
        self.logs.clear()
    
    def set_callback(self, callback: callable):
        """Set callback for new log entries"""
        self.callback = callback