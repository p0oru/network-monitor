"""
Data Manager - Handles SQLite database operations for storing monitoring data
"""

import sqlite3
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class DataManager:
    """Manages SQLite database for storing network and system statistics"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection and create tables if needed"""
        if db_path is None:
            # Determine base directory (workspace root or executable directory)
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                base_dir = os.path.dirname(sys.executable)
            else:
                # Running as script - find workspace root
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, "data", "netscope.db")
        
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Network statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS network_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                interface_name TEXT,
                bytes_sent INTEGER,
                bytes_recv INTEGER,
                upload_speed REAL,
                download_speed REAL,
                ping_latency REAL,
                packets_sent INTEGER,
                packets_recv INTEGER
            )
        """)
        
        # System statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu_percent REAL,
                ram_percent REAL,
                ram_used INTEGER,
                ram_total INTEGER,
                disk_percent REAL,
                disk_used INTEGER,
                disk_total INTEGER,
                uptime_seconds INTEGER
            )
        """)
        
        # Speed test results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS speed_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                download_mbps REAL,
                upload_mbps REAL,
                ping_ms REAL,
                server_name TEXT
            )
        """)
        
        # System events/logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT,
                description TEXT
            )
        """)
        
        # Network info (IP, ISP, location) - cached
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS network_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                public_ip TEXT,
                isp_name TEXT,
                location TEXT,
                country TEXT
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_network_stats_timestamp 
            ON network_stats(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_system_stats_timestamp 
            ON system_stats(timestamp)
        """)
        
        self.conn.commit()
    
    def save_network_stats(self, interface_name: str, bytes_sent: int, bytes_recv: int,
                          upload_speed: float, download_speed: float, ping_latency: float,
                          packets_sent: int, packets_recv: int):
        """Save network statistics to database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO network_stats 
            (interface_name, bytes_sent, bytes_recv, upload_speed, download_speed, 
             ping_latency, packets_sent, packets_recv)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (interface_name, bytes_sent, bytes_recv, upload_speed, download_speed,
              ping_latency, packets_sent, packets_recv))
        self.conn.commit()
    
    def save_system_stats(self, cpu_percent: float, ram_percent: float, ram_used: int,
                         ram_total: int, disk_percent: float, disk_used: int,
                         disk_total: int, uptime_seconds: int):
        """Save system statistics to database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO system_stats 
            (cpu_percent, ram_percent, ram_used, ram_total, disk_percent, 
             disk_used, disk_total, uptime_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (cpu_percent, ram_percent, ram_used, ram_total, disk_percent,
              disk_used, disk_total, uptime_seconds))
        self.conn.commit()
    
    def save_speed_test(self, download_mbps: float, upload_mbps: float, 
                       ping_ms: float, server_name: str = ""):
        """Save speed test results"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO speed_tests (download_mbps, upload_mbps, ping_ms, server_name)
            VALUES (?, ?, ?, ?)
        """, (download_mbps, upload_mbps, ping_ms, server_name))
        self.conn.commit()
    
    def save_event(self, event_type: str, description: str):
        """Save system event to log"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO system_events (event_type, description)
            VALUES (?, ?)
        """, (event_type, description))
        self.conn.commit()
    
    def save_network_info(self, public_ip: str, isp_name: str, location: str, country: str):
        """Save/update network information (IP, ISP, location)"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO network_info (public_ip, isp_name, location, country)
            VALUES (?, ?, ?, ?)
        """, (public_ip, isp_name, location, country))
        self.conn.commit()
    
    def get_network_stats(self, time_window_seconds: int = 3600) -> List[Dict]:
        """Get network statistics within time window"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM network_stats 
            WHERE timestamp >= datetime('now', '-' || ? || ' seconds')
            ORDER BY timestamp ASC
        """, (time_window_seconds,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_system_stats(self, time_window_seconds: int = 3600) -> List[Dict]:
        """Get system statistics within time window"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM system_stats 
            WHERE timestamp >= datetime('now', '-' || ? || ' seconds')
            ORDER BY timestamp ASC
        """, (time_window_seconds,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_latest_network_info(self) -> Optional[Dict]:
        """Get latest network info (IP, ISP, location)"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM network_info ORDER BY timestamp DESC LIMIT 1
        """)
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def export_to_csv(self, output_path: str):
        """Export all data to CSV file"""
        import csv
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Export network stats
            writer.writerow(['=== Network Statistics ==='])
            writer.writerow(['timestamp', 'interface', 'bytes_sent', 'bytes_recv',
                           'upload_speed', 'download_speed', 'ping_latency'])
            for row in self.get_network_stats(86400 * 365):  # 1 year
                writer.writerow([
                    row['timestamp'], row['interface_name'], row['bytes_sent'],
                    row['bytes_recv'], row['upload_speed'], row['download_speed'],
                    row['ping_latency']
                ])
            
            # Export system stats
            writer.writerow(['=== System Statistics ==='])
            writer.writerow(['timestamp', 'cpu_percent', 'ram_percent', 'disk_percent', 'uptime'])
            for row in self.get_system_stats(86400 * 365):
                writer.writerow([
                    row['timestamp'], row['cpu_percent'], row['ram_percent'],
                    row['disk_percent'], row['uptime_seconds']
                ])
            
            # Export speed tests
            writer.writerow(['=== Speed Tests ==='])
            writer.writerow(['timestamp', 'download_mbps', 'upload_mbps', 'ping_ms', 'server'])
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM speed_tests ORDER BY timestamp ASC")
            for row in cursor.fetchall():
                writer.writerow([
                    row['timestamp'], row['download_mbps'], row['upload_mbps'],
                    row['ping_ms'], row['server_name']
                ])
    
    def export_to_json(self, output_path: str):
        """Export all data to JSON file"""
        data = {
            'network_stats': self.get_network_stats(86400 * 365),
            'system_stats': self.get_system_stats(86400 * 365),
            'speed_tests': [],
            'network_info': self.get_latest_network_info()
        }
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM speed_tests ORDER BY timestamp ASC")
        data['speed_tests'] = [dict(row) for row in cursor.fetchall()]
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def close(self):
        """Close database connection"""
        self.conn.close()
