#!/bin/bash

# Colors for better visibility
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo "IS-Migration Platform - Start All Servers"
echo "========================================"
echo

echo -e "${BLUE}Starting all servers for IS-Migration platform...${NC}"
echo

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed or not in PATH${NC}"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if Python is installed
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python is not installed or not in PATH${NC}"
    echo "Please install Python from https://python.org/"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

echo -e "${GREEN}Prerequisites check passed!${NC}"
echo

# Create logs directory if it doesn't exist
mkdir -p logs

echo -e "${YELLOW}Starting servers in background...${NC}"
echo

# Function to start a server and log output
start_server() {
    local name="$1"
    local port="$2"
    local directory="$3"
    local command="$4"
    
    echo -e "${BLUE}Starting $name (Port $port)...${NC}"
    
    # Start server in background and redirect output to log file
    cd "$directory" && $command > "../logs/${name,,}-${port}.log" 2>&1 &
    local pid=$!
    
    # Store PID for later cleanup
    echo $pid >> logs/server_pids.txt
    
    # Go back to original directory
    cd - > /dev/null
    
    # Wait a moment for server to start
    sleep 3
    
    echo -e "${GREEN}$name started with PID $pid${NC}"
}

# Clean up any existing PID file
rm -f logs/server_pids.txt

# Start all servers
start_server "Main-API" "5000" "app" "$PYTHON_CMD app.py"
start_server "BoomiToIS-API" "5003" "BoomiToIS-API" "$PYTHON_CMD app.py"
start_server "MuleToIS-API" "5001" "MuleToIS-API" "$PYTHON_CMD app.py"
start_server "Gemma3-API" "5002" "MuleToIS-API-Gemma3" "$PYTHON_CMD app.py"

# Start Frontend
echo -e "${BLUE}Starting Frontend (Port 5173)...${NC}"
cd IFA-Project/frontend && npm run dev > ../../logs/frontend-5173.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID >> ../../logs/server_pids.txt
cd - > /dev/null
sleep 5
echo -e "${GREEN}Frontend started with PID $FRONTEND_PID${NC}"

echo
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}All servers are running!${NC}"
echo -e "${GREEN}========================================${NC}"
echo
echo -e "${YELLOW}Server URLs:${NC}"
echo -e "${BLUE}Frontend:        ${NC}http://localhost:5173"
echo -e "${BLUE}Main API:        ${NC}http://localhost:5000"
echo -e "${BLUE}BoomiToIS API:   ${NC}http://localhost:5003"
echo -e "${BLUE}MuleToIS API:    ${NC}http://localhost:5001"
echo -e "${BLUE}Gemma-3 API:     ${NC}http://localhost:5002"
echo
echo -e "${YELLOW}Logs are available in the 'logs' directory${NC}"
echo -e "${YELLOW}Server PIDs are stored in logs/server_pids.txt${NC}"
echo
echo -e "${GREEN}Waiting 10 seconds for all servers to fully start...${NC}"
sleep 10

# Try to open browser (works on most systems)
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5173
elif command -v open &> /dev/null; then
    open http://localhost:5173
else
    echo -e "${YELLOW}Please open http://localhost:5173 in your browser${NC}"
fi

echo
echo -e "${GREEN}All servers started successfully!${NC}"
echo -e "${YELLOW}To stop all servers, run: ./stop-all-servers.sh${NC}"
echo -e "${YELLOW}Press Ctrl+C to exit this script (servers will continue running)${NC}"

# Keep script running to show status
while true; do
    sleep 30
    echo -e "${BLUE}[$(date)] All servers are running...${NC}"
done
