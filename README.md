# NetScope v1.0.0

A professional-grade Python desktop application built with PyQt5 that provides real-time network and system performance monitoring. Features a minimal, dark-mode interface with live graphs, historical data storage, and export capabilities.

![NetScope](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## 📸 Screenshots

*Note: Screenshots will be added after the first build and testing*

## ✨ Features

### Network Monitoring
- **Real-time network speed tracking** - Monitor upload/download speeds in Mbps
- **Active adapter detection** - Automatically detects and monitors all active network adapters
- **Ping latency monitoring** - Real-time ping measurements to Google DNS (8.8.8.8)
- **Data usage tracking** - Track total bytes sent and received
- **Public IP detection** - Shows your public IP address, ISP name, and approximate location
- **Automatic speed testing** - Runs lightweight bandwidth tests every 5 minutes when active

### System Monitoring
- **CPU usage monitoring** - Real-time CPU usage percentage
- **RAM usage tracking** - Monitor RAM usage with total and used amounts
- **Disk usage monitoring** - Track disk space usage
- **System uptime** - Display system uptime in human-readable format

### Visualization
- **Real-time graphs** - Live updates for network speed and CPU usage
- **Adjustable time windows** - View data for 30s, 5m, 10m, 30m, 1h, or 24h
- **Adjustable refresh rates** - Control graph update frequency (1s, 3s, or 5s intervals)
- **Smooth animations** - Clean, professional graph rendering with pyqtgraph

### Data Management
- **SQLite database storage** - All stats automatically logged to local database
- **Export to CSV/JSON** - Export historical data with one click
- **Event logging** - System events logged in console panel
- **Historical data retention** - Data persists between sessions

### User Interface
- **Dark theme** - Minimalist dark-mode interface
- **Resizable window** - Adaptive layout that works at any size
- **Tabbed interface** - Organized into Overview, Graphs, and Logs & Export tabs
- **System tray icon** - Minimize to system tray (optional)
- **Top status bar** - Quick view of uptime, IP, and date/time

## 🚀 Installation

### For End Users (Windows)

1. Download the latest `NetScope.exe` from the [Releases](https://github.com/yourusername/netscope/releases) page
2. Double-click `NetScope.exe` to run (no installation required)
3. The application will create a `data/` directory for storing logs and exports

**Requirements:**
- Windows 7 or later
- No additional dependencies needed
- Internet connection for speed tests and IP detection

### For Developers

#### Prerequisites
- Python 3.11 or later
- pip (Python package manager)

#### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/netscope.git
   cd netscope
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **Linux/Mac:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

## 📦 Building the Executable

### Prerequisites
- Python 3.11+ installed
- All dependencies installed (`pip install -r requirements.txt`)
- PyInstaller (included in requirements.txt)

### Build Instructions

#### Windows
```bash
build_exe.bat
```
Or manually:
```bash
pyinstaller --clean NetScope.spec
```

#### Linux/Mac
```bash
./build_exe.sh
```
Or manually:
```bash
pyinstaller --clean NetScope.spec
```

### Output
- **Executable:** `dist/NetScope.exe` (Windows) or `dist/NetScope` (Linux/Mac)
- **Build artifacts:** `build/` directory (can be deleted after successful build)
- **Spec file:** `NetScope.spec` (keep for future builds)

### Build Options
- **Debug build:** Edit `NetScope.spec` and change `console=False` to `console=True`
- **One-folder mode:** Modify the spec file to use `--onedir` instead of `--onefile` for faster startup
- **Custom icon:** Add `icon='path/to/icon.ico'` to the EXE block in the spec file

## 🎯 Usage

### Starting the Application
1. Launch `NetScope.exe` (or run `python main.py` in development)
2. The application will automatically start monitoring network and system stats
3. Data collection begins immediately and logs to the SQLite database

### Viewing Statistics
- **Overview Tab:** Displays all current network and system statistics in real-time
- **Graphs Tab:** View live graphs of network speed and CPU usage with adjustable time windows
- **Logs & Export Tab:** View system event logs and export data to CSV/JSON

### Adjusting Settings
- **Time Window:** Use the dropdown in the Graphs tab to change the data window (30s to 24h)
- **Refresh Rate:** Control how often graphs update (1s, 3s, or 5s intervals)
- **Speed Tests:** Run automatically every 5 minutes, or manually trigger from the logs

### Exporting Data
1. Navigate to the **Logs & Export** tab
2. Click **Export to CSV** or **Export to JSON**
3. Files are saved to `data/exports/` with timestamped filenames

### System Tray
- Right-click the system tray icon to show/hide the window
- Double-click to restore the window
- Use "Quit" from the tray menu to close the application

## 📁 Project Structure

```
NetScope/
│
├── netscope/
│   ├── __init__.py
│   ├── main.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py          # Main UI window
│   │   └── resources/              # UI resources (icons, etc.)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── network_monitor.py      # Network monitoring logic
│   │   ├── system_monitor.py       # System monitoring logic
│   │   └── data_manager.py         # Database operations
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py               # Logging system
│   │   └── exporter.py             # CSV/JSON export
│   └── assets/
│       └── icons/                   # Application icons
│
├── data/                            # Generated at runtime
│   ├── netscope.db                 # SQLite database
│   └── exports/                     # Exported CSV/JSON files
│
├── build/                           # Auto-generated build files
├── dist/                            # Compiled executables
│
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── NetScope.spec                    # PyInstaller spec file
├── build_exe.bat                    # Windows build script
├── build_exe.sh                     # Linux/Mac build script
├── README.md                        # This file
├── LICENSE                          # MIT License
└── changelog.md                     # Version history
```

## 🔧 Configuration

### Default Settings
- **Graph refresh rate:** 1 second
- **Time window:** 5 minutes
- **Speed test interval:** 5 minutes
- **Database location:** `data/netscope.db`
- **Export location:** `data/exports/`

### Database Schema
The application uses SQLite with the following tables:
- `network_stats` - Network statistics over time
- `system_stats` - System statistics over time
- `events` - Application events and logs
- `speed_tests` - Speed test results

## 🐛 Troubleshooting

### Application Won't Start
- **Check Python version:** Ensure Python 3.11+ is installed
- **Install dependencies:** Run `pip install -r requirements.txt`
- **Check console output:** Run with `console=True` in spec file to see errors

### No Network Data Showing
- **Check network adapters:** Ensure you have an active network connection
- **Firewall:** Check if firewall is blocking network access
- **Permissions:** On Linux, may need elevated permissions for network monitoring

### Speed Test Fails
- **Internet connection:** Ensure you have an active internet connection
- **speedtest-cli:** May need to install separately: `pip install speedtest-cli`
- **Network restrictions:** Some networks block speed test servers

### Graphs Not Updating
- **Check refresh rate:** Ensure refresh rate is set appropriately
- **Time window:** Verify time window includes recent data
- **Data collection:** Check that monitoring threads are running (view logs tab)

### Export Fails
- **Permissions:** Ensure write permissions in `data/exports/` directory
- **Disk space:** Check available disk space
- **Data availability:** Verify there is data to export (check database)

## 📝 Changelog

See [CHANGELOG.md](changelog.md) for detailed version history.

### Version 1.0.0 (Current)
- ✅ Core network and system monitoring
- ✅ Real-time graphs with adjustable time windows
- ✅ Dark mode UI with minimalist design
- ✅ SQLite database for historical data
- ✅ CSV/JSON export functionality
- ✅ System event logging
- ✅ Automatic speed testing
- ✅ Adjustable refresh rates
- ✅ System tray icon support

### Planned Features
- **v1.0.1:** Optimized speed test + export fixes
- **v1.0.2:** Enhanced tray icon + better graph scaling
- **v1.1.0:** Plugin system for additional data modules

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PyQt5** - GUI framework
- **psutil** - System and process utilities
- **pyqtgraph** - Real-time plotting
- **speedtest-cli** - Bandwidth testing
- **requests** - HTTP library for IP detection

## 📧 Contact

For issues, questions, or suggestions, please open an issue on GitHub.

---

**NetScope** - Professional Network and System Performance Monitoring