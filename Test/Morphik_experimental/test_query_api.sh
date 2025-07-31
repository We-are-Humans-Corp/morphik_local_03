#!/bin/bash
# Test Morphik query API with different models

echo "=== Testing Morphik Query API ==="
echo

# Test with Ollama model
echo "1. Testing with Ollama model (llama3.2:3b):"
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Hello, can you respond with a simple greeting?",
    "llm_config": {
      "model": "ollama_llama"
    },
    "stream_response": false
  }' \
  -s | jq '.' 2>/dev/null || echo "Query failed"

echo
echo "2. Testing streaming with Ollama model:"
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "query": "Say hello",
    "llm_config": {
      "model": "ollama_llama"
    },
    "stream_response": true
  }' \
  --no-buffer 2>&1 | head -20

echo
echo "3. Checking if models are properly loaded:"
docker exec morphik-core-morphik-1 cat /app/morphik.toml | grep -A2 -B2 "claude_opus"