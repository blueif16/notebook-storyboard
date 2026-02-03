#!/bin/bash

# Colors for output
YELLOW=$'\033[0;33m'
GREEN=$'\033[0;32m'
NC=$'\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "${YELLOW}Clearing all caches...${NC}"

# Clear Python caches
echo -e "${YELLOW}  - Clearing Python __pycache__...${NC}"
find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$PROJECT_ROOT" -type f -name "*.pyo" -delete 2>/dev/null || true
find "$PROJECT_ROOT" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

# Clear Next.js cache
if [ -d "$FRONTEND_DIR/.next" ]; then
    echo -e "${YELLOW}  - Clearing Next.js .next cache...${NC}"
    rm -rf "$FRONTEND_DIR/.next"
fi

# Clear node_modules cache
if [ -d "$FRONTEND_DIR/node_modules/.cache" ]; then
    echo -e "${YELLOW}  - Clearing node_modules cache...${NC}"
    rm -rf "$FRONTEND_DIR/node_modules/.cache"
fi

# Clear .DS_Store files
find "$PROJECT_ROOT" -name ".DS_Store" -delete 2>/dev/null || true

echo -e "${GREEN}Cache cleared successfully!${NC}"
