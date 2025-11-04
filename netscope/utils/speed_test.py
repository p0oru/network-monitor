"""
Speed Test - Lightweight bandwidth testing using speedtest-cli
"""

import speedtest
from typing import Dict, Optional
from threading import Thread


class SpeedTest:
    """Handles speed testing functionality"""
    
    def __init__(self):
        self.st = None
        self.is_running = False
        self.last_result: Optional[Dict] = None
    
    def run_test(self, callback=None) -> Dict:
        """Run speed test synchronously"""
        if self.is_running:
            return {'error': 'Test already running'}
        
        self.is_running = True
        result = {'download_mbps': 0.0, 'upload_mbps': 0.0, 'ping_ms': 0.0, 'server': ''}
        
        try:
            if callback:
                callback("Initializing speed test...")
            
            st = speedtest.Speedtest()
            
            if callback:
                callback("Selecting best server...")
            st.get_best_server()
            
            if callback:
                callback("Testing download speed...")
            download_speed = st.download() / 1_000_000  # Convert to Mbps
            
            if callback:
                callback("Testing upload speed...")
            upload_speed = st.upload() / 1_000_000  # Convert to Mbps
            
            ping = st.results.ping
            server_name = st.results.server.get('name', 'Unknown')
            
            result = {
                'download_mbps': round(download_speed, 2),
                'upload_mbps': round(upload_speed, 2),
                'ping_ms': round(ping, 2),
                'server': server_name
            }
            
            self.last_result = result
            
            if callback:
                callback(f"Speed test complete: {download_speed:.2f} Mbps down, {upload_speed:.2f} Mbps up")
        
        except Exception as e:
            result = {'error': str(e)}
            if callback:
                callback(f"Speed test failed: {str(e)}")
        
        finally:
            self.is_running = False
        
        return result
    
    def run_test_async(self, callback=None, completion_callback=None):
        """Run speed test asynchronously in a thread"""
        def test_thread():
            result = self.run_test(callback)
            if completion_callback:
                completion_callback(result)
        
        thread = Thread(target=test_thread, daemon=True)
        thread.start()
        return thread
    
    def get_last_result(self) -> Optional[Dict]:
        """Get last speed test result"""
        return self.last_result
