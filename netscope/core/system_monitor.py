"""
System Monitor - Handles system statistics collection and monitoring
"""
import os
import psutil
import time
import threading
from typing import Dict, Optional, Callable
from datetime import datetime, timedelta


class SystemMonitor:
    """Monitors system statistics"""
    
    def __init__(self, callback: Optional[Callable] = None):
        """Initialize system monitor"""
        self.callback = callback
        self.running = False
        self.monitoring_thread = None
        self.boot_time = psutil.boot_time()
    
    def get_system_stats(self) -> Dict:
        """Get current system statistics"""
        current_time = time.time()
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        ram_percent = memory.percent
        ram_total = memory.total
        ram_used = memory.used
        
        # Disk usage (C: drive on Windows, / on Linux)
        disk = psutil.disk_usage('/' if os.name != 'nt' else 'C:\\')
        disk_percent = (disk.used / disk.total) * 100
        disk_total = disk.total
        disk_used = disk.used
        
        # System uptime
        uptime_seconds = current_time - self.boot_time
        
        stats = {
            'timestamp': current_time,
            'cpu_usage': cpu_percent,
            'ram_usage': ram_percent,
            'ram_used': ram_used,
            'ram_total': ram_total,
            'disk_usage': disk_percent,
            'disk_used': disk_used,
            'disk_total': disk_total,
            'uptime': uptime_seconds
        }
        
        return stats
    
    def format_uptime(self, seconds: float) -> str:
        """Format uptime as human-readable string"""
        delta = timedelta(seconds=int(seconds))
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def format_bytes(self, bytes: float) -> str:
        """Format bytes as human-readable string"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024.0:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.2f} PB"
    
    def start_monitoring(self, interval: float = 1.0):
        """Start continuous monitoring"""
        if self.running:
            return
        
        self.running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, args=(interval,), daemon=True)
        self.monitoring_thread.start()
    
    def _monitoring_loop(self, interval: float):
        """Internal monitoring loop"""
        while self.running:
            stats = self.get_system_stats()
            if self.callback:
                self.callback(stats)
            time.sleep(interval)
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)