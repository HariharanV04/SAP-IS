#!/bin/bash
# IS-Migration Platform - Simple Launcher
# This script starts the Python launcher

echo "Starting IS-Migration Platform..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    echo "Please install Python3"
    exit 1
fi

# Check if launcher dependencies are installed
python3 -c "import psutil, requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing launcher dependencies..."
    pip3 install -r launcher_requirements.txt
    if [ $? -ne 0 ]; then
        echo "Warning: Could not install dependencies automatically"
        echo "Please run: pip3 install psutil requests"
        echo
    fi
fi

# Make the launcher executable
chmod +x platform_launcher.py

# Start the Python launcher
python3 platform_launcher.py
