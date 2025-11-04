"""
Data Manager - Handles SQLite database operations and data storage
"""
import sqlite3
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any


class DataManager:
    """Manages data storage and retrieval from SQLite database"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the data manager with database path"""
        # Determine database path (works in both dev and exe mode)
        if db_path is None:
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                base_path = os.path.dirname(sys.executable)
            else:
                # Running as script
                base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_path, "data", "netscope.db")
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database schema"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Network stats table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS network_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                adapter TEXT,
                upload_speed REAL,
                download_speed REAL,
                ping REAL,
                bytes_sent REAL,
                bytes_recv REAL,
                public_ip TEXT,
                isp TEXT,
                location TEXT
            )
        """)
        
        # System stats table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                cpu_usage REAL,
                ram_usage REAL,
                ram_total REAL,
                disk_usage REAL,
                disk_total REAL,
                uptime REAL
            )
        """)
        
        # Events log table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                event_type TEXT,
                message TEXT,
                data TEXT
            )
        """)
        
        # Speed test results table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS speed_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                download_speed REAL,
                upload_speed REAL,
                ping REAL,
                server_name TEXT
            )
        """)
        
        self.conn.commit()
    
    def log_network_stats(self, stats: Dict[str, Any]):
        """Log network statistics"""
        self.cursor.execute("""
            INSERT INTO network_stats 
            (timestamp, adapter, upload_speed, download_speed, ping, 
             bytes_sent, bytes_recv, public_ip, isp, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            stats.get('timestamp', datetime.now().timestamp()),
            stats.get('adapter', ''),
            stats.get('upload_speed', 0),
            stats.get('download_speed', 0),
            stats.get('ping', 0),
            stats.get('bytes_sent', 0),
            stats.get('bytes_recv', 0),
            stats.get('public_ip', ''),
            stats.get('isp', ''),
            stats.get('location', '')
        ))
        self.conn.commit()
    
    def log_system_stats(self, stats: Dict[str, Any]):
        """Log system statistics"""
        self.cursor.execute("""
            INSERT INTO system_stats 
            (timestamp, cpu_usage, ram_usage, ram_total, disk_usage, disk_total, uptime)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            stats.get('timestamp', datetime.now().timestamp()),
            stats.get('cpu_usage', 0),
            stats.get('ram_usage', 0),
            stats.get('ram_total', 0),
            stats.get('disk_usage', 0),
            stats.get('disk_total', 0),
            stats.get('uptime', 0)
        ))
        self.conn.commit()
    
    def log_event(self, event_type: str, message: str, data: Optional[Dict] = None):
        """Log system event"""
        self.cursor.execute("""
            INSERT INTO events (timestamp, event_type, message, data)
            VALUES (?, ?, ?, ?)
        """, (
            datetime.now().timestamp(),
            event_type,
            message,
            json.dumps(data) if data else None
        ))
        self.conn.commit()
    
    def log_speed_test(self, download: float, upload: float, ping: float, server: str = ""):
        """Log speed test result"""
        self.cursor.execute("""
            INSERT INTO speed_tests (timestamp, download_speed, upload_speed, ping, server_name)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().timestamp(),
            download,
            upload,
            ping,
            server
        ))
        self.conn.commit()
    
    def get_network_stats(self, time_window: int = 3600) -> List[Dict]:
        """Get network stats within time window (seconds)"""
        cutoff = datetime.now().timestamp() - time_window
        self.cursor.execute("""
            SELECT * FROM network_stats 
            WHERE timestamp >= ? 
            ORDER BY timestamp ASC
        """, (cutoff,))
        
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def get_system_stats(self, time_window: int = 3600) -> List[Dict]:
        """Get system stats within time window (seconds)"""
        cutoff = datetime.now().timestamp() - time_window
        self.cursor.execute("""
            SELECT * FROM system_stats 
            WHERE timestamp >= ? 
            ORDER BY timestamp ASC
        """, (cutoff,))
        
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def get_recent_events(self, limit: int = 100) -> List[Dict]:
        """Get recent events"""
        self.cursor.execute("""
            SELECT * FROM events 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def export_to_csv(self, output_path: str, table: str = "network_stats"):
        """Export table data to CSV"""
        import csv
        
        self.cursor.execute(f"SELECT * FROM {table}")
        columns = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)
    
    def export_to_json(self, output_path: str, table: str = "network_stats"):
        """Export table data to JSON"""
        self.cursor.execute(f"SELECT * FROM {table}")
        columns = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        
        data = [dict(zip(columns, row)) for row in rows]
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()