# NetScope v1.0.0

**Professional-grade Python desktop application for real-time network and system performance monitoring**

![NetScope](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

NetScope is a modern, dark-themed desktop application built with PyQt5 that provides comprehensive real-time monitoring of network adapters, system resources, and performance metrics. The application features live graph visualizations, historical data logging, and export capabilities.

## Features

### Network Monitoring
- ✅ **Automatic adapter detection** - Detects and monitors all active network adapters
- ✅ **Real-time speed tracking** - Upload/download speeds with live updates
- ✅ **Ping latency monitoring** - Continuous latency measurement
- ✅ **Data usage tracking** - Bytes sent/received with session totals
- ✅ **Public IP information** - IP, ISP name, and approximate location
- ✅ **Network adapter listing** - Shows all active interfaces

### System Monitoring
- ✅ **CPU usage** - Real-time CPU percentage with progress bars
- ✅ **RAM usage** - Memory consumption with detailed statistics
- ✅ **Disk usage** - Storage utilization tracking
- ✅ **System uptime** - Continuous uptime display

### Visualization & Analytics
- ✅ **Real-time graphs** - Live network speed and CPU usage graphs
- ✅ **Adjustable time windows** - 30s, 5m, 10m, 30m, 1h, 24h views
- ✅ **Adjustable refresh rates** - 1s, 3s, 5s update intervals
- ✅ **Smooth animations** - PyQtGraph-powered visualizations

### Data Management
- ✅ **SQLite database** - Automatic historical data storage
- ✅ **CSV export** - Export all statistics to CSV format
- ✅ **JSON export** - Export all statistics to JSON format
- ✅ **Event logging** - System events logged automatically

### Speed Testing
- ✅ **Manual speed tests** - On-demand bandwidth testing
- ✅ **Automatic testing** - Periodic speed tests (every 5 minutes)
- ✅ **Results storage** - Speed test history saved to database

### User Interface
- ✅ **Dark theme** - Minimalist dark mode interface
- ✅ **Tabbed layout** - Overview, Graphs, Logs & Exports tabs
- ✅ **System tray support** - Minimize to system tray
- ✅ **Terminal-style logs** - Console output for application events
- ✅ **Resizable window** - Adaptive UI elements

## Screenshots

*Note: Screenshots will be added after first build and testing*

### Overview Tab
- Network statistics panel
- System statistics panel
- Public IP information
- Speed test controls

### Graphs Tab
- Real-time network speed graph (Download/Upload)
- CPU usage graph
- Time window selector
- Refresh rate controls

### Logs & Exports Tab
- Application log console
- CSV export button
- JSON export button

## Installation

### For End Users (Windows)

1. Download `NetScope.exe` from the Releases section
2. Run the executable (no installation required)
3. The application will create a `data/` directory for database storage

**Note:** The executable is a standalone file - no Python installation required.

### For Developers

#### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)

#### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd netscope
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python -m venv venv
   ```
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **Linux/Mac:**
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

## Building Standalone Executable

### Prerequisites
- Python 3.11+
- All dependencies installed (`pip install -r requirements.txt`)
- PyInstaller (included in requirements.txt)

### Build Process

#### Method 1: Using PyInstaller directly

**Windows:**
```bash
pyinstaller --onefile --noconsole --name NetScope --icon=netscope/assets/icons/app_icon.ico --add-data "data;data" netscope/main.py
```

**Linux/Mac:**
```bash
pyinstaller --onefile --name NetScope --icon=netscope/assets/icons/app_icon.ico --add-data "data:data" netscope/main.py
```

#### Method 2: Using the spec file (recommended)

1. Create or use the provided `NetScope.spec` file
2. Build:
   ```bash
   pyinstaller NetScope.spec
   ```

### Output Location
- **Executable:** `dist/NetScope.exe` (Windows) or `dist/NetScope` (Linux/Mac)
- **Build artifacts:** `build/` directory (can be deleted after successful build)

### Build Configuration

The executable will:
- Run as a single-file executable
- Include all dependencies
- Create `data/` directory automatically on first run
- Initialize SQLite database automatically
- Display version number in title bar (NetScope v1.0.0)

## Usage

### Starting the Application

1. Launch `NetScope.exe` (or run `python main.py` from source)
2. The application will automatically:
   - Detect active network adapters
   - Start monitoring network and system stats
   - Fetch public IP information
   - Begin logging data to SQLite database

### Using the Interface

#### Overview Tab
- View real-time network statistics
- Monitor system resources (CPU, RAM, Disk)
- See public IP and ISP information
- Run manual speed tests

#### Graphs Tab
- Select time window from dropdown (30s to 24h)
- Adjust refresh rate (1s, 3s, 5s)
- View live network speed and CPU usage graphs

#### Logs & Exports Tab
- View application event logs
- Export data to CSV or JSON format
- Clear log display

### Speed Testing

- **Manual Test:** Click "Run Speed Test" button in Overview tab
- **Automatic Tests:** Run automatically every 5 minutes when app is active
- Results are saved to database and displayed in the UI

### Exporting Data

1. Navigate to "Logs & Exports" tab
2. Click "Export to CSV" or "Export to JSON"
3. Choose save location
4. All historical data will be exported

## Project Structure

```
NetScope/
│
├── netscope/
│   ├── __init__.py
│   ├── main.py                 # Main entry point
│   ├── ui/
│   │   ├── main_window.py     # Main UI window
│   │   └── resources/
│   ├── core/
│   │   ├── network_monitor.py # Network monitoring
│   │   ├── system_monitor.py  # System monitoring
│   │   └── data_manager.py    # Database operations
│   ├── utils/
│   │   ├── logger.py          # Logging system
│   │   └── speed_test.py      # Speed test functionality
│   └── assets/
│       └── icons/
│
├── data/                       # SQLite database (created automatically)
│   └── netscope.db
│
├── build/                      # Build output directory
├── dist/                       # Executable output
│
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── LICENSE                     # MIT License
└── changelog.md                # Version history
```

## Technical Details

### Tech Stack
- **GUI Framework:** PyQt5 5.15.10
- **System Monitoring:** psutil 5.9.6
- **Speed Testing:** speedtest-cli 2.1.3
- **Graph Visualization:** pyqtgraph 0.13.3
- **HTTP Requests:** requests 2.31.0
- **Database:** SQLite3 (built-in)
- **Packaging:** PyInstaller 6.3.0

### Data Storage
- SQLite database located in `data/netscope.db`
- Automatic schema creation on first run
- Indexed tables for efficient queries
- Stores network stats, system stats, speed tests, and events

### API Usage
- **IP Information:** Uses ipinfo.io API (free tier, no key required)
- **Fallback:** Uses ipify.org for basic IP lookup if ipinfo fails

## Configuration

### Default Settings
- **Refresh Rate:** 1 second
- **Time Window:** 5 minutes
- **Speed Test Interval:** 5 minutes (automatic)
- **Max Logs:** 1000 entries

These can be adjusted via the UI controls in the Graphs tab.

## Troubleshooting

### Issue: Application won't start
- **Solution:** Ensure Python 3.11+ is installed and all dependencies are installed
- Check that PyQt5 is properly installed: `pip install PyQt5`

### Issue: No network adapters detected
- **Solution:** Ensure network adapters are active and have IPv4 addresses
- Check that psutil has proper permissions to access network interfaces

### Issue: Speed test fails
- **Solution:** Check internet connection
- Ensure speedtest-cli is installed: `pip install speedtest-cli`
- Some networks may block speed test servers

### Issue: Database errors
- **Solution:** Ensure write permissions in the application directory
- Check that `data/` directory can be created

### Issue: Graphs not updating
- **Solution:** Check that time window is set correctly
- Ensure refresh rate is not too high (try 1 second)
- Verify that monitoring is active (check Overview tab)

## Version History

See [CHANGELOG.md](changelog.md) for detailed version history.

### Current Version: 1.0.0
- Initial release
- Core monitoring features
- Dark theme UI
- Real-time graphs
- Export functionality

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Future Enhancements (Planned)
- v1.0.1: Optimized speed test + export fixes
- v1.0.2: Enhanced tray icon + better graph scaling
- v1.1.0: Plugin system for extra data modules

## Support

For issues, questions, or feature requests, please open an issue on the GitHub repository.

---

**NetScope v1.0.0** - Professional Network and System Performance Monitor

*Built with Python, PyQt5, and ❤️*
