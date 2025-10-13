#!/bin/bash

# Colors for better visibility
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo "IS-Migration Platform - Stop All Servers"
echo "========================================"
echo

echo -e "${BLUE}Stopping all IS-Migration servers...${NC}"
echo

# Function to stop server by port
stop_by_port() {
    local port=$1
    local name=$2
    
    echo -e "${BLUE}Stopping $name (Port $port)...${NC}"
    
    # Find and kill processes using the port
    local pids=$(lsof -ti:$port 2>/dev/null)
    
    if [ ! -z "$pids" ]; then
        echo $pids | xargs kill -TERM 2>/dev/null
        sleep 2
        
        # Force kill if still running
        local remaining_pids=$(lsof -ti:$port 2>/dev/null)
        if [ ! -z "$remaining_pids" ]; then
            echo $remaining_pids | xargs kill -KILL 2>/dev/null
        fi
        
        echo -e "${GREEN}$name stopped${NC}"
    else
        echo -e "${YELLOW}$name was not running${NC}"
    fi
}

# Stop servers by port
stop_by_port 5000 "Main API"
stop_by_port 5001 "MuleToIS API"
stop_by_port 5002 "Gemma-3 API"
stop_by_port 5003 "BoomiToIS API"
stop_by_port 5173 "Frontend"

# Stop servers using PID file if it exists
if [ -f "logs/server_pids.txt" ]; then
    echo -e "${YELLOW}Stopping servers using PID file...${NC}"
    
    while read pid; do
        if [ ! -z "$pid" ] && kill -0 $pid 2>/dev/null; then
            echo -e "${BLUE}Stopping process $pid...${NC}"
            kill -TERM $pid 2>/dev/null
            sleep 1
            
            # Force kill if still running
            if kill -0 $pid 2>/dev/null; then
                kill -KILL $pid 2>/dev/null
            fi
        fi
    done < logs/server_pids.txt
    
    # Remove PID file
    rm -f logs/server_pids.txt
fi

echo
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}All servers have been stopped!${NC}"
echo -e "${GREEN}========================================${NC}"
echo

# Clean up log files if they exist
if [ -d "logs" ]; then
    echo -e "${YELLOW}Cleaning up log files...${NC}"
    rm -f logs/*.log
    echo -e "${GREEN}Log files cleaned up.${NC}"
fi

echo -e "${GREEN}All IS-Migration servers have been stopped successfully.${NC}"
echo
