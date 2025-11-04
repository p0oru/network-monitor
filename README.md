# NetScope v1.0.0

A professional-grade Python desktop application built with PyQt5 that provides real-time network and system performance monitoring. Features a minimal dark-mode interface with live graphs, historical data logging, and export capabilities.

![NetScope Dashboard](screenshots/dashboard.png) <!-- Screenshot placeholder -->

## Features

### Network Monitoring
- **Real-time upload/download speeds** - Live monitoring of network throughput
- **Active adapter detection** - Automatically detects and displays all active network adapters
- **Ping latency** - Continuous latency monitoring to 8.8.8.8
- **Data usage tracking** - Tracks bytes sent/received and total session usage
- **Public IP information** - Displays public IP, ISP name, and approximate location
- **Automatic speed tests** - Runs lightweight bandwidth tests every 5 minutes

### System Monitoring
- **CPU usage** - Real-time CPU utilization with progress bar
- **RAM usage** - Memory consumption tracking
- **Disk usage** - Storage space monitoring
- **System uptime** - Displays system and application uptime

### Data Visualization
- **Real-time graphs** - Live updates for network speed and CPU usage
- **Adjustable time windows** - View data for 30s, 5m, 10m, 30m, 1h, or 24h
- **Configurable refresh rates** - Choose between 1s, 3s, or 5s update intervals

### Data Management
- **SQLite database** - All stats automatically logged to local database
- **CSV/JSON export** - Export network stats, system stats, or all data
- **Event logging** - Comprehensive log panel for all system events
- **Historical data** - Access past monitoring data from database

### User Interface
- **Dark theme** - Minimalist dark-mode interface
- **Resizable window** - Adaptive layout with collapsible panels
- **Tabbed interface** - Organized into Overview, Graphs, and Logs & Export tabs
- **System tray support** - Minimize to system tray
- **Top status bar** - Quick access to uptime, IP, and date/time

## Installation

### For End Users (Windows)

