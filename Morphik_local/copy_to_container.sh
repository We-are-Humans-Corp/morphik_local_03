#!/bin/bash
# Script to copy all necessary files to the running container

echo "Copying updated files to container..."

# Copy route files
docker cp core/routes/auth.py morphik-core-morphik-1:/app/core/routes/auth.py
docker cp core/routes/models.py morphik-core-morphik-1:/app/core/routes/models.py
docker cp core/routes/model_config.py morphik-core-morphik-1:/app/core/routes/model_config.py

# Copy model files
docker cp core/models/user.py morphik-core-morphik-1:/app/core/models/user.py

# Copy main API file (in case auth router needs to be registered)
docker cp core/api.py morphik-core-morphik-1:/app/core/api.py

echo "All files copied successfully!"
echo "Restarting backend container..."
docker restart morphik-core-morphik-1

echo "Waiting for backend to start..."
sleep 15

echo "Testing endpoints..."
echo "1. Testing /custom endpoint:"
curl -s http://localhost:8000/custom | head -c 100
echo -e "\n\n2. Testing /model-config/ endpoint:"
curl -s http://localhost:8000/model-config/
echo -e "\n\n3. Testing /auth/register endpoint:"
curl -s http://localhost:8000/auth/register -X POST -H "Content-Type: application/json" -d '{"username": "test", "password": "test"}' | head -c 100

echo -e "\n\nDone!"