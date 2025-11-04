"""
Logging utility for application events.
"""
from datetime import datetime
from typing import List, Optional
from PyQt5.QtCore import QObject, pyqtSignal


class Logger(QObject):
    """Thread-safe logger for application events."""
    
    log_added = pyqtSignal(str)
    
    def __init__(self, max_lines: int = 1000):
        super().__init__()
        self.max_lines = max_lines
        self.logs: List[str] = []
    
    def log(self, message: str, level: str = "INFO"):
        """Add a log entry."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        self.logs.append(log_entry)
        
        # Keep only recent logs
        if len(self.logs) > self.max_lines:
            self.logs = self.logs[-self.max_lines:]
        
        # Emit signal for UI update
        self.log_added.emit(log_entry)
    
    def info(self, message: str):
        """Log info message."""
        self.log(message, "INFO")
    
    def warning(self, message: str):
        """Log warning message."""
        self.log(message, "WARNING")
    
    def error(self, message: str):
        """Log error message."""
        self.log(message, "ERROR")
    
    def get_logs(self, limit: Optional[int] = None) -> List[str]:
        """Get recent log entries."""
        if limit:
            return self.logs[-limit:]
        return self.logs.copy()
    
    def clear(self):
        """Clear all logs."""
        self.logs.clear()
