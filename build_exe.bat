@echo off
REM Build script for NetScope Windows executable
REM Run this script to build NetScope.exe

echo Building NetScope executable...
echo.

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Run PyInstaller
pyinstaller NetScope.spec

echo.
echo Build complete!
echo Executable location: dist\NetScope.exe
echo.
pause
