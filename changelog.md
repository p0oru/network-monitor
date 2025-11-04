# Changelog

All notable changes to NetScope will be documented in this file.

## [1.0.0] - 2025-01-XX

### Added
- Initial release of NetScope
- Real-time network monitoring with active adapter detection
- Network statistics display (upload/download speeds, ping latency, data usage)
- Public IP, ISP, and location information
- System statistics monitoring (CPU, RAM, Disk usage, uptime)
- Real-time graph visualization for network speed and CPU usage
- Adjustable time windows (30s, 5m, 10m, 30m, 1h, 24h)
- Adjustable refresh rates (1s, 3s, 5s)
- Speed testing functionality with automatic periodic tests
- SQLite database for historical data storage
- Export functionality to CSV and JSON
- Application logging console with terminal-style output
- Dark theme UI with modern, minimalist design
- System tray icon support
- Tabbed interface (Overview, Graphs, Logs & Exports)
- Session data tracking (total data usage since app start)

### Technical
- Built with PyQt5 for desktop GUI
- Uses psutil for system monitoring
- Uses speedtest-cli for bandwidth testing
- Uses pyqtgraph for real-time graph visualization
- Uses requests for IP information
- Single-file executable build support with PyInstaller

## [1.0.1] - Planned

### Planned
- Optimized speed test performance
- Export functionality improvements
- Bug fixes and stability improvements

## [1.0.2] - Planned

### Planned
- Enhanced system tray functionality
- Improved graph scaling and visualization
- Better error handling

## [1.1.0] - Planned

### Planned
- Plugin system for additional data modules
- Customizable dashboard layouts
- Advanced filtering and data analysis
