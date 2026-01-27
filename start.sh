#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Get the project root directory (where this script is located)
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "${BLUE}Starting HyperBookLM Application...${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${RED}Shutting down services...${NC}"
    kill 0
}

trap cleanup SIGINT SIGTERM

# Start Main Backend (port 8000)
echo -e "${GREEN}Starting Main Backend Server (port 8000)...${NC}"
cd "$BACKEND_DIR"
python run_server.py 2>&1 | sed "s/^/[${YELLOW}BACKEND${NC}] /" &
BACKEND_PID=$!

# Start Storybook AG-UI Service (port 8001)
echo -e "${GREEN}Starting Storybook AG-UI Service (port 8001)...${NC}"
cd "$BACKEND_DIR"
python run_agui_server.py 2>&1 | sed "s/^/[${YELLOW}AG-UI${NC}] /" &
AGUI_PID=$!

# Wait a bit for backends to start
sleep 3

# Start Frontend
echo -e "${GREEN}Starting Frontend Server...${NC}"
cd "$FRONTEND_DIR"
npm run dev 2>&1 | sed "s/^/[${BLUE}FRONTEND${NC}] /" &
FRONTEND_PID=$!

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}HyperBookLM is running!${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Main Backend:    http://localhost:8000"
echo -e "API Docs:        http://localhost:8000/docs"
echo -e "Storybook AG-UI: http://localhost:8001"
echo -e "Frontend:        http://localhost:3847"
echo -e "\nPress Ctrl+C to stop all services"
echo -e "${BLUE}========================================${NC}\n"

# Wait for both processes
wait
