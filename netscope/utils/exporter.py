"""
Export utility for data export functionality.
"""
import json
import csv
from typing import List, Dict
from datetime import datetime


class Exporter:
    """Handles data export to various formats."""
    
    @staticmethod
    def export_to_csv(data: List[Dict], filepath: str) -> bool:
        """Export data to CSV file."""
        try:
            if not data:
                return False
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    @staticmethod
    def export_to_json(data: List[Dict], filepath: str) -> bool:
        """Export data to JSON file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    @staticmethod
    def format_bytes(bytes_value: int) -> str:
        """Format bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    @staticmethod
    def format_speed(bytes_per_second: float) -> str:
        """Format speed to human-readable format."""
        return Exporter.format_bytes(bytes_per_second) + "/s"
