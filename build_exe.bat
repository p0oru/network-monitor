@echo off
REM Build script for NetScope Windows executable

echo Building NetScope executable...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install/upgrade PyInstaller if needed
echo Installing/updating PyInstaller...
pip install --upgrade pyinstaller

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build executable
echo Building executable...
pyinstaller --onefile --noconsole --name NetScope --add-data "data;data" netscope/main.py

if errorlevel 1 (
    echo.
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build complete!
echo Executable location: dist\NetScope.exe
echo.
pause
