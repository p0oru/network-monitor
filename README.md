# Network Monitor Dashboard

A cross-platform desktop application built with Python and Flask that displays real-time network statistics including upload/download speeds, ping latency, connected devices, active ports, and historical data visualizations. Features automatic GitHub synchronization and packages as a standalone Windows executable.

## Tech Stack

- **Backend:** Python 3.12+, Flask, psutil, speedtest-cli
- **Frontend:** HTML, CSS, Chart.js
- **Database:** SQLite
- **Packaging:** PyInstaller

## Installation

**For End Users:** Download the pre-built executable from Releases (no Python installation required).

**For Developers:**

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and configure GitHub credentials
6. (Optional) Configure GitHub auto-sync: Copy `.env.example` to `.env` and fill in Git credentials
7. (Optional) Initialize Git repository: `git init` and add remote: `git remote add origin <your-repo-url>`
8. Run the application: `python app.py`

## Building Standalone Executable

### Prerequisites

- Python 3.12+
- All dependencies installed (`pip install -r requirements.txt`)
- PyInstaller is included in requirements.txt
- Recommended: Test the application in development mode first (`python app.py`)

### Build Command

**Using the spec file (recommended):**

```bash
pyinstaller NetworkMonitor.spec
```

**Alternative one-line command (if spec file doesn't exist):**

**Windows:**
```bash
pyinstaller --onefile --noconsole --name NetworkMonitor --add-data "templates;templates" --add-data "static;static" --hidden-import engineio.async_drivers.eventlet --hidden-import dns.resolver app.py
```

**Linux/Mac:**
```bash
pyinstaller --onefile --name NetworkMonitor --add-data "templates:templates" --add-data "static:static" --hidden-import engineio.async_drivers.eventlet --hidden-import dns.resolver app.py
```

Note: Windows uses semicolon (`;`), Linux/Mac uses colon (`:`) in `--add-data`.

**Important:** The `--noconsole` flag is Windows/macOS specific and not applicable on Linux. Linux builds will always be console binaries.

Build process takes 2-5 minutes depending on your system.

### Build Scripts

**Windows:** Double-click `build_exe.bat` or run from command prompt:
```bash
build_exe.bat
```

**Linux/Mac:** Make executable and run:
```bash
chmod +x build_exe.sh
./build_exe.sh
```

### Output Location

- **Executable:** `dist/NetworkMonitor.exe` (Windows) or `dist/NetworkMonitor` (Linux/Mac)
- **Build artifacts:** `build/` directory (can be deleted after successful build)
- **Spec file:** `NetworkMonitor.spec` (keep for future builds)

### First Run Setup

**What happens on first run:**
- Executable creates `data/` directory automatically
- Database (`network_logs.db`) is initialized with schema
- Browser opens automatically to `http://localhost:5000/`
- Application runs in background (no console window)

**Note:** First run may take 3-5 seconds due to extraction (one-file mode).

### Distribution

- **Single file distribution:** Just copy `NetworkMonitor.exe` to target machine
- **No Python installation required** on target machine
- **No additional dependencies needed**
- **Executable size:** Approximately 40-60 MB (includes Python runtime and all dependencies)
- **Optional:** Include `.env.example` for users who want GitHub sync

### Troubleshooting

#### Issue: Executable won't start or crashes immediately

**Solution:**
- Build with `console=True` in spec file to see error messages
- Run from command prompt to see output: `NetworkMonitor.exe`
- Check Windows Defender or antivirus (may flag PyInstaller executables)

#### Issue: "Failed to execute script" error

**Solution:**
- Missing hidden imports - check spec file hiddenimports list
- Rebuild with `--debug all` flag for detailed logs
- Common missing imports: eventlet, dns, engineio

#### Issue: Templates or static files not found (404 errors)

**Solution:**
- Verify `datas` parameter in spec file includes templates and static
- Check that paths use correct separator (`;` for Windows, `:` for Linux/Mac)
- Rebuild and test

#### Issue: Database not persisting between runs

**Solution:**
- Verify `config.py` uses `get_base_path()` for DATABASE_PATH
- Check that database is created in executable's directory, not temp folder
- Look for `data/` directory next to the .exe file

#### Issue: Port 5000 already in use

**Solution:**
- Change port in `.env` file: `FLASK_PORT=5001`
- Or kill process using port 5000: `netstat -ano | findstr :5000` then `taskkill /PID <pid> /F`

#### Issue: Slow startup (3-5 seconds)

**Explanation:** Normal for `--onefile` mode (extraction to temp directory)

**Solution:**
- Use `--onedir` mode for faster startup (creates folder instead of single file)
- Trade-off: Faster startup vs. single-file convenience

#### Issue: Antivirus flags executable as malware

**Explanation:** PyInstaller executables sometimes trigger false positives

**Solution:**
- Add exception in antivirus software
- Alternative: Code-sign the executable (requires certificate)
- Submit to antivirus vendors for whitelisting

### Advanced Build Options

#### Debug build (with console window)

Edit `NetworkMonitor.spec`, change `console=False` to `console=True`, then rebuild:
```bash
pyinstaller NetworkMonitor.spec
```

Use for troubleshooting startup issues.

#### Smaller executable (disable UPX compression)

Edit spec file, change `upx=True` to `upx=False`. Results in larger file but faster build and fewer compatibility issues.

#### One-folder distribution (faster startup)

Edit spec file:
- Uncomment COLLECT block
- Comment out or modify EXE block's one-file configuration

Results in `dist/NetworkMonitor/` folder with multiple files. Distribute entire folder, run `NetworkMonitor.exe` inside.

#### Custom icon

1. Create or obtain `app_icon.ico` file (256x256 recommended)
2. Place in `static/icons/` directory
3. Edit spec file, add `icon='static/icons/app_icon.ico'` to EXE block
4. Rebuild

### Clean Build

Remove old build artifacts before rebuilding:

**Windows:**
```bash
rmdir /s /q build dist
pyinstaller --clean NetworkMonitor.spec
```

**Linux/Mac:**
```bash
rm -rf build dist
pyinstaller --clean NetworkMonitor.spec
```

Recommended when changing spec file or dependencies.

## Features

- Real-time network monitoring with live graphs
- Connected devices scanner
- Speed test and port scanner tools
- Dark/light theme toggle
- Automatic GitHub synchronization (optional) - Requires Git credentials in .env file
- Exportable statistics to CSV
- Standalone executable - no Python installation required
- Auto-opens browser on startup
- Portable - runs from any directory

## Project Structure

```
network_monitor/
├── templates/          # HTML template files
├── static/             # Static assets
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript files
│   └── icons/          # Icon assets
├── data/               # SQLite database and exports
├── utils/              # Utility modules
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

## Network Statistics (Auto-Updated)

**Last Updated:** <!-- AUTO_UPDATE_TIMESTAMP -->2025-11-03T19:25:30.157636<!-- /AUTO_UPDATE_TIMESTAMP -->

**Average Speed (24h):** <!-- AUTO_UPDATE_SPEED -->0.4 Mbps down / 0.0 Mbps up<!-- /AUTO_UPDATE_SPEED -->

**Total Data Used:** <!-- AUTO_UPDATE_DATA -->17.81 GB<!-- /AUTO_UPDATE_DATA -->

**Network Uptime:** <!-- AUTO_UPDATE_UPTIME -->1m (24h window)<!-- /AUTO_UPDATE_UPTIME -->

**Connected Devices:** <!-- AUTO_UPDATE_DEVICES -->0 active<!-- /AUTO_UPDATE_DEVICES -->

*Automatically updated by GitHub Auto-Sync every 15 minutes*

## GitHub Auto-Sync

This application can automatically commit network statistics to GitHub:

- Syncs `data/network_logs.db` every 15 minutes (configurable)
- Updates README.md with latest statistics
- Requires Git credentials in `.env` file
- Enable/disable in Settings page

**Setup:**
1. Copy `.env.example` to `.env`
2. Fill in Git credentials (name, email, remote URL, token)
3. Initialize Git repository: `git init`
4. Add remote: `git remote add origin <your-repo-url>`
5. Enable sync in Settings page

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

**Note:** The "Network Statistics (Auto-Updated)" section is automatically updated by the application. Manual edits will be overwritten.

