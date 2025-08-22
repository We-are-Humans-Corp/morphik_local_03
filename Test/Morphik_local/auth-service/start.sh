#!/bin/bash

echo "Starting Morphik Auth Service..."
echo "================================"
echo ""
echo "Service will be available at:"
echo "  Main page: http://localhost:8080"
echo "  Login:     http://localhost:8080/login.html"
echo "  Register:  http://localhost:8080/register.html"
echo ""
echo "API Backend: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop"
echo "================================"
echo ""

python3 server.py