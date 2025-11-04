"""
Data management module for storing and retrieving monitoring data.
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class DataManager:
    """Manages SQLite database for storing monitoring data."""
    
    def __init__(self, db_path: str = 'data/netscope.db'):
        """Initialize database connection."""
        # Ensure data directory exists
        if os.path.dirname(db_path):
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        else:
            # If no directory specified, use 'data' directory
            os.makedirs('data', exist_ok=True)
            db_path = os.path.join('data', 'netscope.db')
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        cursor = self.conn.cursor()
        
        # Network statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS network_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                interface_name TEXT,
                bytes_sent INTEGER,
                bytes_recv INTEGER,
                upload_speed REAL,
                download_speed REAL,
                packets_sent INTEGER,
                packets_recv INTEGER
            )
        ''')
        
        # System statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu_percent REAL,
                ram_percent REAL,
                ram_used INTEGER,
                ram_total INTEGER,
                disk_percent REAL,
                disk_used INTEGER,
                disk_total INTEGER
            )
        ''')
        
        # Speed test results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS speed_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                download_mbps REAL,
                upload_mbps REAL,
                ping_ms REAL
            )
        ''')
        
        # System events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT,
                description TEXT
            )
        ''')
        
        # Create indexes for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_network_stats_timestamp 
            ON network_stats(timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_system_stats_timestamp 
            ON system_stats(timestamp)
        ''')
        
        self.conn.commit()
    
    def save_network_stats(self, stats: Dict):
        """Save network statistics to database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO network_stats 
                (interface_name, bytes_sent, bytes_recv, upload_speed, 
                 download_speed, packets_sent, packets_recv)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                stats.get('interface'),
                stats.get('bytes_sent', 0),
                stats.get('bytes_recv', 0),
                stats.get('upload_speed', 0),
                stats.get('download_speed', 0),
                stats.get('packets_sent', 0),
                stats.get('packets_recv', 0)
            ))
            self.conn.commit()
        except Exception as e:
            print(f"Error saving network stats: {e}")
    
    def save_system_stats(self, stats: Dict):
        """Save system statistics to database."""
        try:
            cursor = self.conn.cursor()
            ram = stats.get('ram', {})
            disk = stats.get('disk', {})
            
            cursor.execute('''
                INSERT INTO system_stats 
                (cpu_percent, ram_percent, ram_used, ram_total, 
                 disk_percent, disk_used, disk_total)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                stats.get('cpu_percent', 0),
                ram.get('percent', 0),
                ram.get('used', 0),
                ram.get('total', 0),
                disk.get('percent', 0),
                disk.get('used', 0),
                disk.get('total', 0)
            ))
            self.conn.commit()
        except Exception as e:
            print(f"Error saving system stats: {e}")
    
    def save_speed_test(self, result: Dict):
        """Save speed test results to database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO speed_tests 
                (download_mbps, upload_mbps, ping_ms)
                VALUES (?, ?, ?)
            ''', (
                result.get('download_mbps', 0),
                result.get('upload_mbps', 0),
                result.get('ping_ms', 0)
            ))
            self.conn.commit()
        except Exception as e:
            print(f"Error saving speed test: {e}")
    
    def log_event(self, event_type: str, description: str):
        """Log a system event."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO system_events (event_type, description)
                VALUES (?, ?)
            ''', (event_type, description))
            self.conn.commit()
        except Exception as e:
            print(f"Error logging event: {e}")
    
    def get_network_stats(self, window_seconds: int = 3600) -> List[Dict]:
        """Get network statistics within time window."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM network_stats
                WHERE timestamp >= datetime('now', '-' || ? || ' seconds')
                ORDER BY timestamp DESC
            ''', (window_seconds,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting network stats: {e}")
            return []
    
    def get_system_stats(self, window_seconds: int = 3600) -> List[Dict]:
        """Get system statistics within time window."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM system_stats
                WHERE timestamp >= datetime('now', '-' || ? || ' seconds')
                ORDER BY timestamp DESC
            ''', (window_seconds,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting system stats: {e}")
            return []
    
    def get_speed_tests(self, limit: int = 100) -> List[Dict]:
        """Get recent speed test results."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM speed_tests
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting speed tests: {e}")
            return []
    
    def get_events(self, limit: int = 100) -> List[Dict]:
        """Get recent system events."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM system_events
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting events: {e}")
            return []
    
    def export_to_csv(self, output_path: str, table: str = 'network_stats'):
        """Export table data to CSV."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f'SELECT * FROM {table}')
            rows = cursor.fetchall()
            
            if not rows:
                return False
            
            import csv
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow([description[0] for description in cursor.description])
                # Write data
                for row in rows:
                    writer.writerow(row)
            
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def export_to_json(self, output_path: str, table: str = 'network_stats'):
        """Export table data to JSON."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f'SELECT * FROM {table}')
            rows = cursor.fetchall()
            
            data = [dict(row) for row in rows]
            
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        self.conn.close()
