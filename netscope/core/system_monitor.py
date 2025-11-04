"""
System Monitor - Monitors CPU, RAM, Disk usage and system uptime.
"""
import psutil
import time
from typing import Dict
from datetime import timedelta


class SystemMonitor:
    """Monitors system resources and performance."""
    
    def __init__(self):
        """Initialize system monitor."""
        self.boot_time = psutil.boot_time()
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        try:
            return psutil.cpu_percent(interval=0.1)
        except:
            return 0.0
    
    def get_ram_usage(self) -> Dict:
        """Get RAM usage statistics."""
        try:
            memory = psutil.virtual_memory()
            return {
                'total': memory.total,
                'used': memory.used,
                'free': memory.free,
                'percent': memory.percent
            }
        except:
            return {
                'total': 0,
                'used': 0,
                'free': 0,
                'percent': 0.0
            }
    
    def get_disk_usage(self) -> Dict:
        """Get disk usage for the primary drive."""
        try:
            disk = psutil.disk_usage('/')
            return {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': (disk.used / disk.total) * 100
            }
        except:
            # Try Windows drive
            try:
                disk = psutil.disk_usage('C:\\')
                return {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                }
            except:
                return {
                    'total': 0,
                    'used': 0,
                    'free': 0,
                    'percent': 0.0
                }
    
    def get_uptime(self) -> float:
        """Get system uptime in seconds."""
        try:
            return time.time() - self.boot_time
        except:
            return 0.0
    
    def format_uptime(self, seconds: float) -> str:
        """Format uptime as human-readable string."""
        try:
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
        except:
            return "0s"
    
    def get_all_stats(self) -> Dict:
        """Get all system statistics."""
        cpu = self.get_cpu_usage()
        ram = self.get_ram_usage()
        disk = self.get_disk_usage()
        uptime_seconds = self.get_uptime()
        
        return {
            'cpu_usage': cpu,
            'ram_usage': ram['percent'],
            'disk_usage': disk['percent'],
            'uptime': uptime_seconds,
            'ram_total': ram['total'],
            'ram_used': ram['used'],
            'disk_total': disk['total'],
            'disk_used': disk['used']
        }
