#!/bin/bash
# Test script to check if models are working through the API

echo "=== Testing Morphik Models API ==="
echo

# Test 1: Get available models
echo "1. Getting available models from /custom endpoint:"
curl -s http://localhost:8000/custom | jq '.' | head -20
echo

# Test 2: Check Ollama directly
echo "2. Checking Ollama service directly:"
curl -s http://localhost:11434/api/tags | jq '.' 2>/dev/null || echo "Ollama not accessible"
echo

# Test 3: Test chat completion with Ollama model
echo "3. Testing chat completion with Ollama model (llama3.2:3b):"
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Say hello if you can hear me"}],
    "model": "ollama_llama",
    "stream": false
  }' \
  -v 2>&1 | grep -E "(< HTTP|{|error)" | head -20
echo

# Test 4: Check backend logs for errors
echo "4. Recent backend errors:"
docker logs morphik-core-morphik-1 --tail 50 2>&1 | grep -E "(ERROR|WARN|Exception|traceback)" | tail -10
echo

# Test 5: Test with different model format
echo "5. Testing with different model ID format:"
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Test message"}],
    "model": "ollama/llama3.2:3b",
    "stream": false
  }' \
  -s | jq '.' 2>/dev/null || echo "Request failed"