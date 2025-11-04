# NetScope Quick Start Guide

## Installation

### For Windows Users (Executable)
1. Download `NetScope.exe` from releases
2. Double-click to run
3. No installation required!

### For Developers
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python -m netscope.main
```

## Building Executable

### Windows
```bash
build_exe.bat
```

### Linux/Mac
```bash
./build_exe.sh
```

## First Run

1. The application will automatically:
   - Detect active network adapters
   - Start monitoring network and system stats
   - Create a `data/` directory for logs
   - Begin real-time graph updates

2. Navigate between tabs:
   - **Overview**: All statistics in one place
   - **Graphs**: Real-time visualizations
   - **Logs & Export**: Application logs and data export

## Features

- **Automatic Monitoring**: No configuration needed
- **Real-time Updates**: See stats update live
- **Historical Data**: All data saved to SQLite database
- **Export**: Export to CSV or JSON anytime

## Troubleshooting

- **No network data**: Check your internet connection
- **Import errors**: Ensure all dependencies are installed: `pip install -r requirements.txt`
- **Database errors**: Check write permissions in the application directory
