"""
Network Monitor - Handles network statistics collection and monitoring
"""
import os
import psutil
import time
import socket
import subprocess
import threading
import requests
from typing import Dict, List, Optional, Callable
from datetime import datetime


class NetworkMonitor:
    """Monitors network adapters and statistics"""
    
    def __init__(self, callback: Optional[Callable] = None):
        """Initialize network monitor"""
        self.callback = callback
        self.running = False
        self.monitoring_thread = None
        
        # Network stats tracking
        self.last_bytes_sent = {}
        self.last_bytes_recv = {}
        self.last_check_time = {}
        
        # Public IP info
        self.public_ip = "Loading..."
        self.isp = "Loading..."
        self.location = "Loading..."
        self._fetch_public_info()
        
        # Active adapters
        self.active_adapters = []
        self._detect_active_adapters()
    
    def _detect_active_adapters(self):
        """Detect active network adapters"""
        self.active_adapters = []
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
        for interface_name, addrs in interfaces.items():
            # Check if interface is up and has an IP address
            if interface_name in stats:
                if stats[interface_name].isup:
                    # Check for IPv4 address
                    for addr in addrs:
                        if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                            self.active_adapters.append({
                                'name': interface_name,
                                'ip': addr.address,
                                'netmask': addr.netmask
                            })
                            break
    
    def _fetch_public_info(self):
        """Fetch public IP, ISP, and location"""
        def fetch():
            try:
                # Try ipinfo.io first (free tier, no API key needed)
                response = requests.get('https://ipinfo.io/json', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    self.public_ip = data.get('ip', 'Unknown')
                    self.isp = data.get('org', 'Unknown')
                    loc = data.get('loc', '')
                    city = data.get('city', '')
                    region = data.get('region', '')
                    country = data.get('country', '')
                    
                    location_parts = [p for p in [city, region, country] if p]
                    if loc:
                        location_parts.insert(0, loc)
                    self.location = ', '.join(location_parts) if location_parts else 'Unknown'
                else:
                    # Fallback to simple IP check
                    self.public_ip = requests.get('https://api.ipify.org', timeout=5).text
                    self.isp = "Unknown"
                    self.location = "Unknown"
            except Exception as e:
                self.public_ip = "Error"
                self.isp = "Error"
                self.location = "Error"
        
        # Run in background thread
        threading.Thread(target=fetch, daemon=True).start()
    
    def get_network_stats(self) -> Dict:
        """Get current network statistics"""
        current_time = time.time()
        stats = {
            'timestamp': current_time,
            'adapters': [],
            'total_upload_speed': 0,
            'total_download_speed': 0,
            'ping': 0,
            'total_bytes_sent': 0,
            'total_bytes_recv': 0,
            'public_ip': self.public_ip,
            'isp': self.isp,
            'location': self.location
        }
        
        # Update active adapters
        self._detect_active_adapters()
        
        # Get network I/O stats
        net_io = psutil.net_io_counters(pernic=True)
        
        for adapter in self.active_adapters:
            adapter_name = adapter['name']
            
            if adapter_name in net_io:
                io = net_io[adapter_name]
                bytes_sent = io.bytes_sent
                bytes_recv = io.bytes_recv
                
                # Calculate speeds
                upload_speed = 0
                download_speed = 0
                
                if adapter_name in self.last_check_time:
                    time_diff = current_time - self.last_check_time[adapter_name]
                    if time_diff > 0:
                        upload_speed = (bytes_sent - self.last_bytes_sent.get(adapter_name, 0)) / time_diff
                        download_speed = (bytes_recv - self.last_bytes_recv.get(adapter_name, 0)) / time_diff
                
                # Update tracking
                self.last_bytes_sent[adapter_name] = bytes_sent
                self.last_bytes_recv[adapter_name] = bytes_recv
                self.last_check_time[adapter_name] = current_time
                
                adapter_stats = {
                    'name': adapter_name,
                    'ip': adapter['ip'],
                    'upload_speed': max(0, upload_speed),
                    'download_speed': max(0, download_speed),
                    'bytes_sent': bytes_sent,
                    'bytes_recv': bytes_recv
                }
                
                stats['adapters'].append(adapter_stats)
                stats['total_upload_speed'] += upload_speed
                stats['total_download_speed'] += download_speed
                stats['total_bytes_sent'] += bytes_sent
                stats['total_bytes_recv'] += bytes_recv
        
        # Measure ping (to 8.8.8.8)
        stats['ping'] = self._measure_ping()
        
        return stats
    
    def _measure_ping(self) -> float:
        """Measure ping latency to Google DNS"""
        try:
            # Use ping command for more accurate results
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    ['ping', '-n', '1', '8.8.8.8'],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
                # Parse Windows ping output
                for line in result.stdout.split('\n'):
                    if 'time=' in line or 'time<' in line:
                        try:
                            # Extract time value
                            parts = line.split('time')
                            if len(parts) > 1:
                                time_part = parts[1].split('ms')[0].strip('=<>')
                                return float(time_part)
                        except:
                            pass
            else:  # Linux/Mac
                result = subprocess.run(
                    ['ping', '-c', '1', '8.8.8.8'],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
                # Parse Linux/Mac ping output
                for line in result.stdout.split('\n'):
                    if 'time=' in line:
                        try:
                            time_part = line.split('time=')[1].split(' ms')[0]
                            return float(time_part)
                        except:
                            pass
        except Exception:
            pass
        
        # Fallback: try socket connection
        try:
            start = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('8.8.8.8', 53))
            sock.close()
            if result == 0:
                return (time.time() - start) * 1000
        except Exception:
            pass
        
        return 0.0
    
    def run_speed_test(self) -> Dict:
        """Run a speed test using speedtest-cli"""
        try:
            result = subprocess.run(
                ['speedtest-cli', '--simple'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            download = 0
            upload = 0
            ping = 0
            
            for line in result.stdout.split('\n'):
                if 'Download:' in line:
                    try:
                        download = float(line.split()[1])
                    except:
                        pass
                elif 'Upload:' in line:
                    try:
                        upload = float(line.split()[1])
                    except:
                        pass
                elif 'Ping:' in line:
                    try:
                        ping = float(line.split()[1])
                    except:
                        pass
            
            return {
                'download': download,
                'upload': upload,
                'ping': ping,
                'success': True
            }
        except Exception as e:
            return {
                'download': 0,
                'upload': 0,
                'ping': 0,
                'success': False,
                'error': str(e)
            }
    
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
            stats = self.get_network_stats()
            if self.callback:
                self.callback(stats)
            time.sleep(interval)
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
    
    def get_active_adapters(self) -> List[Dict]:
        """Get list of active network adapters"""
        return self.active_adapters.copy()