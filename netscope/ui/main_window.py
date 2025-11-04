"""
Main Window - PyQt5 UI with dark theme, tabs, and real-time monitoring
"""

import sys
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton, QTextEdit, QComboBox, QGroupBox,
    QGridLayout, QProgressBar, QSystemTrayIcon, QMenu, QAction, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
import pyqtgraph as pg
from typing import Optional

import sys
import os

# Handle imports - support both package and direct execution
try:
    from netscope.core.network_monitor import NetworkMonitor
    from netscope.core.system_monitor import SystemMonitor
    from netscope.core.data_manager import DataManager
    from netscope.utils.logger import Logger
    from netscope.utils.speed_test import SpeedTest
except ImportError:
    # Add parent directory to path for direct execution
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from netscope.core.network_monitor import NetworkMonitor
    from netscope.core.system_monitor import SystemMonitor
    from netscope.core.data_manager import DataManager
    from netscope.utils.logger import Logger
    from netscope.utils.speed_test import SpeedTest


class MainWindow(QMainWindow):
    """Main application window"""
    
    APP_VERSION = "1.0.0"
    
    def __init__(self):
        super().__init__()
        
        # Initialize core components
        self.network_monitor = NetworkMonitor()
        self.system_monitor = SystemMonitor()
        self.data_manager = DataManager()
        self.logger = Logger()
        self.speed_test = SpeedTest()
        
        # UI state
        self.refresh_interval = 1000  # 1 second
        self.time_window_seconds = 300  # 5 minutes default
        self.last_speed_test_time = 0
        self.speed_test_interval = 300  # 5 minutes
        self.total_data_sent = 0
        self.total_data_recv = 0
        
        # Graph data
        self.network_times = []
        self.download_speeds = []
        self.upload_speeds = []
        self.cpu_times = []
        self.cpu_values = []
        
        # Setup UI
        self._setup_ui()
        self._setup_dark_theme()
        self._setup_timers()
        self._setup_system_tray()
        
        # Initial data load
        self._update_all()
        self.logger.info("NetScope v{} started".format(self.APP_VERSION))
        self.data_manager.save_event("startup", "Application started")
    
    def _setup_ui(self):
        """Setup the main UI"""
        self.setWindowTitle(f"NetScope v{self.APP_VERSION}")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Top bar
        top_bar = self._create_top_bar()
        main_layout.addWidget(top_bar)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        
        # Overview tab
        overview_tab = self._create_overview_tab()
        self.tabs.addTab(overview_tab, "Overview")
        
        # Graphs tab
        graphs_tab = self._create_graphs_tab()
        self.tabs.addTab(graphs_tab, "Graphs")
        
        # Logs & Exports tab
        logs_tab = self._create_logs_tab()
        self.tabs.addTab(logs_tab, "Logs & Exports")
        
        main_layout.addWidget(self.tabs)
    
    def _create_top_bar(self) -> QWidget:
        """Create top status bar"""
        top_bar = QWidget()
        top_bar.setFixedHeight(40)
        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # System uptime
        self.uptime_label = QLabel("Uptime: --")
        layout.addWidget(self.uptime_label)
        
        layout.addStretch()
        
        # Public IP
        self.ip_label = QLabel("IP: --")
        layout.addWidget(self.ip_label)
        
        layout.addStretch()
        
        # Date/Time
        self.datetime_label = QLabel()
        self._update_datetime()
        layout.addWidget(self.datetime_label)
        
        return top_bar
    
    def _create_overview_tab(self) -> QWidget:
        """Create overview tab with all stats"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Network stats group
        network_group = QGroupBox("Network Statistics")
        network_layout = QGridLayout()
        
        self.interface_label = QLabel("Interface: --")
        self.download_speed_label = QLabel("Download: -- Mbps")
        self.upload_speed_label = QLabel("Upload: -- Mbps")
        self.ping_label = QLabel("Ping: -- ms")
        self.data_sent_label = QLabel("Data Sent: --")
        self.data_recv_label = QLabel("Data Received: --")
        self.total_data_label = QLabel("Total Data: --")
        
        network_layout.addWidget(QLabel("Active Interface:"), 0, 0)
        network_layout.addWidget(self.interface_label, 0, 1)
        network_layout.addWidget(QLabel("Download Speed:"), 1, 0)
        network_layout.addWidget(self.download_speed_label, 1, 1)
        network_layout.addWidget(QLabel("Upload Speed:"), 2, 0)
        network_layout.addWidget(self.upload_speed_label, 2, 1)
        network_layout.addWidget(QLabel("Ping Latency:"), 3, 0)
        network_layout.addWidget(self.ping_label, 3, 1)
        network_layout.addWidget(QLabel("Data Sent:"), 4, 0)
        network_layout.addWidget(self.data_sent_label, 4, 1)
        network_layout.addWidget(QLabel("Data Received:"), 5, 0)
        network_layout.addWidget(self.data_recv_label, 5, 1)
        network_layout.addWidget(QLabel("Total Data (Session):"), 6, 0)
        network_layout.addWidget(self.total_data_label, 6, 1)
        
        network_group.setLayout(network_layout)
        layout.addWidget(network_group)
        
        # Public IP info group
        ip_group = QGroupBox("Network Information")
        ip_layout = QGridLayout()
        
        self.public_ip_label = QLabel("Public IP: --")
        self.isp_label = QLabel("ISP: --")
        self.location_label = QLabel("Location: --")
        
        ip_layout.addWidget(self.public_ip_label, 0, 0, 1, 2)
        ip_layout.addWidget(self.isp_label, 1, 0, 1, 2)
        ip_layout.addWidget(self.location_label, 2, 0, 1, 2)
        
        refresh_ip_btn = QPushButton("Refresh IP Info")
        refresh_ip_btn.clicked.connect(self._refresh_ip_info)
        ip_layout.addWidget(refresh_ip_btn, 3, 0, 1, 2)
        
        ip_group.setLayout(ip_layout)
        layout.addWidget(ip_group)
        
        # System stats group
        system_group = QGroupBox("System Statistics")
        system_layout = QGridLayout()
        
        self.cpu_label = QLabel("CPU: --%")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setMaximum(100)
        self.ram_label = QLabel("RAM: --%")
        self.ram_bar = QProgressBar()
        self.ram_bar.setMaximum(100)
        self.disk_label = QLabel("Disk: --%")
        self.disk_bar = QProgressBar()
        self.disk_bar.setMaximum(100)
        
        system_layout.addWidget(QLabel("CPU Usage:"), 0, 0)
        system_layout.addWidget(self.cpu_label, 0, 1)
        system_layout.addWidget(self.cpu_bar, 0, 2)
        system_layout.addWidget(QLabel("RAM Usage:"), 1, 0)
        system_layout.addWidget(self.ram_label, 1, 1)
        system_layout.addWidget(self.ram_bar, 1, 2)
        system_layout.addWidget(QLabel("Disk Usage:"), 2, 0)
        system_layout.addWidget(self.disk_label, 2, 1)
        system_layout.addWidget(self.disk_bar, 2, 2)
        
        system_group.setLayout(system_layout)
        layout.addWidget(system_group)
        
        # Speed test group
        speed_group = QGroupBox("Speed Test")
        speed_layout = QVBoxLayout()
        
        self.speed_test_label = QLabel("Last test: Not run")
        speed_layout.addWidget(self.speed_test_label)
        
        speed_test_btn = QPushButton("Run Speed Test")
        speed_test_btn.clicked.connect(self._run_speed_test)
        speed_layout.addWidget(speed_test_btn)
        
        speed_group.setLayout(speed_layout)
        layout.addWidget(speed_group)
        
        layout.addStretch()
        
        return widget
    
    def _create_graphs_tab(self) -> QWidget:
        """Create graphs tab with real-time visualizations"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Time window selector
        time_window_layout = QHBoxLayout()
        time_window_layout.addWidget(QLabel("Time Window:"))
        self.time_window_combo = QComboBox()
        self.time_window_combo.addItems([
            "30 seconds", "5 minutes", "10 minutes", "30 minutes", "1 hour", "24 hours"
        ])
        self.time_window_combo.setCurrentIndex(1)  # Default to 5 minutes
        self.time_window_combo.currentIndexChanged.connect(self._on_time_window_changed)
        time_window_layout.addWidget(self.time_window_combo)
        
        time_window_layout.addStretch()
        
        time_window_layout.addWidget(QLabel("Refresh Rate:"))
        self.refresh_rate_combo = QComboBox()
        self.refresh_rate_combo.addItems(["1 sec", "3 sec", "5 sec"])
        self.refresh_rate_combo.setCurrentIndex(0)
        self.refresh_rate_combo.currentIndexChanged.connect(self._on_refresh_rate_changed)
        time_window_layout.addWidget(self.refresh_rate_combo)
        
        layout.addLayout(time_window_layout)
        
        # Network speed graph
        network_graph_group = QGroupBox("Network Speed")
        network_graph_layout = QVBoxLayout()
        
        self.network_graph = pg.PlotWidget()
        self.network_graph.setLabel('left', 'Speed (Mbps)')
        self.network_graph.setLabel('bottom', 'Time')
        self.network_graph.setBackground('black')
        self.network_graph.showGrid(x=True, y=True, alpha=0.3)
        
        self.download_curve = self.network_graph.plot([], [], pen=pg.mkPen('cyan', width=2), name='Download')
        self.upload_curve = self.network_graph.plot([], [], pen=pg.mkPen('magenta', width=2), name='Upload')
        
        self.network_graph.addLegend()
        
        network_graph_layout.addWidget(self.network_graph)
        network_graph_group.setLayout(network_graph_layout)
        layout.addWidget(network_graph_group)
        
        # CPU usage graph
        cpu_graph_group = QGroupBox("CPU Usage")
        cpu_graph_layout = QVBoxLayout()
        
        self.cpu_graph = pg.PlotWidget()
        self.cpu_graph.setLabel('left', 'CPU Usage (%)')
        self.cpu_graph.setLabel('bottom', 'Time')
        self.cpu_graph.setBackground('black')
        self.cpu_graph.showGrid(x=True, y=True, alpha=0.3)
        self.cpu_graph.setYRange(0, 100)
        
        self.cpu_curve = self.cpu_graph.plot([], [], pen=pg.mkPen('yellow', width=2), name='CPU')
        
        cpu_graph_layout.addWidget(self.cpu_graph)
        cpu_graph_group.setLayout(cpu_graph_layout)
        layout.addWidget(cpu_graph_group)
        
        return widget
    
    def _create_logs_tab(self) -> QWidget:
        """Create logs and exports tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Log console
        log_group = QGroupBox("Application Logs")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier", 9))
        self.log_text.setStyleSheet("background-color: #1e1e1e; color: #00ff00;")
        
        log_layout.addWidget(self.log_text)
        
        clear_logs_btn = QPushButton("Clear Logs")
        clear_logs_btn.clicked.connect(self._clear_logs)
        log_layout.addWidget(clear_logs_btn)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Export section
        export_group = QGroupBox("Export Data")
        export_layout = QVBoxLayout()
        
        export_info = QLabel("Export all recorded statistics to CSV or JSON format")
        export_layout.addWidget(export_info)
        
        export_buttons_layout = QHBoxLayout()
        
        export_csv_btn = QPushButton("Export to CSV")
        export_csv_btn.clicked.connect(self._export_csv)
        export_buttons_layout.addWidget(export_csv_btn)
        
        export_json_btn = QPushButton("Export to JSON")
        export_json_btn.clicked.connect(self._export_json)
        export_buttons_layout.addWidget(export_json_btn)
        
        export_layout.addLayout(export_buttons_layout)
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        layout.addStretch()
        
        return widget
    
    def _setup_dark_theme(self):
        """Apply dark theme to the application"""
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(40, 40, 40))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Button, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        
        self.setPalette(dark_palette)
        
        # Set stylesheet for additional dark styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
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
                background-color: #3d3d3d;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
            QComboBox {
                background-color: #3d3d3d;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 3px;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                border-bottom: 2px solid #3a9eff;
            }
        """)
    
    def _setup_timers(self):
        """Setup update timers"""
        # Main update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_all)
        self.update_timer.start(self.refresh_interval)
        
        # Speed test timer
        self.speed_test_timer = QTimer()
        self.speed_test_timer.timeout.connect(self._check_speed_test)
        self.speed_test_timer.start(60000)  # Check every minute
        
        # DateTime update timer
        self.datetime_timer = QTimer()
        self.datetime_timer.timeout.connect(self._update_datetime)
        self.datetime_timer.start(1000)  # Update every second
        
        # Logger connection
        self.logger.log_added.connect(self._on_log_added)
    
    def _setup_system_tray(self):
        """Setup system tray icon"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            
            # Create tray menu
            tray_menu = QMenu(self)
            show_action = QAction("Show", self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)
            
            quit_action = QAction("Quit", self)
            quit_action.triggered.connect(self.close)
            tray_menu.addAction(quit_action)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
            
            # Hide to tray on close
            self.tray_icon.activated.connect(self._tray_icon_activated)
    
    def _tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.raise_()
            self.activateWindow()
    
    def _update_datetime(self):
        """Update date/time display"""
        now = datetime.now()
        self.datetime_label.setText(now.strftime("%Y-%m-%d %H:%M:%S"))
    
    def _update_all(self):
        """Update all statistics"""
        # Network stats
        interface = self.network_monitor.get_primary_adapter()
        if interface:
            stats = self.network_monitor.get_network_stats(interface)
            
            self.interface_label.setText(f"{stats['interface_name']}")
            self.download_speed_label.setText(f"Download: {stats['download_speed']:.2f} Mbps")
            self.upload_speed_label.setText(f"Upload: {stats['upload_speed']:.2f} Mbps")
            self.ping_label.setText(f"Ping: {stats['ping_latency']:.2f} ms")
            
            # Format data sizes
            sent_gb = stats['bytes_sent'] / (1024**3)
            recv_gb = stats['bytes_recv'] / (1024**3)
            self.data_sent_label.setText(f"Data Sent: {sent_gb:.2f} GB")
            self.data_recv_label.setText(f"Data Received: {recv_gb:.2f} GB")
            
            # Session totals
            self.total_data_sent += stats['bytes_sent']
            self.total_data_recv += stats['bytes_recv']
            total_gb = (self.total_data_sent + self.total_data_recv) / (1024**3)
            self.total_data_label.setText(f"Total Data (Session): {total_gb:.2f} GB")
            
            # Save to database
            self.data_manager.save_network_stats(
                stats['interface_name'], stats['bytes_sent'], stats['bytes_recv'],
                stats['upload_speed'], stats['download_speed'], stats['ping_latency'],
                stats['packets_sent'], stats['packets_recv']
            )
            
            # Update graph data
            current_time = datetime.now().timestamp()
            self.network_times.append(current_time)
            self.download_speeds.append(stats['download_speed'])
            self.upload_speeds.append(stats['upload_speed'])
            
            # Keep only data within time window
            cutoff_time = current_time - self.time_window_seconds
            while self.network_times and self.network_times[0] < cutoff_time:
                self.network_times.pop(0)
                self.download_speeds.pop(0)
                self.upload_speeds.pop(0)
        
        # System stats
        system_stats = self.system_monitor.get_all_stats()
        
        self.cpu_label.setText(f"CPU: {system_stats['cpu_percent']:.1f}%")
        self.cpu_bar.setValue(int(system_stats['cpu_percent']))
        
        self.ram_label.setText(f"RAM: {system_stats['ram_percent']:.1f}%")
        self.ram_bar.setValue(int(system_stats['ram_percent']))
        
        self.disk_label.setText(f"Disk: {system_stats['disk_percent']:.1f}%")
        self.disk_bar.setValue(int(system_stats['disk_percent']))
        
        self.uptime_label.setText(f"System Uptime: {system_stats['uptime_formatted']}")
        
        # Save to database
        self.data_manager.save_system_stats(
            system_stats['cpu_percent'], system_stats['ram_percent'],
            system_stats['ram_used'], system_stats['ram_total'],
            system_stats['disk_percent'], system_stats['disk_used'],
            system_stats['disk_total'], system_stats['uptime_seconds']
        )
        
        # Update CPU graph
        current_time = datetime.now().timestamp()
        self.cpu_times.append(current_time)
        self.cpu_values.append(system_stats['cpu_percent'])
        
        cutoff_time = current_time - self.time_window_seconds
        while self.cpu_times and self.cpu_times[0] < cutoff_time:
            self.cpu_times.pop(0)
            self.cpu_values.pop(0)
        
        # Update graphs
        self._update_graphs()
        
        # Public IP info
        ip_info = self.network_monitor.get_public_info()
        self.public_ip_label.setText(f"Public IP: {ip_info['public_ip']}")
        self.isp_label.setText(f"ISP: {ip_info['isp_name']}")
        self.location_label.setText(f"Location: {ip_info['location']}, {ip_info['country']}")
        self.ip_label.setText(f"IP: {ip_info['public_ip']}")
    
    def _update_graphs(self):
        """Update graph displays"""
        # Network speed graph
        if self.network_times:
            # Convert timestamps to relative times
            base_time = self.network_times[0] if self.network_times else 0
            relative_times = [(t - base_time) for t in self.network_times]
            
            self.download_curve.setData(relative_times, self.download_speeds)
            self.upload_curve.setData(relative_times, self.upload_speeds)
            
            if relative_times:
                self.network_graph.setXRange(0, relative_times[-1] if relative_times else 1)
        
        # CPU graph
        if self.cpu_times:
            base_time = self.cpu_times[0] if self.cpu_times else 0
            relative_times = [(t - base_time) for t in self.cpu_times]
            
            self.cpu_curve.setData(relative_times, self.cpu_values)
            
            if relative_times:
                self.cpu_graph.setXRange(0, relative_times[-1] if relative_times else 1)
    
    def _on_time_window_changed(self, index):
        """Handle time window change"""
        windows = [30, 300, 600, 1800, 3600, 86400]
        if index < len(windows):
            self.time_window_seconds = windows[index]
            self.logger.info(f"Time window changed to {self.time_window_combo.currentText()}")
    
    def _on_refresh_rate_changed(self, index):
        """Handle refresh rate change"""
        rates = [1000, 3000, 5000]
        if index < len(rates):
            self.refresh_interval = rates[index]
            self.update_timer.setInterval(self.refresh_interval)
            self.logger.info(f"Refresh rate changed to {self.refresh_rate_combo.currentText()}")
    
    def _refresh_ip_info(self):
        """Refresh public IP information"""
        self.logger.info("Refreshing public IP information...")
        self.network_monitor.refresh_public_info()
        ip_info = self.network_monitor.get_public_info()
        self.data_manager.save_network_info(
            ip_info['public_ip'], ip_info['isp_name'],
            ip_info['location'], ip_info['country']
        )
        self.logger.success("IP information refreshed")
    
    def _run_speed_test(self):
        """Run speed test"""
        if self.speed_test.is_running:
            self.logger.warning("Speed test already running")
            return
        
        self.logger.info("Starting speed test...")
        self.speed_test.run_test_async(
            callback=lambda msg: self.logger.info(msg),
            completion_callback=self._on_speed_test_complete
        )
    
    def _on_speed_test_complete(self, result):
        """Handle speed test completion"""
        if 'error' in result:
            self.logger.error(f"Speed test failed: {result['error']}")
            self.speed_test_label.setText(f"Last test: Failed - {result['error']}")
        else:
            self.logger.success(
                f"Speed test complete: {result['download_mbps']:.2f} Mbps down, "
                f"{result['upload_mbps']:.2f} Mbps up, {result['ping_ms']:.2f} ms"
            )
            self.speed_test_label.setText(
                f"Last test: {result['download_mbps']:.2f} Mbps down / "
                f"{result['upload_mbps']:.2f} Mbps up ({result['ping_ms']:.2f} ms)"
            )
            
            # Save to database
            self.data_manager.save_speed_test(
                result['download_mbps'], result['upload_mbps'],
                result['ping_ms'], result.get('server', '')
            )
            self.data_manager.save_event("speed_test", 
                f"Download: {result['download_mbps']:.2f} Mbps, "
                f"Upload: {result['upload_mbps']:.2f} Mbps")
            
            self.last_speed_test_time = datetime.now().timestamp()
    
    def _check_speed_test(self):
        """Check if automatic speed test should run"""
        current_time = datetime.now().timestamp()
        if (current_time - self.last_speed_test_time) >= self.speed_test_interval:
            if not self.speed_test.is_running:
                self._run_speed_test()
    
    def _on_log_added(self, log_entry):
        """Handle new log entry"""
        if log_entry:
            self.log_text.append(log_entry)
            # Auto-scroll to bottom
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def _clear_logs(self):
        """Clear log display"""
        self.log_text.clear()
        self.logger.clear()
        self.logger.info("Logs cleared")
    
    def _export_csv(self):
        """Export data to CSV"""
        from PyQt5.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export to CSV", "", "CSV Files (*.csv);;All Files (*)"
        )
        if filename:
            try:
                self.data_manager.export_to_csv(filename)
                self.logger.success(f"Data exported to CSV: {filename}")
                QMessageBox.information(self, "Export Complete", f"Data exported to:\n{filename}")
            except Exception as e:
                self.logger.error(f"Export failed: {str(e)}")
                QMessageBox.critical(self, "Export Failed", f"Error: {str(e)}")
    
    def _export_json(self):
        """Export data to JSON"""
        from PyQt5.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export to JSON", "", "JSON Files (*.json);;All Files (*)"
        )
        if filename:
            try:
                self.data_manager.export_to_json(filename)
                self.logger.success(f"Data exported to JSON: {filename}")
                QMessageBox.information(self, "Export Complete", f"Data exported to:\n{filename}")
            except Exception as e:
                self.logger.error(f"Export failed: {str(e)}")
                QMessageBox.critical(self, "Export Failed", f"Error: {str(e)}")
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.data_manager.save_event("shutdown", "Application closed")
        self.logger.info("NetScope shutting down...")
        self.data_manager.close()
        event.accept()
