#!/bin/bash
# Complete test of Morphik chat API

echo "=== Testing Morphik Chat API ==="
echo

# First, let's create a new chat
echo "1. Creating a new chat:"
CHAT_RESPONSE=$(curl -s -X POST http://localhost:8000/chats \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Chat"}')

echo "Chat response: $CHAT_RESPONSE"
CHAT_ID=$(echo $CHAT_RESPONSE | jq -r '.id' 2>/dev/null)

if [ -z "$CHAT_ID" ] || [ "$CHAT_ID" = "null" ]; then
    echo "Failed to create chat. Response: $CHAT_RESPONSE"
    exit 1
fi

echo "Created chat with ID: $CHAT_ID"
echo

# Now test chat completion
echo "2. Testing chat completion with Ollama model:"
curl -X POST "http://localhost:8000/document/chat/$CHAT_ID/complete" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Hello! Can you hear me? Please respond with a simple greeting."
      }
    ],
    "model": "ollama_llama",
    "temperature": 0.7,
    "stream": false
  }' \
  -v 2>&1 | grep -E "(< HTTP|{|content|error)" | head -30
echo

# Test with streaming
echo "3. Testing streaming chat completion:"
curl -X POST "http://localhost:8000/document/chat/$CHAT_ID/complete" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [
      {
        "role": "user", 
        "content": "Say hello in one word"
      }
    ],
    "model": "ollama_llama",
    "stream": true
  }' \
  --no-buffer 2>&1 | head -20

echo
echo "4. Available models from /custom:"
curl -s http://localhost:8000/custom | jq '.[].id' | head -10

echo
echo "5. Checking recent errors in backend logs:"
docker logs morphik-core-morphik-1 --tail 100 2>&1 | grep -E "(ERROR|Exception|Failed|claude_opus)" | tail -20