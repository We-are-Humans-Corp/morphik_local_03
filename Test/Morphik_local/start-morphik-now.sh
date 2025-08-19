#!/bin/bash

# Start Morphik containers
echo "Starting Morphik containers..."

# Change to project directory
cd /Users/fedor/PycharmProjects/PythonProject/Morphik_local/Test/Morphik_local

# Use docker compose to start containers
/usr/local/bin/docker compose -f docker-compose.local.yml up -d

# Check if containers started
sleep 3
/usr/local/bin/docker ps | grep morphik

echo "Containers should be running now!"
echo "API: http://localhost:8000"
echo "UI: http://localhost:3001"