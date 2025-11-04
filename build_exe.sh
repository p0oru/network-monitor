#!/bin/bash

echo "Building NetScope executable..."
echo ""

# Clean previous builds
rm -rf build dist

# Run PyInstaller
pyinstaller --clean NetScope.spec

echo ""
if [ -f "dist/NetScope" ] || [ -f "dist/NetScope.exe" ]; then
    echo "Build successful! Executable is in dist/"
else
    echo "Build failed! Check the output above for errors."
fi