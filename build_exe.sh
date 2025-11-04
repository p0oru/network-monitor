#!/bin/bash
# Build script for NetScope executable
# Run this script to build NetScope

echo "Building NetScope executable..."
echo

# Clean previous builds
rm -rf build dist

# Run PyInstaller
pyinstaller NetScope.spec

echo
echo "Build complete!"
echo "Executable location: dist/NetScope"
echo
