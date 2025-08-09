#!/bin/bash

# Start Local Development Environment
# This script starts the local development environment connected to the remote server

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Morphik Local Development Setup     ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════╝${NC}"
echo ""

# Load environment variables
if [ -f .env.server ]; then
    echo -e "${GREEN}✓ Loading server configuration from .env.server${NC}"
    export $(cat .env.server | grep -v '^#' | xargs)
else
    echo -e "${RED}✗ .env.server file not found!${NC}"
    echo "Please create .env.server with your server configuration"
    exit 1
fi

# Check what to start
MODE=${1:-both}  # both, api, ui

case $MODE in
    api)
        echo -e "${YELLOW}Starting API only...${NC}"
        ;;
    ui)
        echo -e "${YELLOW}Starting UI only...${NC}"
        ;;
    both)
        echo -e "${YELLOW}Starting both API and UI...${NC}"
        ;;
    *)
        echo -e "${RED}Invalid mode: $MODE${NC}"
        echo "Usage: $0 [api|ui|both]"
        exit 1
        ;;
esac

# Stop any existing local services
echo -e "${YELLOW}Stopping existing local services...${NC}"
docker-compose -f docker-compose.dev.yml down 2>/dev/null

# Setup SSH tunnels
echo ""
echo -e "${YELLOW}Setting up SSH tunnels...${NC}"
./setup-ssh-tunnels.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to setup SSH tunnels${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Starting development services...${NC}"

# Start services based on mode
if [ "$MODE" = "api" ] || [ "$MODE" = "both" ]; then
    echo -e "${BLUE}Starting API on port ${LOCAL_API_PORT:-8001}...${NC}"
    docker-compose -f docker-compose.dev.yml --env-file .env.server up -d morphik-dev
fi

if [ "$MODE" = "ui" ] || [ "$MODE" = "both" ]; then
    echo -e "${BLUE}Starting UI on port ${LOCAL_UI_PORT:-3001}...${NC}"
    
    # Check if we should use Docker or npm
    if [ -f "ee/ui-component/package.json" ]; then
        echo -e "${YELLOW}Using npm for UI development (recommended)${NC}"
        cd ee/ui-component
        
        # Update .env.local
        echo "NEXT_PUBLIC_API_URL=http://localhost:${LOCAL_API_PORT:-8001}" > .env.local
        
        # Install dependencies if needed
        if [ ! -d "node_modules" ]; then
            echo -e "${YELLOW}Installing dependencies...${NC}"
            npm install
        fi
        
        # Start in new terminal if possible
        if command -v gnome-terminal &> /dev/null; then
            gnome-terminal -- bash -c "npm run dev; exec bash"
        elif command -v osascript &> /dev/null; then
            osascript -e "tell app \"Terminal\" to do script \"cd $(pwd) && npm run dev\""
        else
            npm run dev &
        fi
        
        cd ../..
    else
        docker-compose -f docker-compose.dev.yml --env-file .env.server up -d ui-dev
    fi
fi

# Wait for services to start
echo ""
echo -e "${YELLOW}Waiting for services to start...${NC}"
sleep 5

# Show status
echo ""
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}Development environment is ready!${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""

if [ "$MODE" = "api" ] || [ "$MODE" = "both" ]; then
    echo -e "${BLUE}API:${NC} http://localhost:${LOCAL_API_PORT:-8001}"
    echo -e "  - Connected to PostgreSQL on ${SERVER_IP}"
    echo -e "  - Connected to Redis on ${SERVER_IP}"
    echo -e "  - Connected to Ollama on ${SERVER_IP}"
fi

if [ "$MODE" = "ui" ] || [ "$MODE" = "both" ]; then
    echo -e "${BLUE}UI:${NC} http://localhost:${LOCAL_UI_PORT:-3001}"
fi

echo ""
echo -e "${YELLOW}Server services:${NC}"
echo -e "  - Production UI: http://${SERVER_IP}:3000"
echo -e "  - Production API: http://${SERVER_IP}:8000"

echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  - View logs: docker-compose -f docker-compose.dev.yml logs -f"
echo "  - Stop services: docker-compose -f docker-compose.dev.yml down"
echo "  - Stop SSH tunnels: ps aux | grep 'ssh.*${SERVER_IP}' | grep -v grep | awk '{print \$2}' | xargs kill"

echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"