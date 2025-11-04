"""
Logger - Handles application logging and event tracking.
"""
from datetime import datetime
from typing import List, Optional
from PyQt5.QtCore import QObject, pyqtSignal


class Logger(QObject):
    """Application logger with signal-based updates for UI."""
    
    log_updated = pyqtSignal(str, str)  # timestamp, message
    
    def __init__(self, data_manager=None):
        """Initialize logger."""
        super().__init__()
        self.data_manager = data_manager
        self.logs: List[tuple] = []  # List of (timestamp, level, message)
        self.max_logs = 1000
    
    def log(self, level: str, message: str, save_to_db: bool = True):
        """Log a message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = (timestamp, level, message)
        
        self.logs.append(log_entry)
        
        # Keep only recent logs
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]
        
        # Emit signal for UI update
        formatted_message = f"[{timestamp}] [{level}] {message}"
        self.log_updated.emit(timestamp, formatted_message)
        
        # Save to database if available
        if save_to_db and self.data_manager:
            self.data_manager.log_event(level, message)
    
    def info(self, message: str, save_to_db: bool = True):
        """Log info message."""
        self.log("INFO", message, save_to_db)
    
    def warning(self, message: str, save_to_db: bool = True):
        """Log warning message."""
        self.log("WARNING", message, save_to_db)
    
    def error(self, message: str, save_to_db: bool = True):
        """Log error message."""
        self.log("ERROR", message, save_to_db)
    
    def get_recent_logs(self, limit: int = 100) -> List[str]:
        """Get recent log messages."""
        return [
            f"[{ts}] [{level}] {msg}"
            for ts, level, msg in self.logs[-limit:]
        ]
    
    def clear(self):
        """Clear all logs."""
        self.logs.clear()
