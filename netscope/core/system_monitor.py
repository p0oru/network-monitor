"""
System monitoring module for CPU, RAM, disk, and uptime statistics.
"""
import psutil
import time
from typing import Dict


class SystemMonitor:
    """Monitors system resources and performance."""
    
    def __init__(self):
        self.boot_time = psutil.boot_time()
        self.start_time = time.time()
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        return psutil.cpu_percent(interval=0.1)
    
    def get_cpu_per_core(self) -> List[float]:
        """Get CPU usage per core."""
        return psutil.cpu_percent(interval=0.1, percpu=True)
    
    def get_ram_usage(self) -> Dict:
        """Get RAM usage statistics."""
        memory = psutil.virtual_memory()
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'free': memory.free,
            'percent': memory.percent
        }
    
    def get_disk_usage(self) -> Dict:
        """Get disk usage statistics for the main drive."""
        try:
            disk = psutil.disk_usage('/')
            if sys.platform == 'win32':
                # Try Windows drive
                import os
                disk = psutil.disk_usage(os.path.expanduser('~'))
        except Exception:
            try:
                disk = psutil.disk_usage('C:\\' if sys.platform == 'win32' else '/')
            except Exception:
                return {'error': 'Could not get disk usage'}
        
        return {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent
        }
    
    def get_system_uptime(self) -> Dict:
        """Get system uptime since boot."""
        uptime_seconds = time.time() - self.boot_time
        return self._format_uptime(uptime_seconds)
    
    def get_app_uptime(self) -> Dict:
        """Get application uptime."""
        uptime_seconds = time.time() - self.start_time
        return self._format_uptime(uptime_seconds)
    
    def _format_uptime(self, seconds: float) -> Dict:
        """Format uptime into days, hours, minutes, seconds."""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")
        
        return {
            'seconds': seconds,
            'formatted': ' '.join(parts),
            'days': days,
            'hours': hours,
            'minutes': minutes
        }
    
    def get_all_stats(self) -> Dict:
        """Get all system statistics at once."""
        return {
            'cpu_percent': self.get_cpu_usage(),
            'cpu_per_core': self.get_cpu_per_core(),
            'ram': self.get_ram_usage(),
            'disk': self.get_disk_usage(),
            'system_uptime': self.get_system_uptime(),
            'app_uptime': self.get_app_uptime(),
            'timestamp': time.time()
        }


import sys
