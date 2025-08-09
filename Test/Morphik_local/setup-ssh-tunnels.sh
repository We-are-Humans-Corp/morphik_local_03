#!/bin/bash

# SSH Tunnel Setup Script for Morphik Development
# This script creates SSH tunnels to access PostgreSQL and Redis on the remote server

# Load environment variables
if [ -f .env.server ]; then
    export $(cat .env.server | grep -v '^#' | xargs)
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Morphik SSH Tunnel Setup${NC}"
echo "=============================="

# Check if SERVER_IP is set
if [ -z "$SERVER_IP" ]; then
    echo -e "${RED}Error: SERVER_IP not set in .env.server${NC}"
    exit 1
fi

# Function to check if port is already in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to create SSH tunnel
create_tunnel() {
    local local_port=$1
    local remote_port=$2
    local service_name=$3
    
    if check_port $local_port; then
        echo -e "${YELLOW}Port $local_port already in use. Checking if it's our tunnel...${NC}"
        # Check if it's our SSH tunnel
        if ps aux | grep -v grep | grep "ssh.*$local_port:localhost:$remote_port.*$SERVER_IP" > /dev/null; then
            echo -e "${GREEN}✓ $service_name tunnel already running on port $local_port${NC}"
            return 0
        else
            echo -e "${RED}✗ Port $local_port is used by another process${NC}"
            return 1
        fi
    fi
    
    echo -e "${YELLOW}Creating $service_name tunnel (localhost:$local_port -> $SERVER_IP:$remote_port)...${NC}"
    ssh -N -L $local_port:localhost:$remote_port root@$SERVER_IP -f
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $service_name tunnel created successfully${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed to create $service_name tunnel${NC}"
        return 1
    fi
}

# Create tunnels
echo ""
create_tunnel 5432 5432 "PostgreSQL"
create_tunnel 6379 6379 "Redis"

# Test connections
echo ""
echo -e "${YELLOW}Testing connections...${NC}"

# Test PostgreSQL
if PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -p 5432 -U $POSTGRES_USER -d $POSTGRES_DB -c '\q' 2>/dev/null; then
    echo -e "${GREEN}✓ PostgreSQL connection successful${NC}"
else
    echo -e "${RED}✗ PostgreSQL connection failed${NC}"
fi

# Test Redis
if redis-cli -h localhost -p 6379 ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis connection successful${NC}"
else
    echo -e "${RED}✗ Redis connection failed${NC}"
fi

# Test Ollama (direct connection)
if curl -s http://$SERVER_IP:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ollama connection successful${NC}"
else
    echo -e "${YELLOW}⚠ Ollama connection failed (may not be exposed externally)${NC}"
fi

echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "To start development:"
echo "1. Run: docker-compose -f docker-compose.dev.yml --env-file .env.server up"
echo "2. Or for UI development: cd ee/ui-component && npm run dev"
echo ""
echo "To stop tunnels:"
echo "ps aux | grep 'ssh.*$SERVER_IP' | grep -v grep | awk '{print \$2}' | xargs kill"