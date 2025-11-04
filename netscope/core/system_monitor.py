"""
System Monitor - Monitors CPU, RAM, Disk usage and system uptime
"""

import psutil
import time
from datetime import datetime, timedelta
from typing import Dict


class SystemMonitor:
    """Monitors system performance metrics"""
    
    def __init__(self):
        self.boot_time = datetime.fromtimestamp(psutil.boot_time())
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        return psutil.cpu_percent(interval=0.1)
    
    def get_ram_usage(self) -> Dict:
        """Get RAM usage information"""
        mem = psutil.virtual_memory()
        return {
            'percent': mem.percent,
            'used': mem.used,
            'total': mem.total,
            'available': mem.available
        }
    
    def get_disk_usage(self) -> Dict:
        """Get disk usage information (for root partition)"""
        disk = psutil.disk_usage('/')
        return {
            'percent': disk.percent,
            'used': disk.used,
            'total': disk.total,
            'free': disk.free
        }
    
    def get_uptime(self) -> int:
        """Get system uptime in seconds"""
        return int((datetime.now() - self.boot_time).total_seconds())
    
    def get_uptime_formatted(self) -> str:
        """Get formatted uptime string"""
        uptime_seconds = self.get_uptime()
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def get_all_stats(self) -> Dict:
        """Get all system statistics"""
        ram = self.get_ram_usage()
        disk = self.get_disk_usage()
        
        return {
            'cpu_percent': self.get_cpu_usage(),
            'ram_percent': ram['percent'],
            'ram_used': ram['used'],
            'ram_total': ram['total'],
            'disk_percent': disk['percent'],
            'disk_used': disk['used'],
            'disk_total': disk['total'],
            'uptime_seconds': self.get_uptime(),
            'uptime_formatted': self.get_uptime_formatted()
        }
