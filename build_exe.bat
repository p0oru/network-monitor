@echo off
REM Build script for Windows executable
echo Building NetScope executable...

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Build the executable
echo Running PyInstaller...
pyinstaller --clean NetScope.spec

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build complete! Executable is in the dist/ directory.
echo File: dist\NetScope.exe
pause
