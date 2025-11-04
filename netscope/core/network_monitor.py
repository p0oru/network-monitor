"""
Network Monitor - Monitors network adapters, speeds, ping, and public IP information.
"""
import psutil
import time
import requests
import subprocess
import platform
from typing import Dict, List, Optional, Tuple
from threading import Thread, Event
import socket


class NetworkMonitor:
    """Monitors network interfaces and statistics."""
    
    def __init__(self):
        """Initialize network monitor."""
        self.running = False
        self.stop_event = Event()
        self.last_bytes_sent = 0
        self.last_bytes_recv = 0
        self.last_time = time.time()
        self.current_adapter = None
        self.public_ip = None
        self.isp_name = None
        self.location = None
        self._fetch_public_info()
    
    def _fetch_public_info(self):
        """Fetch public IP, ISP, and location from ipinfo.io API."""
        try:
            # Try ipinfo.io first (free tier: 50k requests/month)
            response = requests.get('https://ipinfo.io/json', timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.public_ip = data.get('ip', 'Unknown')
                self.isp_name = data.get('org', 'Unknown')
                location_parts = []
                if data.get('city'):
                    location_parts.append(data['city'])
                if data.get('region'):
                    location_parts.append(data['region'])
                if data.get('country'):
                    location_parts.append(data['country'])
                self.location = ', '.join(location_parts) if location_parts else 'Unknown'
        except Exception as e:
            print(f"Failed to fetch public IP info: {e}")
            # Fallback to simple IP check
            try:
                response = requests.get('https://api.ipify.org?format=json', timeout=5)
                if response.status_code == 200:
                    self.public_ip = response.json().get('ip', 'Unknown')
            except:
                self.public_ip = 'Unknown'
            self.isp_name = 'Unknown'
            self.location = 'Unknown'
    
    def get_active_adapters(self) -> List[Dict]:
        """Get all active network adapters."""
        adapters = []
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
        for interface_name, addresses in interfaces.items():
            # Skip loopback
            if interface_name == 'lo' or interface_name.startswith('Loopback'):
                continue
            
            # Check if interface is up
            if interface_name in stats:
                stat = stats[interface_name]
                if stat.isup:
                    # Get IP address
                    ip_address = None
                    for addr in addresses:
                        if addr.family == socket.AF_INET:
                            ip_address = addr.address
                            break
                    
                    adapters.append({
                        'name': interface_name,
                        'ip': ip_address or 'No IP',
                        'isup': stat.isup,
                        'speed': stat.speed if stat.speed > 0 else 'Unknown'
                    })
        
        return adapters
    
    def get_primary_adapter(self) -> Optional[str]:
        """Get the primary active network adapter."""
        adapters = self.get_active_adapters()
        if not adapters:
            return None
        
        # Prefer adapters with IP addresses
        for adapter in adapters:
            if adapter['ip'] != 'No IP':
                return adapter['name']
        
        # Fallback to first adapter
        return adapters[0]['name']
    
    def get_network_stats(self) -> Dict:
        """Get current network statistics for the primary adapter."""
        if not self.current_adapter:
            self.current_adapter = self.get_primary_adapter()
        
        if not self.current_adapter:
            return {
                'adapter_name': 'No adapter',
                'upload_speed': 0.0,
                'download_speed': 0.0,
                'bytes_sent': 0.0,
                'bytes_received': 0.0,
                'ping_latency': 0.0,
                'public_ip': self.public_ip or 'Unknown',
                'isp_name': self.isp_name or 'Unknown',
                'location': self.location or 'Unknown'
            }
        
        try:
            net_io = psutil.net_io_counters(pernic=True)
            if self.current_adapter not in net_io:
                return self.get_network_stats()
            
            current_bytes_sent = net_io[self.current_adapter].bytes_sent
            current_bytes_recv = net_io[self.current_adapter].bytes_recv
            current_time = time.time()
            
            time_diff = current_time - self.last_time
            if time_diff > 0:
                upload_speed = (current_bytes_sent - self.last_bytes_sent) / time_diff
                download_speed = (current_bytes_recv - self.last_bytes_recv) / time_diff
            else:
                upload_speed = 0.0
                download_speed = 0.0
            
            self.last_bytes_sent = current_bytes_sent
            self.last_bytes_recv = current_bytes_recv
            self.last_time = current_time
            
            # Convert to Mbps
            upload_mbps = (upload_speed * 8) / (1024 * 1024)
            download_mbps = (download_speed * 8) / (1024 * 1024)
            
            # Get ping latency
            ping_latency = self.get_ping_latency()
            
            return {
                'adapter_name': self.current_adapter,
                'upload_speed': upload_mbps,
                'download_speed': download_mbps,
                'bytes_sent': current_bytes_sent,
                'bytes_received': current_bytes_recv,
                'ping_latency': ping_latency,
                'public_ip': self.public_ip or 'Unknown',
                'isp_name': self.isp_name or 'Unknown',
                'location': self.location or 'Unknown'
            }
        except Exception as e:
            print(f"Error getting network stats: {e}")
            return {
                'adapter_name': self.current_adapter or 'Error',
                'upload_speed': 0.0,
                'download_speed': 0.0,
                'bytes_sent': 0.0,
                'bytes_received': 0.0,
                'ping_latency': 0.0,
                'public_ip': self.public_ip or 'Unknown',
                'isp_name': self.isp_name or 'Unknown',
                'location': self.location or 'Unknown'
            }
    
    def get_ping_latency(self, host: str = "8.8.8.8", count: int = 1) -> float:
        """Get ping latency to a host."""
        try:
            system = platform.system().lower()
            
            if system == "windows":
                cmd = ["ping", "-n", str(count), "-w", "1000", host]
            else:
                cmd = ["ping", "-c", str(count), "-W", "1", host]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                output = result.stdout
                # Parse ping output (simplified)
                if "time=" in output or "time<" in output:
                    # Extract time value
                    import re
                    if system == "windows":
                        pattern = r'time[<=](\d+)ms'
                    else:
                        pattern = r'time=([\d.]+)\s*ms'
                    
                    match = re.search(pattern, output)
                    if match:
                        return float(match.group(1))
            
            # Fallback: try socket connection
            start = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            try:
                sock.connect((host, 80))
                latency = (time.time() - start) * 1000  # Convert to ms
                sock.close()
                return latency
            except:
                return 0.0
        except Exception as e:
            return 0.0
    
    def run_speed_test(self) -> Optional[Dict]:
        """Run a speed test using speedtest-cli."""
        try:
            # Try importing speedtest module (from speedtest-cli package)
            try:
                import speedtest
                st = speedtest.Speedtest()
                st.get_best_server()
                
                download_speed = st.download() / 1000000  # Convert to Mbps
                upload_speed = st.upload() / 1000000  # Convert to Mbps
                ping = st.results.ping
                
                server_info = st.results.server
                server_name = f"{server_info.get('name', 'Unknown')}, {server_info.get('country', 'Unknown')}"
                
                return {
                    'download_mbps': round(download_speed, 2),
                    'upload_mbps': round(upload_speed, 2),
                    'ping_ms': round(ping, 2),
                    'server_name': server_name
                }
            except ImportError:
                # Fallback to CLI command
                import subprocess
                import json
                result = subprocess.run(
                    ['speedtest-cli', '--json'],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    return {
                        'download_mbps': round(data.get('download', 0) / 1000000, 2),
                        'upload_mbps': round(data.get('upload', 0) / 1000000, 2),
                        'ping_ms': round(data.get('ping', 0), 2),
                        'server_name': data.get('server', {}).get('name', 'Unknown')
                    }
                return None
        except Exception as e:
            print(f"Speed test error: {e}")
            return None
    
    def get_total_data_usage(self) -> Tuple[float, float]:
        """Get total data sent and received since app start in bytes."""
        try:
            net_io = psutil.net_io_counters()
            return net_io.bytes_sent, net_io.bytes_recv
        except:
            return 0.0, 0.0
