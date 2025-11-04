"""
Main Window - PyQt5 GUI for NetScope network and system monitor.
"""
import sys
from datetime import datetime
from typing import Optional
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton, QTextEdit, QComboBox, QGroupBox,
    QGridLayout, QSystemTrayIcon, QMenu, QAction,
    QApplication, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ..core.network_monitor import NetworkMonitor
from ..core.system_monitor import SystemMonitor
from ..core.data_manager import DataManager
from ..utils.logger import Logger
from ..utils.exporter import Exporter


class SpeedTestThread(QThread):
    """Thread for running speed tests without blocking UI."""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, network_monitor):
        super().__init__()
        self.network_monitor = network_monitor
    
    def run(self):
        try:
            result = self.network_monitor.run_speed_test()
            if result:
                self.finished.emit(result)
            else:
                self.error.emit("Speed test failed")
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window."""
    
    VERSION = "1.0.0"
    
    def __init__(self):
        super().__init__()
        
        # Initialize core components
        self.data_manager = DataManager()
        self.network_monitor = NetworkMonitor()
        self.system_monitor = SystemMonitor()
        self.logger = Logger(self.data_manager)
        self.exporter = Exporter(self.data_manager, self)
        
        # UI state
        self.refresh_rate = 1000  # milliseconds
        self.time_window = 3600  # seconds (1 hour default)
        self.app_start_time = datetime.now()
        self.speed_test_timer = None
        self.speed_test_thread = None
        
        # Data storage for graphs
        self.network_data = {'time': [], 'upload': [], 'download': []}
        self.system_data = {'time': [], 'cpu': []}
        
        # Setup UI
        self.setup_ui()
        self.setup_timers()
        self.setup_system_tray()
        self.apply_dark_theme()
        
        # Connect signals
        self.exporter.export_complete.connect(self.on_export_complete)
        self.logger.log_updated.connect(self.update_log_display)
        
        # Log startup
        self.logger.info(f"NetScope v{self.VERSION} started")
        self.logger.info("Initializing monitoring...")
        
        # Initial update
        self.update_all_stats()
    
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle(f"NetScope v{self.VERSION}")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top bar
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)
        
        # Main content area with tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #333;
                background: #1e1e1e;
            }
            QTabBar::tab {
                background: #2d2d2d;
                color: #ffffff;
                padding: 8px 16px;
                border: 1px solid #333;
            }
            QTabBar::tab:selected {
                background: #0078d4;
            }
            QTabBar::tab:hover {
                background: #3d3d3d;
            }
        """)
        
        # Overview tab
        overview_tab = self.create_overview_tab()
        self.tab_widget.addTab(overview_tab, "Overview")
        
        # Graphs tab
        graphs_tab = self.create_graphs_tab()
        self.tab_widget.addTab(graphs_tab, "Graphs")
        
        # Logs & Export tab
        logs_tab = self.create_logs_tab()
        self.tab_widget.addTab(logs_tab, "Logs & Export")
        
        main_layout.addWidget(self.tab_widget)
    
    def create_top_bar(self) -> QWidget:
        """Create top status bar."""
        bar = QWidget()
        bar.setFixedHeight(40)
        bar.setStyleSheet("background: #252526; border-bottom: 1px solid #333;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # System uptime
        self.uptime_label = QLabel("Uptime: --")
        self.uptime_label.setStyleSheet("color: #cccccc;")
        layout.addWidget(self.uptime_label)
        
        layout.addStretch()
        
        # Public IP
        self.ip_label = QLabel("IP: --")
        self.ip_label.setStyleSheet("color: #cccccc;")
        layout.addWidget(self.ip_label)
        
        layout.addStretch()
        
        # Date/Time
        self.datetime_label = QLabel()
        self.datetime_label.setStyleSheet("color: #cccccc;")
        layout.addWidget(self.datetime_label)
        
        # Refresh rate selector
        layout.addWidget(QLabel("Refresh:"))
        self.refresh_combo = QComboBox()
        self.refresh_combo.addItems(["1s", "3s", "5s"])
        self.refresh_combo.setCurrentIndex(0)
        self.refresh_combo.setStyleSheet("""
            QComboBox {
                background: #2d2d2d;
                color: #ffffff;
                border: 1px solid #555;
                padding: 3px;
            }
        """)
        self.refresh_combo.currentIndexChanged.connect(self.on_refresh_rate_changed)
        layout.addWidget(self.refresh_combo)
        
        return bar
    
    def create_overview_tab(self) -> QWidget:
        """Create overview tab with all stats."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Network adapters section
        adapters_group = QGroupBox("Active Network Adapters")
        adapters_group.setStyleSheet(self.get_groupbox_style())
        adapters_layout = QVBoxLayout(adapters_group)
        self.adapters_label = QLabel("Detecting adapters...")
        self.adapters_label.setStyleSheet("color: #cccccc;")
        adapters_layout.addWidget(self.adapters_label)
        layout.addWidget(adapters_group)
        
        # Network stats grid
        network_group = QGroupBox("Network Statistics")
        network_group.setStyleSheet(self.get_groupbox_style())
        network_layout = QGridLayout(network_group)
        
        # Upload speed
        network_layout.addWidget(QLabel("Upload Speed:"), 0, 0)
        self.upload_label = QLabel("0.00 Mbps")
        self.upload_label.setStyleSheet("color: #4ec9b0; font-size: 14px; font-weight: bold;")
        network_layout.addWidget(self.upload_label, 0, 1)
        
        # Download speed
        network_layout.addWidget(QLabel("Download Speed:"), 0, 2)
        self.download_label = QLabel("0.00 Mbps")
        self.download_label.setStyleSheet("color: #4ec9b0; font-size: 14px; font-weight: bold;")
        network_layout.addWidget(self.download_label, 0, 3)
        
        # Ping
        network_layout.addWidget(QLabel("Ping Latency:"), 1, 0)
        self.ping_label = QLabel("0 ms")
        self.ping_label.setStyleSheet("color: #cccccc;")
        network_layout.addWidget(self.ping_label, 1, 1)
        
        # Data sent
        network_layout.addWidget(QLabel("Data Sent:"), 1, 2)
        self.sent_label = QLabel("0 B")
        self.sent_label.setStyleSheet("color: #cccccc;")
        network_layout.addWidget(self.sent_label, 1, 3)
        
        # Data received
        network_layout.addWidget(QLabel("Data Received:"), 2, 0)
        self.received_label = QLabel("0 B")
        self.received_label.setStyleSheet("color: #cccccc;")
        network_layout.addWidget(self.received_label, 2, 1)
        
        # Total data usage (since app start)
        network_layout.addWidget(QLabel("Total Usage (Session):"), 2, 2)
        self.total_usage_label = QLabel("0 B")
        self.total_usage_label.setStyleSheet("color: #cccccc;")
        network_layout.addWidget(self.total_usage_label, 2, 3)
        
        # Public IP info
        network_layout.addWidget(QLabel("Public IP:"), 3, 0)
        self.public_ip_label = QLabel("--")
        self.public_ip_label.setStyleSheet("color: #cccccc;")
        network_layout.addWidget(self.public_ip_label, 3, 1)
        
        network_layout.addWidget(QLabel("ISP:"), 3, 2)
        self.isp_label = QLabel("--")
        self.isp_label.setStyleSheet("color: #cccccc;")
        network_layout.addWidget(self.isp_label, 3, 3)
        
        network_layout.addWidget(QLabel("Location:"), 4, 0)
        self.location_label = QLabel("--")
        self.location_label.setStyleSheet("color: #cccccc;")
        network_layout.addWidget(self.location_label, 4, 1)
        
        layout.addWidget(network_group)
        
        # System stats grid
        system_group = QGroupBox("System Statistics")
        system_group.setStyleSheet(self.get_groupbox_style())
        system_layout = QGridLayout(system_group)
        
        # CPU usage with progress bar
        system_layout.addWidget(QLabel("CPU Usage:"), 0, 0)
        self.cpu_label = QLabel("0%")
        self.cpu_label.setStyleSheet("color: #cccccc;")
        system_layout.addWidget(self.cpu_label, 0, 1)
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setStyleSheet(self.get_progressbar_style())
        system_layout.addWidget(self.cpu_progress, 0, 2, 1, 2)
        
        # RAM usage
        system_layout.addWidget(QLabel("RAM Usage:"), 1, 0)
        self.ram_label = QLabel("0%")
        self.ram_label.setStyleSheet("color: #cccccc;")
        system_layout.addWidget(self.ram_label, 1, 1)
        self.ram_progress = QProgressBar()
        self.ram_progress.setStyleSheet(self.get_progressbar_style())
        system_layout.addWidget(self.ram_progress, 1, 2, 1, 2)
        
        # Disk usage
        system_layout.addWidget(QLabel("Disk Usage:"), 2, 0)
        self.disk_label = QLabel("0%")
        self.disk_label.setStyleSheet("color: #cccccc;")
        system_layout.addWidget(self.disk_label, 2, 1)
        self.disk_progress = QProgressBar()
        self.disk_progress.setStyleSheet(self.get_progressbar_style())
        system_layout.addWidget(self.disk_progress, 2, 2, 1, 2)
        
        # System uptime
        system_layout.addWidget(QLabel("System Uptime:"), 3, 0)
        self.system_uptime_label = QLabel("--")
        self.system_uptime_label.setStyleSheet("color: #cccccc;")
        system_layout.addWidget(self.system_uptime_label, 3, 1)
        
        layout.addStretch()
        
        return widget
    
    def create_graphs_tab(self) -> QWidget:
        """Create graphs tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Time window selector
        window_layout = QHBoxLayout()
        window_layout.addWidget(QLabel("Time Window:"))
        self.window_combo = QComboBox()
        self.window_combo.addItems([
            "30 seconds", "5 minutes", "10 minutes", "30 minutes", "1 hour", "24 hours"
        ])
        self.window_combo.setCurrentIndex(4)  # 1 hour default
        self.window_combo.setStyleSheet("""
            QComboBox {
                background: #2d2d2d;
                color: #ffffff;
                border: 1px solid #555;
                padding: 5px;
            }
        """)
        self.window_combo.currentIndexChanged.connect(self.on_time_window_changed)
        window_layout.addWidget(self.window_combo)
        window_layout.addStretch()
        layout.addLayout(window_layout)
        
        # Network speed graph
        network_graph_group = QGroupBox("Network Speed")
        network_graph_group.setStyleSheet(self.get_groupbox_style())
        network_graph_layout = QVBoxLayout(network_graph_group)
        
        self.network_figure = Figure(figsize=(10, 4), facecolor='#1e1e1e')
        self.network_canvas = FigureCanvas(self.network_figure)
        self.network_ax = self.network_figure.add_subplot(111)
        self.network_ax.set_facecolor('#1e1e1e')
        self.network_ax.tick_params(colors='#cccccc')
        self.network_ax.spines['bottom'].set_color('#555')
        self.network_ax.spines['top'].set_color('#555')
        self.network_ax.spines['right'].set_color('#555')
        self.network_ax.spines['left'].set_color('#555')
        self.network_ax.set_xlabel('Time', color='#cccccc')
        self.network_ax.set_ylabel('Speed (Mbps)', color='#cccccc')
        self.network_ax.set_title('Upload/Download Speed', color='#ffffff', fontsize=12)
        self.network_line_upload = self.network_ax.plot([], [], label='Upload', color='#4ec9b0')[0]
        self.network_line_download = self.network_ax.plot([], [], label='Download', color='#569cd6')[0]
        self.network_ax.legend(facecolor='#2d2d2d', edgecolor='#555', labelcolor='#cccccc')
        self.network_figure.tight_layout()
        
        network_graph_layout.addWidget(self.network_canvas)
        layout.addWidget(network_graph_group)
        
        # CPU usage graph
        cpu_graph_group = QGroupBox("CPU Usage")
        cpu_graph_group.setStyleSheet(self.get_groupbox_style())
        cpu_graph_layout = QVBoxLayout(cpu_graph_group)
        
        self.cpu_figure = Figure(figsize=(10, 4), facecolor='#1e1e1e')
        self.cpu_canvas = FigureCanvas(self.cpu_figure)
        self.cpu_ax = self.cpu_figure.add_subplot(111)
        self.cpu_ax.set_facecolor('#1e1e1e')
        self.cpu_ax.tick_params(colors='#cccccc')
        self.cpu_ax.spines['bottom'].set_color('#555')
        self.cpu_ax.spines['top'].set_color('#555')
        self.cpu_ax.spines['right'].set_color('#555')
        self.cpu_ax.spines['left'].set_color('#555')
        self.cpu_ax.set_xlabel('Time', color='#cccccc')
        self.cpu_ax.set_ylabel('CPU Usage (%)', color='#cccccc')
        self.cpu_ax.set_title('CPU Usage Over Time', color='#ffffff', fontsize=12)
        self.cpu_ax.set_ylim(0, 100)
        self.cpu_line = self.cpu_ax.plot([], [], color='#f48771')[0]
        self.cpu_figure.tight_layout()
        
        cpu_graph_layout.addWidget(self.cpu_canvas)
        layout.addWidget(cpu_graph_group)
        
        return widget
    
    def create_logs_tab(self) -> QWidget:
        """Create logs and export tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Export section
        export_group = QGroupBox("Export Data")
        export_group.setStyleSheet(self.get_groupbox_style())
        export_layout = QVBoxLayout(export_group)
        
        export_buttons_layout = QHBoxLayout()
        
        btn_export_network_csv = QPushButton("Export Network Stats (CSV)")
        btn_export_network_csv.setStyleSheet(self.get_button_style())
        btn_export_network_csv.clicked.connect(lambda: self.exporter.export_csv("network_stats"))
        export_buttons_layout.addWidget(btn_export_network_csv)
        
        btn_export_system_csv = QPushButton("Export System Stats (CSV)")
        btn_export_system_csv.setStyleSheet(self.get_button_style())
        btn_export_system_csv.clicked.connect(lambda: self.exporter.export_csv("system_stats"))
        export_buttons_layout.addWidget(btn_export_system_csv)
        
        btn_export_network_json = QPushButton("Export Network Stats (JSON)")
        btn_export_network_json.setStyleSheet(self.get_button_style())
        btn_export_network_json.clicked.connect(lambda: self.exporter.export_json("network_stats"))
        export_buttons_layout.addWidget(btn_export_network_json)
        
        btn_export_system_json = QPushButton("Export System Stats (JSON)")
        btn_export_system_json.setStyleSheet(self.get_button_style())
        btn_export_system_json.clicked.connect(lambda: self.exporter.export_json("system_stats"))
        export_buttons_layout.addWidget(btn_export_system_json)
        
        btn_export_all = QPushButton("Export All Data")
        btn_export_all.setStyleSheet(self.get_button_style())
        btn_export_all.clicked.connect(self.exporter.export_all_tables)
        export_buttons_layout.addWidget(btn_export_all)
        
        export_layout.addLayout(export_buttons_layout)
        layout.addWidget(export_group)
        
        # Logs section
        logs_group = QGroupBox("System Logs")
        logs_group.setStyleSheet(self.get_groupbox_style())
        logs_layout = QVBoxLayout(logs_group)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background: #1e1e1e;
                color: #cccccc;
                border: 1px solid #333;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10pt;
            }
        """)
        logs_layout.addWidget(self.log_display)
        
        btn_clear_logs = QPushButton("Clear Logs")
        btn_clear_logs.setStyleSheet(self.get_button_style())
        btn_clear_logs.clicked.connect(self.clear_logs)
        logs_layout.addWidget(btn_clear_logs)
        
        layout.addWidget(logs_group)
        
        return widget
    
    def setup_timers(self):
        """Setup update timers."""
        # Main stats update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_all_stats)
        self.update_timer.start(self.refresh_rate)
        
        # Speed test timer (every 5 minutes)
        self.speed_test_timer = QTimer()
        self.speed_test_timer.timeout.connect(self.run_speed_test)
        self.speed_test_timer.start(300000)  # 5 minutes
        
        # DateTime update timer
        self.datetime_timer = QTimer()
        self.datetime_timer.timeout.connect(self.update_datetime)
        self.datetime_timer.start(1000)  # Every second
        self.update_datetime()
        
        # Graph update timer
        self.graph_timer = QTimer()
        self.graph_timer.timeout.connect(self.update_graphs)
        self.graph_timer.start(1000)  # Every second
    
    def setup_system_tray(self):
        """Setup system tray icon."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        
        self.tray_icon = QSystemTrayIcon(self)
        # Use default icon for now
        self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_ComputerIcon))
        
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
    
    def tray_icon_activated(self, reason):
        """Handle system tray icon activation."""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
    
    def apply_dark_theme(self):
        """Apply dark theme to the application."""
        self.setStyleSheet("""
            QMainWindow {
                background: #1e1e1e;
            }
            QWidget {
                background: #1e1e1e;
                color: #cccccc;
            }
            QLabel {
                color: #cccccc;
            }
        """)
        
        # Set matplotlib style
        plt.style.use('dark_background')
    
    def get_groupbox_style(self) -> str:
        """Get style for group boxes."""
        return """
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """
    
    def get_button_style(self) -> str:
        """Get style for buttons."""
        return """
            QPushButton {
                background: #0078d4;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #106ebe;
            }
            QPushButton:pressed {
                background: #005a9e;
            }
        """
    
    def get_progressbar_style(self) -> str:
        """Get style for progress bars."""
        return """
            QProgressBar {
                border: 1px solid #555;
                border-radius: 3px;
                text-align: center;
                color: #ffffff;
                background: #2d2d2d;
            }
            QProgressBar::chunk {
                background: #0078d4;
                border-radius: 2px;
            }
        """
    
    def format_bytes(self, bytes_value: float) -> str:
        """Format bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    def update_all_stats(self):
        """Update all statistics displays."""
        # Network stats
        network_stats = self.network_monitor.get_network_stats()
        self.upload_label.setText(f"{network_stats['upload_speed']:.2f} Mbps")
        self.download_label.setText(f"{network_stats['download_speed']:.2f} Mbps")
        self.ping_label.setText(f"{network_stats['ping_latency']:.1f} ms")
        self.sent_label.setText(self.format_bytes(network_stats['bytes_sent']))
        self.received_label.setText(self.format_bytes(network_stats['bytes_received']))
        self.public_ip_label.setText(network_stats['public_ip'])
        self.ip_label.setText(f"IP: {network_stats['public_ip']}")
        self.isp_label.setText(network_stats['isp_name'])
        self.location_label.setText(network_stats['location'])
        
        # Total data usage
        total_sent, total_recv = self.network_monitor.get_total_data_usage()
        total_usage = total_sent + total_recv
        self.total_usage_label.setText(self.format_bytes(total_usage))
        
        # System stats
        system_stats = self.system_monitor.get_all_stats()
        self.cpu_label.setText(f"{system_stats['cpu_usage']:.1f}%")
        self.cpu_progress.setValue(int(system_stats['cpu_usage']))
        self.ram_label.setText(f"{system_stats['ram_usage']:.1f}%")
        self.ram_progress.setValue(int(system_stats['ram_usage']))
        self.disk_label.setText(f"{system_stats['disk_usage']:.1f}%")
        self.disk_progress.setValue(int(system_stats['disk_usage']))
        self.system_uptime_label.setText(
            self.system_monitor.format_uptime(system_stats['uptime'])
        )
        
        # App uptime
        app_uptime = (datetime.now() - self.app_start_time).total_seconds()
        self.uptime_label.setText(
            f"Uptime: {self.system_monitor.format_uptime(app_uptime)}"
        )
        
        # Update adapters
        adapters = self.network_monitor.get_active_adapters()
        adapter_text = "\n".join([
            f"• {adapter['name']} - {adapter['ip']} ({adapter['speed']})"
            for adapter in adapters
        ]) if adapters else "No active adapters found"
        self.adapters_label.setText(adapter_text)
        
        # Log to database
        self.data_manager.log_network_stats(network_stats)
        self.data_manager.log_system_stats(system_stats)
    
    def update_graphs(self):
        """Update graph displays."""
        current_time = datetime.now().timestamp()
        
        # Get network stats
        network_stats = self.network_monitor.get_network_stats()
        
        # Add to network data
        self.network_data['time'].append(current_time)
        self.network_data['upload'].append(network_stats['upload_speed'])
        self.network_data['download'].append(network_stats['download_speed'])
        
        # Get system stats
        system_stats = self.system_monitor.get_all_stats()
        self.system_data['time'].append(current_time)
        self.system_data['cpu'].append(system_stats['cpu_usage'])
        
        # Filter data based on time window
        cutoff_time = current_time - self.time_window
        
        # Network graph
        network_times = [t for t in self.network_data['time'] if t >= cutoff_time]
        network_upload = self.network_data['upload'][-len(network_times):]
        network_download = self.network_data['download'][-len(network_times):]
        
        if network_times:
            # Convert to relative time
            relative_times = [(t - network_times[0]) / 60 for t in network_times]  # Minutes
            
            self.network_ax.clear()
            self.network_ax.set_facecolor('#1e1e1e')
            self.network_ax.tick_params(colors='#cccccc')
            self.network_ax.spines['bottom'].set_color('#555')
            self.network_ax.spines['top'].set_color('#555')
            self.network_ax.spines['right'].set_color('#555')
            self.network_ax.spines['left'].set_color('#555')
            self.network_ax.set_xlabel('Time (minutes)', color='#cccccc')
            self.network_ax.set_ylabel('Speed (Mbps)', color='#cccccc')
            self.network_ax.set_title('Upload/Download Speed', color='#ffffff', fontsize=12)
            
            self.network_ax.plot(relative_times, network_upload, label='Upload', color='#4ec9b0', linewidth=1.5)
            self.network_ax.plot(relative_times, network_download, label='Download', color='#569cd6', linewidth=1.5)
            self.network_ax.legend(facecolor='#2d2d2d', edgecolor='#555', labelcolor='#cccccc')
            self.network_ax.grid(True, alpha=0.3, color='#555')
            self.network_figure.tight_layout()
            self.network_canvas.draw()
        
        # CPU graph
        cpu_times = [t for t in self.system_data['time'] if t >= cutoff_time]
        cpu_values = self.system_data['cpu'][-len(cpu_times):]
        
        if cpu_times:
            relative_times = [(t - cpu_times[0]) / 60 for t in cpu_times]  # Minutes
            
            self.cpu_ax.clear()
            self.cpu_ax.set_facecolor('#1e1e1e')
            self.cpu_ax.tick_params(colors='#cccccc')
            self.cpu_ax.spines['bottom'].set_color('#555')
            self.cpu_ax.spines['top'].set_color('#555')
            self.cpu_ax.spines['right'].set_color('#555')
            self.cpu_ax.spines['left'].set_color('#555')
            self.cpu_ax.set_xlabel('Time (minutes)', color='#cccccc')
            self.cpu_ax.set_ylabel('CPU Usage (%)', color='#cccccc')
            self.cpu_ax.set_title('CPU Usage Over Time', color='#ffffff', fontsize=12)
            self.cpu_ax.set_ylim(0, 100)
            
            self.cpu_ax.plot(relative_times, cpu_values, color='#f48771', linewidth=1.5)
            self.cpu_ax.fill_between(relative_times, cpu_values, alpha=0.3, color='#f48771')
            self.cpu_ax.grid(True, alpha=0.3, color='#555')
            self.cpu_figure.tight_layout()
            self.cpu_canvas.draw()
        
        # Limit data size
        if len(self.network_data['time']) > 10000:
            keep = len(network_times) if network_times else 1000
            self.network_data = {
                'time': self.network_data['time'][-keep:],
                'upload': self.network_data['upload'][-keep:],
                'download': self.network_data['download'][-keep:]
            }
        
        if len(self.system_data['time']) > 10000:
            keep = len(cpu_times) if cpu_times else 1000
            self.system_data = {
                'time': self.system_data['time'][-keep:],
                'cpu': self.system_data['cpu'][-keep:]
            }
    
    def update_datetime(self):
        """Update date/time display."""
        now = datetime.now()
        self.datetime_label.setText(now.strftime("%Y-%m-%d %H:%M:%S"))
    
    def on_refresh_rate_changed(self, index: int):
        """Handle refresh rate change."""
        rates = [1000, 3000, 5000]  # milliseconds
        self.refresh_rate = rates[index]
        self.update_timer.setInterval(self.refresh_rate)
        self.logger.info(f"Refresh rate changed to {index + 1}s")
    
    def on_time_window_changed(self, index: int):
        """Handle time window change."""
        windows = [30, 300, 600, 1800, 3600, 86400]  # seconds
        self.time_window = windows[index]
        self.logger.info(f"Time window changed to {self.window_combo.currentText()}")
    
    def run_speed_test(self):
        """Run speed test in background thread."""
        if self.speed_test_thread and self.speed_test_thread.isRunning():
            return
        
        self.logger.info("Starting speed test...")
        self.speed_test_thread = SpeedTestThread(self.network_monitor)
        self.speed_test_thread.finished.connect(self.on_speed_test_finished)
        self.speed_test_thread.error.connect(self.on_speed_test_error)
        self.speed_test_thread.start()
    
    def on_speed_test_finished(self, result: dict):
        """Handle speed test completion."""
        self.logger.info(
            f"Speed test completed: {result['download_mbps']:.2f} Mbps down, "
            f"{result['upload_mbps']:.2f} Mbps up, {result['ping_ms']:.2f} ms ping"
        )
        self.data_manager.log_speed_test(
            result['download_mbps'],
            result['upload_mbps'],
            result['ping_ms'],
            result.get('server_name', '')
        )
    
    def on_speed_test_error(self, error: str):
        """Handle speed test error."""
        self.logger.warning(f"Speed test failed: {error}")
    
    def update_log_display(self, timestamp: str, message: str):
        """Update log display with new message."""
        self.log_display.append(message)
        # Auto-scroll to bottom
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_logs(self):
        """Clear log display."""
        self.log_display.clear()
        self.logger.clear()
        self.logger.info("Logs cleared")
    
    def on_export_complete(self, success: bool, message: str):
        """Handle export completion."""
        if success:
            self.logger.info(message)
            QMessageBox.information(self, "Export Complete", message)
        else:
            self.logger.error(message)
            QMessageBox.warning(self, "Export Failed", message)
    
    def closeEvent(self, event):
        """Handle window close event."""
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            QMessageBox.information(
                self,
                "NetScope",
                "The application will continue to run in the system tray. "
                "To quit, right-click the tray icon and select Quit."
            )
            self.hide()
            event.ignore()
        else:
            self.logger.info("NetScope shutting down")
            event.accept()
