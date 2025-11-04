"""
Network monitoring module for real-time network statistics.
"""
import sys
import psutil
import time
import socket
import subprocess
import threading
from typing import Dict, List, Optional, Callable


class NetworkMonitor:
    """Monitors network adapters and provides real-time statistics."""
    
    def __init__(self, callback: Optional[Callable] = None):
        self.callback = callback
        self.running = False
        self.monitor_thread = None
        self.last_stats = {}
        self.current_interface = None
        self.speed_test_results = {}
        self.ping_latency = {}
        self.data_sent_total = 0
        self.data_received_total = 0
        self.start_time = time.time()
        
    def get_active_interfaces(self) -> List[Dict]:
        """Get all active network interfaces."""
        interfaces = []
        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()
        
        for interface_name, stats_info in stats.items():
            if stats_info.isup:
                addrs_info = addrs.get(interface_name, [])
                ip_address = None
                for addr in addrs_info:
                    if addr.family == socket.AF_INET:
                        ip_address = addr.address
                        break
                
                interfaces.append({
                    'name': interface_name,
                    'ip': ip_address,
                    'isup': True,
                    'speed': stats_info.speed if stats_info.speed > 0 else None
                })
        
        return interfaces
    
    def get_primary_interface(self) -> Optional[str]:
        """Detect the primary active network interface."""
        interfaces = self.get_active_interfaces()
        if not interfaces:
            return None
        
        # Prefer interfaces with IP addresses
        for interface in interfaces:
            if interface['ip'] and interface['ip'] != '127.0.0.1':
                return interface['name']
        
        # Fallback to first active interface
        return interfaces[0]['name'] if interfaces else None
    
    def get_network_stats(self, interface: str) -> Dict:
        """Get current network statistics for an interface."""
        try:
            counters = psutil.net_io_counters(pernic=True)
            if interface not in counters:
                return {}
            
            counter = counters[interface]
            current_time = time.time()
            
            if interface in self.last_stats:
                last_time, last_sent, last_recv = self.last_stats[interface]
                time_diff = current_time - last_time
                
                if time_diff > 0:
                    upload_speed = (counter.bytes_sent - last_sent) / time_diff
                    download_speed = (counter.bytes_recv - last_recv) / time_diff
                else:
                    upload_speed = 0
                    download_speed = 0
            else:
                upload_speed = 0
                download_speed = 0
            
            self.last_stats[interface] = (
                current_time,
                counter.bytes_sent,
                counter.bytes_recv
            )
            
            self.data_sent_total = counter.bytes_sent
            self.data_received_total = counter.bytes_recv
            
            return {
                'interface': interface,
                'bytes_sent': counter.bytes_sent,
                'bytes_recv': counter.bytes_recv,
                'packets_sent': counter.packets_sent,
                'packets_recv': counter.packets_recv,
                'upload_speed': upload_speed,  # bytes per second
                'download_speed': download_speed,  # bytes per second
                'timestamp': current_time
            }
        except Exception as e:
            return {'error': str(e)}
    
    def measure_ping(self, target: str = '8.8.8.8') -> float:
        """Measure ping latency to a target (in milliseconds)."""
        try:
            if sys.platform == 'win32':
                result = subprocess.run(
                    ['ping', '-n', '1', '-w', '1000', target],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
            else:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '1', target],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
            
            if result.returncode == 0:
                # Parse ping output
                output = result.stdout
                if 'time=' in output or 'time<' in output:
                    import re
                    match = re.search(r'time[=<>](\d+(?:\.\d+)?)', output)
                    if match:
                        return float(match.group(1))
            
            return None
        except Exception:
            return None
    
    def get_public_ip_info(self) -> Dict:
        """Get public IP, ISP, and location information."""
        try:
            import requests
            response = requests.get('https://ipinfo.io/json', timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'ip': data.get('ip', 'Unknown'),
                    'isp': data.get('org', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('region', 'Unknown'),
                    'country': data.get('country', 'Unknown'),
                    'location': f"{data.get('city', '')}, {data.get('region', '')}"
                }
        except Exception as e:
            try:
                # Fallback to simpler API
                response = requests.get('https://api.ipify.org?format=json', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'ip': data.get('ip', 'Unknown'),
                        'isp': 'Unknown',
                        'city': 'Unknown',
                        'region': 'Unknown',
                        'country': 'Unknown',
                        'location': 'Unknown'
                    }
            except Exception:
                pass
        
        return {
            'ip': 'Unknown',
            'isp': 'Unknown',
            'city': 'Unknown',
            'region': 'Unknown',
            'country': 'Unknown',
            'location': 'Unknown'
        }
    
    def run_speed_test(self) -> Dict:
        """Run a lightweight speed test."""
        try:
            # Try speedtest-cli first (command line version)
            import subprocess
            result = subprocess.run(
                ['speedtest-cli', '--simple'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Parse output: "Ping: X ms\nDownload: Y Mbit/s\nUpload: Z Mbit/s"
                import re
                ping_match = re.search(r'Ping:\s+([\d.]+)\s+ms', result.stdout)
                download_match = re.search(r'Download:\s+([\d.]+)\s+Mbit/s', result.stdout)
                upload_match = re.search(r'Upload:\s+([\d.]+)\s+Mbit/s', result.stdout)
                
                ping = float(ping_match.group(1)) if ping_match else 0
                download = float(download_match.group(1)) if download_match else 0
                upload = float(upload_match.group(1)) if upload_match else 0
                
                result_dict = {
                    'download_mbps': round(download, 2),
                    'upload_mbps': round(upload, 2),
                    'ping_ms': round(ping, 2),
                    'timestamp': time.time()
                }
                
                self.speed_test_results = result_dict
                return result_dict
            else:
                # Fallback to speedtest library if available
                try:
                    import speedtest
                    st = speedtest.Speedtest()
                    st.get_best_server()
                    
                    download_speed = st.download() / 1_000_000  # Convert to Mbps
                    upload_speed = st.upload() / 1_000_000  # Convert to Mbps
                    ping = st.results.ping
                    
                    result_dict = {
                        'download_mbps': round(download_speed, 2),
                        'upload_mbps': round(upload_speed, 2),
                        'ping_ms': round(ping, 2),
                        'timestamp': time.time()
                    }
                    
                    self.speed_test_results = result_dict
                    return result_dict
                except ImportError:
                    return {'error': 'speedtest-cli not available'}
        except Exception as e:
            return {'error': str(e)}
    
    def start_monitoring(self, interval: float = 1.0):
        """Start monitoring in a separate thread."""
        if self.running:
            return
        
        self.running = True
        self.current_interface = self.get_primary_interface()
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
    
    def _monitor_loop(self, interval: float):
        """Main monitoring loop."""
        ping_targets = ['8.8.8.8', '1.1.1.1', '208.67.222.222']
        ping_index = 0
        speed_test_counter = 0
        
        while self.running:
            try:
                # Update primary interface if needed
                if not self.current_interface:
                    self.current_interface = self.get_primary_interface()
                
                if self.current_interface:
                    stats = self.get_network_stats(self.current_interface)
                    
                    # Measure ping periodically
                    if ping_index < len(ping_targets):
                        latency = self.measure_ping(ping_targets[ping_index])
                        if latency:
                            self.ping_latency[ping_targets[ping_index]] = latency
                        ping_index = (ping_index + 1) % len(ping_targets)
                    
                    # Run speed test every few minutes (when counter reaches threshold)
                    speed_test_counter += 1
                    if speed_test_counter >= 300:  # Every 5 minutes at 1s interval
                        speed_test_counter = 0
                        threading.Thread(
                            target=self.run_speed_test,
                            daemon=True
                        ).start()
                    
                    if self.callback:
                        self.callback(stats)
                
                time.sleep(interval)
            except Exception as e:
                if self.callback:
                    self.callback({'error': str(e)})
                time.sleep(interval)
    
    def get_total_data_usage(self) -> Dict:
        """Get total data usage since app start."""
        return {
            'sent': self.data_sent_total,
            'received': self.data_received_total,
            'total': self.data_sent_total + self.data_received_total
        }


import sys
