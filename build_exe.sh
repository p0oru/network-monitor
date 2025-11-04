#!/bin/bash
# Build script for Linux/Mac executable

echo "Building NetScope executable..."

# Check if PyInstaller is installed
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Build the executable
echo "Running PyInstaller..."
pyinstaller --clean NetScope.spec

if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi

echo ""
echo "Build complete! Executable is in the dist/ directory."
echo "File: dist/NetScope"
