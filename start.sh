#!/bin/bash

# Colors for output
GREEN=$'\033[0;32m'
BLUE=$'\033[0;34m'
RED=$'\033[0;31m'
YELLOW=$'\033[0;33m'
NC=$'\033[0m' # No Color

# Get the project root directory (where this script is located)
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/new_front"

echo -e "${BLUE}Starting HyperBookLM Application...${NC}"

# Clear all caches (commented out - use clear-cache.sh if needed)
# echo -e "${YELLOW}Clearing all caches...${NC}"

# Clear Python caches
# echo -e "${YELLOW}  - Clearing Python __pycache__...${NC}"
# find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
# find "$PROJECT_ROOT" -type f -name "*.pyc" -delete 2>/dev/null || true
# find "$PROJECT_ROOT" -type f -name "*.pyo" -delete 2>/dev/null || true
# find "$PROJECT_ROOT" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

# Clear Next.js cache
# if [ -d "$FRONTEND_DIR/.next" ]; then
#     echo -e "${YELLOW}  - Clearing Next.js .next cache...${NC}"
#     rm -rf "$FRONTEND_DIR/.next"
# fi

# Clear node_modules cache
# if [ -d "$FRONTEND_DIR/node_modules/.cache" ]; then
#     echo -e "${YELLOW}  - Clearing node_modules cache...${NC}"
#     rm -rf "$FRONTEND_DIR/node_modules/.cache"
# fi

# Clear .DS_Store files
# find "$PROJECT_ROOT" -name ".DS_Store" -delete 2>/dev/null || true

# echo -e "${GREEN}Cache cleared successfully!${NC}\n"

# Activate virtual environment
if [ -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source "$PROJECT_ROOT/.venv/bin/activate"
elif [ -d "$BACKEND_DIR/.venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source "$BACKEND_DIR/.venv/bin/activate"
else
    echo -e "${RED}Warning: Virtual environment not found${NC}"
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${RED}Shutting down services...${NC}"
    kill 0
}

trap cleanup SIGINT SIGTERM

# Start Unified Backend (port 8005)
echo -e "${GREEN}Starting Unified Backend Server (port 8005)...${NC}"
echo -e "${BLUE}Handles REST API + AG-UI Streaming${NC}"
cd "$BACKEND_DIR"
python run_server.py 2>&1 | sed "s/^/[${YELLOW}BACKEND${NC}] /" &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start Frontend
echo -e "${GREEN}Starting Frontend Server...${NC}"
cd "$FRONTEND_DIR"
npm run dev 2>&1 | sed "s/^/[${BLUE}FRONTEND${NC}] /" &
FRONTEND_PID=$!

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}HyperBookLM is running!${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Backend:         http://localhost:8005"
echo -e "API Docs:        http://localhost:8005/docs"
echo -e "AG-UI Stream:    http://localhost:8005/storybook"
echo -e "Frontend:        http://localhost:3848"
echo -e "\nPress Ctrl+C to stop all services"
echo -e "${BLUE}========================================${NC}\n"

# Wait for both processes
wait
