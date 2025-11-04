"""
Exporter - Handles data export to CSV and JSON formats.
"""
import os
from typing import Optional
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal


class Exporter(QObject):
    """Handles data export functionality."""
    
    export_complete = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, data_manager, parent=None):
        """Initialize exporter."""
        super().__init__(parent)
        self.data_manager = data_manager
    
    def export_csv(self, table: str = "network_stats", seconds: Optional[int] = None) -> bool:
        """Export data to CSV file."""
        try:
            # Get save path
            file_path, _ = QFileDialog.getSaveFileName(
                self.parent(),
                "Export to CSV",
                f"{table}_export.csv",
                "CSV Files (*.csv);;All Files (*.*)"
            )
            
            if not file_path:
                return False
            
            success = self.data_manager.export_to_csv(file_path, table, seconds)
            
            if success:
                self.export_complete.emit(True, f"Successfully exported to {file_path}")
                return True
            else:
                self.export_complete.emit(False, "Export failed")
                return False
        except Exception as e:
            self.export_complete.emit(False, f"Export error: {str(e)}")
            return False
    
    def export_json(self, table: str = "network_stats", seconds: Optional[int] = None) -> bool:
        """Export data to JSON file."""
        try:
            # Get save path
            file_path, _ = QFileDialog.getSaveFileName(
                self.parent(),
                "Export to JSON",
                f"{table}_export.json",
                "JSON Files (*.json);;All Files (*.*)"
            )
            
            if not file_path:
                return False
            
            success = self.data_manager.export_to_json(file_path, table, seconds)
            
            if success:
                self.export_complete.emit(True, f"Successfully exported to {file_path}")
                return True
            else:
                self.export_complete.emit(False, "Export failed")
                return False
        except Exception as e:
            self.export_complete.emit(False, f"Export error: {str(e)}")
            return False
    
    def export_all_tables(self) -> bool:
        """Export all tables to a directory."""
        try:
            dir_path = QFileDialog.getExistingDirectory(
                self.parent(),
                "Select Export Directory"
            )
            
            if not dir_path:
                return False
            
            tables = ["network_stats", "system_stats", "speed_tests", "events"]
            success_count = 0
            
            for table in tables:
                csv_path = os.path.join(dir_path, f"{table}.csv")
                json_path = os.path.join(dir_path, f"{table}.json")
                
                if self.data_manager.export_to_csv(csv_path, table):
                    success_count += 1
                if self.data_manager.export_to_json(json_path, table):
                    success_count += 1
            
            if success_count > 0:
                self.export_complete.emit(
                    True,
                    f"Exported {success_count} files to {dir_path}"
                )
                return True
            else:
                self.export_complete.emit(False, "Export failed")
                return False
        except Exception as e:
            self.export_complete.emit(False, f"Export error: {str(e)}")
            return False
