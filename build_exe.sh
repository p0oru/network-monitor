#!/bin/bash
# Build script for NetScope executable (Linux/Mac)

echo "Building NetScope executable..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Install/upgrade PyInstaller if needed
echo "Installing/updating PyInstaller..."
pip3 install --upgrade pyinstaller

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Build executable
echo "Building executable..."
pyinstaller --onefile --name NetScope --add-data "data:data" netscope/main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "Build failed!"
    exit 1
fi

echo ""
echo "Build complete!"
echo "Executable location: dist/NetScope"
echo ""
