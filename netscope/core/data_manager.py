"""
Data Manager - Handles SQLite database operations for storing historical monitoring data.
"""
import sqlite3
import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import threading


def get_base_path():
    """Get base path for data storage (works for both development and PyInstaller)."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = os.path.dirname(sys.executable)
    else:
        # Running as script
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return base_path


class DataManager:
    """Manages SQLite database for storing network and system monitoring data."""
    
    def __init__(self, db_path: str = None):
        """Initialize data manager with database path."""
        if db_path is None:
            base_path = get_base_path()
            db_path = os.path.join(base_path, "data", "network_logs.db")
        self.db_path = db_path
        self.lock = threading.Lock()
        self._ensure_database()
    
    def _ensure_database(self):
        """Ensure database file and directory exist, create schema if needed."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Network stats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS network_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    adapter_name TEXT,
                    upload_speed REAL,
                    download_speed REAL,
                    ping_latency REAL,
                    bytes_sent REAL,
                    bytes_received REAL,
                    public_ip TEXT,
                    isp_name TEXT,
                    location TEXT
                )
            ''')
            
            # System stats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    cpu_usage REAL,
                    ram_usage REAL,
                    disk_usage REAL,
                    uptime REAL
                )
            ''')
            
            # Speed test results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS speed_tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    download_mbps REAL,
                    upload_mbps REAL,
                    ping_ms REAL,
                    server_name TEXT
                )
            ''')
            
            # Events log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    event_type TEXT,
                    message TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
    
    def log_network_stats(self, stats: Dict):
        """Log network statistics to database."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO network_stats 
                (timestamp, adapter_name, upload_speed, download_speed, ping_latency,
                 bytes_sent, bytes_received, public_ip, isp_name, location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().timestamp(),
                stats.get('adapter_name'),
                stats.get('upload_speed'),
                stats.get('download_speed'),
                stats.get('ping_latency'),
                stats.get('bytes_sent'),
                stats.get('bytes_received'),
                stats.get('public_ip'),
                stats.get('isp_name'),
                stats.get('location')
            ))
            
            conn.commit()
            conn.close()
    
    def log_system_stats(self, stats: Dict):
        """Log system statistics to database."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_stats 
                (timestamp, cpu_usage, ram_usage, disk_usage, uptime)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().timestamp(),
                stats.get('cpu_usage'),
                stats.get('ram_usage'),
                stats.get('disk_usage'),
                stats.get('uptime')
            ))
            
            conn.commit()
            conn.close()
    
    def log_speed_test(self, download_mbps: float, upload_mbps: float, 
                       ping_ms: float, server_name: str = ""):
        """Log speed test results."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO speed_tests 
                (timestamp, download_mbps, upload_mbps, ping_ms, server_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().timestamp(),
                download_mbps,
                upload_mbps,
                ping_ms,
                server_name
            ))
            
            conn.commit()
            conn.close()
    
    def log_event(self, event_type: str, message: str):
        """Log system event."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO events (timestamp, event_type, message)
                VALUES (?, ?, ?)
            ''', (
                datetime.now().timestamp(),
                event_type,
                message
            ))
            
            conn.commit()
            conn.close()
    
    def get_network_history(self, seconds: int = 3600) -> List[Dict]:
        """Get network stats history for the last N seconds."""
        cutoff_time = datetime.now().timestamp() - seconds
        
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, adapter_name, upload_speed, download_speed, 
                       ping_latency, bytes_sent, bytes_received
                FROM network_stats
                WHERE timestamp >= ?
                ORDER BY timestamp ASC
            ''', (cutoff_time,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'timestamp': row[0],
                    'adapter_name': row[1],
                    'upload_speed': row[2],
                    'download_speed': row[3],
                    'ping_latency': row[4],
                    'bytes_sent': row[5],
                    'bytes_received': row[6]
                }
                for row in rows
            ]
    
    def get_system_history(self, seconds: int = 3600) -> List[Dict]:
        """Get system stats history for the last N seconds."""
        cutoff_time = datetime.now().timestamp() - seconds
        
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, cpu_usage, ram_usage, disk_usage, uptime
                FROM system_stats
                WHERE timestamp >= ?
                ORDER BY timestamp ASC
            ''', (cutoff_time,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'timestamp': row[0],
                    'cpu_usage': row[1],
                    'ram_usage': row[2],
                    'disk_usage': row[3],
                    'uptime': row[4]
                }
                for row in rows
            ]
    
    def get_recent_events(self, limit: int = 100) -> List[Dict]:
        """Get recent events."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, event_type, message
                FROM events
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'timestamp': row[0],
                    'event_type': row[1],
                    'message': row[2]
                }
                for row in reversed(rows)  # Return in chronological order
            ]
    
    def export_to_csv(self, output_path: str, table: str = "network_stats", 
                     seconds: Optional[int] = None) -> bool:
        """Export data to CSV file."""
        try:
            import csv
            
            cutoff_time = None
            if seconds:
                cutoff_time = datetime.now().timestamp() - seconds
            
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                if cutoff_time:
                    cursor.execute(f'SELECT * FROM {table} WHERE timestamp >= ?', (cutoff_time,))
                else:
                    cursor.execute(f'SELECT * FROM {table}')
                
                rows = cursor.fetchall()
                
                # Get column names
                cursor.execute(f'PRAGMA table_info({table})')
                columns = [col[1] for col in cursor.fetchall()]
                
                conn.close()
            
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                writer.writerows(rows)
            
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False
    
    def export_to_json(self, output_path: str, table: str = "network_stats",
                      seconds: Optional[int] = None) -> bool:
        """Export data to JSON file."""
        try:
            cutoff_time = None
            if seconds:
                cutoff_time = datetime.now().timestamp() - seconds
            
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                if cutoff_time:
                    cursor.execute(f'SELECT * FROM {table} WHERE timestamp >= ?', (cutoff_time,))
                else:
                    cursor.execute(f'SELECT * FROM {table}')
                
                rows = cursor.fetchall()
                
                # Get column names
                cursor.execute(f'PRAGMA table_info({table})')
                columns = [col[1] for col in cursor.fetchall()]
                
                conn.close()
            
            data = [dict(zip(columns, row)) for row in rows]
            
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False
