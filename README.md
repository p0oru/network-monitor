# NetScope - Network and System Performance Monitor

A professional-grade Python desktop application built with PyQt5 that provides real-time network and system performance monitoring. NetScope features a minimal, dark-mode interface with comprehensive monitoring capabilities.

![NetScope v1.0.0](https://img.shields.io/badge/NetScope-v1.0.0-blue)

## Features

### Network Monitoring
- **Automatic Adapter Detection**: Automatically detects and monitors all active network adapters
- **Real-time Speed Monitoring**: Current upload/download speeds with live updates
- **Ping Latency**: Continuous ping monitoring to multiple DNS servers
- **Data Usage Tracking**: Total data sent/received with session totals
- **Public IP Information**: Displays public IP, ISP name, and approximate location
- **Speed Testing**: Automatic lightweight bandwidth tests every few minutes

### System Monitoring
- **CPU Usage**: Real-time CPU usage percentage with per-core support
- **RAM Usage**: Current memory usage with total/used/free statistics
- **Disk Usage**: Disk space monitoring for system drives
- **System Uptime**: Displays both system and application uptime

### Data Visualization
- **Real-time Graphs**: Live graph updates for network speed and CPU usage
- **Adjustable Time Windows**: 
  - 30 seconds
  - 5 minutes
  - 10 minutes
  - 30 minutes
  - 1 hour
  - 24 hours
- **Adjustable Refresh Rates**: 1 second, 3 seconds, or 5 seconds

### Data Management
- **Automatic Logging**: All statistics automatically saved to SQLite database
- **Export Functionality**: Export data to CSV or JSON formats
- **Event Logging**: System events (startup, shutdown, speed tests) logged to console
- **Historical Data**: Access to historical statistics from previous sessions

### User Interface
- **Dark Theme**: Professional dark-mode interface
- **Minimal Design**: Clean, minimalist dashboard layout
- **Smooth Animations**: Smooth transitions and updates
- **Resizable Window**: Adaptive layout for different window sizes
- **Tabbed Interface**: Organized tabs for Overview, Graphs, and Logs

## Screenshots

### Overview Tab
![Overview Tab](screenshots/overview.png)
*Comprehensive statistics display with network and system information*

### Graphs Tab
![Graphs Tab](screenshots/graphs.png)
*Real-time visualization of network speed and CPU usage*

### Logs & Export Tab
![Logs Tab](screenshots/logs.png)
*Application logs and data export functionality*

## Installation

### For End Users (Windows)

1. Download the pre-built executable from the [Releases](https://github.com/yourusername/netscope/releases) page
2. Run `NetScope.exe` - no Python installation required!
3. The application will create a `data/` directory automatically for storing logs

**Note**: The executable is a single-file distribution with no dependencies required.

### For Developers

#### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)

#### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/netscope.git
   cd netscope
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python -m netscope.main
   ```

## Building Windows Executable

### Using PyInstaller

1. **Install PyInstaller** (if not already installed)
   ```bash
   pip install pyinstaller
   ```

2. **Build the executable**
   ```bash
   pyinstaller --onefile --noconsole --name NetScope --icon=netscope/assets/icons/app_icon.ico netscope/main.py
   ```

   Or use the provided spec file:
   ```bash
   pyinstaller NetScope.spec
   ```

3. **Find the executable**
   - The executable will be in the `dist/` directory
   - File: `dist/NetScope.exe`

### Build Configuration

The application includes a `NetScope.spec` file for PyInstaller with optimized settings:
- Single-file executable (`--onefile`)
- No console window (`--noconsole`)
- Hidden imports included
- Version information embedded

## Project Structure

```
NetScope/
│
├── netscope/
│   ├── main.py              # Application entry point
│   ├── ui/
│   │   ├── main_window.py   # Main UI window
│   │   └── resources/       # UI resources
│   ├── core/
│   │   ├── network_monitor.py  # Network monitoring logic
│   │   ├── system_monitor.py    # System monitoring logic
│   │   └── data_manager.py      # Database management
│   ├── utils/
│   │   ├── logger.py        # Logging utility
│   │   └── exporter.py      # Export functionality
│   └── assets/
│       └── icons/            # Application icons
│
├── build/                    # Build artifacts (auto-generated)
├── dist/                     # Distribution files (executable)
├── data/                     # SQLite database and logs
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── LICENSE                   # MIT License
├── changelog.md              # Version changelog
└── NetScope.spec            # PyInstaller spec file
```

## Usage

### Starting the Application

Simply run the executable or start the Python script. The application will:
1. Automatically detect active network adapters
2. Start monitoring network and system statistics
3. Begin logging data to the SQLite database
4. Display real-time graphs and statistics

### Monitoring Features

- **Network Adapters**: The application automatically detects which network interfaces are active
- **Speed Monitoring**: Upload/download speeds update in real-time
- **Ping Monitoring**: Continuous ping to Google (8.8.8.8), Cloudflare (1.1.1.1), and OpenDNS (208.67.222.222)
- **Speed Tests**: Automatic speed tests run every 5 minutes when the app is active

### Data Export

1. Navigate to the "Logs & Export" tab
2. Click "Export to CSV" or "Export to JSON"
3. Choose a location to save the file
4. The exported file contains all network statistics from the database

### Graph Customization

- **Time Window**: Select from 30 seconds to 24 hours to view different time ranges
- **Refresh Rate**: Adjust update frequency (1s, 3s, or 5s) for performance optimization

## Technical Details

### Tech Stack
- **GUI Framework**: PyQt5
- **System Monitoring**: psutil
- **Network Testing**: speedtest-cli
- **IP Information**: ipinfo.io API
- **Graph Visualization**: pyqtgraph
- **Database**: SQLite3

### Database Schema

The application uses SQLite with the following tables:
- `network_stats`: Network statistics over time
- `system_stats`: System resource usage over time
- `speed_tests`: Speed test results
- `system_events`: Application events (startup, shutdown, etc.)

### Performance

- **Memory Usage**: Typically 50-100 MB
- **CPU Usage**: < 1% on modern systems
- **Disk Usage**: Database grows ~1-5 MB per day depending on activity

## Troubleshooting

### Application won't start
- Ensure Python 3.11+ is installed (for source code)
- Check that all dependencies are installed
- On Windows, ensure Microsoft Visual C++ Redistributable is installed

### No network data displayed
- Check that you have an active network connection
- Verify that network adapters are enabled
- Check Windows Firewall settings

### Speed test fails
- Ensure you have an active internet connection
- Check firewall settings
- Some networks may block speed test servers

### Database errors
- Ensure write permissions in the application directory
- Check available disk space
- Try deleting the `data/` directory and restarting

## Version History

See [changelog.md](changelog.md) for detailed version history.

### Current Version: v1.0.0
- Core monitoring features
- Dark mode UI
- Logging and export functionality
- Real-time graphing

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)
- Uses [psutil](https://github.com/giampaolo/psutil) for system monitoring
- Graph visualization powered by [pyqtgraph](https://www.pyqtgraph.org/)

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**NetScope v1.0.0** - Professional Network and System Monitoring
