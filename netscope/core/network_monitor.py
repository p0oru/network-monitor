"""
Network Monitor - Monitors network adapters, speeds, ping, and public IP info
"""

import psutil
import socket
import requests
import time
from typing import Dict, List, Optional, Tuple
from threading import Thread


class NetworkMonitor:
    """Monitors network adapters and statistics"""
    
    def __init__(self):
        self.last_bytes_sent = {}
        self.last_bytes_recv = {}
        self.last_packets_sent = {}
        self.last_packets_recv = {}
        self.last_check_time = {}
        self.public_ip = None
        self.isp_name = None
        self.location = None
        self.country = None
        self._fetch_public_info()
    
    def get_active_adapters(self) -> List[Dict]:
        """Get all active network adapters"""
        adapters = []
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
        for interface_name, addresses in interfaces.items():
            # Check if interface is up and has IPv4 address
            is_up = stats[interface_name].isup if interface_name in stats else False
            has_ipv4 = any(addr.family == socket.AF_INET for addr in addresses)
            
            if is_up and has_ipv4:
                ipv4 = next((addr.address for addr in addresses if addr.family == socket.AF_INET), None)
                adapters.append({
                    'name': interface_name,
                    'ip': ipv4,
                    'is_active': True
                })
        
        return adapters
    
    def get_primary_adapter(self) -> Optional[str]:
        """Get the primary active network adapter"""
        adapters = self.get_active_adapters()
        if not adapters:
            return None
        
        # Prefer adapters with names like 'Wi-Fi', 'Ethernet', 'eth0', 'en0'
        preferred = ['Wi-Fi', 'Ethernet', 'eth0', 'en0', 'wlan0']
        for pref in preferred:
            for adapter in adapters:
                if pref.lower() in adapter['name'].lower():
                    return adapter['name']
        
        return adapters[0]['name']
    
    def get_network_stats(self, interface_name: Optional[str] = None) -> Dict:
        """Get current network statistics for an interface"""
        if interface_name is None:
            interface_name = self.get_primary_adapter()
            if interface_name is None:
                return {
                    'interface_name': 'N/A',
                    'bytes_sent': 0,
                    'bytes_recv': 0,
                    'upload_speed': 0.0,
                    'download_speed': 0.0,
                    'packets_sent': 0,
                    'packets_recv': 0,
                    'ping_latency': 0.0
                }
        
        io_counters = psutil.net_io_counters(pernic=True)
        if interface_name not in io_counters:
            return {
                'interface_name': interface_name,
                'bytes_sent': 0,
                'bytes_recv': 0,
                'upload_speed': 0.0,
                'download_speed': 0.0,
                'packets_sent': 0,
                'packets_recv': 0,
                'ping_latency': 0.0
            }
        
        current = io_counters[interface_name]
        current_time = time.time()
        
        bytes_sent = current.bytes_sent
        bytes_recv = current.bytes_recv
        packets_sent = current.packets_sent
        packets_recv = current.packets_recv
        
        # Calculate speeds
        upload_speed = 0.0
        download_speed = 0.0
        
        if interface_name in self.last_check_time:
            time_diff = current_time - self.last_check_time[interface_name]
            if time_diff > 0:
                bytes_sent_diff = bytes_sent - self.last_bytes_sent.get(interface_name, 0)
                bytes_recv_diff = bytes_recv - self.last_bytes_recv.get(interface_name, 0)
                
                upload_speed = (bytes_sent_diff * 8) / (time_diff * 1_000_000)  # Mbps
                download_speed = (bytes_recv_diff * 8) / (time_diff * 1_000_000)  # Mbps
        
        # Update last values
        self.last_bytes_sent[interface_name] = bytes_sent
        self.last_bytes_recv[interface_name] = bytes_recv
        self.last_packets_sent[interface_name] = packets_sent
        self.last_packets_recv[interface_name] = packets_recv
        self.last_check_time[interface_name] = current_time
        
        # Get ping latency
        ping_latency = self._get_ping_latency()
        
        return {
            'interface_name': interface_name,
            'bytes_sent': bytes_sent,
            'bytes_recv': bytes_recv,
            'upload_speed': upload_speed,
            'download_speed': download_speed,
            'packets_sent': packets_sent,
            'packets_recv': packets_recv,
            'ping_latency': ping_latency
        }
    
    def _get_ping_latency(self, target: str = "8.8.8.8") -> float:
        """Get ping latency to a target (in milliseconds)"""
        try:
            import subprocess
            import platform
            
            # Use ping command based on OS
            if platform.system().lower() == 'windows':
                result = subprocess.run(
                    ['ping', '-n', '1', '-w', '1000', target],
                    capture_output=True, text=True, timeout=2
                )
            else:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '1', target],
                    capture_output=True, text=True, timeout=2
                )
            
            if result.returncode == 0:
                # Parse ping output (simplified)
                output = result.stdout
                if 'time=' in output or 'time<' in output:
                    # Extract time value
                    for line in output.split('\n'):
                        if 'time=' in line or 'time<' in line:
                            try:
                                if 'time=' in line:
                                    time_str = line.split('time=')[1].split()[0]
                                else:
                                    time_str = line.split('time<')[1].split()[0]
                                return float(time_str.replace('ms', ''))
                            except:
                                pass
        except:
            pass
        
        return 0.0
    
    def _fetch_public_info(self):
        """Fetch public IP, ISP, and location information"""
        try:
            # Try ipinfo.io first (free tier, no API key needed)
            response = requests.get('https://ipinfo.io/json', timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.public_ip = data.get('ip', 'Unknown')
                self.isp_name = data.get('org', 'Unknown')
                loc = data.get('loc', '').split(',')
                if len(loc) == 2:
                    self.location = f"{loc[0]}, {loc[1]}"
                else:
                    self.location = data.get('city', 'Unknown')
                self.country = data.get('country', 'Unknown')
                return
        except:
            pass
        
        # Fallback: just get IP
        try:
            response = requests.get('https://api.ipify.org?format=json', timeout=5)
            if response.status_code == 200:
                self.public_ip = response.json().get('ip', 'Unknown')
                self.isp_name = 'Unknown'
                self.location = 'Unknown'
                self.country = 'Unknown'
        except:
            self.public_ip = 'Unknown'
            self.isp_name = 'Unknown'
            self.location = 'Unknown'
            self.country = 'Unknown'
    
    def get_public_info(self) -> Dict:
        """Get public IP, ISP, and location information"""
        return {
            'public_ip': self.public_ip or 'Unknown',
            'isp_name': self.isp_name or 'Unknown',
            'location': self.location or 'Unknown',
            'country': self.country or 'Unknown'
        }
    
    def refresh_public_info(self):
        """Refresh public IP information"""
        self._fetch_public_info()
