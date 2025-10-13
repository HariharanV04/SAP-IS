@echo off
REM IS-Migration Platform - Simple Launcher
REM This script starts the Python launcher

echo Starting IS-Migration Platform...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://python.org/
    pause
    exit /b 1
)

REM Check if launcher dependencies are installed
python -c "import psutil, requests" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Installing launcher dependencies...
    pip install -r launcher_requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo Warning: Could not install dependencies automatically
        echo Please run: pip install psutil requests
        echo.
    )
)

REM Start the Python launcher
python platform_launcher.py

pause
