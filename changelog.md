# NetScope Changelog

## Version 1.0.0 (Initial Release)

### Features
- Real-time network monitoring with automatic adapter detection
- Display of upload/download speeds, ping latency, and data usage
- Public IP, ISP, and location information
- System statistics: CPU, RAM, disk usage, and uptime
- Real-time graphs for network speed and CPU usage
- Adjustable time windows (30s, 5m, 10m, 30m, 1h, 24h)
- Adjustable refresh rates (1s, 3s, 5s)
- Automatic data logging to SQLite database
- Export functionality (CSV and JSON)
- Application log console
- Dark mode UI with smooth animations
- Automatic speed tests every few minutes
- System tray icon support (optional)

### Technical Details
- Built with PyQt5 for cross-platform compatibility
- Uses psutil for system monitoring
- SQLite database for historical data storage
- pyqtgraph for real-time graph visualization
- Single-file Windows executable support

### Known Issues
- Speed test may take time on slower connections
- First IP lookup may be slow on initial startup

## Future Updates

### v1.0.1 (Planned)
- Optimized speed test with better error handling
- Export functionality improvements
- Bug fixes

### v1.0.2 (Planned)
- System tray icon implementation
- Better graph scaling
- Performance optimizations

### v1.1.0 (Planned)
- Plugin system for additional data modules
- Customizable dashboard layouts
- Advanced filtering options
