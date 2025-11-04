"""
Exporter - Handles data export to CSV and JSON formats
"""
import csv
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional


class Exporter:
    """Handles data export functionality"""
    
    @staticmethod
    def _get_base_path():
        """Get base path for exports (works in both dev and exe mode)"""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            return os.path.dirname(sys.executable)
        else:
            # Running as script
            return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    @staticmethod
    def export_to_csv(data: List[Dict], output_path: str, fieldnames: Optional[List[str]] = None):
        """Export data to CSV file"""
        if not data:
            raise ValueError("No data to export")
        
        # Get fieldnames from first row if not provided
        if not fieldnames:
            fieldnames = list(data[0].keys())
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in data:
                # Convert datetime objects to strings
                clean_row = {}
                for key, value in row.items():
                    if isinstance(value, datetime):
                        clean_row[key] = value.isoformat()
                    else:
                        clean_row[key] = value
                writer.writerow(clean_row)
    
    @staticmethod
    def export_to_json(data: List[Dict], output_path: str, indent: int = 2):
        """Export data to JSON file"""
        if not data:
            raise ValueError("No data to export")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Convert datetime objects to ISO format strings
        clean_data = []
        for row in data:
            clean_row = {}
            for key, value in row.items():
                if isinstance(value, datetime):
                    clean_row[key] = value.isoformat()
                else:
                    clean_row[key] = value
            clean_data.append(clean_row)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(clean_data, f, indent=indent, ensure_ascii=False)
    
    @staticmethod
    def generate_export_filename(base_name: str, extension: str) -> str:
        """Generate timestamped export filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_name}_{timestamp}.{extension}"
        
        # Create exports directory if it doesn't exist
        base_path = Exporter._get_base_path()
        exports_dir = os.path.join(base_path, "data", "exports")
        os.makedirs(exports_dir, exist_ok=True)
        
        return os.path.join(exports_dir, filename)