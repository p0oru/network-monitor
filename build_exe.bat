@echo off
echo Building NetScope executable...
echo.

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Run PyInstaller
pyinstaller --clean NetScope.spec

echo.
if exist dist\NetScope.exe (
    echo Build successful! Executable is in dist\NetScope.exe
) else (
    echo Build failed! Check the output above for errors.
)

pause