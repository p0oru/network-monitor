"""
Main Window - PyQt5 UI for NetScope
"""
import sys
import threading
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton, QTextEdit, QComboBox, QGroupBox, QGridLayout,
    QSystemTrayIcon, QMenu, QApplication, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette
import pyqtgraph as pg
from typing import Dict, List, Optional

from ..core.network_monitor import NetworkMonitor
from ..core.system_monitor import SystemMonitor
from ..core.data_manager import DataManager
from ..utils.logger import Logger, LogLevel
from ..utils.exporter import Exporter


class MainWindow(QMainWindow):
    """Main application window"""
    
    # Signals for thread-safe UI updates
    network_stats_updated = pyqtSignal(dict)
    system_stats_updated = pyqtSignal(dict)
    log_updated = pyqtSignal(dict)
    
    def __init__(self, version: str = "1.0.0"):
        super().__init__()
        self.version = version
        self.setWindowTitle(f"NetScope v{version}")
        self.setMinimumSize(1200, 800)
        
        # Initialize components
        self.data_manager = DataManager()
        self.logger = Logger()
        self.logger.set_callback(self._on_log_updated)
        
        # Monitors
        self.network_monitor = NetworkMonitor(callback=self._on_network_stats)
        self.system_monitor = SystemMonitor(callback=self._on_system_stats)
        
        # Data storage
        self.network_data: List[Dict] = []
        self.system_data: List[Dict] = []
        self.current_time_window = 300  # 5 minutes default
        
        # Graph refresh rate
        self.graph_refresh_rate = 1.0  # seconds
        
        # Setup UI
        self._setup_ui()
        self._setup_dark_theme()
        self._setup_timers()
        self._setup_signals()
        self._setup_tray_icon()
        
        # Start monitoring
        self.logger.info("NetScope started", {"version": version})
        self.logger.event("Application startup")
        self.network_monitor.start_monitoring(self.graph_refresh_rate)
        self.system_monitor.start_monitoring(self.graph_refresh_rate)
        
        # Auto speed test timer (every 5 minutes when active)
        self.speed_test_timer = QTimer()
        self.speed_test_timer.timeout.connect(self._run_speed_test)
        self.speed_test_timer.start(300000)  # 5 minutes
    
    def _setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Top bar
        top_bar = self._create_top_bar()
        main_layout.addWidget(top_bar)
        
        # Main content (tabs)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #555;
                background: #1e1e1e;
            }
            QTabBar::tab {
                background: #2d2d2d;
                color: #fff;
                padding: 8px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #3d3d3d;
            }
            QTabBar::tab:hover {
                background: #353535;
            }
        """)
        
        # Overview tab
        overview_tab = self._create_overview_tab()
        self.tabs.addTab(overview_tab, "Overview")
        
        # Graphs tab
        graphs_tab = self._create_graphs_tab()
        self.tabs.addTab(graphs_tab, "Graphs")
        
        # Logs tab
        logs_tab = self._create_logs_tab()
        self.tabs.addTab(logs_tab, "Logs & Export")
        
        main_layout.addWidget(self.tabs)
    
    def _create_top_bar(self) -> QWidget:
        """Create top status bar"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # System uptime
        self.uptime_label = QLabel("Uptime: --")
        self.uptime_label.setStyleSheet("color: #aaa; font-size: 11px;")
        layout.addWidget(self.uptime_label)
        
        layout.addStretch()
        
        # Public IP
        self.ip_label = QLabel("IP: Loading...")
        self.ip_label.setStyleSheet("color: #aaa; font-size: 11px;")
        layout.addWidget(self.ip_label)
        
        layout.addStretch()
        
        # Date/time
        self.datetime_label = QLabel()
        self.datetime_label.setStyleSheet("color: #aaa; font-size: 11px;")
        layout.addWidget(self.datetime_label)
        
        # Update datetime every second
        self.datetime_timer = QTimer()
        self.datetime_timer.timeout.connect(self._update_datetime)
        self.datetime_timer.start(1000)
        self._update_datetime()
        
        return widget
    
    def _create_overview_tab(self) -> QWidget:
        """Create overview tab with all stats"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Network stats section
        network_group = QGroupBox("Network Statistics")
        network_group.setStyleSheet(self._get_groupbox_style())
        network_layout = QGridLayout(network_group)
        
        # Network labels
        self.network_labels = {}
        network_stats = [
            ("Active Adapters", "adapters"),
            ("Download Speed", "download_speed"),
            ("Upload Speed", "upload_speed"),
            ("Ping", "ping"),
            ("Data Sent", "data_sent"),
            ("Data Received", "data_recv"),
            ("ISP", "isp"),
            ("Location", "location")
        ]
        
        row = 0
        for label, key in network_stats:
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("color: #bbb;")
            value_widget = QLabel("--")
            value_widget.setStyleSheet("color: #fff; font-weight: bold;")
            value_widget.setWordWrap(True)
            
            network_layout.addWidget(label_widget, row, 0)
            network_layout.addWidget(value_widget, row, 1)
            
            self.network_labels[key] = value_widget
            row += 1
        
        layout.addWidget(network_group)
        
        # System stats section
        system_group = QGroupBox("System Statistics")
        system_group.setStyleSheet(self._get_groupbox_style())
        system_layout = QGridLayout(system_group)
        
        # System labels
        self.system_labels = {}
        system_stats = [
            ("CPU Usage", "cpu"),
            ("RAM Usage", "ram"),
            ("RAM Total", "ram_total"),
            ("Disk Usage", "disk"),
            ("Disk Total", "disk_total"),
            ("System Uptime", "uptime")
        ]
        
        row = 0
        for label, key in system_stats:
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("color: #bbb;")
            value_widget = QLabel("--")
            value_widget.setStyleSheet("color: #fff; font-weight: bold;")
            
            system_layout.addWidget(label_widget, row, 0)
            system_layout.addWidget(value_widget, row, 1)
            
            self.system_labels[key] = value_widget
            row += 1
        
        layout.addWidget(system_group)
        
        layout.addStretch()
        
        return widget
    
    def _create_graphs_tab(self) -> QWidget:
        """Create graphs tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Time window selector
        controls_layout.addWidget(QLabel("Time Window:"))
        self.time_window_combo = QComboBox()
        self.time_window_combo.addItems([
            "30 seconds", "5 minutes", "10 minutes", 
            "30 minutes", "1 hour", "24 hours"
        ])
        self.time_window_combo.setCurrentIndex(1)  # 5 minutes
        self.time_window_combo.currentIndexChanged.connect(self._on_time_window_changed)
        controls_layout.addWidget(self.time_window_combo)
        
        controls_layout.addStretch()
        
        # Refresh rate selector
        controls_layout.addWidget(QLabel("Refresh Rate:"))
        self.refresh_rate_combo = QComboBox()
        self.refresh_rate_combo.addItems(["1 sec", "3 sec", "5 sec"])
        self.refresh_rate_combo.setCurrentIndex(0)
        self.refresh_rate_combo.currentIndexChanged.connect(self._on_refresh_rate_changed)
        controls_layout.addWidget(self.refresh_rate_combo)
        
        layout.addLayout(controls_layout)
        
        # Network speed graph
        network_graph_group = QGroupBox("Network Speed")
        network_graph_group.setStyleSheet(self._get_groupbox_style())
        network_graph_layout = QVBoxLayout(network_graph_group)
        
        self.network_graph = pg.PlotWidget()
        self.network_graph.setBackground('#1e1e1e')
        self.network_graph.setLabel('left', 'Speed (Mbps)', color='#fff')
        self.network_graph.setLabel('bottom', 'Time', color='#fff')
        self.network_graph.showGrid(x=True, y=True, alpha=0.3)
        self.network_graph.setTitle("Upload/Download Speed", color='#fff', size='12pt')
        
        # Download line (blue)
        self.download_curve = self.network_graph.plot([], [], pen=pg.mkPen(color='#4a9eff', width=2), name='Download')
        # Upload line (green)
        self.upload_curve = self.network_graph.plot([], [], pen=pg.mkPen(color='#4aff4a', width=2), name='Upload')
        
        # Legend
        self.network_graph.addLegend()
        
        network_graph_layout.addWidget(self.network_graph)
        layout.addWidget(network_graph_group)
        
        # CPU usage graph
        cpu_graph_group = QGroupBox("CPU Usage")
        cpu_graph_group.setStyleSheet(self._get_groupbox_style())
        cpu_graph_layout = QVBoxLayout(cpu_graph_group)
        
        self.cpu_graph = pg.PlotWidget()
        self.cpu_graph.setBackground('#1e1e1e')
        self.cpu_graph.setLabel('left', 'Usage (%)', color='#fff')
        self.cpu_graph.setLabel('bottom', 'Time', color='#fff')
        self.cpu_graph.showGrid(x=True, y=True, alpha=0.3)
        self.cpu_graph.setTitle("CPU Usage", color='#fff', size='12pt')
        self.cpu_graph.setYRange(0, 100)
        
        # CPU line (red)
        self.cpu_curve = self.cpu_graph.plot([], [], pen=pg.mkPen(color='#ff4a4a', width=2), name='CPU')
        
        cpu_graph_layout.addWidget(self.cpu_graph)
        layout.addWidget(cpu_graph_group)
        
        return widget
    
    def _create_logs_tab(self) -> QWidget:
        """Create logs and export tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Export section
        export_group = QGroupBox("Export Data")
        export_group.setStyleSheet(self._get_groupbox_style())
        export_layout = QHBoxLayout(export_group)
        
        export_csv_btn = QPushButton("Export to CSV")
        export_csv_btn.setStyleSheet(self._get_button_style())
        export_csv_btn.clicked.connect(self._export_to_csv)
        export_layout.addWidget(export_csv_btn)
        
        export_json_btn = QPushButton("Export to JSON")
        export_json_btn.setStyleSheet(self._get_button_style())
        export_json_btn.clicked.connect(self._export_to_json)
        export_layout.addWidget(export_json_btn)
        
        layout.addWidget(export_group)
        
        # Logs console
        logs_group = QGroupBox("System Logs")
        logs_group.setStyleSheet(self._get_groupbox_style())
        logs_layout = QVBoxLayout(logs_group)
        
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #fff;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10pt;
                border: 1px solid #555;
            }
        """)
        
        logs_layout.addWidget(self.log_console)
        
        # Clear logs button
        clear_logs_btn = QPushButton("Clear Logs")
        clear_logs_btn.setStyleSheet(self._get_button_style())
        clear_logs_btn.clicked.connect(self._clear_logs)
        logs_layout.addWidget(clear_logs_btn)
        
        layout.addWidget(logs_group)
        
        return widget
    
    def _setup_dark_theme(self):
        """Setup dark theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #fff;
            }
        """)
        
        # Set dark palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(30, 30, 30))
        palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
        palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(45, 45, 45))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        self.setPalette(palette)
    
    def _setup_timers(self):
        """Setup update timers"""
        # Graph update timer
        self.graph_update_timer = QTimer()
        self.graph_update_timer.timeout.connect(self._update_graphs)
        self.graph_update_timer.start(int(self.graph_refresh_rate * 1000))
    
    def _setup_signals(self):
        """Setup signal connections"""
        self.network_stats_updated.connect(self._update_network_ui)
        self.system_stats_updated.connect(self._update_system_ui)
        self.log_updated.connect(self._append_log)
    
    def _setup_tray_icon(self):
        """Setup system tray icon"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_ComputerIcon))
            
            tray_menu = QMenu()
            show_action = tray_menu.addAction("Show")
            show_action.triggered.connect(self.show)
            quit_action = tray_menu.addAction("Quit")
            quit_action.triggered.connect(self.close)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.activated.connect(self._tray_icon_activated)
            self.tray_icon.show()
    
    def _tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.raise_()
            self.activateWindow()
    
    def _get_groupbox_style(self) -> str:
        """Get groupbox style"""
        return """
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
        """
    
    def _get_button_style(self) -> str:
        """Get button style"""
        return """
            QPushButton {
                background-color: #3d3d3d;
                color: #fff;
                border: 1px solid #555;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
        """
    
    def _on_network_stats(self, stats: Dict):
        """Handle network stats update (called from monitoring thread)"""
        self.network_stats_updated.emit(stats)
        
        # Store data
        self.network_data.append(stats)
        # Keep only data within time window
        cutoff = stats['timestamp'] - self.current_time_window
        self.network_data = [d for d in self.network_data if d['timestamp'] >= cutoff]
        
        # Log to database
        for adapter in stats.get('adapters', []):
            self.data_manager.log_network_stats({
                'timestamp': stats['timestamp'],
                'adapter': adapter['name'],
                'upload_speed': adapter['upload_speed'],
                'download_speed': adapter['download_speed'],
                'ping': stats['ping'],
                'bytes_sent': adapter['bytes_sent'],
                'bytes_recv': adapter['bytes_recv'],
                'public_ip': stats['public_ip'],
                'isp': stats['isp'],
                'location': stats['location']
            })
    
    def _on_system_stats(self, stats: Dict):
        """Handle system stats update (called from monitoring thread)"""
        self.system_stats_updated.emit(stats)
        
        # Store data
        self.system_data.append(stats)
        # Keep only data within time window
        cutoff = stats['timestamp'] - self.current_time_window
        self.system_data = [d for d in self.system_data if d['timestamp'] >= cutoff]
        
        # Log to database
        self.data_manager.log_system_stats(stats)
    
    def _on_log_updated(self, log_entry: Dict):
        """Handle log update"""
        self.log_updated.emit(log_entry)
    
    @pyqtSlot(dict)
    def _update_network_ui(self, stats: Dict):
        """Update network UI elements (thread-safe)"""
        # Active adapters
        adapters = stats.get('adapters', [])
        adapter_names = [a['name'] for a in adapters]
        self.network_labels['adapters'].setText(', '.join(adapter_names) if adapter_names else 'None')
        
        # Download speed (convert to Mbps)
        download_mbps = (stats.get('total_download_speed', 0) * 8) / (1024 * 1024)
        self.network_labels['download_speed'].setText(f"{download_mbps:.2f} Mbps")
        
        # Upload speed
        upload_mbps = (stats.get('total_upload_speed', 0) * 8) / (1024 * 1024)
        self.network_labels['upload_speed'].setText(f"{upload_mbps:.2f} Mbps")
        
        # Ping
        ping = stats.get('ping', 0)
        self.network_labels['ping'].setText(f"{ping:.1f} ms")
        
        # Data sent/received
        total_sent = stats.get('total_bytes_sent', 0)
        total_recv = stats.get('total_bytes_recv', 0)
        self.network_labels['data_sent'].setText(self._format_bytes(total_sent))
        self.network_labels['data_recv'].setText(self._format_bytes(total_recv))
        
        # ISP and location
        self.network_labels['isp'].setText(stats.get('isp', 'Unknown'))
        self.network_labels['location'].setText(stats.get('location', 'Unknown'))
        
        # Update IP label in top bar
        self.ip_label.setText(f"IP: {stats.get('public_ip', 'Loading...')}")
    
    @pyqtSlot(dict)
    def _update_system_ui(self, stats: Dict):
        """Update system UI elements (thread-safe)"""
        # CPU
        cpu = stats.get('cpu_usage', 0)
        self.system_labels['cpu'].setText(f"{cpu:.1f}%")
        
        # RAM
        ram_percent = stats.get('ram_usage', 0)
        ram_used = stats.get('ram_used', 0)
        ram_total = stats.get('ram_total', 0)
        self.system_labels['ram'].setText(f"{ram_percent:.1f}% ({self._format_bytes(ram_used)})")
        self.system_labels['ram_total'].setText(self._format_bytes(ram_total))
        
        # Disk
        disk_percent = stats.get('disk_usage', 0)
        disk_used = stats.get('disk_used', 0)
        disk_total = stats.get('disk_total', 0)
        self.system_labels['disk'].setText(f"{disk_percent:.1f}% ({self._format_bytes(disk_used)})")
        self.system_labels['disk_total'].setText(self._format_bytes(disk_total))
        
        # Uptime
        uptime = stats.get('uptime', 0)
        uptime_str = self.system_monitor.format_uptime(uptime)
        self.system_labels['uptime'].setText(uptime_str)
        self.uptime_label.setText(f"Uptime: {uptime_str}")
    
    @pyqtSlot(dict)
    def _append_log(self, log_entry: Dict):
        """Append log to console (thread-safe)"""
        timestamp = log_entry['timestamp'].strftime("%H:%M:%S")
        level = log_entry['level']
        message = log_entry['message']
        
        # Color based on level
        color_map = {
            'INFO': '#aaa',
            'WARNING': '#ffaa00',
            'ERROR': '#ff4444',
            'SUCCESS': '#44ff44',
            'EVENT': '#4a9eff'
        }
        color = color_map.get(level, '#fff')
        
        log_text = f'<span style="color: {color}">[{timestamp}] [{level}] {message}</span><br>'
        self.log_console.append(log_text)
        
        # Auto-scroll to bottom
        scrollbar = self.log_console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _update_graphs(self):
        """Update graph displays"""
        # Network speed graph
        if self.network_data:
            times = [d['timestamp'] for d in self.network_data]
            download_speeds = [(d['total_download_speed'] * 8) / (1024 * 1024) for d in self.network_data]
            upload_speeds = [(d['total_upload_speed'] * 8) / (1024 * 1024) for d in self.network_data]
            
            # Normalize times to start from 0
            if times:
                start_time = times[0]
                times = [t - start_time for t in times]
            
            self.download_curve.setData(times, download_speeds)
            self.upload_curve.setData(times, upload_speeds)
        
        # CPU graph
        if self.system_data:
            times = [d['timestamp'] for d in self.system_data]
            cpu_usage = [d['cpu_usage'] for d in self.system_data]
            
            # Normalize times to start from 0
            if times:
                start_time = times[0]
                times = [t - start_time for t in times]
            
            self.cpu_curve.setData(times, cpu_usage)
    
    def _update_datetime(self):
        """Update date/time label"""
        now = datetime.now()
        self.datetime_label.setText(now.strftime("%Y-%m-%d %H:%M:%S"))
    
    def _on_time_window_changed(self, index: int):
        """Handle time window change"""
        windows = [30, 300, 600, 1800, 3600, 86400]
        self.current_time_window = windows[index]
        self.logger.info(f"Time window changed to {self.time_window_combo.currentText()}")
    
    def _on_refresh_rate_changed(self, index: int):
        """Handle refresh rate change"""
        rates = [1.0, 3.0, 5.0]
        self.graph_refresh_rate = rates[index]
        self.graph_update_timer.setInterval(int(self.graph_refresh_rate * 1000))
        self.logger.info(f"Refresh rate changed to {self.refresh_rate_combo.currentText()}")
    
    def _run_speed_test(self):
        """Run speed test in background"""
        def run_test():
            self.logger.info("Starting speed test...")
            result = self.network_monitor.run_speed_test()
            if result.get('success'):
                self.logger.success(
                    f"Speed test completed: {result['download']:.2f} Mbps down, {result['upload']:.2f} Mbps up",
                    result
                )
                self.data_manager.log_speed_test(
                    result['download'],
                    result['upload'],
                    result['ping']
                )
            else:
                self.logger.error(f"Speed test failed: {result.get('error', 'Unknown error')}")
        
        threading.Thread(target=run_test, daemon=True).start()
    
    def _export_to_csv(self):
        """Export data to CSV"""
        try:
            filename = Exporter.generate_export_filename("netscope_export", "csv")
            network_stats = self.data_manager.get_network_stats(86400)  # Last 24 hours
            if network_stats:
                Exporter.export_to_csv(network_stats, filename)
                self.logger.success(f"Data exported to CSV: {filename}")
                QMessageBox.information(self, "Export Successful", f"Data exported to:\n{filename}")
            else:
                QMessageBox.warning(self, "No Data", "No data available to export")
        except Exception as e:
            self.logger.error(f"CSV export failed: {str(e)}")
            QMessageBox.critical(self, "Export Failed", f"Error: {str(e)}")
    
    def _export_to_json(self):
        """Export data to JSON"""
        try:
            filename = Exporter.generate_export_filename("netscope_export", "json")
            network_stats = self.data_manager.get_network_stats(86400)  # Last 24 hours
            if network_stats:
                Exporter.export_to_json(network_stats, filename)
                self.logger.success(f"Data exported to JSON: {filename}")
                QMessageBox.information(self, "Export Successful", f"Data exported to:\n{filename}")
            else:
                QMessageBox.warning(self, "No Data", "No data available to export")
        except Exception as e:
            self.logger.error(f"JSON export failed: {str(e)}")
            QMessageBox.critical(self, "Export Failed", f"Error: {str(e)}")
    
    def _clear_logs(self):
        """Clear log console"""
        self.log_console.clear()
        self.logger.info("Log console cleared")
    
    def _format_bytes(self, bytes: float) -> str:
        """Format bytes as human-readable string"""
        return self.system_monitor.format_bytes(bytes)
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.logger.event("Application shutdown")
        self.network_monitor.stop_monitoring()
        self.system_monitor.stop_monitoring()
        self.data_manager.close()
        event.accept()