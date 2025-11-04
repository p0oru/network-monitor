"""
Logger - Console-style logging for application events
"""

from datetime import datetime
from typing import List, Optional
from PyQt5.QtCore import QObject, pyqtSignal


class Logger(QObject):
    """Logging system with console-style output"""
    
    log_added = pyqtSignal(str)  # Signal emitted when log is added
    
    def __init__(self):
        super().__init__()
        self.logs: List[str] = []
        self.max_logs = 1000  # Keep last 1000 logs
    
    def log(self, message: str, level: str = "INFO"):
        """Add a log entry"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.logs.append(log_entry)
        
        # Keep only last max_logs entries
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]
        
        # Emit signal for UI update
        self.log_added.emit(log_entry)
    
    def info(self, message: str):
        """Log info message"""
        self.log(message, "INFO")
    
    def warning(self, message: str):
        """Log warning message"""
        self.log(message, "WARN")
    
    def error(self, message: str):
        """Log error message"""
        self.log(message, "ERROR")
    
    def success(self, message: str):
        """Log success message"""
        self.log(message, "SUCCESS")
    
    def get_logs(self, limit: Optional[int] = None) -> List[str]:
        """Get log entries"""
        if limit:
            return self.logs[-limit:]
        return self.logs
    
    def clear(self):
        """Clear all logs"""
        self.logs.clear()
        self.log_added.emit("")
