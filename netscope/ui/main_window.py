"""
Main window UI for NetScope application.
"""
import sys
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTabWidget, QPushButton, QComboBox, QTextEdit, QGroupBox,
    QGridLayout, QProgressBar, QFrame
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QPalette, QColor
import pyqtgraph as pg
from pyqtgraph import PlotWidget
import time

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.network_monitor import NetworkMonitor
from core.system_monitor import SystemMonitor
from core.data_manager import DataManager
from utils.logger import Logger
from utils.exporter import Exporter


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetScope v1.0.0")
        self.setMinimumSize(1200, 800)
        
        # Initialize components
        self.network_monitor = NetworkMonitor(callback=self.on_network_update)
        self.system_monitor = SystemMonitor()
        self.data_manager = DataManager()
        self.logger = Logger()
        self.exporter = Exporter()
        
        # Data storage
        self.network_data = {'time': [], 'upload': [], 'download': [], 'cpu': []}
        self.time_window = 30  # seconds
        self.refresh_rate = 1  # seconds
        
        # UI setup
        self.init_ui()
        self.apply_dark_theme()
        
        # Start monitoring
        self.start_monitoring()
        
        # Log startup
        self.logger.info("NetScope started")
        self.data_manager.log_event("startup", "Application started")
    
    def init_ui(self):
        """Initialize user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Top bar
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)
        
        # Main content tabs
        tabs = QTabWidget()
        tabs.addTab(self.create_overview_tab(), "Overview")
        tabs.addTab(self.create_graphs_tab(), "Graphs")
        tabs.addTab(self.create_logs_tab(), "Logs & Export")
        
        main_layout.addWidget(tabs)
    
    def create_top_bar(self) -> QWidget:
        """Create top information bar."""
        bar = QFrame()
        bar.setFrameShape(QFrame.StyledPanel)
        bar.setMaximumHeight(50)
        
        layout = QHBoxLayout()
        bar.setLayout(layout)
        
        # System uptime
        self.uptime_label = QLabel("Uptime: --")
        layout.addWidget(self.uptime_label)
        
        layout.addWidget(QFrame())  # Spacer
        
        # IP info
        self.ip_label = QLabel("IP: Loading...")
        layout.addWidget(self.ip_label)
        
        layout.addWidget(QFrame())  # Spacer
        
        # Date/time
        self.datetime_label = QLabel()
        self.update_datetime()
        layout.addWidget(self.datetime_label)
        
        # Update datetime every second
        self.datetime_timer = QTimer()
        self.datetime_timer.timeout.connect(self.update_datetime)
        self.datetime_timer.start(1000)
        
        return bar
    
    def create_overview_tab(self) -> QWidget:
        """Create overview tab with all stats."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Network stats section
        network_group = QGroupBox("Network Statistics")
        network_layout = QGridLayout()
        
        self.network_labels = {
            'interface': QLabel("Interface: --"),
            'upload_speed': QLabel("Upload: --"),
            'download_speed': QLabel("Download: --"),
            'ping': QLabel("Ping: --"),
            'data_sent': QLabel("Data Sent: --"),
            'data_recv': QLabel("Data Received: --"),
            'total_data': QLabel("Total Data: --"),
            'public_ip': QLabel("Public IP: --"),
            'isp': QLabel("ISP: --"),
            'location': QLabel("Location: --")
        }
        
        row = 0
        for key, label in self.network_labels.items():
            network_layout.addWidget(label, row // 2, row % 2)
            row += 1
        
        network_group.setLayout(network_layout)
        layout.addWidget(network_group)
        
        # System stats section
        system_group = QGroupBox("System Statistics")
        system_layout = QGridLayout()
        
        self.system_labels = {
            'cpu': QLabel("CPU: --"),
            'ram': QLabel("RAM: --"),
            'disk': QLabel("Disk: --"),
            'system_uptime': QLabel("System Uptime: --")
        }
        
        # CPU progress bar
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setMaximum(100)
        system_layout.addWidget(QLabel("CPU Usage:"), 0, 0)
        system_layout.addWidget(self.cpu_progress, 0, 1)
        
        # RAM progress bar
        self.ram_progress = QProgressBar()
        self.ram_progress.setMaximum(100)
        system_layout.addWidget(QLabel("RAM Usage:"), 1, 0)
        system_layout.addWidget(self.ram_progress, 1, 1)
        
        # Disk progress bar
        self.disk_progress = QProgressBar()
        self.disk_progress.setMaximum(100)
        system_layout.addWidget(QLabel("Disk Usage:"), 2, 0)
        system_layout.addWidget(self.disk_progress, 2, 1)
        
        row = 3
        for key, label in self.system_labels.items():
            system_layout.addWidget(label, row, 0, 1, 2)
            row += 1
        
        system_group.setLayout(system_layout)
        layout.addWidget(system_group)
        
        layout.addStretch()
        
        return widget
    
    def create_graphs_tab(self) -> QWidget:
        """Create graphs tab with real-time visualizations."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Time window selector
        controls_layout.addWidget(QLabel("Time Window:"))
        self.time_window_combo = QComboBox()
        self.time_window_combo.addItems([
            "30 seconds", "5 minutes", "10 minutes", 
            "30 minutes", "1 hour", "24 hours"
        ])
        self.time_window_combo.currentIndexChanged.connect(self.on_time_window_changed)
        controls_layout.addWidget(self.time_window_combo)
        
        # Refresh rate selector
        controls_layout.addWidget(QLabel("Refresh Rate:"))
        self.refresh_rate_combo = QComboBox()
        self.refresh_rate_combo.addItems(["1 sec", "3 sec", "5 sec"])
        self.refresh_rate_combo.currentIndexChanged.connect(self.on_refresh_rate_changed)
        controls_layout.addWidget(self.refresh_rate_combo)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Network speed graph
        network_graph_group = QGroupBox("Network Speed")
        network_graph_layout = QVBoxLayout()
        
        self.network_graph = PlotWidget()
        self.network_graph.setLabel('left', 'Speed (MB/s)')
        self.network_graph.setLabel('bottom', 'Time')
        self.network_graph.addLegend()
        self.network_graph.setBackground('black')
        
        self.upload_curve = self.network_graph.plot(
            [], [], pen='g', name='Upload'
        )
        self.download_curve = self.network_graph.plot(
            [], [], pen='r', name='Download'
        )
        
        network_graph_layout.addWidget(self.network_graph)
        network_graph_group.setLayout(network_graph_layout)
        layout.addWidget(network_graph_group)
        
        # CPU usage graph
        cpu_graph_group = QGroupBox("CPU Usage")
        cpu_graph_layout = QVBoxLayout()
        
        self.cpu_graph = PlotWidget()
        self.cpu_graph.setLabel('left', 'CPU Usage (%)')
        self.cpu_graph.setLabel('bottom', 'Time')
        self.cpu_graph.setBackground('black')
        self.cpu_graph.setYRange(0, 100)
        
        self.cpu_curve = self.cpu_graph.plot(
            [], [], pen='y', name='CPU'
        )
        
        cpu_graph_layout.addWidget(self.cpu_graph)
        cpu_graph_group.setLayout(cpu_graph_layout)
        layout.addWidget(cpu_graph_group)
        
        return widget
    
    def create_logs_tab(self) -> QWidget:
        """Create logs and export tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Export buttons
        export_layout = QHBoxLayout()
        
        export_csv_btn = QPushButton("Export to CSV")
        export_csv_btn.clicked.connect(self.export_to_csv)
        export_layout.addWidget(export_csv_btn)
        
        export_json_btn = QPushButton("Export to JSON")
        export_json_btn.clicked.connect(self.export_to_json)
        export_layout.addWidget(export_json_btn)
        
        export_layout.addStretch()
        layout.addLayout(export_layout)
        
        # Log console
        log_group = QGroupBox("Application Logs")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier", 9))
        log_layout.addWidget(self.log_text)
        
        # Connect logger signal
        self.logger.log_added.connect(self.log_text.append)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        return widget
    
    def apply_dark_theme(self):
        """Apply dark theme to the application."""
        palette = QPalette()
        
        # Window colors
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        
        # Base colors
        palette.setColor(QPalette.Base, QColor(40, 40, 40))
        palette.setColor(QPalette.AlternateBase, QColor(50, 50, 50))
        
        # Text colors
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
        
        # Button colors
        palette.setColor(QPalette.Button, QColor(50, 50, 50))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        
        self.setPalette(palette)
        
        # Set stylesheet for additional styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #404040;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #353535;
            }
            QProgressBar {
                border: 1px solid #555;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 2px;
            }
            QTabWidget::pane {
                border: 1px solid #555;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2e2e2e;
                color: white;
                padding: 8px 20px;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                border-bottom: 2px solid #4CAF50;
            }
            QTextEdit {
                background-color: #252525;
                border: 1px solid #555;
                color: #00ff00;
            }
        """)
    
    def start_monitoring(self):
        """Start monitoring threads."""
        # Start network monitoring
        self.network_monitor.start_monitoring(interval=self.refresh_rate)
        
        # Start system stats update timer
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_system_stats)
        self.stats_timer.start(self.refresh_rate * 1000)
        
        # Get public IP info (async)
        self.update_public_ip()
        
        self.logger.info("Monitoring started")
    
    def on_network_update(self, stats: Dict):
        """Callback for network statistics updates."""
        if 'error' in stats:
            self.logger.error(f"Network error: {stats['error']}")
            return
        
        # Update labels
        interface = stats.get('interface', 'Unknown')
        upload_speed = stats.get('upload_speed', 0) / (1024 * 1024)  # MB/s
        download_speed = stats.get('download_speed', 0) / (1024 * 1024)  # MB/s
        
        self.network_labels['interface'].setText(f"Interface: {interface}")
        self.network_labels['upload_speed'].setText(
            f"Upload: {upload_speed:.2f} MB/s"
        )
        self.network_labels['download_speed'].setText(
            f"Download: {download_speed:.2f} MB/s"
        )
        self.network_labels['data_sent'].setText(
            f"Data Sent: {Exporter.format_bytes(stats.get('bytes_sent', 0))}"
        )
        self.network_labels['data_recv'].setText(
            f"Data Received: {Exporter.format_bytes(stats.get('bytes_recv', 0))}"
        )
        
        total = stats.get('bytes_sent', 0) + stats.get('bytes_recv', 0)
        self.network_labels['total_data'].setText(
            f"Total Data: {Exporter.format_bytes(total)}"
        )
        
        # Update ping
        if self.network_monitor.ping_latency:
            avg_ping = sum(self.network_monitor.ping_latency.values()) / len(self.network_monitor.ping_latency.values())
            self.network_labels['ping'].setText(f"Ping: {avg_ping:.2f} ms")
        
        # Save to database
        self.data_manager.save_network_stats(stats)
        
        # Update graph data
        current_time = stats.get('timestamp', time.time())
        self.network_data['time'].append(current_time)
        self.network_data['upload'].append(upload_speed)
        self.network_data['download'].append(download_speed)
        
        # Limit data to time window
        self.trim_data_to_window()
        
        # Update graphs
        self.update_graphs()
    
    def update_system_stats(self):
        """Update system statistics."""
        stats = self.system_monitor.get_all_stats()
        
        # Update labels
        cpu_percent = stats['cpu_percent']
        self.system_labels['cpu'].setText(f"CPU: {cpu_percent:.1f}%")
        self.cpu_progress.setValue(int(cpu_percent))
        
        ram = stats['ram']
        ram_percent = ram['percent']
        self.system_labels['ram'].setText(
            f"RAM: {Exporter.format_bytes(ram['used'])} / "
            f"{Exporter.format_bytes(ram['total'])} ({ram_percent:.1f}%)"
        )
        self.ram_progress.setValue(int(ram_percent))
        
        disk = stats['disk']
        if 'error' not in disk:
            disk_percent = disk['percent']
            self.system_labels['disk'].setText(
                f"Disk: {Exporter.format_bytes(disk['used'])} / "
                f"{Exporter.format_bytes(disk['total'])} ({disk_percent:.1f}%)"
            )
            self.disk_progress.setValue(int(disk_percent))
        
        uptime = stats['system_uptime']
        self.system_labels['system_uptime'].setText(
            f"System Uptime: {uptime['formatted']}"
        )
        
        # Update uptime label in top bar
        app_uptime = stats['app_uptime']
        self.uptime_label.setText(f"Uptime: {app_uptime['formatted']}")
        
        # Save to database
        self.data_manager.save_system_stats(stats)
        
        # Update CPU graph
        current_time = stats['timestamp']
        self.network_data['time'].append(current_time)
        self.network_data['cpu'].append(cpu_percent)
        
        # Limit data to time window
        self.trim_data_to_window()
        
        # Update graphs
        self.update_graphs()
    
    def update_public_ip(self):
        """Update public IP information (async)."""
        def fetch_ip():
            info = self.network_monitor.get_public_ip_info()
            self.network_labels['public_ip'].setText(f"Public IP: {info['ip']}")
            self.network_labels['isp'].setText(f"ISP: {info['isp']}")
            self.network_labels['location'].setText(f"Location: {info['location']}")
            self.ip_label.setText(f"IP: {info['ip']}")
            self.logger.info(f"Public IP: {info['ip']} ({info['location']})")
        
        import threading
        threading.Thread(target=fetch_ip, daemon=True).start()
    
    def update_datetime(self):
        """Update date/time label."""
        now = datetime.now()
        self.datetime_label.setText(now.strftime("%Y-%m-%d %H:%M:%S"))
    
    def trim_data_to_window(self):
        """Trim data arrays to current time window."""
        if not self.network_data['time']:
            return
        
        current_time = time.time()
        window_start = current_time - self.time_window
        
        # Find index where data is still within window
        indices_to_keep = [
            i for i, t in enumerate(self.network_data['time'])
            if t >= window_start
        ]
        
        if indices_to_keep:
            start_idx = indices_to_keep[0]
            self.network_data['time'] = self.network_data['time'][start_idx:]
            self.network_data['upload'] = self.network_data['upload'][start_idx:]
            self.network_data['download'] = self.network_data['download'][start_idx:]
            self.network_data['cpu'] = self.network_data['cpu'][start_idx:]
    
    def update_graphs(self):
        """Update graph displays."""
        if not self.network_data['time']:
            return
        
        # Normalize time to start from 0
        if self.network_data['time']:
            time_base = self.network_data['time'][0]
            normalized_times = [t - time_base for t in self.network_data['time']]
            
            # Update network speed graph
            if len(normalized_times) == len(self.network_data['upload']):
                self.upload_curve.setData(normalized_times, self.network_data['upload'])
                self.download_curve.setData(normalized_times, self.network_data['download'])
            
            # Update CPU graph
            if len(normalized_times) == len(self.network_data['cpu']):
                self.cpu_curve.setData(normalized_times, self.network_data['cpu'])
    
    def on_time_window_changed(self, index: int):
        """Handle time window selection change."""
        windows = [30, 300, 600, 1800, 3600, 86400]  # seconds
        self.time_window = windows[index]
        self.trim_data_to_window()
        self.update_graphs()
        self.logger.info(f"Time window changed to {self.time_window_combo.currentText()}")
    
    def on_refresh_rate_changed(self, index: int):
        """Handle refresh rate selection change."""
        rates = [1, 3, 5]  # seconds
        self.refresh_rate = rates[index]
        
        # Restart monitoring with new rate
        self.network_monitor.stop_monitoring()
        self.network_monitor.start_monitoring(interval=self.refresh_rate)
        
        self.stats_timer.setInterval(self.refresh_rate * 1000)
        self.logger.info(f"Refresh rate changed to {self.refresh_rate} seconds")
    
    def export_to_csv(self):
        """Export data to CSV."""
        from PyQt5.QtWidgets import QFileDialog
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export to CSV", "", "CSV Files (*.csv)"
        )
        
        if filepath:
            # Export network stats
            success = self.data_manager.export_to_csv(filepath, 'network_stats')
            if success:
                self.logger.info(f"Data exported to {filepath}")
            else:
                self.logger.error("Export failed")
    
    def export_to_json(self):
        """Export data to JSON."""
        from PyQt5.QtWidgets import QFileDialog
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export to JSON", "", "JSON Files (*.json)"
        )
        
        if filepath:
            # Export network stats
            success = self.data_manager.export_to_json(filepath, 'network_stats')
            if success:
                self.logger.info(f"Data exported to {filepath}")
            else:
                self.logger.error("Export failed")
    
    def closeEvent(self, event):
        """Handle application close."""
        self.logger.info("NetScope shutting down")
        self.data_manager.log_event("shutdown", "Application stopped")
        self.network_monitor.stop_monitoring()
        self.data_manager.close()
        event.accept()