1. **Download the executable:**
   - Download `NetScope.exe` from the [Releases](https://github.com/yourusername/NetScope/releases) page
   - No Python installation required
   - No additional dependencies needed

2. **Run the application:**
   - Double-click `NetScope.exe`
   - The application will create a `data/` folder automatically for storing logs
   - First run may take 2-3 seconds to initialize

### For Developers

#### Prerequisites
- Python 3.11 or higher
- pip package manager

#### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/NetScope.git
   cd NetScope
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
 
   ```

## Building Windows Executable

### Prerequisites
- Python 3.11+ installed
- All dependencies installed (`pip install -r requirements.txt`)
- PyInstaller (included in requirements.txt)

### Build Command

**Using the spec file (recommended):**
```bash
pyinstaller NetScope.spec
```

**Manual build:**
```bash
pyinstaller --onefile --noconsole --name NetScope --hidden-import PyQt5 --hidden-import matplotlib --hidden-import speedtest main.py
```

### Output Location
- **Executable:** `dist/NetScope.exe`
- **Build artifacts:** `build/` directory (can be deleted after successful build)
- **Spec file:** `NetScope.spec` (keep for future builds)

### Build Notes
- Build process takes 2-5 minutes depending on your system
- Executable size: Approximately 50-70 MB (includes Python runtime and all dependencies)
- The executable is standalone and requires no installation
- First run may take 3-5 seconds due to extraction (one-file mode)

## Project Structure

```
NetScope/
│
├── netscope/                 # Main package
│   ├── __init__.py
│   ├── main.py              # Package entry point
│   ├── ui/                  # User interface modules
│   │   ├── __init__.py
│   │   ├── main_window.py   # Main GUI window
│   │   └── resources/       # UI resources
│   ├── core/                # Core monitoring modules
│   │   ├── __init__.py
│   │   ├── network_monitor.py    # Network monitoring
│   │   ├── system_monitor.py     # System monitoring
│   │   └── data_manager.py       # Database management
│   ├── utils/               # Utility modules
│   │   ├── __init__.py
│   │   ├── logger.py        # Logging system
│   │   └── exporter.py      # Data export
│   └── assets/              # Assets folder
│       └── icons/           # Application icons
│
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── setup.py                 # Package setup script
├── NetScope.spec            # PyInstaller configuration
├── README.md                # This file
├── LICENSE                  # MIT License
├── changelog.md             # Version changelog
├── data/                    # Data storage (auto-created)
│   └── network_logs.db      # SQLite database
└── build/                   # Build output directory
    └── NetScope.exe         # Windows executable
```

## Usage Guide

### Overview Tab
- View all active network adapters
- Monitor real-time network statistics (upload/download speeds, ping, data usage)
- Check public IP, ISP, and location information
- Monitor system resources (CPU, RAM, Disk usage)
- View system and application uptime

### Graphs Tab
- **Time Window Selector:** Choose how much historical data to display
- **Network Speed Graph:** Real-time visualization of upload/download speeds
- **CPU Usage Graph:** Real-time CPU utilization over time

### Logs & Export Tab
- **Export Buttons:** Export data to CSV or JSON format
  - Export Network Stats (CSV/JSON)
  - Export System Stats (CSV/JSON)
  - Export All Data (exports all tables)
- **System Logs Panel:** View all application events and actions
- **Clear Logs:** Clear the log display (does not affect database)

### Settings
- **Refresh Rate:** Adjust update frequency (1s, 3s, 5s) from top bar
- **Time Window:** Adjust graph time range (30s to 24h) from Graphs tab

### System Tray
- Right-click the system tray icon to:
  - Show/Hide the main window
  - Quit the application
- Double-click the tray icon to toggle window visibility

## Configuration

### Database Location
The SQLite database is stored in `data/network_logs.db` relative to the executable location.

### Speed Test Frequency
Speed tests run automatically every 5 minutes when the application is active. This can be adjusted in `main_window.py` by modifying the `speed_test_timer` interval.

### API Usage
NetScope uses the following free APIs:
- **ipinfo.io** - For public IP, ISP, and location (50k requests/month free tier)
- **api.ipify.org** - Fallback for IP detection

## Troubleshooting

### Application won't start
- **Check Python version:** Ensure Python 3.11+ is installed
- **Check dependencies:** Run `pip install -r requirements.txt`
- **Check console:** Run `python main.py` from command line to see error messages

### No network data showing
- **Check network adapter:** Ensure at least one network adapter is active
- **Check permissions:** On Linux/Mac, you may need elevated permissions
- **Check firewall:** Ensure firewall isn't blocking the application

### Speed test fails
- **Check internet connection:** Ensure you have an active internet connection
- **Check firewall:** Some firewalls block speedtest servers
- **Check speedtest-cli:** Verify installation with `pip show speedtest-cli`

### Graphs not updating
- **Check refresh rate:** Ensure refresh rate is set appropriately
- **Check time window:** Verify time window includes recent data
- **Check log panel:** Look for any error messages

### Export not working
- **Check file permissions:** Ensure write permissions in target directory
- **Check disk space:** Ensure sufficient disk space for export file
- **Check log panel:** Look for error messages

### Executable issues
- **Antivirus false positive:** Some antivirus software flags PyInstaller executables
  - Add exception in antivirus settings
  - Submit for whitelisting if needed
- **Slow startup:** Normal for one-file executables (3-5 seconds first run)
- **Missing DLL errors:** Ensure all dependencies are included in build

## Development

### Running Tests
Currently, no automated tests are included. Manual testing is recommended.

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 Python style guide
- Use type hints where appropriate
- Document functions and classes with docstrings

## Version History

See [changelog.md](changelog.md) for detailed version history.

### Current Version: v1.0.0
- Initial release
- Core network and system monitoring
- Real-time graphs and data visualization
- SQLite database logging
- CSV/JSON export functionality
- Dark theme UI
- System tray support

### Planned Updates
- **v1.0.1:** Optimized speed test + export fixes
- **v1.0.2:** Better graph scaling + enhanced tray icon
- **v1.1.0:** Plugin system for custom data modules

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributors

- Your Name - Initial work - [YourGitHub](https://github.com/yourusername)

## Acknowledgments

- **PyQt5** - GUI framework
- **psutil** - System and process utilities
- **matplotlib** - Data visualization
- **speedtest-cli** - Bandwidth testing
- **ipinfo.io** - IP geolocation API

## Support

For issues, questions, or contributions:
- Open an issue on [GitHub](https://github.com/yourusername/NetScope/issues)
- Check the [Wiki](https://github.com/yourusername/NetScope/wiki) for detailed documentation

---

**Note:** Screenshots in this README are placeholders. Replace with actual screenshots of the application UI.
